import RegisteredAbsorptionChains.LocalMove
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

inductive Letter where
  | p
  | d
  deriving DecidableEq, Repr

/-- The ordered kernel parents and their union at one actual fusion. -/
structure FusionRecord (α : Type*) where
  left : Finset α
  right : Finset α
  result : Finset α

/-- The selected registration record and subsequent carrier absorptions. -/
structure Execution (n : ℕ) (α : Type*) where
  placed : Placement n (Finset α)
  origin : Option (FusionRecord α)
  chain : List (FusionRecord α)

variable {n : ℕ} {α : Type*} [NeZero n] [DecidableEq α]

def fusionPlacement (s : Placement n (Finset α)) : Placement n (Finset α) :=
  fun q =>
    if q = 0 then
      match s 0, s 1 with
      | none, other => other
      | other, none => other
      | some u, some v => some (u ∪ v)
    else if q = 1 then none else s q

/-- Literal `d` step with registration and selected-chain updates. -/
def stepDefect (F : Finset α) (s : Execution n α) : Execution n α :=
  let placed := fusionPlacement s.placed
  match s.placed 0, s.placed 1 with
  | some u, some v =>
      let event : FusionRecord α := ⟨u, v, u ∪ v⟩
      { placed
        origin := if s.origin.isNone && u ∪ v = F then some event else s.origin
        chain := if s.origin.isSome && (F ⊆ u || F ⊆ v) then
          s.chain ++ [event] else s.chain }
  | _, _ => { s with placed }

def step (F : Finset α) (s : Execution n α) : Letter → Execution n α
  | .p => { s with placed := rotate 1 s.placed }
  | .d => stepDefect F s

/-- Chronological execution: the first list element acts first. -/
def run (F : Finset α) (s : Execution n α) (word : List Letter) : Execution n α :=
  word.foldl (step F) s

/-- Every defect letter sees an empty kernel port in its actual predecessor. -/
def FusionFree (F : Finset α) (s : Execution n α) : List Letter → Prop
  | [] => True
  | .p :: rest => FusionFree F (step F s .p) rest
  | .d :: rest =>
      (s.placed 0 = none ∨ s.placed 1 = none) ∧
        FusionFree F (step F s .d) rest

/-- An actual word of `k` successive rotation letters. -/
def pWord : ℕ → List Letter
  | 0 => []
  | k + 1 => pWord k ++ [.p]

/-- The concrete expansion of the local nonfusion macro `E_j`. -/
def localLetters (j : ZMod n) : List Letter :=
  pWord (-j).val ++ [.d] ++ pWord j.val

/-- Expand a sequence of local moves into a chronological `p,d` word. -/
def routeLetters (positions : List (ZMod n)) : List Letter :=
  positions.flatMap localLetters

def routePlacement (s : Placement n (Finset α)) :
    List (ZMod n) → Placement n (Finset α)
  | [] => s
  | j :: rest => routePlacement (moveBack j s) rest

/-- Each local move must see an actual hole in its current placement. -/
def RouteLegal (s : Placement n (Finset α)) : List (ZMod n) → Prop
  | [] => True
  | j :: rest => s j = none ∧ RouteLegal (moveBack j s) rest

/-- Walk one hole forward through `k` consecutive circular positions. -/
def holeWalk : ZMod n → ℕ → List (ZMod n)
  | _, 0 => []
  | j, k + 1 => j :: holeWalk (j + 1) k

omit [NeZero n] [DecidableEq α] in
theorem rotate_add (a b : ZMod n) (s : Placement n α) :
    rotate a (rotate b s) = rotate (a + b) s := by
  funext q
  simp [rotate, sub_sub]

omit [NeZero n] [DecidableEq α] in
theorem rotate_zero (s : Placement n α) : rotate 0 s = s := by
  funext q
  simp [rotate]

omit [NeZero n] in
theorem run_append (F : Finset α) (s : Execution n α) (u v : List Letter) :
    run F s (u ++ v) = run F (run F s u) v := by
  simp [run, List.foldl_append]

omit [NeZero n] in
theorem fusionFree_append (F : Finset α) (s : Execution n α)
    (u v : List Letter) :
    FusionFree F s (u ++ v) ↔
      FusionFree F s u ∧ FusionFree F (run F s u) v := by
  induction u generalizing s with
  | nil => simp [FusionFree, run]
  | cons a u ih =>
      cases a <;> simp [FusionFree, run, ih, and_assoc]

omit [NeZero n] in
theorem fusionFree_pWord (F : Finset α) (s : Execution n α) (k : ℕ) :
    FusionFree F s (pWord k) := by
  induction k with
  | zero => trivial
  | succ k ih =>
      rw [pWord, fusionFree_append]
      exact ⟨ih, by simp [FusionFree]⟩

omit [NeZero n] in
theorem run_pWord (F : Finset α) (s : Execution n α) (k : ℕ) :
    run F s (pWord k) = { s with placed := rotate (k : ZMod n) s.placed } := by
  induction k with
  | zero => cases s; simp [pWord, run, rotate_zero]
  | succ k ih =>
      rw [pWord, run_append, ih]
      simp [run, step, rotate_add, Nat.cast_succ, add_comm]

theorem run_rotation (F : Finset α) (s : Execution n α) (j : ZMod n) :
    run F s (pWord j.val) = { s with placed := rotate j s.placed } := by
  simpa [ZMod.natCast_zmod_val] using run_pWord F s j.val

theorem fusionFree_localLetters (F : Finset α) (s : Execution n α)
    (j : ZMod n) (hole : s.placed j = none) :
    FusionFree F s (localLetters j) := by
  have hprefix : (run F s (pWord (-j).val)).placed 0 = none := by
    rw [run_rotation]
    simpa [rotate_to_zero] using hole
  change FusionFree F s ((pWord (-j).val ++ [.d]) ++ pWord j.val)
  rw [fusionFree_append, fusionFree_append]
  exact ⟨⟨fusionFree_pWord F s _, by simp [FusionFree, hprefix]⟩,
    fusionFree_pWord F (run F s (pWord (-j).val ++ [.d])) _⟩

omit [NeZero n] in
theorem stepDefect_no_origin_or_chain (F : Finset α) (s : Execution n α)
    (hole : s.placed 0 = none) :
    (stepDefect F s).origin = s.origin ∧
      (stepDefect F s).chain = s.chain := by
  simp [stepDefect, hole]

omit [NeZero n] in
theorem stepDefect_no_fusion_placement (F : Finset α) (s : Execution n α)
    (hole : s.placed 0 = none) :
    (stepDefect F s).placed = fusionPlacement s.placed := by
  simp [stepDefect, hole]

omit [NeZero n] in
theorem defect_eq_fusionPlacement (s : Placement n (Finset α))
    (hole : s 0 = none) : defect s = some (fusionPlacement s) := by
  simp only [defect, hole, ne_eq, not_true_eq_false, false_and, ite_false]
  congr 1
  funext q
  by_cases hq : q = 0
  · simp [fusionPlacement, hq, hole]
  · simp [fusionPlacement, hq]

theorem run_localLetters_safe (F : Finset α) (s : Execution n α)
    (j : ZMod n) (hn : 2 ≤ n) (hole : s.placed j = none) :
    run F s (localLetters j) =
      { s with placed := moveBack j s.placed } := by
  have hp := run_pWord F s (-j).val
  have hp' : run F s (pWord (-j).val) =
      { s with placed := rotate (-j) s.placed } := by
    simpa [ZMod.natCast_zmod_val] using hp
  let t : Execution n α := { s with placed := rotate (-j) s.placed }
  have ht : t.placed 0 = none := by
    simpa [t, rotate_to_zero] using hole
  have hd := stepDefect_no_origin_or_chain F t ht
  have hplace : rotate j (fusionPlacement (rotate (-j) s.placed)) =
      moveBack j s.placed := by
    have hl := localWord_moves_into_hole j s.placed hn hole
    rw [localWord, defect_eq_fusionPlacement _ (by simpa [rotate_to_zero] using hole)] at hl
    simpa using Option.some.inj hl
  rw [localLetters, run_append, run_append, hp']
  change run F (stepDefect F t) (pWord j.val) = _
  rw [run_pWord]
  have hj : ((j.val : ℕ) : ZMod n) = j := ZMod.natCast_zmod_val j
  rw [hj]
  have hpl := stepDefect_no_fusion_placement F t ht
  cases s with
  | mk placed origin chain =>
    rw [hpl, hplace, hd.1, hd.2]

theorem run_routeLetters_safe (F : Finset α) (s : Execution n α)
    (positions : List (ZMod n)) (hn : 2 ≤ n)
    (legal : RouteLegal s.placed positions) :
    run F s (routeLetters positions) =
      { s with placed := routePlacement s.placed positions } := by
  induction positions generalizing s with
  | nil => cases s; simp [routeLetters, routePlacement, run]
  | cons j rest ih =>
      obtain ⟨hole, tail⟩ := legal
      simp only [routeLetters, List.flatMap_cons, routePlacement]
      rw [run_append, run_localLetters_safe F s j hn hole]
      simpa [routeLetters] using ih { s with placed := moveBack j s.placed } tail

omit [NeZero n] [DecidableEq α] in
theorem moveBack_hole_next (s : Placement n α) (j : ZMod n)
    (hole : s j = none) :
    moveBack j s (j + 1) = none := by
  by_cases h : j + 1 = j
  · simp [moveBack, h, hole]
  · simp [moveBack, h]

omit [NeZero n] [DecidableEq α] in
theorem holeWalk_legal (s : Placement n (Finset α)) (j : ZMod n)
    (k : ℕ) (hole : s j = none) : RouteLegal s (holeWalk j k) := by
  induction k generalizing s j with
  | zero => trivial
  | succ k ih =>
      constructor
      · exact hole
      · exact ih (moveBack j s) (j + 1) (moveBack_hole_next s j hole)

theorem run_holeWalk_safe (F : Finset α) (s : Execution n α)
    (j : ZMod n) (k : ℕ) (hn : 2 ≤ n) (hole : s.placed j = none) :
    run F s (routeLetters (holeWalk j k)) =
      { s with placed := routePlacement s.placed (holeWalk j k) } :=
  run_routeLetters_safe F s _ hn (holeWalk_legal s.placed j k hole)

private def exampleSeed4 : Execution 4 (ZMod 4) :=
  { placed := fun q => some {q}, origin := none, chain := [] }

private def exampleF4 : Finset (ZMod 4) := {0, 1}

private example :
    (run exampleF4 exampleSeed4 [.d, .p, .d, .p, .d]).chain.length = 2 := by
  decide

private example :
    (run exampleF4 exampleSeed4 [.d, .p, .p, .d, .p, .d, .p, .d]).chain.length = 1 := by
  decide

private example :
    (run exampleF4 exampleSeed4 [.d, .p, .d, .p, .d]).placed =
      (run exampleF4 exampleSeed4 [.d, .p, .p, .d, .p, .d, .p, .d]).placed := by
  decide

end RegisteredAbsorptionChains
