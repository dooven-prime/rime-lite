import Mathlib.GroupTheory.Coset.Basic
import Mathlib.Algebra.Group.Subgroup.Finite

/-!
# Right-phase cosets and deterministic left updates

Phase acts on the left, so the state class is H*x. No normality of H is
assumed. State-set compression and deterministic labelled descent are
separate results.
-/

namespace Rime.Paper37

universe u v

abbrev RightPhaseSpace (G : Type u) [Group G] (H : Subgroup G) :=
  Quotient (QuotientGroup.rightRel H)

def rightPhaseClass {G : Type u} [Group G] (H : Subgroup G) (g : G) :
    RightPhaseSpace G H := Quotient.mk'' g

theorem rightPhaseClass_eq_iff {G : Type u} [Group G]
    (H : Subgroup G) (x y : G) :
    rightPhaseClass H x = rightPhaseClass H y ↔ y * x⁻¹ ∈ H := by
  change Quotient.mk'' x = Quotient.mk'' y ↔ _
  rw [Quotient.eq'', QuotientGroup.rightRel_apply]

def lanePhaseSetoid {Lane : Type v} {G : Type u} [Group G] (H : Subgroup G) :
    Setoid (Lane × G) where
  r x y := x.1 = y.1 ∧ (QuotientGroup.rightRel H) x.2 y.2
  iseqv := ⟨fun x => ⟨rfl, (QuotientGroup.rightRel H).iseqv.refl x.2⟩,
    fun h => ⟨h.1.symm, (QuotientGroup.rightRel H).iseqv.symm h.2⟩,
    fun hxy hyz => ⟨hxy.1.trans hyz.1,
      (QuotientGroup.rightRel H).iseqv.trans hxy.2 hyz.2⟩⟩

def lanePhaseMap {Lane : Type v} {G : Type u} [Group G] (H : Subgroup G) :
    Quotient (lanePhaseSetoid (Lane := Lane) H) → Lane × RightPhaseSpace G H :=
  Quotient.lift (fun x => (x.1, rightPhaseClass H x.2)) fun x y h => by
    exact Prod.ext h.1 (Quotient.sound h.2)

theorem lanePhaseMap_bijective {Lane : Type v} {G : Type u} [Group G]
    (H : Subgroup G) : Function.Bijective (lanePhaseMap (Lane := Lane) H) := by
  constructor
  · intro x y
    induction x using Quotient.inductionOn with
    | h x =>
      induction y using Quotient.inductionOn with
      | h y =>
        intro heq
        change (x.1, rightPhaseClass H x.2) = (y.1, rightPhaseClass H y.2) at heq
        apply Quotient.sound
        change x.1 = y.1 ∧ (QuotientGroup.rightRel H) x.2 y.2
        have hlane := congrArg (fun z : Lane × RightPhaseSpace G H => z.1) heq
        have hphase := congrArg (fun z : Lane × RightPhaseSpace G H => z.2) heq
        exact ⟨hlane, Quotient.exact hphase⟩
  · rintro ⟨lane, phase⟩
    induction phase using Quotient.inductionOn with
    | h g => exact ⟨Quotient.mk'' (lane, g), rfl⟩

/-- Corollary 4.2's abstract state-set bijection. -/
noncomputable def lanePhaseEquiv {Lane : Type v} {G : Type u} [Group G]
    (H : Subgroup G) :
    Quotient (lanePhaseSetoid (Lane := Lane) H) ≃ Lane × RightPhaseSpace G H :=
  Equiv.ofBijective (lanePhaseMap H) (lanePhaseMap_bijective H)

def PhaseDeterministic {G : Type u} [Group G] (H : Subgroup G) (sigma : G) : Prop :=
  ∀ x y, rightPhaseClass H x = rightPhaseClass H y →
    rightPhaseClass H (sigma * x) = rightPhaseClass H (sigma * y)

/-- Proposition 4.3: finite phase fibers convert one-way conjugation
inclusion to the exact normalizer condition. -/
theorem phaseDeterministic_iff_mem_normalizer {G : Type u} [Group G]
    (H : Subgroup G) [Finite H] (sigma : G) :
    PhaseDeterministic H sigma ↔ sigma ∈ Subgroup.normalizer (H : Set G) := by
  constructor
  · intro hdet
    apply Subgroup.mem_normalizer_fintype
    intro h hh
    have hphase : rightPhaseClass H 1 = rightPhaseClass H h :=
      (rightPhaseClass_eq_iff H 1 h).mpr (by simpa using hh)
    have himage := (rightPhaseClass_eq_iff H (sigma * 1) (sigma * h)).mp
      (hdet 1 h hphase)
    simpa [mul_assoc] using himage
  · intro hnormal x y hphase
    apply (rightPhaseClass_eq_iff H _ _).mpr
    have hxy := (rightPhaseClass_eq_iff H x y).mp hphase
    have hconj := (Subgroup.mem_normalizer_iff.mp hnormal (y * x⁻¹)).mp hxy
    simpa only [mul_inv_rev, mul_assoc] using hconj

theorem phase_non_descent_witness {G : Type u} [Group G]
    (H : Subgroup G) [Finite H] {sigma : G}
    (h : sigma ∉ Subgroup.normalizer (H : Set G)) :
    ∃ x y, rightPhaseClass H x = rightPhaseClass H y ∧
      rightPhaseClass H (sigma * x) ≠ rightPhaseClass H (sigma * y) := by
  classical
  have hnot : ¬ PhaseDeterministic H sigma :=
    fun hdet => h ((phaseDeterministic_iff_mem_normalizer H sigma).mp hdet)
  obtain ⟨x, hx⟩ := not_forall.mp hnot
  obtain ⟨y, hy⟩ := not_forall.mp hx
  exact ⟨x, y, Classical.not_imp.mp hy⟩

end Rime.Paper37
