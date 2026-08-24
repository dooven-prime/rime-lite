import Formalization.UniformModularZeroRoute

/-!
# Uniform modular zero-route classification over finite fields

This file supplies the semantic bridge omitted by the finite shape core. It
defines the projective carrier `F ∪ {infinity}`, the labelled modular maps,
the marked two-sector interface, Boolean route candidates, and actual ordered
two-step routes. The main theorem applies to every finite field of cardinality
at least three; the odd-prime statement is a corollary.
-/

namespace Formalization

namespace UniformModularZeroRoute

section FieldSemantics

variable (F : Type*) [Field F] [Fintype F] [DecidableEq F]

abbrev ProjectivePoint := Option F

def pointSector : ProjectivePoint F → Sector
  | none => 0
  | some _ => 1

def evalGenerator : Label → ProjectivePoint F → ProjectivePoint F
  | .S, none => some 0
  | .S, some x => if x = 0 then none else some (-x⁻¹)
  | .R, none => some 0
  | .R, some x => if x = -1 then none else some (-(x + 1)⁻¹)
  | .RInv, none => some (-1)
  | .RInv, some x => if x = 0 then none else some (-1 - x⁻¹)

def EdgeSupported (a : Label) (target source : Sector) : Prop :=
  ∃ x : ProjectivePoint F,
    pointSector F x = source ∧ pointSector F (evalGenerator F a x) = target

def BooleanCandidate (route : Route) : Prop :=
  let ((a, b), (target, middle, source)) := route
  EdgeSupported F a middle source ∧ EdgeSupported F b target middle

def RouteRealized (route : Route) : Prop :=
  let ((a, b), (target, middle, source)) := route
  ∃ x : ProjectivePoint F,
    pointSector F x = source
      ∧ pointSector F (evalGenerator F a x) = middle
      ∧ pointSector F (evalGenerator F b (evalGenerator F a x)) = target

def SemanticZeroRoute (route : Route) : Prop :=
  BooleanCandidate F route ∧ ¬ RouteRealized F route

@[simp] theorem pointSector_none : pointSector F none = 0 := rfl

@[simp] theorem pointSector_some (x : F) : pointSector F (some x) = 1 := rfl

theorem edge_infinity_to_infinity_is_absent (a : Label) :
    ¬ EdgeSupported F a 0 0 := by
  rintro ⟨x, hx, hax⟩
  cases x with
  | none =>
      cases a <;> simp [pointSector, evalGenerator] at hax
  | some x =>
      simp [pointSector] at hx

theorem edge_finite_to_infinity_is_present (a : Label) :
    EdgeSupported F a 0 1 := by
  cases a with
  | S =>
      exact ⟨some 0, rfl, by simp [pointSector, evalGenerator]⟩
  | R =>
      exact ⟨some (-1), rfl, by simp [pointSector, evalGenerator]⟩
  | RInv =>
      exact ⟨some 0, rfl, by simp [pointSector, evalGenerator]⟩

theorem edge_infinity_to_finite_is_present (a : Label) :
    EdgeSupported F a 1 0 := by
  cases a <;> exact ⟨none, rfl, rfl⟩

theorem edge_finite_to_finite_is_present (a : Label) :
    EdgeSupported F a 1 1 := by
  cases a with
  | S =>
      exact ⟨some 1, rfl, by simp [pointSector, evalGenerator]⟩
  | R =>
      exact ⟨some 0, rfl, by simp [pointSector, evalGenerator]⟩
  | RInv =>
      exact ⟨some (-1), rfl, by simp [pointSector, evalGenerator]⟩

theorem common_support_template (a : Label) (target source : Sector) :
    EdgeSupported F a target source ↔
      (target, source) ∈ ({(1, 0), (0, 1), (1, 1)} : Finset (Sector × Sector)) := by
  fin_cases target <;> fin_cases source
  · simpa using edge_infinity_to_infinity_is_absent F a
  · simpa using edge_finite_to_infinity_is_present F a
  · simpa using edge_infinity_to_finite_is_present F a
  · simpa using edge_finite_to_finite_is_present F a

theorem boolean_candidate_iff_candidate_route (route : Route) :
    BooleanCandidate F route ↔ route ∈ candidateRoutes := by
  rcases route with ⟨⟨a, b⟩, ⟨target, middle, source⟩⟩
  simp only [BooleanCandidate]
  rw [common_support_template, common_support_template]
  fin_cases a <;> fin_cases b <;> fin_cases target <;> fin_cases middle <;>
    fin_cases source <;> native_decide

theorem cardinal_ge_three {hcard : 3 ≤ Fintype.card F} :
    (3 : Cardinal) ≤ Cardinal.mk F := by
  rw [Cardinal.mk_fintype]
  exact_mod_cast hcard

theorem add_one_ne_zero_of_ne_neg_one {x : F} (h : x ≠ -1) : x + 1 ≠ 0 := by
  intro hx
  apply h
  calc x = (x + 1) - 1 := by ring
       _ = -1 := by rw [hx]; ring

theorem rInv_value_ne_zero {x : F} (hx0 : x ≠ 0) (hxm1 : x ≠ -1) :
    -1 - x⁻¹ ≠ 0 := by
  intro h
  apply hxm1
  field_simp [hx0] at h
  linear_combination -h

theorem r_value_ne_zero_of_ne_neg_one {x : F} (hxm1 : x ≠ -1) :
    -(x + 1)⁻¹ ≠ 0 := by
  exact neg_ne_zero.mpr (inv_ne_zero (add_one_ne_zero_of_ne_neg_one F hxm1))

theorem r_value_ne_neg_one {x : F} (hx0 : x ≠ 0) (hxm1 : x ≠ -1) :
    -(x + 1)⁻¹ ≠ -1 := by
  intro h
  apply hx0
  have hn := add_one_ne_zero_of_ne_neg_one F hxm1
  field_simp [hn] at h
  linear_combination h

theorem rInv_value_ne_neg_one {x : F} (hx0 : x ≠ 0) :
    -1 - x⁻¹ ≠ -1 := by
  intro h
  apply hx0
  have hz : -x⁻¹ = 0 := by
    calc
      -x⁻¹ = (-1 - x⁻¹) + 1 := by ring
      _ = (-1) + 1 := by rw [h]
      _ = 0 := by ring
  simpa using hz

@[simp] theorem sector_eq_zero_iff (x : ProjectivePoint F) :
    pointSector F x = 0 ↔ x = none := by
  cases x <;> simp [pointSector]

@[simp] theorem sector_eq_one_iff (x : ProjectivePoint F) :
    pointSector F x = 1 ↔ ∃ y : F, x = some y := by
  cases x <;> simp [pointSector]

theorem middle_infinity_routes_are_realized (a b : Label) :
    RouteRealized F ((a, b), shapeMiddleInfinity) := by
  cases a with
  | S =>
      refine ⟨some 0, rfl, ?_, ?_⟩
      · simp [evalGenerator]
      · cases b <;> simp [evalGenerator]
  | R =>
      refine ⟨some (-1), rfl, ?_, ?_⟩
      · simp [evalGenerator]
      · cases b <;> simp [evalGenerator]
  | RInv =>
      refine ⟨some 0, rfl, ?_, ?_⟩
      · simp [evalGenerator]
      · cases b <;> simp [evalGenerator]

theorem source_infinity_target_infinity_realization_iff (a b : Label) :
    RouteRealized F ((a, b), shapeSourceInfinityTargetInfinity) ↔
      (a, b) ∉ zeroWordsSourceInfinityTargetInfinity := by
  fin_cases a <;> fin_cases b <;>
    simp [RouteRealized, shapeSourceInfinityTargetInfinity, evalGenerator,
      sector_eq_zero_iff, sector_eq_one_iff,
      zeroWordsSourceInfinityTargetInfinity, labelS, labelR, labelRInv]

theorem source_infinity_target_finite_realization_iff (a b : Label) :
    RouteRealized F ((a, b), shapeSourceInfinityTargetFinite) ↔
      (a, b) ∉ zeroWordsSourceInfinityTargetFinite := by
  fin_cases a <;> fin_cases b <;>
    simp [RouteRealized, shapeSourceInfinityTargetFinite, evalGenerator,
      sector_eq_zero_iff, sector_eq_one_iff,
      zeroWordsSourceInfinityTargetFinite, labelS, labelR, labelRInv]

theorem source_finite_target_infinity_realized_SR :
    RouteRealized F ((.S, .R), shapeSourceFiniteTargetInfinity) := by
  refine ⟨some 1, rfl, ?_, ?_⟩
  · simp [evalGenerator, pointSector]
  · simp [evalGenerator, pointSector]

theorem source_finite_target_infinity_realized_RR :
    RouteRealized F ((.R, .R), shapeSourceFiniteTargetInfinity) := by
  refine ⟨some 0, rfl, ?_, ?_⟩
  · simp [evalGenerator, pointSector]
  · simp [evalGenerator, pointSector]

theorem source_finite_target_infinity_realized_RInvS :
    RouteRealized F ((.RInv, .S), shapeSourceFiniteTargetInfinity) := by
  refine ⟨some (-1), rfl, ?_, ?_⟩
  · simp [evalGenerator, pointSector]
  · simp [evalGenerator, pointSector]

theorem source_finite_target_infinity_realized_RInvRInv :
    RouteRealized F ((.RInv, .RInv), shapeSourceFiniteTargetInfinity) := by
  refine ⟨some (-1), rfl, ?_, ?_⟩
  · simp [evalGenerator, pointSector]
  · simp [evalGenerator, pointSector]

theorem source_finite_target_infinity_not_realized_SRInv :
    ¬ RouteRealized F ((.S, .RInv), shapeSourceFiniteTargetInfinity) := by
  rintro ⟨x, hsource, hmiddle, htarget⟩
  rcases (sector_eq_one_iff F x).mp hsource with ⟨y, rfl⟩
  simp only [evalGenerator] at hmiddle htarget
  by_cases hy : y = 0
  · subst y
    simp_all [pointSector]
  · simp [hy, pointSector, inv_ne_zero hy] at hmiddle htarget

theorem source_finite_target_infinity_not_realized_RS :
    ¬ RouteRealized F ((.R, .S), shapeSourceFiniteTargetInfinity) := by
  rintro ⟨x, hsource, hmiddle, htarget⟩
  rcases (sector_eq_one_iff F x).mp hsource with ⟨y, rfl⟩
  simp only [evalGenerator] at hmiddle htarget
  by_cases hy : y = -1
  · subst y
    simp_all [pointSector]
  · have hy1 := add_one_ne_zero_of_ne_neg_one F hy
    simp [hy, hy1, pointSector, inv_ne_zero hy1] at hmiddle htarget

theorem source_finite_target_infinity_not_realized_RRInv :
    ¬ RouteRealized F ((.R, .RInv), shapeSourceFiniteTargetInfinity) := by
  rintro ⟨x, hsource, hmiddle, htarget⟩
  rcases (sector_eq_one_iff F x).mp hsource with ⟨y, rfl⟩
  simp only [evalGenerator] at hmiddle htarget
  by_cases hy : y = -1
  · subst y
    simp_all [pointSector]
  · have hy1 := add_one_ne_zero_of_ne_neg_one F hy
    simp [hy, hy1, pointSector, inv_ne_zero hy1] at hmiddle htarget

theorem source_finite_target_infinity_not_realized_RInvR :
    ¬ RouteRealized F ((.RInv, .R), shapeSourceFiniteTargetInfinity) := by
  rintro ⟨x, hsource, hmiddle, htarget⟩
  rcases (sector_eq_one_iff F x).mp hsource with ⟨y, rfl⟩
  simp only [evalGenerator] at hmiddle htarget
  by_cases hy : y = 0
  · subst y
    simp_all [pointSector]
  · simp [hy, pointSector, inv_ne_zero hy] at hmiddle htarget

theorem source_finite_target_infinity_not_realized_SS :
    ¬ RouteRealized F ((.S, .S), shapeSourceFiniteTargetInfinity) := by
  rintro ⟨x, hsource, hmiddle, htarget⟩
  rcases (sector_eq_one_iff F x).mp hsource with ⟨y, rfl⟩
  simp only [evalGenerator] at hmiddle htarget
  by_cases hy : y = 0
  · subst y
    simp_all [pointSector]
  · simp [hy, pointSector, inv_ne_zero hy] at hmiddle htarget

theorem source_finite_target_infinity_realization_iff (a b : Label) :
    RouteRealized F ((a, b), shapeSourceFiniteTargetInfinity) ↔
      (a, b) ∉ zeroWordsSourceFiniteTargetInfinity := by
  fin_cases a <;> fin_cases b
  · simp [source_finite_target_infinity_not_realized_SS,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_realized_SR,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_not_realized_SRInv,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_not_realized_RS,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_realized_RR,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_not_realized_RRInv,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_realized_RInvS,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_not_realized_RInvR,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]
  · simp [source_finite_target_infinity_realized_RInvRInv,
      zeroWordsSourceFiniteTargetInfinity, zeroWordsSourceInfinityTargetFinite,
      labelS, labelR, labelRInv]

theorem all_finite_routes_are_realized
    {hcard : 3 ≤ Fintype.card F} (a b : Label) :
    RouteRealized F ((a, b), shapeAllFinite) := by
  fin_cases a <;> fin_cases b
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hx0, hxm1⟩ := Cardinal.exists_ne_ne_of_three_le hc (0 : F) (-1)
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0, inv_ne_zero hx0]
    · simp [evalGenerator, pointSector, hx0, inv_ne_zero hx0]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hx0, hx1⟩ := Cardinal.exists_ne_ne_of_three_le hc (0 : F) 1
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0]
    · simp [evalGenerator, pointSector, hx0, hx1]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hx0, hx1⟩ := Cardinal.exists_ne_ne_of_three_le hc (0 : F) 1
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0, inv_ne_zero hx0]
    · simp [evalGenerator, pointSector, hx0, inv_ne_zero hx0]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hxm1, hx0⟩ := Cardinal.exists_ne_ne_of_three_le hc (-1 : F) 0
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hxm1,
        add_one_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1]
    · simp [evalGenerator, pointSector, hxm1,
        add_one_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hxm1, hx0⟩ := Cardinal.exists_ne_ne_of_three_le hc (-1 : F) 0
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hxm1,
        add_one_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1]
    · simp [evalGenerator, pointSector, hxm1,
        add_one_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hxm1, hx0⟩ := Cardinal.exists_ne_ne_of_three_le hc (-1 : F) 0
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1, sector_eq_zero_iff,
        sector_eq_one_iff]
    · simp [evalGenerator, pointSector, hxm1,
        r_value_ne_zero_of_ne_neg_one F hxm1,
        r_value_ne_neg_one F hx0 hxm1, sector_eq_zero_iff,
        sector_eq_one_iff]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hxm1, hx0⟩ := Cardinal.exists_ne_ne_of_three_le hc (-1 : F) 0
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0,
        rInv_value_ne_zero F hx0 hxm1, sector_eq_zero_iff,
        sector_eq_one_iff]

    · simp [evalGenerator, pointSector, hx0,
        rInv_value_ne_zero F hx0 hxm1]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hx0, hxm1⟩ := Cardinal.exists_ne_ne_of_three_le hc (0 : F) (-1)
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0,
        rInv_value_ne_zero F hx0 hxm1, sector_eq_zero_iff,
        sector_eq_one_iff]
    · simp [evalGenerator, pointSector, hx0,
        rInv_value_ne_zero F hx0 hxm1,
        rInv_value_ne_neg_one F hx0]
  · have hc := cardinal_ge_three (F := F) (hcard := hcard)
    obtain ⟨x, hx0, hxm1⟩ := Cardinal.exists_ne_ne_of_three_le hc (0 : F) (-1)
    refine ⟨some x, rfl, ?_, ?_⟩
    · simp [evalGenerator, pointSector, hx0]
    · simp [evalGenerator, pointSector, hx0,
        rInv_value_ne_zero F hx0 hxm1, sector_eq_zero_iff,
        sector_eq_one_iff]

theorem route_realized_on_candidate_shape_iff
    {hcard : 3 ≤ Fintype.card F} (a b : Label) (shape : Shape)
    (hshape : shape ∈ candidateShapes) :
    RouteRealized F ((a, b), shape) ↔
      ((shape = shapeMiddleInfinity ∨ shape = shapeAllFinite) ∨
        (shape = shapeSourceInfinityTargetInfinity ∧
          (a, b) ∉ zeroWordsSourceInfinityTargetInfinity) ∨
        (shape = shapeSourceInfinityTargetFinite ∧
          (a, b) ∉ zeroWordsSourceInfinityTargetFinite) ∨
        (shape = shapeSourceFiniteTargetInfinity ∧
          (a, b) ∉ zeroWordsSourceFiniteTargetInfinity)) := by
  rcases shape with ⟨target, middle, source⟩
  fin_cases target <;> fin_cases middle <;> fin_cases source
  all_goals
    simp [candidateShapes, shapeMiddleInfinity,
      shapeSourceInfinityTargetInfinity, shapeSourceInfinityTargetFinite,
      shapeSourceFiniteTargetInfinity, shapeAllFinite] at hshape ⊢
  · simpa [shapeSourceInfinityTargetInfinity] using
      source_infinity_target_infinity_realization_iff (F := F) a b
  · simpa [shapeSourceFiniteTargetInfinity] using
      source_finite_target_infinity_realization_iff (F := F) a b
  · exact middle_infinity_routes_are_realized (F := F) a b
  · simpa [shapeSourceInfinityTargetFinite] using
      source_infinity_target_finite_realization_iff (F := F) a b
  · exact all_finite_routes_are_realized
      (F := F) (hcard := hcard) a b

theorem semantic_zero_route_iff
    {hcard : 3 ≤ Fintype.card F} (route : Route) :
    SemanticZeroRoute F route ↔ route ∈ zeroRoutes := by
  rcases route with ⟨⟨a, b⟩, shape⟩
  rw [SemanticZeroRoute, boolean_candidate_iff_candidate_route]
  constructor
  · rintro ⟨hcandidate, hnot⟩
    have hshape : shape ∈ candidateShapes := by
      simpa [candidateRoutes, orderedLabelPairs] using hcandidate
    rw [route_realized_on_candidate_shape_iff
      (F := F) (hcard := hcard) a b shape hshape] at hnot
    have hcases : shape = shapeMiddleInfinity
        ∨ shape = shapeSourceInfinityTargetInfinity
        ∨ shape = shapeSourceInfinityTargetFinite
        ∨ shape = shapeSourceFiniteTargetInfinity
        ∨ shape = shapeAllFinite := by
      simpa [candidateShapes] using hshape
    rcases hcases with h | h | h | h | h <;> subst shape <;>
      simp [zeroRoutes, shapeMiddleInfinity,
        shapeSourceInfinityTargetInfinity, shapeSourceInfinityTargetFinite,
        shapeSourceFiniteTargetInfinity, shapeAllFinite] at hnot ⊢
    all_goals assumption
  · intro hzero
    have hcandidate : ((a, b), shape) ∈ candidateRoutes :=
      zero_routes_are_candidates hzero
    refine ⟨hcandidate, ?_⟩
    have hshape : shape ∈ candidateShapes := by
      simpa [candidateRoutes, orderedLabelPairs] using hcandidate
    rw [route_realized_on_candidate_shape_iff
      (F := F) (hcard := hcard) a b shape hshape]
    have hcases : shape = shapeMiddleInfinity
        ∨ shape = shapeSourceInfinityTargetInfinity
        ∨ shape = shapeSourceInfinityTargetFinite
        ∨ shape = shapeSourceFiniteTargetInfinity
        ∨ shape = shapeAllFinite := by
      simpa [candidateShapes] using hshape
    rcases hcases with h | h | h | h | h <;> subst shape <;>
      simp [zeroRoutes, shapeMiddleInfinity,
        shapeSourceInfinityTargetInfinity, shapeSourceInfinityTargetFinite,
        shapeSourceFiniteTargetInfinity, shapeAllFinite] at hzero ⊢
    all_goals assumption

noncomputable def semanticZeroRoutes
    (F : Type*) [Field F] [Fintype F] [DecidableEq F] : Finset Route := by
  classical
  exact candidateRoutes.filter (SemanticZeroRoute F)

theorem semantic_zero_routes_eq
    {hcard : 3 ≤ Fintype.card F} :
    semanticZeroRoutes F = zeroRoutes := by
  ext route
  simp [semanticZeroRoutes, semantic_zero_route_iff (F := F) (hcard := hcard),
    zero_routes_are_candidates]

theorem semantic_zero_route_count
    {hcard : 3 ≤ Fintype.card F} :
    (semanticZeroRoutes F).card = 14 := by
  rw [semantic_zero_routes_eq (F := F) (hcard := hcard)]
  exact zero_route_count

structure FiniteFieldModularRouteContract where
  carrierTag : String
  alphabetOrder : List Label
  markedPartitionTag : String
  routeSemanticsTag : String

def finiteFieldContract : FiniteFieldModularRouteContract :=
  {
    carrierTag := "P^1(F)"
    alphabetOrder := [.S, .R, .RInv]
    markedPartitionTag := "{infinity} disjoint union F"
    routeSemanticsTag := "ordered two-step Boolean-supported route semantics"
  }

theorem uniform_modular_zero_route_classification
    {hcard : 3 ≤ Fintype.card F} :
    finiteFieldContract.carrierTag = "P^1(F)"
      ∧ finiteFieldContract.alphabetOrder = [.S, .R, .RInv]
      ∧ finiteFieldContract.markedPartitionTag = "{infinity} disjoint union F"
      ∧ finiteFieldContract.routeSemanticsTag =
        "ordered two-step Boolean-supported route semantics"
      ∧ candidateRoutes.card = 45
      ∧ semanticZeroRoutes F = zeroRoutes
      ∧ (semanticZeroRoutes F).card = 14 := by
  exact ⟨rfl, rfl, rfl, rfl, candidate_route_count,
    semantic_zero_routes_eq (F := F) (hcard := hcard),
    semantic_zero_route_count (F := F) (hcard := hcard)⟩

end FieldSemantics

theorem odd_prime_uniform_modular_zero_route_classification
    {p : Nat} [hp : Fact (Nat.Prime p)] (hodd : Odd p) :
    finiteFieldContract.carrierTag = "P^1(F)"
      ∧ finiteFieldContract.alphabetOrder = [.S, .R, .RInv]
      ∧ finiteFieldContract.markedPartitionTag = "{infinity} disjoint union F"
      ∧ finiteFieldContract.routeSemanticsTag =
        "ordered two-step Boolean-supported route semantics"
      ∧ candidateRoutes.card = 45
      ∧ semanticZeroRoutes (ZMod p) = zeroRoutes
      ∧ (semanticZeroRoutes (ZMod p)).card = 14 := by
  have hp_ne_two : p ≠ 2 := by
    intro h
    subst p
    norm_num at hodd
  have hp_three : 3 ≤ p := by
    have hp_two := hp.out.two_le
    omega
  have hcard : 3 ≤ Fintype.card (ZMod p) := by
    simpa [ZMod.card p] using hp_three
  exact uniform_modular_zero_route_classification
    (F := ZMod p) (hcard := hcard)

end UniformModularZeroRoute

end Formalization
