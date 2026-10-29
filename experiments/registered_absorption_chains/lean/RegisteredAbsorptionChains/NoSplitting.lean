import RegisteredAbsorptionChains.SourceOrderInvariant
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The source-to-position map follows the same chronological letters as the
placed execution. This is a map of actual atoms, not a symbolic block plan. -/
def forwardMapStep (f : ZMod n → ZMod n) : Letter → (ZMod n → ZMod n)
  | .p => fun atom => f atom + 1
  | .d => collapsePosition ∘ f

def forwardMapRun (f : ZMod n → ZMod n) (word : List Letter) :
    ZMod n → ZMod n :=
  word.foldl forwardMapStep f

theorem step_placementOfMap (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (a : Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) :
    (step F s a).placed = placementOfMap (forwardMapStep f a) := by
  cases a with
  | p =>
      change rotate 1 s.placed = placementOfMap (fun atom => f atom + 1)
      rw [hplaced]
      exact (placementOfMap_rotate f).symm
  | d =>
      rw [show (step F s .d).placed = fusionPlacement s.placed from
        stepDefect_placed F s, hplaced]
      exact (placementOfMap_defect f hn).symm

theorem run_placementOfMap (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f) :
    (run F s word).placed = placementOfMap (forwardMapRun f word) := by
  induction word generalizing s f with
  | nil => simpa [run, forwardMapRun] using hplaced
  | cons a rest ih =>
      change (run F (step F s a) rest).placed =
        placementOfMap (forwardMapRun (forwardMapStep f a) rest)
      exact ih (step F s a) (forwardMapStep f a)
        (step_placementOfMap F s f a hn hplaced)

omit [NeZero n] in
theorem forwardMapRun_preserves_equal (f : ZMod n → ZMod n)
    (word : List Letter) (x y : ZMod n) (hxy : f x = f y) :
    forwardMapRun f word x = forwardMapRun f word y := by
  induction word generalizing f with
  | nil => simpa [forwardMapRun] using hxy
  | cons a rest ih =>
      apply ih (forwardMapStep f a)
      cases a with
      | p =>
          change f x + 1 = f y + 1
          exact congrArg (· + 1) hxy
      | d =>
          change collapsePosition (f x) = collapsePosition (f y)
          exact congrArg collapsePosition hxy

/-- Two atoms that already share one packet remain in one packet after
every actual continuation. Thus a target cut separating them cannot be
assembled from this particular source state. -/
theorem no_split_after_actual_word (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (f : ZMod n → ZMod n)
    (word : List Letter) (hn : 2 ≤ n)
    (hplaced : s.placed = placementOfMap f)
    (x y : ZMod n) (hxy : f x = f y) :
    ∃ q B, (run F s word).placed q = some B ∧ x ∈ B ∧ y ∈ B := by
  let g := forwardMapRun f word
  let q := g x
  have hsame : g x = g y := forwardMapRun_preserves_equal f word x y hxy
  have hx : x ∈ sourceFiber g q := by simp [q]
  have hy : y ∈ sourceFiber g q :=
    (mem_sourceFiber g y q).mpr hsame.symm
  have hnonempty : (sourceFiber g q).Nonempty := ⟨x, hx⟩
  refine ⟨q, sourceFiber g q, ?_, hx, hy⟩
  rw [run_placementOfMap F s f word hn hplaced]
  exact (placementOfMap_some_iff g q (sourceFiber g q)).mpr ⟨rfl, hnonempty⟩

theorem no_split_from_sourceOrdered (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (ordered : SourceOrdered s.placed)
    (q : ZMod n) (B : Finset (ZMod n))
    (hpacket : s.placed q = some B)
    (x y : ZMod n) (hx : x ∈ B) (hy : y ∈ B) :
    ∃ q' B', (run F s word).placed q' = some B' ∧
      x ∈ B' ∧ y ∈ B' := by
  obtain ⟨lift, hplaced⟩ := ordered
  have hfiber :=
    (placementOfMap_some_iff lift.position q B).mp (hplaced ▸ hpacket)
  have hxy : lift.position x = lift.position y := by
    have hfx : lift.position x = q :=
      (mem_sourceFiber lift.position x q).mp (hfiber.1.symm ▸ hx)
    have hfy : lift.position y = q :=
      (mem_sourceFiber lift.position y q).mp (hfiber.1.symm ▸ hy)
    exact hfx.trans hfy.symm
  exact no_split_after_actual_word F s lift.position word hn hplaced x y hxy

theorem no_split_from_reachable (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (word : List Letter) (hn : 2 ≤ n)
    (reachable : ReachableFromSingleton F s.placed)
    (q : ZMod n) (B : Finset (ZMod n))
    (hpacket : s.placed q = some B)
    (x y : ZMod n) (hx : x ∈ B) (hy : y ∈ B) :
    ∃ q' B', (run F s word).placed q' = some B' ∧
      x ∈ B' ∧ y ∈ B' := by
  exact no_split_from_sourceOrdered F s word hn
    (reachable_source_ordered F s.placed hn reachable)
    q B hpacket x y hx hy

end RegisteredAbsorptionChains
