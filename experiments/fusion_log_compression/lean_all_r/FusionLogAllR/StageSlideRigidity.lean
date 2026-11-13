import FusionLogAllR.RawAllRUpperExecution
import FusionLogAllR.MinimalWordRigidity

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # Literal stage rigidity from the next singleton's actual motion

The strongest local theorem uses a canonical boundary, the next specified
fusion, activity of actual defect letters, and one turn of rotations.  It
derives the defect count and slide ordering rather than assuming them.  The
global equality-case budgets are supplied by `RawAllRUniqueness`.
-/

/-- Every defect in the word moves the marked atom from port 1 to port 0.
The height is updated by the same physical map used in `CarrierRotation`.
This predicate does not prescribe the positions of the rotation letters. -/
def AtomDefectsPaid (n z : ℕ) : List Letter → Prop
  | [] => True
  | .p :: rest => AtomDefectsPaid n (z + 1) rest
  | .d :: rest => (z : ZMod n) = 1 ∧
      AtomDefectsPaid n (carrierHeightStep n z .d) rest

theorem carrierDownSteps_le_defect_count (n z : ℕ) (word : List Letter) :
    carrierDownSteps n z word ≤ word.count .d := by
  induction word generalizing z with
  | nil => simp [carrierDownSteps]
  | cons letter rest ih =>
      cases letter with
      | p => simpa [carrierDownSteps] using ih (z + 1)
      | d =>
          have h := ih (carrierHeightStep n z .d)
          simp only [carrierDownSteps, List.count_cons_self]
          split_ifs <;> omega

theorem atomDefectsPaid_of_downSteps_eq_count (n z : ℕ) (word : List Letter)
    (hcount : carrierDownSteps n z word = word.count .d) :
    AtomDefectsPaid n z word := by
  induction word generalizing z with
  | nil => trivial
  | cons letter rest ih =>
      cases letter with
      | p =>
          exact ih (z + 1) (by simpa [carrierDownSteps] using hcount)
      | d =>
          have hbound := carrierDownSteps_le_defect_count n
            (carrierHeightStep n z .d) rest
          have hz : (z : ZMod n) = 1 := by
            by_contra hz
            simp only [carrierDownSteps, hz, if_false,
              List.count_cons_self, zero_add] at hcount
            omega
          refine ⟨hz, ih _ ?_⟩
          simp only [carrierDownSteps, hz, if_true, List.count_cons_self] at hcount
          omega

theorem AtomDefectsPaid.downSteps_eq_count {n z : ℕ} {word : List Letter}
    (hpaid : AtomDefectsPaid n z word) :
    carrierDownSteps n z word = word.count .d := by
  induction word generalizing z with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => exact ih hpaid
      | d =>
          have hrest := ih hpaid.2
          simp [carrierDownSteps, hpaid.1, hrest, Nat.add_comm]

private theorem natCast_ne_one_of_between {n z : ℕ} [NeZero n]
    (hn : 2 ≤ n) (hz : 2 ≤ z) (hzn : z ≤ n) : (z : ZMod n) ≠ 1 := by
  have : Fact (1 < n) := ⟨by omega⟩
  by_cases hzeq : z = n
  · subst z
    simp
  · intro heq
    have hv := congrArg ZMod.val heq
    rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_one] at hv
    omega

theorem AtomDefectsPaid.height_ge_turn {n z : ℕ} [NeZero n]
    (hn : 2 ≤ n) {word : List Letter} (hz : n ≤ z)
    (hpaid : AtomDefectsPaid n z word) :
    n ≤ carrierHeightRun n z word := by
  have : Fact (1 < n) := ⟨by omega⟩
  induction word generalizing z with
  | nil => simpa [carrierHeightRun] using hz
  | cons letter rest ih =>
      cases letter with
      | p =>
          apply ih (z := z + 1) (by omega) hpaid
      | d =>
          have hne : z ≠ n := by
            intro heq
            have hsite := hpaid.1
            simp [heq] at hsite
          have hstep : n ≤ carrierHeightStep n z .d := by
            simp only [carrierHeightStep, hpaid.1, if_true]
            omega
          exact ih hstep hpaid.2

private theorem pWord_cons (k : ℕ) : pWord (k + 1) = .p :: pWord k := by
  induction k with
  | zero => rfl
  | succ k ih =>
      change pWord (k + 1) ++ [.p] = .p :: (pWord k ++ [.p])
      rw [ih]
      rfl

private theorem pdWord_cons (k : ℕ) : pdWord (k + 1) = .p :: .d :: pdWord k := by
  induction k with
  | zero => rfl
  | succ k ih =>
      change pdWord (k + 1) ++ [.p, .d] = .p :: .d :: (pdWord k ++ [.p, .d])
      rw [ih]
      rfl

private theorem pWord_count_p (k : ℕ) : (pWord k).count .p = k := by
  induction k with
  | zero => rfl
  | succ k ih => simp [pWord, ih]

private theorem atomDefectsPaid_pWord (n z k : ℕ) (word : List Letter) :
    AtomDefectsPaid n z (pWord k ++ word) ↔ AtomDefectsPaid n (z + k) word := by
  induction k generalizing z with
  | zero => simp [pWord]
  | succ k ih =>
      rw [pWord_cons]
      simpa [AtomDefectsPaid, Nat.add_assoc, Nat.add_comm,
        Nat.add_left_comm] using ih (z + 1)

private theorem first_defect_decomposition (word : List Letter)
    (hdefect : 0 < word.count .d) :
    ∃ k rest, word = pWord k ++ .d :: rest := by
  induction word with
  | nil => simp at hdefect
  | cons letter rest ih =>
      cases letter with
      | d => exact ⟨0, rest, rfl⟩
      | p =>
          obtain ⟨k, tail, htail⟩ := ih (by simpa using hdefect)
          exact ⟨k + 1, tail, by simp [pWord_cons, htail]⟩

/-- With fewer than one full turn left, a marked atom at lifted height `n`
can pay equally many rotations and defects only in literal `pd` order. -/
theorem AtomDefectsPaid.word_eq_pdWord {n k : ℕ} [NeZero n]
    (hn : 2 ≤ n) (hk : k < n) {word : List Letter}
    (hpaid : AtomDefectsPaid n n word)
    (hp : word.count .p = k) (hd : word.count .d = k) :
    word = pdWord k := by
  have : Fact (1 < n) := ⟨by omega⟩
  induction k generalizing word with
  | zero =>
      have hlen := count_p_add_count_d word
      have hnil : word = [] := List.length_eq_zero_iff.mp (by omega)
      simpa [pdWord] using hnil
  | succ k ih =>
      obtain ⟨q, rest, hword⟩ := first_defect_decomposition word (by omega)
      have hp' : q + rest.count .p = k + 1 := by
        simpa [hword, pWord_count_p] using hp
      have hd' : rest.count .d = k := by
        simpa [hword, pWord_count_d] using hd
      rw [hword, atomDefectsPaid_pWord] at hpaid
      have hsite : (q : ZMod n) = 1 := by
        simpa using hpaid.1
      have hq : q = 1 := by
        have hval := congrArg ZMod.val hsite
        rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_one] at hval
        exact hval
      subst q
      have hrest : AtomDefectsPaid n n rest := by
        simpa [AtomDefectsPaid, carrierHeightStep] using hpaid.2
      have hrestp : rest.count .p = k := by omega
      have htail := ih (by omega) hrest hrestp hd'
      simp [hword, pWord, pdWord_cons, htail]

/-- A one-particle equality case fixes all raw letters.  Ending at port 0,
with `n` rotations and `j+1` defects, forces every defect to move the next
singleton, and forces their order to be `p^(n-j) d (p d)^j`. -/
theorem atom_stage_word_unique {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    {word : List Letter} (hp : word.count .p = n)
    (hd : word.count .d = j + 1)
    (hend : (carrierHeightRun n (j + 1) word : ZMod n) = 0) :
    word = allRStage n j := by
  have : Fact (1 < n) := ⟨by omega⟩
  let height := carrierHeightRun n (j + 1) word
  have hbalance := carrierHeightRun_balance n (j + 1) (by omega) word
  have hdown := carrierDownSteps_le_defect_count n (j + 1) word
  rw [hp] at hbalance
  rw [hd] at hdown
  have hlower : n ≤ height := by dsimp [height]; omega
  have hupper : height < 2 * n := by dsimp [height]; omega
  have hresidue : (((height - n : ℕ) : ZMod n)) = 0 := by
    rw [Nat.cast_sub hlower]
    simpa [height] using hend
  have hheight : height = n := by
    have hval := congrArg ZMod.val hresidue
    rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_zero] at hval
    omega
  have hdown_eq : carrierDownSteps n (j + 1) word = word.count .d := by
    change carrierHeightRun n (j + 1) word = n at hheight
    omega
  have hpaid := atomDefectsPaid_of_downSteps_eq_count n (j + 1) word hdown_eq
  obtain ⟨q, rest, hword⟩ := first_defect_decomposition word (by omega)
  have hp' : q + rest.count .p = n := by
    simpa [hword, pWord_count_p] using hp
  have hd' : rest.count .d = j := by
    simpa [hword, pWord_count_d] using hd
  rw [hword, atomDefectsPaid_pWord] at hpaid
  have hsite : ((j + 1 + q : ℕ) : ZMod n) = 1 := hpaid.1
  have hturn : n ≤ j + 1 + q := by
    by_contra hturn
    have hv := congrArg ZMod.val hsite
    rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_one] at hv
    omega
  have hsite' : (((j + 1 + q - n : ℕ) : ZMod n)) = 1 := by
    rw [Nat.cast_sub hturn]
    simpa using hsite
  have hq : q = n - j := by
    have hv := congrArg ZMod.val hsite'
    rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_one] at hv
    omega
  have hnext : carrierHeightStep n (j + 1 + q) .d = n := by
    simp only [carrierHeightStep, hsite, if_true]
    omega
  have hrest : rest = pdWord j :=
    AtomDefectsPaid.word_eq_pdWord (by omega) (by omega)
      (hnext ▸ hpaid.2) (by omega) hd'
  simp [hword, hq, hrest, allRStage]

/-- The local rigidity theorem is tied to a real execution: the next source
singleton starts at `j+1` and belongs to the actual packet at terminal port 0.
No gap trace, intended slide positions, or word factorization is assumed. -/
theorem allRStage_word_unique {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    {word : List Letter} {B : Finset (ZMod n)}
    (hend : (run F start word).placed 0 = some B)
    (hnext : ((j + 1 : ℕ) : ZMod n) ∈ B)
    (hp : word.count .p = n) (hd : word.count .d = j + 1) :
    word = allRStage n j := by
  let a : ZMod n := (j + 1 : ℕ)
  have ha : a.val = j + 1 := ZMod.val_natCast_of_lt (by omega)
  have ha0 : a ≠ 0 := by
    intro heq
    have hval := congrArg ZMod.val heq
    rw [ha, ZMod.val_zero] at hval
    omega
  have hpacket : start.placed a = some {a} := by
    rw [hstart]
    simp [allRBoundaryPlaced, ha0, ha]
  obtain ⟨lift, hplaced⟩ := ordered
  have hsource := (placementOfMap_some_iff lift.position a {a}).mp
    (hplaced ▸ hpacket)
  have hsite : lift.position a = ((j + 1 : ℕ) : ZMod n) := by
    exact (mem_sourceFiber lift.position a a).mp
      (hsource.1.symm ▸ Finset.mem_singleton_self a)
  apply atom_stage_word_unique hn hj hjn hp hd
  exact carrierHeightRun_site F start lift.position a 0 (j + 1) word B
    (by omega) hplaced hsite hend hnext

/-- An equivalent local zero-surplus interface uses the actual stage length
and its already extracted exact rotation budget. -/
theorem allRStage_word_unique_of_length {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    {word : List Letter} {B : Finset (ZMod n)}
    (hend : (run F start word).placed 0 = some B)
    (hnext : ((j + 1 : ℕ) : ZMod n) ∈ B)
    (hp : word.count .p = n) (hlen : word.length = n + j + 1) :
    word = allRStage n j := by
  apply allRStage_word_unique hn hj hjn F start ordered hstart hend hnext hp
  have hcount := count_p_add_count_d word
  omega

/-- The convenient zero-surplus form: exact stage length plus the exact
rotation budget determines the exact number of defects, after which the
literal one-particle argument fixes their positions. -/
theorem allRStage_word_unique_of_zero_surplus {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    {word : List Letter} {B : Finset (ZMod n)}
    (hend : (run F start word).placed 0 = some B)
    (hnext : ((j + 1 : ℕ) : ZMod n) ∈ B)
    (hp : word.count .p = n)
    (hbudget : word.length = n + (j + 1)) :
    word = allRStage n j := by
  apply allRStage_word_unique_of_length hn hj hjn F start ordered hstart
    hend hnext hp
  exact hbudget

/-- The endpoint-specialized form used by the stage induction.  The target
boundary itself supplies the membership of the next source singleton, so the
caller only needs to expose the literal endpoint equality. -/
theorem allRStage_word_unique_to_canonical {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    {word : List Letter}
    (hend : (run F start word).placed = allRBoundaryPlaced (j + 1))
    (hp : word.count .p = n)
    (hbudget : word.length = n + (j + 1)) :
    word = allRStage n j := by
  have : Fact (1 < n) := ⟨by omega⟩
  apply allRStage_word_unique_of_zero_surplus hn hj hjn F start ordered hstart
    (B := allRCarrier n (j + 1))
  · simpa [allRBoundaryPlaced] using congrFun hend (0 : ZMod n)
  · simp only [allRCarrier, Finset.mem_filter, Finset.mem_univ, true_and]
    have hv : (((j + 1 : ℕ) : ZMod n)).val = j + 1 :=
      ZMod.val_natCast_of_lt (by omega)
    simpa only [Nat.cast_add, Nat.cast_one] using hv.le
  · exact hp
  · exact hbudget

/-- The operational part of zero surplus that is needed below: every `d`
sees an occupied port 1.  Unlike `AtomDefectsPaid`, this does not specify
which packet is there, and it allows effective fusions. -/
def ActiveDefectsRun {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (start : Execution n (ZMod n)) :
    List Letter → Prop
  | [] => True
  | .p :: rest => ActiveDefectsRun F (step F start .p) rest
  | .d :: rest => start.placed 1 ≠ none ∧
      ActiveDefectsRun F (step F start .d) rest

theorem activeDefectsRun_append {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (u v : List Letter) :
    ActiveDefectsRun F start (u ++ v) ↔
      ActiveDefectsRun F start u ∧
        ActiveDefectsRun F (run F start u) v := by
  induction u generalizing start with
  | nil => simp [ActiveDefectsRun, run]
  | cons letter rest ih =>
      cases letter <;> simp [ActiveDefectsRun, run, ih, and_assoc]

theorem PhysicalTrace.activeDefectsRun_of_paid
    {n : ℕ} [NeZero n] {F : Finset (ZMod n)} {a : ZMod n}
    {start finish : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a start word finish g h)
    (hpaid : trace.toExecutionTrace.AllDefectsPaid) :
    ActiveDefectsRun F start word := by
  induction trace with
  | nil hrep => trivial
  | p hrep rest ih => exact ih hpaid
  | @d s word t g h k hrep transition hnext hmatch rest ih =>
      have hpaid' : transition.Paid ∧ rest.toExecutionTrace.AllDefectsPaid := hpaid
      have hidle : transition.idleStep = 0 := by
        cases transition <;> simp_all [HoleTransition.Paid, HoleTransition.idleStep]
      have hactive : s.placed 1 ≠ none := by
        intro hnone
        have := hmatch.idle
        simp [hnone, hidle] at this
      exact ⟨hactive, ih hpaid'.2⟩

private theorem atom_mem_placementOfMap {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (a q : ZMod n) :
    a ∈ (placementOfMap f q).getD ∅ ↔ f a = q := by
  by_cases h : (sourceFiber f q).Nonempty
  · simp [placementOfMap, h]
  · have hnone : sourceFiber f q = ∅ := Finset.not_nonempty_iff_eq_empty.mp h
    have hne : f a ≠ q := by
      intro heq
      have : a ∈ sourceFiber f q := (mem_sourceFiber f a q).mpr heq
      simp [hnone] at this
    simp [placementOfMap, h, hne]

/-- If all other atoms stay in the integer strip `[2,n]`, an occupied port 1
must contain the distinguished atom.  The strip accounts for every rotation
remaining in the actual word, so no background atom can wrap to port 1. -/
theorem atomDefectsPaid_of_background_strip {n z : ℕ} [NeZero n]
    (hn : 2 ≤ n) (F : Finset (ZMod n))
    (start : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (a : ZMod n) (word : List Letter)
    (hplaced : start.placed = placementOfMap f)
    (hsite : f a = (z : ZMod n))
    (hbackground : ∀ b, b ≠ a → ∃ k : ℕ,
      2 ≤ k ∧ k + word.count .p ≤ n ∧ f b = (k : ZMod n))
    (hactive : ActiveDefectsRun F start word) :
    AtomDefectsPaid n z word := by
  induction word generalizing start f z with
  | nil => trivial
  | cons letter rest ih =>
      have hnext := step_placementOfMap F start f letter hn hplaced
      cases letter with
      | p =>
          apply ih (step F start .p) (forwardMapStep f .p) hnext
          · simp [forwardMapStep, hsite]
          · intro b hb
            obtain ⟨k, hk, hkn, hkb⟩ := hbackground b hb
            refine ⟨k + 1, by omega, ?_, ?_⟩
            · simpa [Nat.add_assoc, Nat.add_comm, Nat.add_left_comm] using hkn
            · simp [forwardMapStep, hkb]
          · exact hactive
      | d =>
          have hb1 : ∀ b, b ≠ a → f b ≠ 1 := by
            intro b hb
            obtain ⟨k, hk, hkn, hkb⟩ := hbackground b hb
            rw [hkb]
            exact natCast_ne_one_of_between hn hk (by omega)
          have ha1 : f a = 1 := by
            have hport : placementOfMap f 1 ≠ none := hplaced ▸ hactive.1
            have hnonempty : (sourceFiber f 1).Nonempty := by
              by_contra hempty
              apply hport
              simp [placementOfMap, hempty]
            obtain ⟨b, hb⟩ := hnonempty
            have hbsite : f b = 1 := (mem_sourceFiber f b 1).mp hb
            have hba : b = a := by
              by_contra hba
              exact hb1 b hba hbsite
            simpa [hba] using hbsite
          have hz : (z : ZMod n) = 1 := hsite ▸ ha1
          refine ⟨hz, ih (step F start .d) (forwardMapStep f .d) hnext ?_ ?_ hactive.2⟩
          · simpa [forwardMapStep, carrierHeightStep, collapsePosition,
              ha1, hz] using (carrierHeightStep_cast n z hn .d).symm
          · intro b hb
            obtain ⟨k, hk, hkn, hkb⟩ := hbackground b hb
            refine ⟨k, hk, by simpa using hkn, ?_⟩
            change collapsePosition (f b) = (k : ZMod n)
            rw [collapsePosition, if_neg (hb1 b hb)]
            exact hkb

private theorem boundary_map_value {n j : ℕ} [NeZero n]
    (start : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (hplaced : start.placed = placementOfMap f)
    (hstart : start.placed = allRBoundaryPlaced j) (b : ZMod n) :
    f b = if b.val ≤ j then 0 else b := by
  apply (atom_mem_placementOfMap f b _).mp
  rw [← hplaced, hstart]
  by_cases hb : b.val ≤ j
  · simp [hb, allRBoundaryPlaced, allRCarrier]
  · have hb0 : b ≠ 0 := by
      intro heq
      simp [heq] at hb
    simp [hb, allRBoundaryPlaced, hb0]

/-- Before the first slide the only occupied packet with a hole immediately
behind it is the next singleton.  This is an actual port calculation in the
canonical placement, and it covers the cyclic wrap explicitly. -/
theorem allRBoundary_first_slide_rotation {n j q : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2) (hq : q ≤ n)
    (h0 : rotate (q : ZMod n) (allRBoundaryPlaced j) 0 = none)
    (h1 : rotate (q : ZMod n) (allRBoundaryPlaced j) 1 ≠ none) :
    q = n - j := by
  have : Fact (1 < n) := ⟨by omega⟩
  have hqpos : 0 < q := by
    by_contra hqpos
    have heq : q = 0 := by omega
    simp [heq, rotate, allRBoundaryPlaced, ZMod.val_one, hj] at h1
  have hcast : -(q : ZMod n) = ((n - q : ℕ) : ZMod n) := by
    rw [Nat.cast_sub hq]
    simp
  have hzero : allRBoundaryPlaced j ((n - q : ℕ) : ZMod n) = none := by
    simpa [rotate, hcast] using h0
  have hv0 : (((n - q : ℕ) : ZMod n)).val = n - q :=
    ZMod.val_natCast_of_lt (by omega)
  have hpos0 : 0 < n - q := by
    by_contra hpos0
    have heq : n - q = 0 := by omega
    simp [heq, allRBoundaryPlaced] at hzero
  have hne0 : ((n - q : ℕ) : ZMod n) ≠ 0 := by
    intro heq
    have hv := congrArg ZMod.val heq
    rw [hv0, ZMod.val_zero] at hv
    omega
  have hsmall : n - q ≤ j := by
    simpa [allRBoundaryPlaced, hne0, hv0] using hzero
  have hcast1 : 1 - (q : ZMod n) = ((n - q + 1 : ℕ) : ZMod n) := by
    rw [Nat.cast_add, Nat.cast_one, Nat.cast_sub hq]
    simp only [ZMod.natCast_self, zero_sub]
    ring
  have hv1 : (((n - q + 1 : ℕ) : ZMod n)).val = n - q + 1 :=
    ZMod.val_natCast_of_lt (by omega)
  have hne1 : ((n - q + 1 : ℕ) : ZMod n) ≠ 0 := by
    intro heq
    have hv := congrArg ZMod.val heq
    rw [hv1, ZMod.val_zero] at hv
    omega
  have hlarge : ¬n - q + 1 ≤ j := by
    change allRBoundaryPlaced j (1 - (q : ZMod n)) ≠ none at h1
    rw [hcast1] at h1
    intro hle
    apply h1
    simp only [allRBoundaryPlaced, if_neg hne1, hv1, if_pos hle]
  omega

private theorem forwardMapRun_pWord (n : ℕ) [NeZero n]
    (f : ZMod n → ZMod n) (k : ℕ) :
    forwardMapRun f (pWord k) = fun b => f b + (k : ZMod n) := by
  induction k with
  | zero => simp [pWord, forwardMapRun]
  | succ k ih =>
      change forwardMapRun f (pWord k ++ [.p]) = _
      simp only [forwardMapRun, List.foldl_append, List.foldl_cons, List.foldl_nil]
      change forwardMapStep (forwardMapRun f (pWord k)) .p = _
      rw [ih]
      funext b
      simp [forwardMapStep, Nat.cast_succ, add_assoc]

theorem word_eq_pWord_of_no_defects (word : List Letter)
    (hd : word.count .d = 0) : word = pWord (word.count .p) := by
  induction word with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => simpa [pWord_cons] using congrArg (List.cons .p) (ih (by simpa using hd))
      | d => simp at hd

/-- Strong local rigidity.  No stage defect count or canonical terminal
placement is assumed.  The prefix is the actual interval before the next
specified fusion, all defects are active, and its exact rotation budget is
one turn.  The first slide and the background strip then force all remaining
defects to move the next singleton, fixing the literal stage word. -/
theorem allRStage_word_unique_of_active {n j : ℕ} [NeZero n]
    (hn : 3 ≤ n) (hj : 1 ≤ j) (hjn : j ≤ n - 2)
    (F : Finset (ZMod n)) (start : Execution n (ZMod n))
    (ordered : SourceOrdered start.placed)
    (hstart : start.placed = allRBoundaryPlaced j)
    (pre : List Letter) (hfree : FusionFree F start pre)
    (hactive : ActiveDefectsRun F start (pre ++ [.d]))
    (hp : pre.count .p = n)
    (hport : (run F start pre).placed 1 = some {((j + 1 : ℕ) : ZMod n)}) :
    pre ++ [.d] = allRStage n j := by
  have : Fact (1 < n) := ⟨by omega⟩
  let a : ZMod n := (j + 1 : ℕ)
  have ha : a.val = j + 1 := ZMod.val_natCast_of_lt (by omega)
  have hpreD : 0 < pre.count .d := by
    by_contra hpreD
    have hnod : pre.count .d = 0 := by omega
    have hword := word_eq_pWord_of_no_defects pre hnod
    have hnilport : (run F start pre).placed 1 = none := by
      rw [hword, hp, run_pWord]
      simp [hstart, allRBoundaryPlaced, rotate, ZMod.val_one, hj]
    rw [hport] at hnilport
    contradiction
  obtain ⟨q, rest, hpre⟩ := first_defect_decomposition pre hpreD
  have hcounts : q + rest.count .p = n := by
    simpa [hpre, pWord_count_p] using hp
  have hfree' := (fusionFree_append F start (pWord q) (.d :: rest)).mp
    (hpre ▸ hfree)
  have hwhole : pre ++ [.d] = (pWord q ++ [.d]) ++ (rest ++ [.d]) := by
    simp [hpre]
  have hactiveFirst := (activeDefectsRun_append F start (pWord q)
    (.d :: (rest ++ [.d]))).mp (by simpa [hpre] using hactive)
  have hfirst1 : (run F start (pWord q)).placed 1 ≠ none := hactiveFirst.2.1
  have hfirst0 : (run F start (pWord q)).placed 0 = none :=
    hfree'.2.1.resolve_right hfirst1
  have hq : q = n - j := by
    apply allRBoundary_first_slide_rotation hn hj hjn (by omega)
    · simpa [run_pWord, hstart] using hfirst0
    · simpa [run_pWord, hstart] using hfirst1
  have hrestP : (rest ++ [Letter.d]).count .p = j := by
    have hc : rest.count .p = j := by omega
    simpa using hc
  obtain ⟨lift, hplaced⟩ := ordered
  let f := lift.position
  let first : Execution n (ZMod n) := step F (run F start (pWord q)) .d
  let nextMap := forwardMapStep (forwardMapRun f (pWord q)) .d
  have hfirstMap : first.placed = placementOfMap nextMap :=
    step_placementOfMap F (run F start (pWord q)) (forwardMapRun f (pWord q))
      .d (by omega) (run_placementOfMap F start f (pWord q) (by omega) hplaced)
  have hmap (b : ZMod n) : nextMap b = collapsePosition (f b + (q : ZMod n)) := by
    simp [nextMap, forwardMapStep, forwardMapRun_pWord]
  have hqcast : (q : ZMod n) = -(j : ZMod n) := by
    rw [hq, Nat.cast_sub (by omega : j ≤ n)]
    simp
  have hfa : f a = a := by
    have h := boundary_map_value start f hplaced hstart a
    rw [ha, if_neg (by omega)] at h
    exact h
  have hnextSite : nextMap a = ((n : ℕ) : ZMod n) := by
    rw [hmap, hfa, hqcast]
    have heq : a + -(j : ZMod n) = 1 := by simp [a]
    simp [heq, collapsePosition]
  have hbackground : ∀ b, b ≠ a → ∃ k : ℕ,
      2 ≤ k ∧ k + (rest ++ [Letter.d]).count .p ≤ n ∧ nextMap b = (k : ZMod n) := by
    intro b hba
    have hbmap := boundary_map_value start f hplaced hstart b
    by_cases hb : b.val ≤ j
    · refine ⟨q, by omega, by omega, ?_⟩
      have hq1 : (q : ZMod n) ≠ 1 :=
        natCast_ne_one_of_between (by omega) (by omega) (by omega)
      simp [hmap, hbmap, hb, collapsePosition, hq1]
    · have hbval : b.val ≠ j + 1 := by
        intro heq
        apply hba
        apply ZMod.val_injective
        rw [heq, ha]
      have hbge : j + 2 ≤ b.val := by omega
      have hbupper := ZMod.val_lt b
      refine ⟨b.val - j, by omega, by omega, ?_⟩
      have hcast : b + (q : ZMod n) = ((b.val - j : ℕ) : ZMod n) := by
        rw [hqcast, Nat.cast_sub (by omega : j ≤ b.val), ZMod.natCast_zmod_val]
        ring
      have hk1 : ((b.val - j : ℕ) : ZMod n) ≠ 1 :=
        natCast_ne_one_of_between (by omega) (by omega) (by omega)
      rw [hmap, hbmap, if_neg hb, hcast, collapsePosition, if_neg hk1]
  have hrestActive : ActiveDefectsRun F first (rest ++ [.d]) := by
    have h := (activeDefectsRun_append F start (pWord q ++ [.d])
      (rest ++ [.d])).mp (hwhole ▸ hactive)
    simpa [run_append, run, first] using h.2
  have hpaid := atomDefectsPaid_of_background_strip (by omega) F first nextMap a
    (rest ++ [.d]) hfirstMap hnextSite hbackground hrestActive
  have hwholeRun : run F start (pre ++ [.d]) = run F first (rest ++ [.d]) := by
    simp [hwhole, run, first]
  have hfinalAtom : a ∈ ((run F first (rest ++ [.d])).placed 0).getD ∅ := by
    rw [← hwholeRun, run_append]
    change a ∈ ((stepDefect F (run F start pre)).placed 0).getD ∅
    rw [stepDefect_placed]
    cases h0 : (run F start pre).placed 0 <;>
      simp [fusionPlacement, h0, hport, a]
  obtain ⟨B, hB, haB⟩ : ∃ B,
      (run F first (rest ++ [.d])).placed 0 = some B ∧ a ∈ B := by
    cases h0 : (run F first (rest ++ [.d])).placed 0 with
    | none => simp [h0] at hfinalAtom
    | some B => exact ⟨B, rfl, by simpa [h0] using hfinalAtom⟩
  have hresidue := carrierHeightRun_site F first nextMap a 0 n
    (rest ++ [.d]) B (by omega) hfirstMap hnextSite hB haB
  have hlower := hpaid.height_ge_turn (by omega) (le_refl n)
  have hbalance := carrierHeightRun_balance n n (by omega) (rest ++ [.d])
  have hdown := hpaid.downSteps_eq_count
  rw [hrestP] at hbalance
  have hupper : carrierHeightRun n n (rest ++ [.d]) < 2 * n := by omega
  have hsub : (((carrierHeightRun n n (rest ++ [.d]) - n : ℕ) : ZMod n)) = 0 := by
    rw [Nat.cast_sub hlower]
    simpa using hresidue
  have hheight : carrierHeightRun n n (rest ++ [.d]) = n := by
    have hv := congrArg ZMod.val hsub
    rw [ZMod.val_natCast_of_lt (by omega), ZMod.val_zero] at hv
    omega
  have hrestD : (rest ++ [Letter.d]).count .d = j := by omega
  have htail := AtomDefectsPaid.word_eq_pdWord (by omega) (by omega)
    hpaid hrestP hrestD
  rw [hwhole, List.append_assoc, htail, hq]
  simp [allRStage, List.append_assoc]

end FusionLogAllR
