import ProperArc.OriginBoundary
import RegisteredAbsorptionChains.CleanChainWitness

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def renameRecord (e : ZMod n ≃ ZMod n) (rho : FusionRecord (ZMod n)) :
    FusionRecord (ZMod n) :=
  ⟨rho.left.image e, rho.right.image e, rho.result.image e⟩

def renameExecution (e : ZMod n ≃ ZMod n) (s : Execution n (ZMod n)) :
    Execution n (ZMod n) :=
  ⟨fun q => (s.placed q).map (Finset.image e),
    s.origin.map (renameRecord e), s.chain.map (renameRecord e)⟩

theorem rename_fusionPlacement (e : ZMod n ≃ ZMod n)
    (P : Placement n (Finset (ZMod n))) :
    fusionPlacement (fun q => (P q).map (Finset.image e)) =
      fun q => (fusionPlacement P q).map (Finset.image e) := by
  funext q
  simp only [fusionPlacement]
  split_ifs <;> cases h0 : P 0 <;> cases h1 : P 1 <;>
    simp [Finset.image_union]

/-- Source renaming changes atom identities, not physical ports or chronological
letters. Registration and selected-event guards are transported exactly. -/
theorem rename_step (e : ZMod n ≃ ZMod n) (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (a : Letter) :
    renameExecution e (step F s a) =
      step (F.image e) (renameExecution e s) a := by
  cases a with
  | p => rfl
  | d =>
      have hp := rename_fusionPlacement e s.placed
      cases ho : s.origin <;> cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
        simp [step, stepDefect, renameExecution, renameRecord, h0, h1,
          ho, ← hp, ← Finset.image_union, Finset.image_inj e.injective,
          Finset.image_subset_image_iff e.injective] <;>
        split_ifs <;> simp_all [renameRecord, List.map_append, Finset.image_union]

theorem rename_run (e : ZMod n ≃ ZMod n) (F : Finset (ZMod n))
    (s : Execution n (ZMod n)) (w : List Letter) :
    renameExecution e (run F s w) =
      run (F.image e) (renameExecution e s) w := by
  induction w generalizing s with
  | nil => rfl
  | cons a w ih => simpa only [run, List.foldl_cons, rename_step] using ih (step F s a)

def sourceShift (c : ZMod n) : ZMod n ≃ ZMod n := Equiv.addLeft c

@[simp] theorem sourceShift_apply (c a : ZMod n) : sourceShift c a = c+a := rfl

theorem shift_interval (c : ZMod n) (lo hi : ℕ) :
    (interval (0 : ZMod n) lo hi).image (sourceShift c) = interval c lo hi := by
  simp [interval, Finset.image_image, Function.comp_def]

theorem shift_arc (c : ZMod n) (r : ℕ) :
    (arc (0 : ZMod n) r).image (sourceShift c) = arc c r :=
  shift_interval c 0 r

theorem shift_origin (c : ZMod n) (r t : ℕ) :
    renameRecord (sourceShift c) (originRecord 0 r t) = originRecord c r t := by
  simp [renameRecord, originRecord, shift_interval, shift_arc]

theorem shift_seed (c : ZMod n) :
    renameExecution (sourceShift c) (singletonExecution n) = alignedExecution c := by
  rfl

theorem shift_boundary (c : ZMod n) (r : ℕ) (origin : Option (FusionRecord (ZMod n))) :
    renameExecution (sourceShift c) ⟨boundaryPlacement 0 r, origin, []⟩ =
      ⟨boundaryPlacement c r, origin.map (renameRecord (sourceShift c)), []⟩ := by
  unfold renameExecution
  simp only [List.map_nil]
  congr 1
  funext q
  simp only [boundaryPlacement]
  split_ifs <;> simp [shift_arc]

theorem rename_clean (e : ZMod n ≃ ZMod n) (C : Finset (ZMod n))
    (s : Execution n (ZMod n)) (h : CleanOutside C s) :
    CleanOutside (C.image e) (renameExecution e s) := by
  obtain ⟨⟨q, hq⟩, hout⟩ := h
  constructor
  · exact ⟨q, by simp [renameExecution, hq]⟩
  · intro q B hB
    have hB' : (s.placed q).map (Finset.image e) = some B := hB
    cases hs : s.placed q with
    | none => simp [hs] at hB'
    | some U =>
        have hU : U.image e = B := by simpa [hs] using hB'
        rcases hout q U hs with rfl | ⟨a, rfl⟩
        · exact Or.inl hU.symm
        · exact Or.inr ⟨e a, by simpa using hU.symm⟩

end ProperArc.Chains
