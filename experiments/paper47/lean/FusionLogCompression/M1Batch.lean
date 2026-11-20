import RegisteredAbsorptionChains.Execution

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n : ℕ} {α : Type*} [NeZero n] [DecidableEq α]

/-- Chronological repetition of the two raw letters `p,d`. -/
def pdWord : ℕ → List Letter
  | 0 => []
  | k + 1 => pdWord k ++ [.p, .d]

/-- The compressed raw word for moving a packet at `q` across `f` holes. -/
def batchWord (q : ZMod n) (f : ℕ) : List Letter :=
  pWord (1 - q).val ++ [.d] ++ pdWord (f - 1) ++ pWord (q - f).val

/-- Remove the distinguished packet from the stationary background. -/
def eraseSite (q : ZMod n) (s : Placement n (Finset α)) : Placement n (Finset α) :=
  fun z => if z = q then none else s z

/-- The normalized frame after the initial `d` and `k` repeated `p,d` pairs. -/
def batchFrame (s : Placement n (Finset α)) (q : ZMod n) (B : Finset α)
    (k : ℕ) : Placement n (Finset α) :=
  fun z => if z = 0 then some B
    else rotate ((1 - q) + (k : ZMod n)) (eraseSite q s) z

/-- Exact physical placement after translating the packet from `q` to `q-f`. -/
def batchTarget (s : Placement n (Finset α)) (q : ZMod n) (f : ℕ) :
    Placement n (Finset α) :=
  fun z => if z = q - (f : ZMod n) then s q
    else if z = q then none else s z

def withPlaced (s : Execution n α) (p : Placement n (Finset α)) : Execution n α :=
  { s with placed := p }

/-- Explicit accounting for a constructed routing segment. -/
structure RouteBudget where
  batches : ℕ
  holeTransfers : ℕ
  rawLetters : ℕ

/-- One invocation of `batchWord` is one batch containing `f` hole transfers. -/
def batchWordBudget (q : ZMod n) (f : ℕ) : RouteBudget :=
  ⟨1, f, (batchWord q f).length⟩

theorem pWord_length (k : ℕ) : (pWord k).length = k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pWord, ih]

theorem pdWord_length (k : ℕ) : (pdWord k).length = 2 * k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pdWord, ih, Nat.mul_succ]

/-- Literal letter cost; no macro is assigned unit cost. -/
theorem batchWord_length (q : ZMod n) (f : ℕ) :
    (batchWord q f).length = (1 - q).val + 1 + 2 * (f - 1) + (q - f).val := by
  simp [batchWord, pWord_length, pdWord_length]
  omega

/-- The least-residue exponents save one rotation per transferred hole. -/
theorem batchWord_length_le (q : ZMod n) (f : ℕ)
    (hf₁ : 1 ≤ f) (hfn : f ≤ n - 2) :
    (batchWord q f).length ≤ 2 * n + f := by
  rw [batchWord_length]
  let a := (1 - q).val
  let b := (q - (f : ZMod n)).val
  have ha : a < n := ZMod.val_lt _
  have hb : b < n := ZMod.val_lt _
  have hn : 3 ≤ n := by omega
  have hcast : ((a + b + f : ℕ) : ZMod n) = ((1 : ℕ) : ZMod n) := by
    calc
      ((a + b + f : ℕ) : ZMod n) =
          (a : ZMod n) + (b : ZMod n) + (f : ZMod n) := by simp
      _ = (1 - q) + (q - (f : ZMod n)) + (f : ZMod n) := by
        rw [show (a : ZMod n) = 1 - q by
          simp [a],
          show (b : ZMod n) = q - (f : ZMod n) by
          simp [b]]
      _ = ((1 : ℕ) : ZMod n) := by ring
  have hmod := (ZMod.natCast_eq_natCast_iff' (a + b + f) 1 n).mp hcast
  have hmod' : (a + b + f) % n = 1 := by
    simpa [Nat.mod_eq_of_lt (by omega : 1 < n)] using hmod
  have htotal_lt : a + b + f < 3 * n := by omega
  have hdiv := Nat.mod_add_div (a + b + f) n
  rw [hmod'] at hdiv
  have hquot : (a + b + f) / n < 3 := by
    exact (Nat.div_lt_iff_lt_mul (by omega : 0 < n)).2 htotal_lt
  have hsum : a + b + f ≤ 2 * n + 1 := by
    interval_cases hq : (a + b + f) / n <;> omega
  change (1 - q).val + 1 + 2 * (f - 1) + (q - f).val ≤ 2 * n + f
  dsimp [a, b] at hsum
  omega

/-- Batch count, unit hole-transfer count, and literal-letter bound. -/
theorem batchWord_budget (q : ZMod n) (f : ℕ) (hf₁ : 1 ≤ f)
    (hfn : f ≤ n - 2) :
    (batchWordBudget q f).batches = 1 ∧
    (batchWordBudget q f).holeTransfers = f ∧
    (batchWordBudget q f).rawLetters ≤ 2 * n + f := by
  exact ⟨rfl, rfl, batchWord_length_le q f hf₁ hfn⟩

/-- The distinguished packet has exactly the consecutive holes required by M1. -/
def LegalBatch (s : Execution n α) (q : ZMod n) (f : ℕ) : Prop :=
  1 ≤ f ∧ f ≤ n - 2 ∧ s.placed q ≠ none ∧
    ∀ k : ℕ, 1 ≤ k → k ≤ f → s.placed (q - k) = none

private theorem firstBatchFrame (F : Finset α) (s : Execution n α)
    (q : ZMod n) (B : Finset α) (hB : s.placed q = some B)
    (hhole : s.placed (q - 1) = none) :
    run F s (pWord (1 - q).val ++ [.d]) =
      withPlaced s (batchFrame s.placed q B 0) := by
  have hrot : run F s (pWord (1 - q).val) =
      withPlaced s (rotate (1 - q) s.placed) := by
    simpa [withPlaced] using run_rotation F s (1 - q)
  have h0 : rotate (1 - q) s.placed 0 = none := by
    change s.placed (0 - (1 - q)) = none
    rw [show (0 : ZMod n) - (1 - q) = q - 1 by ring]
    exact hhole
  have h1 : rotate (1 - q) s.placed 1 = some B := by
    change s.placed (1 - (1 - q)) = some B
    rw [show (1 : ZMod n) - (1 - q) = q by ring]
    exact hB
  have hplace : fusionPlacement (rotate (1 - q) s.placed) =
      batchFrame s.placed q B 0 := by
    funext z
    by_cases hz0 : z = 0
    · subst z
      simp [fusionPlacement, h0, h1, batchFrame]
    · by_cases hz1 : z = 1
      · subst z
        simp [fusionPlacement, h0, hz0, batchFrame, rotate, eraseSite]
      · have hsrc : z - (1 - q) ≠ q := by
          intro heq
          apply hz1
          calc
            z = (z - (1 - q)) + (1 - q) := by ring
            _ = q + (1 - q) := by rw [heq]
            _ = 1 := by ring
        simp [fusionPlacement, hz0, hz1, batchFrame, rotate, eraseSite, hsrc]
  rw [run_append, hrot]
  change stepDefect F (withPlaced s (rotate (1 - q) s.placed)) =
      withPlaced s (batchFrame s.placed q B 0)
  simp [stepDefect, withPlaced, h0, hplace]

private theorem batchFrame_hole (s : Placement n (Finset α)) (q : ZMod n)
    (B : Finset α) (k : ℕ) (_hn : 2 ≤ n) (_hk : 1 ≤ k)
    (h : s (q - (k : ZMod n)) = none) :
    batchFrame s q B k 1 = none := by
  have hone : (1 : ZMod n) ≠ 0 := by
    intro hzero
    have hn1 : n = 1 := ZMod.one_eq_zero_iff.mp hzero
    omega
  simp only [batchFrame, if_neg hone, rotate]
  change eraseSite q s (1 - ((1 - q) + (k : ZMod n))) = none
  have hcoord : (1 : ZMod n) - ((1 - q) + (k : ZMod n)) = q - k := by
    ring
  rw [hcoord]
  unfold eraseSite
  by_cases heq : q - (k : ZMod n) = q
  · simp only [if_pos heq]
  · simp only [if_neg heq]
    exact h

private theorem batchFrame_rotated_port0 (s : Placement n (Finset α))
    (q : ZMod n) (B : Finset α) (k : ℕ) (hn : 2 ≤ n) (hk : 1 ≤ k + 2)
    (h : s (q - ((k + 2 : ℕ) : ZMod n)) = none) :
    rotate 1 (batchFrame s q B k) 0 = none := by
  change batchFrame s q B k (0 - 1) = none
  have hone : (1 : ZMod n) ≠ 0 := by
    intro hzero
    have hn1 : n = 1 := ZMod.one_eq_zero_iff.mp hzero
    omega
  have hminus : (0 : ZMod n) - 1 ≠ 0 := by
    intro hz
    have hone' : (1 : ZMod n) = 0 := (sub_eq_zero.mp hz).symm
    exact hone hone'
  simp only [batchFrame, if_neg hminus, rotate]
  change eraseSite q s ((0 - 1) - ((1 - q) + (k : ZMod n))) = none
  rw [show (0 : ZMod n) - 1 = -1 by ring]
  have hcoord : (-1 : ZMod n) - ((1 - q) + (k : ZMod n)) =
      q - (k + 2) := by
    push_cast
    ring
  rw [hcoord]
  unfold eraseSite
  have h' : s (q - ((k : ZMod n) + 2)) = none := by
    simpa [Nat.cast_add] using h
  by_cases heq : q - ((k : ZMod n) + 2) = q
  · simp only [if_pos heq]
  · simp only [if_neg heq]
    exact h'

private theorem batchFrame_step (s : Placement n (Finset α)) (q : ZMod n)
    (B : Finset α) (k : ℕ) (hn : 2 ≤ n)
    (h₁ : s (q - ((k + 1 : ℕ) : ZMod n)) = none)
    (h₂ : s (q - ((k + 2 : ℕ) : ZMod n)) = none) :
    fusionPlacement (rotate 1 (batchFrame s q B k)) = batchFrame s q B (k + 1) := by
  have h0 : rotate 1 (batchFrame s q B k) 0 = none :=
    batchFrame_rotated_port0 s q B k hn (by omega) h₂
  have h1 : rotate 1 (batchFrame s q B k) 1 = some B := by
    change batchFrame s q B k (1 - 1) = some B
    simp [batchFrame]
  funext z
  by_cases hz0 : z = 0
  · subst z
    simp [fusionPlacement, h0, h1, batchFrame]
  · by_cases hz1 : z = 1
    · subst z
      have h₁' : s (q - ((k + 1 : ℕ) : ZMod n)) = none := by
        simpa [Nat.cast_add, add_comm] using h₁
      rw [batchFrame_hole s q B (k + 1) (by omega) (by omega) h₁']
      simp [fusionPlacement, hz0]
    · have hzsub : z - 1 ≠ 0 := by
        intro hsub
        apply hz1
        calc
          z = (z - 1) + 1 := by ring
          _ = 0 + 1 := by rw [hsub]
          _ = 1 := by ring
      have hcoord : z - 1 - ((1 - q) + (k : ZMod n)) =
          z - ((1 - q) + ((k + 1 : ℕ) : ZMod n)) := by
        push_cast
        ring
      simp [fusionPlacement, hz0, hz1, batchFrame, rotate, eraseSite, hzsub, hcoord]

private theorem run_pdWord_frame (F : Finset α) (s : Execution n α)
    (q : ZMod n) (B : Finset α) (f k : ℕ) (hn : 2 ≤ n)
    (hk : k ≤ f - 1)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    run F (withPlaced s (batchFrame s.placed q B 0)) (pdWord k) =
      withPlaced s (batchFrame s.placed q B k) := by
  induction k with
  | zero => simp [pdWord, run]
  | succ k ih =>
      have hk' : k ≤ f - 1 := by omega
      have h₁ := hholes (k + 1) (by omega) (by omega)
      have h₂ := hholes (k + 2) (by omega) (by omega)
      rw [pdWord, run_append, ih hk']
      change run F (withPlaced s (batchFrame s.placed q B k))
        ([Letter.p, Letter.d] : List Letter) = _
      rw [show ([Letter.p, Letter.d] : List Letter) =
        [Letter.p] ++ [Letter.d] by rfl, run_append]
      change stepDefect F
        (withPlaced s (rotate 1 (batchFrame s.placed q B k))) = _
      have h0 := batchFrame_rotated_port0 s.placed q B k hn (by omega) h₂
      have hplace := stepDefect_no_fusion_placement F
        (withPlaced s (rotate 1 (batchFrame s.placed q B k))) h0
      have hplace' :
          (stepDefect F (withPlaced s (rotate 1 (batchFrame s.placed q B k)))).placed =
            batchFrame s.placed q B (k + 1) := by
        rw [hplace]
        change fusionPlacement (rotate 1 (batchFrame s.placed q B k)) = _
        exact batchFrame_step s.placed q B k hn h₁ h₂
      have hfp : fusionPlacement (rotate 1 (batchFrame s.placed q B k)) =
          batchFrame s.placed q B (k + 1) :=
        batchFrame_step s.placed q B k hn h₁ h₂
      have hstep : stepDefect F
          (withPlaced s (rotate 1 (batchFrame s.placed q B k))) =
          withPlaced s (batchFrame s.placed q B (k + 1)) := by
        cases s with
        | mk placed origin chain =>
            simp [stepDefect, withPlaced, h0, hfp]
      exact hstep

private theorem fusionFree_pdWord_frame (F : Finset α) (s : Execution n α)
    (q : ZMod n) (B : Finset α) (f k : ℕ) (hn : 2 ≤ n)
    (hk : k ≤ f - 1)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    FusionFree F (withPlaced s (batchFrame s.placed q B 0)) (pdWord k) := by
  induction k with
  | zero => trivial
  | succ k ih =>
      have hk' : k ≤ f - 1 := by omega
      have h₂ := hholes (k + 2) (by omega) (by omega)
      rw [pdWord, fusionFree_append]
      refine ⟨ih hk', ?_⟩
      have h0 := batchFrame_rotated_port0 s.placed q B k hn (by omega) h₂
      have hrun := run_pdWord_frame F s q B f k hn hk' hholes
      rw [hrun]
      change FusionFree F
        (withPlaced s (batchFrame s.placed q B k)) [.p, .d]
      change FusionFree F
        (step F (withPlaced s (batchFrame s.placed q B k)) .p) [.d]
      change FusionFree F
        (withPlaced s (rotate 1 (batchFrame s.placed q B k))) [.d]
      simp only [FusionFree]
      exact ⟨Or.inl h0, by simp [run, step]⟩

private theorem fusionFree_batchWord (F : Finset α) (s : Execution n α)
    (q : ZMod n) (B : Finset α) (f : ℕ) (hn : 3 ≤ n)
    (hf₁ : 1 ≤ f) (hB : s.placed q = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    FusionFree F s (batchWord q f) := by
  have hhole1 : s.placed (q - 1) = none := by
    simpa using hholes 1 (by omega) (by omega)
  have hprefix := fusionFree_pWord F s (1 - q).val
  have hfirst : FusionFree F
      (run F s (pWord (1 - q).val)) [.d] := by
    have hrun := run_pWord F s (1 - q).val
    rw [hrun]
    have hphase : ((1 - q).val : ZMod n) = 1 - q := ZMod.natCast_zmod_val _
    have h0 : rotate (1 - q) s.placed 0 = none := by
      change s.placed (0 - (1 - q)) = none
      rw [show (0 : ZMod n) - (1 - q) = q - 1 by ring]
      exact hhole1
    rw [hphase]
    simp only [FusionFree]
    exact ⟨Or.inl h0, by simp [run, step]⟩
  have hroute := fusionFree_pdWord_frame F s q B f (f - 1) (by omega)
      (by omega) (by
        intro i hi hi'
        exact hholes i hi hi')
  have htail := fusionFree_pWord F
      (withPlaced s (batchFrame s.placed q B (f - 1)))
      (q - (f : ZMod n)).val
  rw [batchWord]
  rw [show pWord (1 - q).val ++ [.d] ++ pdWord (f - 1) ++
      pWord (q - (f : ZMod n)).val =
      (pWord (1 - q).val ++ [.d]) ++
        (pdWord (f - 1) ++ pWord (q - (f : ZMod n)).val) by
        simp [List.append_assoc]]
  rw [fusionFree_append]
  refine ⟨?_, ?_⟩
  · rw [fusionFree_append]
    exact ⟨hprefix, hfirst⟩
  · have hfirstRun := firstBatchFrame F s q B hB hhole1
    rw [hfirstRun, fusionFree_append]
    have hrouteRun := run_pdWord_frame F s q B f (f - 1) (by omega)
      (by omega) (by intro i hi hi'; exact hholes i hi hi')
    rw [hrouteRun]
    exact ⟨fusionFree_pdWord_frame F s q B f (f - 1) (by omega)
      (by omega) (by intro i hi hi'; exact hholes i hi hi'), htail⟩

/-- Every `d` in the raw batch sees an empty port in its actual predecessor. -/
theorem batchWord_fusionFree (F : Finset α) (s : Execution n α) (q : ZMod n)
    (B : Finset α) (f : ℕ) (hn : 3 ≤ n) (hf₁ : 1 ≤ f)
    (hB : s.placed q = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    FusionFree F s (batchWord q f) := by
  exact fusionFree_batchWord F s q B f hn hf₁ hB hholes

private theorem q_sub_f_ne (q : ZMod n) (f : ℕ)
    (hn : 3 ≤ n) (hf₁ : 1 ≤ f) (hfn : f ≤ n - 2) :
    q - (f : ZMod n) ≠ q := by
  have hf0 : (f : ZMod n) ≠ 0 := by
    intro hz
    have hzero : (f : ZMod n) = (0 : ZMod n) := hz
    have hlt : f < n := by omega
    have hv := congrArg ZMod.val hzero
    rw [ZMod.val_natCast_of_lt hlt, ZMod.val_zero] at hv
    omega
  intro hq
  apply hf0
  calc
    (f : ZMod n) = q - (q - (f : ZMod n)) := by ring
    _ = q - q := by rw [hq]
    _ = 0 := by ring

private theorem batchFrame_final (s : Placement n (Finset α)) (q : ZMod n)
    (B : Finset α) (f : ℕ) (hn : 3 ≤ n) (hf₁ : 1 ≤ f)
    (hfn : f ≤ n - 2) :
    rotate (q - (f : ZMod n)) (batchFrame s q B (f - 1)) =
      fun z => if z = q - (f : ZMod n) then some B else eraseSite q s z := by
  have hsub : f - 1 + 1 = f := Nat.sub_add_cancel hf₁
  have hfcast : ((f - 1 : ℕ) : ZMod n) + 1 = (f : ZMod n) := by
    have hnat : ((f - 1 + 1 : ℕ) : ZMod n) = (f : ZMod n) :=
      congrArg (fun x : ℕ => (x : ZMod n)) hsub
    simpa only [Nat.cast_add, Nat.cast_one] using hnat
  have hphase : ((1 - q) + ((f - 1 : ℕ) : ZMod n)) +
      (q - (f : ZMod n)) = 0 := by
    have hcast : ((f - 1 : ℕ) : ZMod n) = (f : ZMod n) - 1 := by
      linear_combination hfcast
    rw [hcast]
    ring
  have htarget : q - (f : ZMod n) ≠ q := q_sub_f_ne q f hn hf₁ hfn
  funext z
  by_cases hz : z = q - (f : ZMod n)
  · subst z
    simp only [rotate, batchFrame]
    have hzero : (q - (f : ZMod n)) - (q - (f : ZMod n)) = 0 := by ring
    simp [hzero]
  · have harg : z - (q - (f : ZMod n)) ≠ 0 := by
      intro hzero
      apply hz
      calc
        z = (z - (q - (f : ZMod n))) + (q - (f : ZMod n)) := by ring
        _ = q - (f : ZMod n) := by rw [hzero]; ring
    simp only [rotate, batchFrame, if_neg harg]
    have hcoord : z - (q - (f : ZMod n)) -
        ((1 - q) + ((f - 1 : ℕ) : ZMod n)) = z := by
      have hphase' : (q - (f : ZMod n)) +
          ((1 - q) + ((f - 1 : ℕ) : ZMod n)) = 0 := by
        rw [add_comm]
        exact hphase
      calc
        z - (q - (f : ZMod n)) -
            ((1 - q) + ((f - 1 : ℕ) : ZMod n)) =
            z - ((q - (f : ZMod n)) +
              ((1 - q) + ((f - 1 : ℕ) : ZMod n))) := by abel
        _ = z := by rw [hphase']; simp
    rw [hcoord]
    simp [htarget, hz, eraseSite]

theorem run_batchWord (F : Finset α) (s : Execution n α) (q : ZMod n)
    (B : Finset α) (f : ℕ) (hn : 3 ≤ n) (hf₁ : 1 ≤ f) (hfn : f ≤ n - 2)
    (hB : s.placed q = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f → s.placed (q - (i : ZMod n)) = none) :
    run F s (batchWord q f) =
      withPlaced s (batchTarget s.placed q f) := by
  have hhole1 : s.placed (q - 1) = none := by
    simpa using hholes 1 (by omega) (by omega)
  have hfirst := firstBatchFrame F s q B hB hhole1
  have hroute := run_pdWord_frame F s q B f (f - 1)
      (by omega : 2 ≤ n) (by omega)
    (by
      intro i hi hi'
      exact hholes i hi (by omega))
  have htail := run_pWord F (withPlaced s (batchFrame s.placed q B (f - 1)))
    (q - (f : ZMod n)).val
  rw [batchWord]
  rw [show pWord (1 - q).val ++ [.d] ++ pdWord (f - 1) ++
      pWord (q - (f : ZMod n)).val =
      (pWord (1 - q).val ++ [.d]) ++
        (pdWord (f - 1) ++ pWord (q - (f : ZMod n)).val) by
        simp [List.append_assoc]]
  rw [run_append, run_append, hfirst]
  rw [hroute, htail]
  have hval : ((q - (f : ZMod n)).val : ZMod n) = q - (f : ZMod n) :=
    ZMod.natCast_zmod_val _
  rw [hval]
  have hrotate := batchFrame_final s.placed q B f hn hf₁ hfn
  have hplaced :
      rotate (q - (f : ZMod n)) (batchFrame s.placed q B (f - 1)) =
        batchTarget s.placed q f := by
    rw [hrotate]
    funext z
    by_cases hz : z = q - (f : ZMod n)
    · subst z
      simp [batchTarget, hB]
    · simp [batchTarget, eraseSite, hz]
  cases s with
  | mk placed origin chain =>
      simp only [batchTarget] at hplaced ⊢
      simp [withPlaced, hplaced]

/--
Reusable M1 interface: one literal `p,d` batch crosses `f` consecutive holes,
has no intermediate fusion, reaches the exact target placement, and costs at
most `2*n + f` raw letters.
-/
theorem batchWord_spec (F : Finset α) (s : Execution n α) (q : ZMod n)
    (B : Finset α) (f : ℕ) (hn : 3 ≤ n) (hf₁ : 1 ≤ f)
    (hfn : f ≤ n - 2) (hB : s.placed q = some B)
    (hholes : ∀ i : ℕ, 1 ≤ i → i ≤ f →
      s.placed (q - (i : ZMod n)) = none) :
    FusionFree F s (batchWord q f) ∧
    run F s (batchWord q f) = withPlaced s (batchTarget s.placed q f) ∧
    (batchWord q f).length ≤ 2 * n + f := by
  exact ⟨batchWord_fusionFree F s q B f hn hf₁ hB hholes,
    run_batchWord F s q B f hn hf₁ hfn hB hholes,
    batchWord_length_le q f hf₁ hfn⟩

end FusionLogCompression
