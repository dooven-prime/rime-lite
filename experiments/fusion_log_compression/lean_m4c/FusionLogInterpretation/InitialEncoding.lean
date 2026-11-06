import FusionLogInterpretation.PacketInterpretation

namespace FusionLogInterpretation

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay

variable {n : ℕ} [NeZero n]
variable {α : Type*} [DecidableEq α]

/-- The last integer at or before x congruent to an occupied site q. -/
def lastAtSite (q : ZMod n) (x : ℤ) : ℤ :=
  (q.val : ℤ) + (x - q.val) / (n : ℤ) * n

theorem lastAtSite_le (q : ZMod n) (x : ℤ) : lastAtSite q x ≤ x := by
  have nonzero : (n : ℤ) ≠ 0 := by exact_mod_cast NeZero.ne n
  have bound := Int.ediv_mul_le (x - q.val) nonzero
  unfold lastAtSite
  omega

theorem lastAtSite_monotone (q : ZMod n) : Monotone (lastAtSite q) := by
  intro x y le
  have positive : (0 : ℤ) < n := by exact_mod_cast NeZero.pos n
  have div := Int.ediv_le_ediv positive (show x - q.val ≤ y - q.val by omega)
  have mul := mul_le_mul_of_nonneg_right div (le_of_lt positive)
  dsimp [lastAtSite]
  omega

theorem lastAtSite_periodic (q : ZMod n) (x k : ℤ) :
    lastAtSite q (x + k * n) = lastAtSite q x + k * n := by
  have nonzero : (n : ℤ) ≠ 0 := by exact_mod_cast NeZero.ne n
  unfold lastAtSite
  rw [show x + k * n - q.val = (x - q.val) + k * n by ring,
    Int.add_mul_ediv_right _ _ nonzero]
  ring

@[simp] theorem lastAtSite_cast (q : ZMod n) (x : ℤ) :
    (lastAtSite q x : ZMod n) = q := by
  simp [lastAtSite]

def occupiedRounding (S : Finset (ZMod n)) (nonempty : S.Nonempty) : SourceOrderLift n where
  map := fun x => S.sup' nonempty (fun q => lastAtSite q x)
  monotone := by
    intro x y le
    exact Finset.sup'_mono_fun (fun q _ => lastAtSite_monotone q le)
  periodic := by
    intro x k
    obtain ⟨q, hq, top⟩ := Finset.exists_mem_eq_sup' nonempty (fun q => lastAtSite q (x + k * n))
    obtain ⟨p, hp, base⟩ := Finset.exists_mem_eq_sup' nonempty (fun q => lastAtSite q x)
    apply le_antisymm
    · rw [top, lastAtSite_periodic]
      have below := Finset.le_sup' (fun q => lastAtSite q x) hq
      omega
    · rw [base, ← lastAtSite_periodic]
      exact Finset.le_sup' (fun q => lastAtSite q (x + k * n)) hp

theorem occupiedRounding_image (S : Finset (ZMod n)) (nonempty : S.Nonempty) (a : ZMod n) :
    (occupiedRounding S nonempty).position a ∈ S := by
  obtain ⟨q, hq, top⟩ := Finset.exists_mem_eq_sup' nonempty (fun q => lastAtSite q a.val)
  change ((S.sup' nonempty (fun q => lastAtSite q a.val) : ℤ) : ZMod n) ∈ S
  rw [top, lastAtSite_cast]
  exact hq

theorem occupiedRounding_fixed (S : Finset (ZMod n)) (nonempty : S.Nonempty)
    (q : ZMod n) (present : q ∈ S) :
    (occupiedRounding S nonempty).position q = q := by
  have top : S.sup' nonempty (fun p => lastAtSite p q.val) = (q.val : ℤ) := by
    apply le_antisymm
    · exact Finset.sup'_le _ _ (fun p _ => lastAtSite_le p q.val)
    · calc
        (q.val : ℤ) = lastAtSite q q.val := by simp only [lastAtSite, sub_self,
          Int.zero_ediv, zero_mul, add_zero]
        _ ≤ _ := Finset.le_sup' (fun p => lastAtSite p q.val) present
  change ((S.sup' nonempty (fun p => lastAtSite p q.val) : ℤ) : ZMod n) = q
  rw [top]
  simp

/-- Occupied-site indices carry their original packet; auxiliary hole
indices carry the empty label. No new physical packet is introduced. -/
def siteLabels (P : Placement n (Finset α)) (q : ZMod n) : Finset α :=
  (P q).getD ∅

def canonicalPlacement (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) : Placement n (Finset (ZMod n)) :=
  placementOfMap (occupiedRounding (occupiedSites P) nonempty).position

theorem canonicalPlacement_ordered (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) : SourceOrdered (canonicalPlacement P nonempty) :=
  ⟨occupiedRounding (occupiedSites P) nonempty, rfl⟩

theorem initial_placement_interprets (P : Placement n (Finset α))
    (nonempty : (occupiedSites P).Nonempty) :
    P = expandPlacement (siteLabels P) (canonicalPlacement P nonempty) := by
  let lift := occupiedRounding (occupiedSites P) nonempty
  funext q
  cases hP : P q with
  | none =>
      have empty : sourceFiber lift.position q = ∅ := by
        apply Finset.eq_empty_iff_forall_notMem.mpr
        intro z hz
        have atSite := (mem_sourceFiber lift.position z q).mp hz
        have image := occupiedRounding_image (occupiedSites P) nonempty z
        change lift.position z ∈ occupiedSites P at image
        rw [atSite] at image
        simpa [occupiedSites, hP] using image
      have encoded : canonicalPlacement P nonempty q = none :=
        (placementOfMap_none_iff lift.position q).mpr empty
      simp [expandPlacement, hP, encoded]
  | some B =>
      have present : q ∈ occupiedSites P := by simp [occupiedSites, hP]
      have fixed := occupiedRounding_fixed (occupiedSites P) nonempty q present
      have member : q ∈ sourceFiber lift.position q := (mem_sourceFiber _ _ _).mpr fixed
      have fiberNonempty : (sourceFiber lift.position q).Nonempty := ⟨q, member⟩
      have encoded : canonicalPlacement P nonempty q = some (sourceFiber lift.position q) :=
        (placementOfMap_some_iff lift.position q _).mpr ⟨rfl, fiberNonempty⟩
      have decoded : expandBlock (siteLabels P) (sourceFiber lift.position q) = B := by
        ext a
        simp only [expandBlock, Finset.mem_biUnion]
        constructor
        · rintro ⟨z, hz, ha⟩
          cases hzP : P z with
          | none => simp [siteLabels, hzP] at ha
          | some C =>
              have zPresent : z ∈ occupiedSites P := by simp [occupiedSites, hzP]
              have zFixed := occupiedRounding_fixed (occupiedSites P) nonempty z zPresent
              have atSite := (mem_sourceFiber lift.position z q).mp hz
              have eq : z = q := zFixed.symm.trans atSite
              subst z
              simpa [siteLabels, hP] using ha
        · intro ha
          exact ⟨q, member, by simpa [siteLabels, hP] using ha⟩
      simp [expandPlacement, hP, encoded, decoded]

end FusionLogInterpretation
