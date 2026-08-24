import Formalization.UniformModularZeroRouteField

/-!
# Finite-field route profiles: paper-owned Lean entry point

This file exposes the theorem surface owned by Paper XXI. It imports the
source-addressed finite-field semantics vendored in this paper-owned Lake
project and adds the arbitrary-depth Boolean candidate
count, the exact depth-three support-shape enumeration, and the complete
characteristic-aware depth-three zero-route count.
-/

namespace FiniteFieldRouteProfiles

open Formalization.UniformModularZeroRoute

section DepthTwo

variable (F : Type*) [Field F] [Fintype F] [DecidableEq F]

/-- Paper-facing depth-two theorem over every finite field of cardinality at
least three.  The set equality is stronger than the numerical `14 / 45`
statement: it identifies every semantic zero route with the declared finite
classification. -/
theorem finite_field_depth_two_semantic_classification
    (hcard : 3 <= Fintype.card F) :
    candidateRoutes.card = 45
      /\ semanticZeroRoutes F = zeroRoutes
      /\ (semanticZeroRoutes F).card = 14 := by
  exact ⟨candidate_route_count,
    semantic_zero_routes_eq (F := F) (hcard := hcard),
    semantic_zero_route_count (F := F) (hcard := hcard)⟩

end DepthTwo

section CandidateCount

/-- Dynamic-programming state `(ending at infinity, ending finite)` after
`depth` supported steps in the common two-sector support template. -/
def supportedShapeStateCounts : Nat -> Nat × Nat
  | 0 => (1, 1)
  | depth + 1 =>
      let previous := supportedShapeStateCounts depth
      (previous.2, previous.1 + previous.2)

def supportedShapeCount (depth : Nat) : Nat :=
  (supportedShapeStateCounts depth).1 + (supportedShapeStateCounts depth).2

theorem supported_shape_state_counts_eq_fib (depth : Nat) :
    supportedShapeStateCounts depth =
      (Nat.fib (depth + 1), Nat.fib (depth + 2)) := by
  induction depth with
  | zero => norm_num [supportedShapeStateCounts]
  | succ depth ih =>
      simp [supportedShapeStateCounts, ih, Nat.fib_add_two, Nat.add_assoc]

theorem supported_shape_count_eq_fib (depth : Nat) :
    supportedShapeCount depth = Nat.fib (depth + 3) := by
  rw [supportedShapeCount, supported_shape_state_counts_eq_fib]
  simp [Nat.fib_add_two, Nat.add_assoc]

/-- Three independently labelled generators multiply the supported path count
by `3^depth`. -/
def booleanCandidateCount (depth : Nat) : Nat :=
  3 ^ depth * supportedShapeCount depth

theorem boolean_candidate_count_eq (depth : Nat) :
    booleanCandidateCount depth = 3 ^ depth * Nat.fib (depth + 3) := by
  simp [booleanCandidateCount, supported_shape_count_eq_fib]

end CandidateCount

section DepthThreeSupport

structure DepthThreeShape where
  source : Sector
  middleOne : Sector
  middleTwo : Sector
  target : Sector
  deriving DecidableEq, Fintype, Repr

abbrev LabelTriple := Label × Label × Label
abbrev DepthThreeCandidate := LabelTriple × DepthThreeShape

def shape0101 : DepthThreeShape := ⟨0, 1, 0, 1⟩
def shape0110 : DepthThreeShape := ⟨0, 1, 1, 0⟩
def shape0111 : DepthThreeShape := ⟨0, 1, 1, 1⟩
def shape1010 : DepthThreeShape := ⟨1, 0, 1, 0⟩
def shape1011 : DepthThreeShape := ⟨1, 0, 1, 1⟩
def shape1101 : DepthThreeShape := ⟨1, 1, 0, 1⟩
def shape1110 : DepthThreeShape := ⟨1, 1, 1, 0⟩
def shape1111 : DepthThreeShape := ⟨1, 1, 1, 1⟩

def depthThreeSupportedShapes : Finset DepthThreeShape :=
  {shape0101, shape0110, shape0111, shape1010,
    shape1011, shape1101, shape1110, shape1111}

def orderedLabelTriples : Finset LabelTriple := Finset.univ

def depthThreeCandidates : Finset DepthThreeCandidate :=
  orderedLabelTriples.product depthThreeSupportedShapes

def DepthThreeRouteRealized
    (F : Type*) [Field F] [DecidableEq F]
    (route : DepthThreeCandidate) : Prop :=
  let ((a, b, c), shape) := route
  ∃ x : ProjectivePoint F,
    pointSector F x = shape.source
      ∧ pointSector F (evalGenerator F a x) = shape.middleOne
      ∧ pointSector F (evalGenerator F b (evalGenerator F a x)) = shape.middleTwo
      ∧ pointSector F
          (evalGenerator F c (evalGenerator F b (evalGenerator F a x))) =
            shape.target

theorem depth_three_supported_shape_count :
    depthThreeSupportedShapes.card = 8 := by
  native_decide

theorem ordered_label_triple_count : orderedLabelTriples.card = 27 := by
  native_decide

theorem depth_three_candidate_count : depthThreeCandidates.card = 216 := by
  native_decide

section SemanticEnumeration

variable (F : Type*) [Field F] [Fintype F] [DecidableEq F]

/-- Semantic zero routes at depth three, restricted to the declared Boolean
candidate set.  This is a finite typed set, not a scalar histogram. -/
noncomputable def depthThreeSemanticZeroRoutes
    (F : Type*) [Field F] [Fintype F] [DecidableEq F] :
    Finset DepthThreeCandidate := by
  classical
  exact depthThreeCandidates.filter (fun route => ¬ DepthThreeRouteRealized F route)

noncomputable def depthThreeZeroShapeCount
    (F : Type*) [Field F] [Fintype F] [DecidableEq F]
    (shape : DepthThreeShape) : Nat :=
  (depthThreeSemanticZeroRoutes F).filter (fun route => route.2 = shape) |>.card

/-- A computable finite enumeration of the same semantic predicate.  This is
used for the exact `ZMod 2` and `ZMod 3` exception receipts. -/
def depthThreeRouteRealizedBool
    (F : Type*) [Field F] [Fintype F] [DecidableEq F]
    (route : DepthThreeCandidate) : Bool :=
  let ((a, b, c), shape) := route
  let witnesses := (Finset.univ : Finset (ProjectivePoint F)).filter (fun x =>
    pointSector F x = shape.source
      ∧ pointSector F (evalGenerator F a x) = shape.middleOne
      ∧ pointSector F
        (evalGenerator F b (evalGenerator F a x)) = shape.middleTwo
      ∧ pointSector F
        (evalGenerator F c
          (evalGenerator F b (evalGenerator F a x))) = shape.target)
  decide witnesses.Nonempty

def depthThreeSemanticZeroRoutesComputable
    (F : Type*) [Field F] [Fintype F] [DecidableEq F] :
    Finset DepthThreeCandidate :=
  depthThreeCandidates.filter (fun route =>
    !(depthThreeRouteRealizedBool F route))

def depthThreeZeroShapeCountComputable
    (F : Type*) [Field F] [Fintype F] [DecidableEq F]
    (shape : DepthThreeShape) : Nat :=
  (depthThreeSemanticZeroRoutesComputable F).filter
    (fun route => route.2 = shape) |>.card

theorem depth_three_route_realized_bool_iff
    (route : DepthThreeCandidate) :
    depthThreeRouteRealizedBool F route = true ↔
      DepthThreeRouteRealized F route := by
  classical
  rcases route with ⟨⟨a, b, c⟩, shape⟩
  simp [depthThreeRouteRealizedBool, DepthThreeRouteRealized,
    Finset.filter_nonempty_iff]

theorem depth_three_route_not_realized_bool_iff
    (route : DepthThreeCandidate) :
    depthThreeRouteRealizedBool F route = false ↔
      ¬ DepthThreeRouteRealized F route := by
  constructor
  · intro hfalse hrealized
    have htrue := (depth_three_route_realized_bool_iff F route).2 hrealized
    rw [hfalse] at htrue
    simp at htrue
  · intro hnot
    cases hbool : depthThreeRouteRealizedBool F route with
    | false => rfl
    | true =>
        exact False.elim
          (hnot ((depth_three_route_realized_bool_iff F route).1 hbool))

theorem depth_three_semantic_zero_routes_computable_eq :
    depthThreeSemanticZeroRoutesComputable F =
      depthThreeSemanticZeroRoutes F := by
  classical
  ext route
  simp only [depthThreeSemanticZeroRoutesComputable,
    depthThreeSemanticZeroRoutes, Finset.mem_filter]
  constructor
  · rintro ⟨hcandidate, hfalse⟩
    refine ⟨hcandidate, ?_⟩
    intro hrealized
    have htrue := (depth_three_route_realized_bool_iff F route).2 hrealized
    rw [htrue] at hfalse
    simp at hfalse
  · rintro ⟨hcandidate, hnot⟩
    refine ⟨hcandidate, ?_⟩
    cases hbool : depthThreeRouteRealizedBool F route with
    | false => simp [hbool]
    | true =>
        exact False.elim
          (hnot ((depth_three_route_realized_bool_iff F route).1 hbool))

theorem depth_three_semantic_zero_routes_subset :
    depthThreeSemanticZeroRoutes F ⊆ depthThreeCandidates := by
  classical
  intro route hroute
  exact (Finset.mem_filter.mp hroute).1

end SemanticEnumeration

section ExceptionalEnumeration

def zmodTwoShapeHistogram : List Nat :=
  [depthThreeZeroShapeCountComputable (ZMod 2) shape0101,
    depthThreeZeroShapeCountComputable (ZMod 2) shape0110,
    depthThreeZeroShapeCountComputable (ZMod 2) shape0111,
    depthThreeZeroShapeCountComputable (ZMod 2) shape1010,
    depthThreeZeroShapeCountComputable (ZMod 2) shape1011,
    depthThreeZeroShapeCountComputable (ZMod 2) shape1101,
    depthThreeZeroShapeCountComputable (ZMod 2) shape1110,
    depthThreeZeroShapeCountComputable (ZMod 2) shape1111]

def zmodThreeShapeHistogram : List Nat :=
  [depthThreeZeroShapeCountComputable (ZMod 3) shape0101,
    depthThreeZeroShapeCountComputable (ZMod 3) shape0110,
    depthThreeZeroShapeCountComputable (ZMod 3) shape0111,
    depthThreeZeroShapeCountComputable (ZMod 3) shape1010,
    depthThreeZeroShapeCountComputable (ZMod 3) shape1011,
    depthThreeZeroShapeCountComputable (ZMod 3) shape1101,
    depthThreeZeroShapeCountComputable (ZMod 3) shape1110,
    depthThreeZeroShapeCountComputable (ZMod 3) shape1111]

theorem zmod_two_shape_histogram_exact :
    zmodTwoShapeHistogram = [12, 22, 20, 12, 15, 15, 20, 19] := by
  native_decide

theorem zmod_three_shape_histogram_exact :
    zmodThreeShapeHistogram = [12, 23, 19, 12, 15, 15, 19, 1] := by
  native_decide

theorem zmod_two_zero_route_count_exact :
    (depthThreeSemanticZeroRoutesComputable (ZMod 2)).card = 135 := by
  native_decide

theorem zmod_three_zero_route_count_exact :
    (depthThreeSemanticZeroRoutesComputable (ZMod 3)).card = 116 := by
  native_decide

end ExceptionalEnumeration

end DepthThreeSupport

section PolePreimageTerms

variable (F : Type*) [Field F] [Fintype F] [DecidableEq F]

/-- The paper's `v_a = a(infinity)`. -/
def valueAtInfinity (a : Label) : ProjectivePoint F :=
  evalGenerator F a none

/-- The unique finite pole for each declared labelled generator. -/
def pole : Label -> F
  | .S => 0
  | .R => -1
  | .RInv => 0

omit [Fintype F] in
@[simp] theorem eval_generator_eq_infinity_iff
    (a : Label) (x : ProjectivePoint F) :
    evalGenerator F a x = none ↔ x = some (pole F a) := by
  cases a <;> cases x <;> simp [evalGenerator, pole]

omit [Fintype F] [DecidableEq F] in
@[simp] theorem projective_is_finite_iff (x : ProjectivePoint F) :
    (∃ y : F, x = some y) ↔ x ≠ none := by
  cases x <;> simp

omit [Field F] [Fintype F] [DecidableEq F] in
@[simp] theorem sector_one_iff_ne_infinity (x : ProjectivePoint F) :
    pointSector F x = 1 ↔ x ≠ none := by
  cases x <;> simp [pointSector]

omit [Fintype F] in
@[simp] theorem generator_maps_infinity_to_finite (a : Label) :
    evalGenerator F a none ≠ none := by
  cases a <;> simp [evalGenerator]

omit [Fintype F] in
@[simp] theorem generator_maps_pole_to_infinity (a : Label) :
    evalGenerator F a (some (pole F a)) = none :=
  (eval_generator_eq_infinity_iff F a _).2 rfl

def inverseLabel : Label -> Label
  | .S => .S
  | .R => .RInv
  | .RInv => .R

@[simp] theorem inverse_label_involutive (a : Label) :
    inverseLabel (inverseLabel a) = a := by
  cases a <;> rfl

theorem eval_inverse_label (a : Label) (x : ProjectivePoint F) :
    evalGenerator F (inverseLabel a) (evalGenerator F a x) = x := by
  cases a with
  | S =>
      cases x with
      | none => simp [inverseLabel, evalGenerator]
      | some x =>
          by_cases hx : x = 0
          · simp [inverseLabel, evalGenerator, hx]
          · simp [inverseLabel, evalGenerator, hx, inv_ne_zero hx]
  | R =>
      cases x with
      | none => simp [inverseLabel, evalGenerator]
      | some x =>
          by_cases hx : x = -1
          · simp [inverseLabel, evalGenerator, hx]
          · have hx1 := add_one_ne_zero_of_ne_neg_one F hx
            simp [inverseLabel, evalGenerator, hx, hx1]
  | RInv =>
      cases x with
      | none => simp [inverseLabel, evalGenerator]
      | some x =>
          by_cases hx : x = 0
          · simp [inverseLabel, evalGenerator, hx]
          · have hvalue := rInv_value_ne_neg_one F hx
            simp [inverseLabel, evalGenerator, hx, hvalue]
            have hinner : -1 - x⁻¹ + 1 = -x⁻¹ := by ring
            rw [hinner]
            simp

theorem eval_label_inverse (a : Label) (x : ProjectivePoint F) :
    evalGenerator F a (evalGenerator F (inverseLabel a) x) = x := by
  simpa using eval_inverse_label F (inverseLabel a) x

theorem eval_generator_injective (a : Label) :
    Function.Injective (evalGenerator F a) := by
  intro x y h
  calc
    x = evalGenerator F (inverseLabel a) (evalGenerator F a x) :=
      (eval_inverse_label F a x).symm
    _ = evalGenerator F (inverseLabel a) (evalGenerator F a y) :=
      congrArg (evalGenerator F (inverseLabel a)) h
    _ = y := eval_inverse_label F a y

theorem inverse_image_ne_infinity_iff (a : Label) (x : ProjectivePoint F) :
    evalGenerator F (inverseLabel a) x ≠ none ↔
      x ≠ evalGenerator F a none := by
  constructor
  · intro hinv hx
    apply hinv
    rw [hx, eval_inverse_label]
  · intro hx hinv
    apply hx
    have h := congrArg (evalGenerator F a) hinv
    simpa [eval_label_inverse] using h

/-- The paper's `e_ab = b(v_a)`. -/
def twoStepInfinityValue (a b : Label) : ProjectivePoint F :=
  evalGenerator F b (valueAtInfinity F a)

def AvoidsThreePrefixPoles (a b c : Label) (x : F) : Prop :=
  x ≠ pole F a
    ∧ evalGenerator F a (some x) ≠ some (pole F b)
    ∧ evalGenerator F b (evalGenerator F a (some x)) ≠ some (pole F c)

theorem route_0101_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape0101) ↔
      valueAtInfinity F a = some (pole F b) := by
  simp [DepthThreeRouteRealized, shape0101, valueAtInfinity,
    eval_generator_eq_infinity_iff]
  intro h
  rw [h]
  simp

theorem route_0110_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape0110) ↔
      valueAtInfinity F a ≠ some (pole F b)
        ∧ twoStepInfinityValue F a b = some (pole F c) := by
  simp [DepthThreeRouteRealized, shape0110, valueAtInfinity,
    twoStepInfinityValue, eval_generator_eq_infinity_iff]

theorem route_0111_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape0111) ↔
      valueAtInfinity F a ≠ some (pole F b)
        ∧ twoStepInfinityValue F a b ≠ some (pole F c) := by
  simp [DepthThreeRouteRealized, shape0111, valueAtInfinity,
    twoStepInfinityValue, eval_generator_eq_infinity_iff]

theorem route_1010_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1010) ↔
      valueAtInfinity F b = some (pole F c) := by
  simp [DepthThreeRouteRealized, shape1010, valueAtInfinity,
    eval_generator_eq_infinity_iff]

theorem route_1011_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1011) ↔
      valueAtInfinity F b ≠ some (pole F c) := by
  simp [DepthThreeRouteRealized, shape1011, valueAtInfinity,
    eval_generator_eq_infinity_iff]

theorem route_1101_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1101) ↔
      valueAtInfinity F a ≠ some (pole F b) := by
  simp only [DepthThreeRouteRealized, shape1101]
  constructor
  · rintro ⟨x, hx, hax, hba, htail⟩ hvalue
    have hba' : evalGenerator F a x = some (pole F b) :=
      (eval_generator_eq_infinity_iff F b _).mp
        ((sector_eq_zero_iff F _).mp hba)
    have hnone : x = none := by
      apply eval_generator_injective F a
      simpa [valueAtInfinity] using hba'.trans hvalue.symm
    subst x
    simp at hx
  · intro hvalue
    let target : ProjectivePoint F := some (pole F b)
    let x := evalGenerator F (inverseLabel a) target
    have hx : x ≠ none := by
      rw [inverse_image_ne_infinity_iff]
      exact hvalue.symm
    refine ⟨x, ?_, ?_, ?_, ?_⟩
    · exact (sector_one_iff_ne_infinity F x).2 hx
    · rw [eval_label_inverse]
      rfl
    · rw [eval_label_inverse]
      simp [target, generator_maps_pole_to_infinity]
    · rw [eval_label_inverse]
      simp [target, generator_maps_pole_to_infinity]

theorem route_1110_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1110) ↔
      valueAtInfinity F b ≠ some (pole F c)
        ∧ twoStepInfinityValue F a b ≠ some (pole F c) := by
  simp only [DepthThreeRouteRealized, shape1110]
  constructor
  · rintro ⟨x, hx, hax, hbax, hcbax⟩
    have hz : evalGenerator F b (evalGenerator F a x) = some (pole F c) :=
      (eval_generator_eq_infinity_iff F c _).mp
        ((sector_eq_zero_iff F _).mp hcbax)
    constructor
    · intro hvb
      have hy : evalGenerator F a x = none := by
        apply eval_generator_injective F b
        simpa [valueAtInfinity] using hz.trans hvb.symm
      rw [hy] at hax
      simp at hax
    · intro heab
      have hsource : x = none := by
        apply eval_generator_injective F a
        apply eval_generator_injective F b
        simpa [twoStepInfinityValue, valueAtInfinity] using hz.trans heab.symm
      subst x
      simp at hx
  · rintro ⟨hvb, heab⟩
    let target : ProjectivePoint F := some (pole F c)
    let y := evalGenerator F (inverseLabel b) target
    let x := evalGenerator F (inverseLabel a) y
    have hy : y ≠ none := by
      rw [inverse_image_ne_infinity_iff]
      exact hvb.symm
    have hyva : y ≠ valueAtInfinity F a := by
      intro h
      apply heab
      calc
        twoStepInfinityValue F a b = evalGenerator F b y := by
          simp [twoStepInfinityValue, valueAtInfinity, h]
        _ = target := eval_label_inverse F b target
        _ = some (pole F c) := rfl
    have hx : x ≠ none := by
      rw [inverse_image_ne_infinity_iff]
      simpa [valueAtInfinity] using hyva
    refine ⟨x, ?_, ?_, ?_, ?_⟩
    · exact (sector_one_iff_ne_infinity F x).2 hx
    · rw [eval_label_inverse]
      exact (sector_one_iff_ne_infinity F y).2 hy
    · rw [eval_label_inverse, eval_label_inverse]
      rfl
    · rw [eval_label_inverse, eval_label_inverse]
      simp [target, generator_maps_pole_to_infinity]

theorem route_1111_realized_iff (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1111) ↔
      ∃ x : F, AvoidsThreePrefixPoles F a b c x := by
  change
    (∃ x : ProjectivePoint F,
      pointSector F x = 1
        ∧ pointSector F (evalGenerator F a x) = 1
        ∧ pointSector F (evalGenerator F b (evalGenerator F a x)) = 1
        ∧ pointSector F
            (evalGenerator F c (evalGenerator F b (evalGenerator F a x))) = 1)
      ↔ ∃ x : F, AvoidsThreePrefixPoles F a b c x
  constructor
  · rintro ⟨x, hx, hax, hbax, hcbax⟩
    cases x with
    | none => simp at hx
    | some x =>
        refine ⟨x, ?_, ?_, ?_⟩
        · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hax
        · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hbax
        · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hcbax
  · rintro ⟨x, hxa, hax, hbax⟩
    refine ⟨some x, ?_, ?_, ?_, ?_⟩
    · rfl
    · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hxa
    · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hax
    · simpa [AvoidsThreePrefixPoles, eval_generator_eq_infinity_iff] using hbax

def forbiddenProjectiveInputs (a b c : Label) :
    Finset (ProjectivePoint F) :=
  {none,
    some (pole F a),
    evalGenerator F (inverseLabel a) (some (pole F b)),
    evalGenerator F (inverseLabel a)
      (evalGenerator F (inverseLabel b) (some (pole F c)))}

theorem all_finite_route_realized_of_four_le_card
    (hcard : 4 ≤ Fintype.card F) (a b c : Label) :
    DepthThreeRouteRealized F ((a, b, c), shape1111) := by
  let bad := forbiddenProjectiveInputs F a b c
  have hbad : bad.card ≤ 4 := by
    simpa [bad, forbiddenProjectiveInputs] using
      (Finset.card_le_four :
        ({none,
          some (pole F a),
          evalGenerator F (inverseLabel a) (some (pole F b)),
          evalGenerator F (inverseLabel a)
            (evalGenerator F (inverseLabel b) (some (pole F c)))} :
          Finset (ProjectivePoint F)).card ≤ 4)
  have hoption : 4 < Fintype.card (ProjectivePoint F) := by
    simp [ProjectivePoint]
    omega
  have hlt : bad.card < (Finset.univ : Finset (ProjectivePoint F)).card := by
    rw [Finset.card_univ]
    omega
  obtain ⟨point, -, hpoint⟩ :=
    Finset.exists_mem_notMem_of_card_lt_card hlt
  have hpnone : point ≠ none := by
    intro h
    subst point
    exact hpoint (by simp [bad, forbiddenProjectiveInputs])
  obtain ⟨x, rfl⟩ := Option.ne_none_iff_exists'.mp hpnone
  rw [route_1111_realized_iff]
  refine ⟨x, ?_, ?_, ?_⟩
  · intro hx
    apply hpoint
    simp [bad, forbiddenProjectiveInputs, hx]
  · intro hax
    apply hpoint
    have hpreimage :
        (some x : ProjectivePoint F) =
          evalGenerator F (inverseLabel a) (some (pole F b)) := by
      calc
        some x = evalGenerator F (inverseLabel a)
            (evalGenerator F a (some x)) := (eval_inverse_label F a _).symm
        _ = evalGenerator F (inverseLabel a) (some (pole F b)) := by rw [hax]
    simp [bad, forbiddenProjectiveInputs, hpreimage]
  · intro hbax
    apply hpoint
    have hmiddle :
        evalGenerator F a (some x) =
          evalGenerator F (inverseLabel b) (some (pole F c)) := by
      calc
        evalGenerator F a (some x) = evalGenerator F (inverseLabel b)
            (evalGenerator F b (evalGenerator F a (some x))) :=
              (eval_inverse_label F b _).symm
        _ = evalGenerator F (inverseLabel b) (some (pole F c)) := by rw [hbax]
    have hpreimage :
        (some x : ProjectivePoint F) = evalGenerator F (inverseLabel a)
          (evalGenerator F (inverseLabel b) (some (pole F c))) := by
      calc
        some x = evalGenerator F (inverseLabel a)
            (evalGenerator F a (some x)) := (eval_inverse_label F a _).symm
        _ = _ := by rw [hmiddle]
    simp [bad, forbiddenProjectiveInputs, hpreimage]

omit [Fintype F] in
theorem declared_pole_maps_to_infinity (a : Label) :
    evalGenerator F a (some (pole F a)) = none := by
  exact generator_maps_pole_to_infinity F a

end PolePreimageTerms

section ShapeCountHelpers

variable (F : Type*) [Field F] [Fintype F] [DecidableEq F]

def zeroWords0101 : Finset LabelTriple :=
  {((.S, .R, .S)), ((.S, .R, .R)), ((.S, .R, .RInv)),
   ((.R, .R, .S)), ((.R, .R, .R)), ((.R, .R, .RInv)),
   ((.RInv, .S, .S)), ((.RInv, .S, .R)), ((.RInv, .S, .RInv)),
   ((.RInv, .RInv, .S)), ((.RInv, .RInv, .R)),
   ((.RInv, .RInv, .RInv))}

def zeroWords0110Odd : Finset LabelTriple :=
  {((.R, .R, .RInv)), ((.R, .R, .S)), ((.R, .RInv, .R)),
   ((.R, .RInv, .RInv)), ((.R, .RInv, .S)), ((.R, .S, .R)),
   ((.R, .S, .RInv)), ((.R, .S, .S)), ((.RInv, .R, .R)),
   ((.RInv, .R, .RInv)), ((.RInv, .R, .S)),
   ((.RInv, .RInv, .R)), ((.RInv, .S, .R)),
   ((.RInv, .S, .RInv)), ((.RInv, .S, .S)),
   ((.S, .R, .RInv)), ((.S, .R, .S)), ((.S, .RInv, .R)),
   ((.S, .RInv, .RInv)), ((.S, .RInv, .S)), ((.S, .S, .R)),
   ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords0110CharTwo : Finset LabelTriple :=
  {((.R, .R, .RInv)), ((.R, .R, .S)), ((.R, .RInv, .R)),
   ((.R, .RInv, .RInv)), ((.R, .RInv, .S)), ((.R, .S, .R)),
   ((.R, .S, .RInv)), ((.R, .S, .S)), ((.RInv, .R, .R)),
   ((.RInv, .R, .RInv)), ((.RInv, .R, .S)),
   ((.RInv, .RInv, .R)), ((.RInv, .S, .RInv)),
   ((.RInv, .S, .S)), ((.S, .R, .RInv)), ((.S, .R, .S)),
   ((.S, .RInv, .R)), ((.S, .RInv, .RInv)), ((.S, .RInv, .S)),
   ((.S, .S, .R)), ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords0111Odd : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .RInv, .R)), ((.R, .RInv, .RInv)),
   ((.R, .RInv, .S)), ((.R, .S, .R)), ((.R, .S, .RInv)),
   ((.R, .S, .S)), ((.RInv, .R, .R)), ((.RInv, .R, .RInv)),
   ((.RInv, .R, .S)), ((.RInv, .RInv, .RInv)),
   ((.RInv, .RInv, .S)), ((.S, .R, .R)), ((.S, .RInv, .R)),
   ((.S, .RInv, .RInv)), ((.S, .RInv, .S)), ((.S, .S, .R)),
   ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords0111CharTwo : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .RInv, .R)), ((.R, .RInv, .RInv)),
   ((.R, .RInv, .S)), ((.R, .S, .R)), ((.R, .S, .RInv)),
   ((.R, .S, .S)), ((.RInv, .R, .R)), ((.RInv, .R, .RInv)),
   ((.RInv, .R, .S)), ((.RInv, .RInv, .RInv)),
   ((.RInv, .RInv, .S)), ((.RInv, .S, .R)),
   ((.S, .R, .R)), ((.S, .RInv, .R)), ((.S, .RInv, .RInv)),
   ((.S, .RInv, .S)), ((.S, .S, .R)), ((.S, .S, .RInv)),
   ((.S, .S, .S))}

def zeroWords1010 : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .RInv, .RInv)), ((.R, .RInv, .S)),
   ((.R, .S, .R)), ((.RInv, .R, .R)), ((.RInv, .RInv, .RInv)),
   ((.RInv, .RInv, .S)), ((.RInv, .S, .R)), ((.S, .R, .R)),
   ((.S, .RInv, .RInv)), ((.S, .RInv, .S)), ((.S, .S, .R))}

def zeroWords1011 : Finset LabelTriple :=
  {((.R, .R, .RInv)), ((.R, .R, .S)), ((.R, .RInv, .R)),
   ((.R, .S, .RInv)), ((.R, .S, .S)), ((.RInv, .R, .RInv)),
   ((.RInv, .R, .S)), ((.RInv, .RInv, .R)),
   ((.RInv, .S, .RInv)), ((.RInv, .S, .S)),
   ((.S, .R, .RInv)), ((.S, .R, .S)), ((.S, .RInv, .R)),
   ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords1101 : Finset LabelTriple :=
  {((.R, .RInv, .R)), ((.R, .RInv, .RInv)), ((.R, .RInv, .S)),
   ((.R, .S, .R)), ((.R, .S, .RInv)), ((.R, .S, .S)),
   ((.RInv, .R, .R)), ((.RInv, .R, .RInv)), ((.RInv, .R, .S)),
   ((.S, .RInv, .R)), ((.S, .RInv, .RInv)), ((.S, .RInv, .S)),
   ((.S, .S, .R)), ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords1110Odd : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .R, .RInv)), ((.R, .R, .S)),
   ((.R, .RInv, .R)), ((.R, .S, .RInv)), ((.R, .S, .S)),
   ((.RInv, .R, .RInv)), ((.RInv, .R, .S)),
   ((.RInv, .RInv, .R)), ((.RInv, .RInv, .RInv)),
   ((.RInv, .RInv, .S)), ((.RInv, .S, .RInv)),
   ((.RInv, .S, .S)), ((.S, .R, .R)), ((.S, .R, .RInv)),
   ((.S, .R, .S)), ((.S, .RInv, .R)), ((.S, .S, .RInv)),
   ((.S, .S, .S))}

def zeroWords1110CharTwo : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .R, .RInv)), ((.R, .R, .S)),
   ((.R, .RInv, .R)), ((.R, .S, .RInv)), ((.R, .S, .S)),
   ((.RInv, .R, .RInv)), ((.RInv, .R, .S)),
   ((.RInv, .RInv, .R)), ((.RInv, .RInv, .RInv)),
   ((.RInv, .RInv, .S)), ((.RInv, .S, .R)),
   ((.RInv, .S, .RInv)), ((.RInv, .S, .S)), ((.S, .R, .R)),
   ((.S, .R, .RInv)), ((.S, .R, .S)), ((.S, .RInv, .R)),
   ((.S, .S, .RInv)), ((.S, .S, .S))}

def zeroWords1111CardTwo : Finset LabelTriple :=
  {((.R, .R, .R)), ((.R, .R, .RInv)), ((.R, .R, .S)),
   ((.R, .RInv, .RInv)), ((.R, .RInv, .S)), ((.R, .S, .R)),
   ((.RInv, .R, .R)), ((.RInv, .RInv, .R)),
   ((.RInv, .RInv, .RInv)), ((.RInv, .RInv, .S)),
   ((.RInv, .S, .R)), ((.RInv, .S, .RInv)), ((.RInv, .S, .S)),
   ((.S, .R, .R)), ((.S, .R, .RInv)), ((.S, .R, .S)),
   ((.S, .RInv, .RInv)), ((.S, .RInv, .S)), ((.S, .S, .R))}

def zeroWords1111CardThree : Finset LabelTriple :=
  {((.RInv, .S, .R))}

def depthThreeZeroWordFilterComputable (shape : DepthThreeShape) :
    Finset LabelTriple :=
  orderedLabelTriples.filter (fun triple =>
    depthThreeRouteRealizedBool F (triple, shape) = false)

theorem finite_card_two_eq_zero_or_one
    (hcard : Fintype.card F = 2) (x : F) : x = 0 ∨ x = 1 := by
  by_cases hx0 : x = 0
  · exact Or.inl hx0
  right
  by_contra hx1
  have hset : ({0, 1, x} : Finset F).card = 3 := by
    have h0not : (0 : F) ∉ ({1, x} : Finset F) := by
      simp [Ne.symm hx0, zero_ne_one]
    have h1not : (1 : F) ∉ ({x} : Finset F) := by
      simp [Ne.symm hx1]
    rw [Finset.card_insert_of_notMem h0not,
      Finset.card_insert_of_notMem h1not]
    simp
  have hle : ({0, 1, x} : Finset F).card ≤ Fintype.card F := by
    rw [← Finset.card_univ]
    exact Finset.card_le_card (Finset.subset_univ _)
  omega

theorem finite_card_three_eq_zero_or_one_or_neg_one
    (hcard : Fintype.card F = 3) (x : F) :
    x = 0 ∨ x = 1 ∨ x = -1 := by
  have hchar : (-1 : F) ≠ 1 := by
    intro h
    have hring : ringChar F = 2 := (neg_one_eq_one_iff).mp h
    have heven := FiniteField.even_card_of_char_two (F := F) hring
    omega
  by_cases hx0 : x = 0
  · exact Or.inl hx0
  by_cases hx1 : x = 1
  · exact Or.inr (Or.inl hx1)
  right
  right
  by_contra hxm1
  have hset : ({0, 1, -1, x} : Finset F).card = 4 := by
    have h0not : (0 : F) ∉ ({1, -1, x} : Finset F) := by
      simp [Ne.symm hx0, neg_ne_zero.mpr one_ne_zero]
    have h1not : (1 : F) ∉ ({-1, x} : Finset F) := by
      simp [Ne.symm hchar, Ne.symm hx1]
    have hm1not : (-1 : F) ∉ ({x} : Finset F) := by
      simp [Ne.symm hxm1]
    rw [Finset.card_insert_of_notMem h0not,
      Finset.card_insert_of_notMem h1not,
      Finset.card_insert_of_notMem hm1not]
    simp
  have hle : ({0, 1, -1, x} : Finset F).card ≤ Fintype.card F := by
    rw [← Finset.card_univ]
    exact Finset.card_le_card (Finset.subset_univ _)
  omega

theorem exists_avoids_three_prefix_poles_card_three
    (hcard : Fintype.card F = 3) (a b c : Label) :
    (∃ x : F, AvoidsThreePrefixPoles F a b c x) ↔
      AvoidsThreePrefixPoles F a b c 0 ∨
        AvoidsThreePrefixPoles F a b c 1 ∨
        AvoidsThreePrefixPoles F a b c (-1) := by
  constructor
  · rintro ⟨x, hx⟩
    rcases finite_card_three_eq_zero_or_one_or_neg_one F hcard x with
      rfl | rfl | rfl
    · exact Or.inl hx
    · exact Or.inr (Or.inl hx)
    · exact Or.inr (Or.inr hx)
  · rintro (hx | hx | hx)
    · exact ⟨0, hx⟩
    · exact ⟨1, hx⟩
    · exact ⟨-1, hx⟩

theorem exists_avoids_three_prefix_poles_card_two
    (hcard : Fintype.card F = 2) (a b c : Label) :
    (∃ x : F, AvoidsThreePrefixPoles F a b c x) ↔
      AvoidsThreePrefixPoles F a b c 0 ∨
        AvoidsThreePrefixPoles F a b c 1 := by
  constructor
  · rintro ⟨x, hx⟩
    rcases finite_card_two_eq_zero_or_one F hcard x with rfl | rfl
    · exact Or.inl hx
    · exact Or.inr hx
  · rintro (hx | hx)
    · exact ⟨0, hx⟩
    · exact ⟨1, hx⟩

theorem zero_words0101_spec :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape0101) = false ↔
        triple ∈ zeroWords0101 := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_0101_realized_iff, zeroWords0101, valueAtInfinity, pole,
      evalGenerator]

theorem zero_words1010_spec :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1010) = false ↔
        triple ∈ zeroWords1010 := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_1010_realized_iff, zeroWords1010, valueAtInfinity, pole,
      evalGenerator]

theorem zero_words1011_spec :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1011) = false ↔
        triple ∈ zeroWords1011 := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_1011_realized_iff, zeroWords1011, valueAtInfinity, pole,
      evalGenerator]

theorem zero_words1101_spec :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1101) = false ↔
        triple ∈ zeroWords1101 := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_1101_realized_iff, zeroWords1101, valueAtInfinity, pole,
      evalGenerator]

theorem zero_words0110_odd_spec (hchar : (-1 : F) ≠ 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape0110) = false ↔
        triple ∈ zeroWords0110Odd := by
  intro triple
  have hchar' : (1 : F) ≠ -1 := fun h => hchar h.symm
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_0110_realized_iff, zeroWords0110Odd, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar, hchar']

theorem zero_words0111_odd_spec (hchar : (-1 : F) ≠ 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape0111) = false ↔
        triple ∈ zeroWords0111Odd := by
  intro triple
  have hchar' : (1 : F) ≠ -1 := fun h => hchar h.symm
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_0111_realized_iff, zeroWords0111Odd, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar, hchar']

theorem zero_words1110_odd_spec (hchar : (-1 : F) ≠ 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1110) = false ↔
        triple ∈ zeroWords1110Odd := by
  intro triple
  have hchar' : (1 : F) ≠ -1 := fun h => hchar h.symm
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_1110_realized_iff, zeroWords1110Odd, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar, hchar']

theorem zero_words0110_char_two_spec (hchar : (-1 : F) = 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape0110) = false ↔
        triple ∈ zeroWords0110CharTwo := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_0110_realized_iff, zeroWords0110CharTwo, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar]

theorem zero_words0111_char_two_spec (hchar : (-1 : F) = 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape0111) = false ↔
        triple ∈ zeroWords0111CharTwo := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_0111_realized_iff, zeroWords0111CharTwo, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar]

theorem zero_words1110_char_two_spec (hchar : (-1 : F) = 1) :
    ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1110) = false ↔
        triple ∈ zeroWords1110CharTwo := by
  intro triple
  rcases triple with ⟨a, b, c⟩
  fin_cases a <;> fin_cases b <;> fin_cases c <;>
    simp [depth_three_route_not_realized_bool_iff,
      route_1110_realized_iff, zeroWords1110CharTwo, valueAtInfinity, pole,
      twoStepInfinityValue, evalGenerator, hchar]

theorem depth_three_zero_shape_count_computable_eq_word_filter
    (shape : DepthThreeShape)
    (hshape : shape ∈ depthThreeSupportedShapes) :
    depthThreeZeroShapeCountComputable F shape =
      (depthThreeZeroWordFilterComputable F shape).card := by
  classical
  unfold depthThreeZeroShapeCountComputable
  unfold depthThreeSemanticZeroRoutesComputable
  have hfilter :
      (depthThreeCandidates.filter (fun route =>
        !(depthThreeRouteRealizedBool F route))).filter
          (fun route => route.2 = shape) =
        (depthThreeZeroWordFilterComputable F shape).product {shape} := by
    ext route
    rcases route with ⟨triple, routeShape⟩
    rcases triple with ⟨a, b, c⟩
    by_cases h : routeShape = shape
    · subst routeShape
      simp [depthThreeZeroWordFilterComputable, depthThreeCandidates,
        Finset.mem_product, hshape]
    · simp [depthThreeZeroWordFilterComputable, depthThreeCandidates,
        Finset.mem_product, hshape, h, Ne.symm h]
  rw [hfilter]
  simp [Finset.card_product]

theorem depth_three_zero_shape_count_computable_eq_explicit
    (shape : DepthThreeShape)
    (hshape : shape ∈ depthThreeSupportedShapes)
    (zeroWords : Finset LabelTriple)
    (hzero : ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape) = false ↔
        triple ∈ zeroWords) :
    depthThreeZeroShapeCountComputable F shape = zeroWords.card := by
  rw [depth_three_zero_shape_count_computable_eq_word_filter F shape hshape]
  congr 1
  ext triple
  simp [depthThreeZeroWordFilterComputable, orderedLabelTriples, hzero]

def firstSevenShapeHistogram : List Nat :=
  [depthThreeZeroShapeCountComputable F shape0101,
    depthThreeZeroShapeCountComputable F shape0110,
    depthThreeZeroShapeCountComputable F shape0111,
    depthThreeZeroShapeCountComputable F shape1010,
    depthThreeZeroShapeCountComputable F shape1011,
    depthThreeZeroShapeCountComputable F shape1101,
    depthThreeZeroShapeCountComputable F shape1110]

theorem first_seven_shape_histogram_char_two (hchar : (-1 : F) = 1) :
    firstSevenShapeHistogram F = [12, 22, 20, 12, 15, 15, 20] := by
  have h0101 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0101 (by native_decide) zeroWords0101 (zero_words0101_spec F)
  have h0110 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0110 (by native_decide) zeroWords0110CharTwo
      (zero_words0110_char_two_spec F hchar)
  have h0111 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0111 (by native_decide) zeroWords0111CharTwo
      (zero_words0111_char_two_spec F hchar)
  have h1010 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1010 (by native_decide) zeroWords1010 (zero_words1010_spec F)
  have h1011 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1011 (by native_decide) zeroWords1011 (zero_words1011_spec F)
  have h1101 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1101 (by native_decide) zeroWords1101 (zero_words1101_spec F)
  have h1110 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1110 (by native_decide) zeroWords1110CharTwo
      (zero_words1110_char_two_spec F hchar)
  simp [firstSevenShapeHistogram, h0101, h0110, h0111, h1010, h1011,
    h1101, h1110]
  native_decide

theorem first_seven_shape_histogram_odd (hchar : (-1 : F) ≠ 1) :
    firstSevenShapeHistogram F = [12, 23, 19, 12, 15, 15, 19] := by
  have h0101 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0101 (by native_decide) zeroWords0101 (zero_words0101_spec F)
  have h0110 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0110 (by native_decide) zeroWords0110Odd
      (zero_words0110_odd_spec F hchar)
  have h0111 := depth_three_zero_shape_count_computable_eq_explicit F
    shape0111 (by native_decide) zeroWords0111Odd
      (zero_words0111_odd_spec F hchar)
  have h1010 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1010 (by native_decide) zeroWords1010 (zero_words1010_spec F)
  have h1011 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1011 (by native_decide) zeroWords1011 (zero_words1011_spec F)
  have h1101 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1101 (by native_decide) zeroWords1101 (zero_words1101_spec F)
  have h1110 := depth_three_zero_shape_count_computable_eq_explicit F
    shape1110 (by native_decide) zeroWords1110Odd
      (zero_words1110_odd_spec F hchar)
  simp [firstSevenShapeHistogram, h0101, h0110, h0111, h1010, h1011,
    h1101, h1110]
  native_decide

theorem depth_three_zero_shape1111_count_zero
    (hcard : 4 ≤ Fintype.card F) :
    depthThreeZeroShapeCount F shape1111 = 0 := by
  classical
  unfold depthThreeZeroShapeCount
  apply Finset.card_eq_zero.mpr
  ext route
  constructor
  · intro hroute
    rcases route with ⟨⟨a, b, c⟩, shape⟩
    have hshape : shape = shape1111 :=
      (Finset.mem_filter.mp hroute).2
    subst shape
    have hsemantic := (Finset.mem_filter.mp hroute).1
    have hnot := (Finset.mem_filter.mp hsemantic).2
    exact False.elim
      (hnot (all_finite_route_realized_of_four_le_card F hcard a b c))
  · simp

theorem depth_three_zero_shape1111_count_card_two
    (hcard : Fintype.card F = 2) :
    depthThreeZeroShapeCountComputable F shape1111 = 19 := by
  have hzero : ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1111) = false ↔
        triple ∈ zeroWords1111CardTwo := by
    intro triple
    rcases triple with ⟨a, b, c⟩
    have hchar : (-1 : F) = 1 := by
      rcases finite_card_two_eq_zero_or_one F hcard (-1) with h | h
      · simp at h
      · exact h
    rw [depth_three_route_not_realized_bool_iff,
      route_1111_realized_iff,
      exists_avoids_three_prefix_poles_card_two F hcard]
    fin_cases a <;> fin_cases b <;> fin_cases c <;>
      simp [zeroWords1111CardTwo, AvoidsThreePrefixPoles, valueAtInfinity,
        pole, evalGenerator, hchar]
  exact depth_three_zero_shape_count_computable_eq_explicit F shape1111
    (by native_decide) zeroWords1111CardTwo hzero

theorem depth_three_zero_shape1111_count_card_three
    (hcard : Fintype.card F = 3) :
    depthThreeZeroShapeCountComputable F shape1111 = 1 := by
  letI : Fact (Nat.Prime 3) := ⟨by norm_num⟩
  have hcharP : CharP F 3 := charP_of_card_eq_prime hcard
  have hthree : (3 : F) = 0 := CharP.cast_eq_zero F 3
  have hplus : (1 : F) + 1 = -1 := by
    linear_combination hthree
  have hchar : (-1 : F) ≠ 1 := by
    intro h
    have hring : ringChar F = 2 := (neg_one_eq_one_iff).mp h
    have heven := FiniteField.even_card_of_char_two (F := F) hring
    rw [hcard] at heven
    norm_num at heven
  have hchar' : (1 : F) ≠ -1 := fun h => hchar h.symm
  have hdouble : (-1 : F) - 1 ≠ 0 := by
    intro h
    apply hchar
    calc
      (-1 : F) = ((-1 : F) - 1) + 1 := by ring
      _ = 0 + 1 := by rw [h]
      _ = 1 := by ring
  have hminus : (-1 : F) - 1 = 1 := by
    calc
      (-1 : F) - 1 = -(1 + 1) := by ring
      _ = -(-1) := by rw [hplus]
      _ = 1 := by ring
  have hzero : ∀ triple : LabelTriple,
      depthThreeRouteRealizedBool F (triple, shape1111) = false ↔
        triple ∈ zeroWords1111CardThree := by
    intro triple
    rcases triple with ⟨a, b, c⟩
    rw [depth_three_route_not_realized_bool_iff,
      route_1111_realized_iff,
      exists_avoids_three_prefix_poles_card_three F hcard]
    fin_cases a <;> fin_cases b <;> fin_cases c <;>
      simp [zeroWords1111CardThree, AvoidsThreePrefixPoles, valueAtInfinity,
        pole, evalGenerator, hchar, hchar', hplus, hdouble, hminus]
  exact depth_three_zero_shape_count_computable_eq_explicit F shape1111
    (by native_decide) zeroWords1111CardThree hzero

noncomputable def depthThreeZeroRouteCount : Nat :=
  (depthThreeSemanticZeroRoutes F).card

theorem depth_three_zero_shape_count_eq_computable (shape : DepthThreeShape) :
    depthThreeZeroShapeCount F shape =
      depthThreeZeroShapeCountComputable F shape := by
  unfold depthThreeZeroShapeCount depthThreeZeroShapeCountComputable
  rw [depth_three_semantic_zero_routes_computable_eq F]

theorem depth_three_zero_route_count_eq_shape_sum :
    depthThreeZeroRouteCount F =
      depthThreeSupportedShapes.sum (fun shape =>
        depthThreeZeroShapeCount F shape) := by
  have hmaps :
      (depthThreeSemanticZeroRoutes F : Set DepthThreeCandidate).MapsTo
        (fun route => route.2) depthThreeSupportedShapes := by
    intro route hroute
    exact (Finset.mem_product.mp
      (depth_three_semantic_zero_routes_subset F hroute)).2
  have hcard := Finset.card_eq_sum_card_fiberwise
    (s := depthThreeSemanticZeroRoutes F)
    (t := depthThreeSupportedShapes)
    (f := fun route : DepthThreeCandidate => route.2) hmaps
  simpa [depthThreeZeroRouteCount, depthThreeZeroShapeCount] using hcard

noncomputable def depthThreeFirstSevenZeroCount : Nat :=
  depthThreeZeroShapeCount F shape0101
    + depthThreeZeroShapeCount F shape0110
    + depthThreeZeroShapeCount F shape0111
    + depthThreeZeroShapeCount F shape1010
    + depthThreeZeroShapeCount F shape1011
    + depthThreeZeroShapeCount F shape1101
    + depthThreeZeroShapeCount F shape1110

theorem depth_three_first_seven_zero_count_char_two (hchar : (-1 : F) = 1) :
    depthThreeFirstSevenZeroCount F = 116 := by
  have h := first_seven_shape_histogram_char_two F hchar
  have h0101 := depth_three_zero_shape_count_eq_computable F shape0101
  have h0110 := depth_three_zero_shape_count_eq_computable F shape0110
  have h0111 := depth_three_zero_shape_count_eq_computable F shape0111
  have h1010 := depth_three_zero_shape_count_eq_computable F shape1010
  have h1011 := depth_three_zero_shape_count_eq_computable F shape1011
  have h1101 := depth_three_zero_shape_count_eq_computable F shape1101
  have h1110 := depth_three_zero_shape_count_eq_computable F shape1110
  simp [depthThreeFirstSevenZeroCount, h0101, h0110, h0111, h1010,
    h1011, h1101, h1110, firstSevenShapeHistogram] at h ⊢
  omega

theorem depth_three_first_seven_zero_count_odd (hchar : (-1 : F) ≠ 1) :
    depthThreeFirstSevenZeroCount F = 115 := by
  have h := first_seven_shape_histogram_odd F hchar
  have h0101 := depth_three_zero_shape_count_eq_computable F shape0101
  have h0110 := depth_three_zero_shape_count_eq_computable F shape0110
  have h0111 := depth_three_zero_shape_count_eq_computable F shape0111
  have h1010 := depth_three_zero_shape_count_eq_computable F shape1010
  have h1011 := depth_three_zero_shape_count_eq_computable F shape1011
  have h1101 := depth_three_zero_shape_count_eq_computable F shape1101
  have h1110 := depth_three_zero_shape_count_eq_computable F shape1110
  simp [depthThreeFirstSevenZeroCount, h0101, h0110, h0111, h1010,
    h1011, h1101, h1110, firstSevenShapeHistogram] at h ⊢
  omega

theorem depth_three_zero_route_count_eq_first_seven_add_all_finite :
    depthThreeZeroRouteCount F =
      depthThreeFirstSevenZeroCount F +
        depthThreeZeroShapeCount F shape1111 := by
  rw [depth_three_zero_route_count_eq_shape_sum F]
  rw [depthThreeSupportedShapes]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  rw [Finset.sum_insert (by native_decide)]
  simp [depthThreeFirstSevenZeroCount]
  omega

theorem depth_three_zero_route_count_char_two_card_ge_four
    (hchar : ringChar F = 2) (hcard : 4 ≤ Fintype.card F) :
    depthThreeZeroRouteCount F = 116 := by
  have hneg : (-1 : F) = 1 := (neg_one_eq_one_iff).2 hchar
  have hfirst := depth_three_first_seven_zero_count_char_two F hneg
  have hall := depth_three_zero_shape1111_count_zero F hcard
  rw [depth_three_zero_route_count_eq_first_seven_add_all_finite F]
  omega

theorem depth_three_zero_route_count_odd_card_ge_four
    (hchar : ringChar F ≠ 2) (hcard : 4 ≤ Fintype.card F) :
    depthThreeZeroRouteCount F = 115 := by
  have hneg : (-1 : F) ≠ 1 := fun h => hchar ((neg_one_eq_one_iff).mp h)
  have hfirst := depth_three_first_seven_zero_count_odd F hneg
  have hall := depth_three_zero_shape1111_count_zero F hcard
  rw [depth_three_zero_route_count_eq_first_seven_add_all_finite F]
  omega

theorem depth_three_zero_route_count_card_two
    (hcard : Fintype.card F = 2) :
    depthThreeZeroRouteCount F = 135 := by
  have hneg : (-1 : F) = 1 := by
    rcases finite_card_two_eq_zero_or_one F hcard (-1) with h | h
    · exact False.elim ((neg_ne_zero.mpr one_ne_zero) h)
    · exact h
  have hfirst := depth_three_first_seven_zero_count_char_two F hneg
  have hshape := depth_three_zero_shape_count_eq_computable F shape1111
  have hall := depth_three_zero_shape1111_count_card_two F hcard
  rw [depth_three_zero_route_count_eq_first_seven_add_all_finite F]
  rw [hshape]
  omega

theorem depth_three_zero_route_count_card_three
    (hcard : Fintype.card F = 3) :
    depthThreeZeroRouteCount F = 116 := by
  have hneg : (-1 : F) ≠ 1 := by
    intro h
    have hchar : ringChar F = 2 := (neg_one_eq_one_iff).mp h
    have heven := FiniteField.even_card_of_char_two (F := F) hchar
    rw [hcard] at heven
    norm_num at heven
  have hfirst := depth_three_first_seven_zero_count_odd F hneg
  have hshape := depth_three_zero_shape_count_eq_computable F shape1111
  have hall := depth_three_zero_shape1111_count_card_three F hcard
  rw [depth_three_zero_route_count_eq_first_seven_add_all_finite F]
  rw [hshape]
  omega

theorem uniform_finite_field_depth_three_zero_route_count :
    depthThreeZeroRouteCount F =
      115
        + (if ringChar F = 2 then 1 else 0)
        + (if Fintype.card F = 2 then 19 else 0)
        + (if Fintype.card F = 3 then 1 else 0) := by
  by_cases hcard2 : Fintype.card F = 2
  · have hchar : ringChar F = 2 := by
      have hneg : (-1 : F) = 1 := by
        rcases finite_card_two_eq_zero_or_one F hcard2 (-1) with h | h
        · exact False.elim ((neg_ne_zero.mpr one_ne_zero) h)
        · exact h
      exact (neg_one_eq_one_iff).mp hneg
    have hcount := depth_three_zero_route_count_card_two F hcard2
    simpa [hcard2, hchar] using hcount
  · by_cases hcard3 : Fintype.card F = 3
    · have hcount := depth_three_zero_route_count_card_three F hcard3
      have hchar : ringChar F ≠ 2 := by
        intro hchar
        have heven := FiniteField.even_card_of_char_two (F := F) hchar
        rw [hcard3] at heven
        norm_num at heven
      simpa [hcard2, hcard3, hchar] using hcount
    · have hcard_ge_two : 2 ≤ Fintype.card F := by
        exact (Fintype.one_lt_card_iff_nontrivial.mpr inferInstance)
      have hcard4 : 4 ≤ Fintype.card F := by omega
      by_cases hchar : ringChar F = 2
      · have hcount :=
          depth_three_zero_route_count_char_two_card_ge_four F hchar hcard4
        simpa [hcard2, hcard3, hchar] using hcount
      · have hcount :=
          depth_three_zero_route_count_odd_card_ge_four F hchar hcard4
        simpa [hcard2, hcard3, hchar] using hcount

end ShapeCountHelpers

end FiniteFieldRouteProfiles
