import FusionLogEnumeration.BoundaryBijection
import Mathlib.Data.Fintype.Powerset

namespace FusionLogEnumeration

variable {α : Type*} [DecidableEq α]

/-- An occupied-site choice for a rank-`s` endpoint in an `n`-site circle. -/
abbrev OccupiedSiteChoices (n s : ℕ) :=
  {sites : Finset (Fin n) // sites.card = s}

/-- Choose the occupied sites and then the packet occupying the chosen cyclic
anchor site. For a fixed positively ordered packet circle this is the endpoint
coordinate normal form. -/
abbrev EndpointChoices (n s : ℕ) :=
  Σ sites : OccupiedSiteChoices n s, {anchor : Fin n // anchor ∈ sites.1}

theorem card_endpointChoices (n s : ℕ) :
    Fintype.card (EndpointChoices n s) = s * Nat.choose n s := by
  classical
  rw [Fintype.card_sigma]
  calc
    (∑ sites : OccupiedSiteChoices n s,
        Fintype.card {anchor : Fin n // anchor ∈ sites.1}) =
        ∑ _sites : OccupiedSiteChoices n s, s := by
          apply Finset.sum_congr rfl
          intro sites _
          rw [Fintype.card_coe]
          exact sites.property
    _ = s * Nat.choose n s := by
          simp [Fintype.card_finset_len, Nat.mul_comm]

/-- The finite product model for joint complete-log/endpoint data. `C` is the
initial marked packet circle; the endpoint factor is its site-and-anchor
coordinate normal form for a fixed positively ordered terminal packet circle.
Its identification with M4D literal compatible placements is a separate
interface theorem. -/
abbrev JointCountModel (C : MarkedCircle α) (n s : ℕ) :=
  Σ _log : AdmissibleLogs C (C.rank - s), EndpointChoices n s

theorem card_jointCountModel (C : MarkedCircle α) (n s : ℕ)
    (positive : 1 ≤ s) (bounded : s ≤ C.rank) :
    Fintype.card (JointCountModel C n s) =
      (C.rank.factorial / s.factorial) * (s * Nat.choose n s) := by
  classical
  rw [Fintype.card_sigma]
  calc
    (∑ _log : AdmissibleLogs C (C.rank - s),
        Fintype.card (EndpointChoices n s)) =
        Fintype.card (AdmissibleLogs C (C.rank - s)) *
          Fintype.card (EndpointChoices n s) := by
            simp
    _ = (C.rank.factorial / s.factorial) * (s * Nat.choose n s) := by
          rw [card_admissibleLogs_rank C s positive bounded, card_endpointChoices]

/-- Forget the complete log while retaining only the occupied-site set and
the coordinate of the first packet in the fixed positive packet cycle. This
is a coordinate observation, not a literal-packet endpoint map. -/
def forgetLogCoordinates {C : MarkedCircle α} {n s : ℕ}
    (joint : JointCountModel C n s) : EndpointChoices n s := joint.2

/-- A coordinate-only fibre: packet identities and surviving boundary labels
are intentionally forgotten. -/
abbrev CoordinateLogFiber (C : MarkedCircle α) (n s : ℕ)
    (endpoint : EndpointChoices n s) :=
  {joint : JointCountModel C n s // forgetLogCoordinates joint = endpoint}

noncomputable def coordinateLogFiberEquiv (C : MarkedCircle α) (n s : ℕ)
    (endpoint : EndpointChoices n s) :
    CoordinateLogFiber C n s endpoint ≃ AdmissibleLogs C (C.rank - s) where
  toFun fiber := fiber.1.1
  invFun log := ⟨⟨log, endpoint⟩, rfl⟩
  left_inv := by
    rintro ⟨⟨log, otherEndpoint⟩, equality⟩
    cases equality
    rfl
  right_inv := by intro log; rfl

/-- At rank one the coordinate-only endpoint carries only the carrier phase,
so its fibre has the full `t!` histories, including every choice of the
invisible last surviving boundary. -/
theorem card_rankOne_coordinateLogFiber (C : MarkedCircle α) (n : ℕ)
    (endpoint : EndpointChoices n 1) :
    Fintype.card (CoordinateLogFiber C n 1 endpoint) = C.rank.factorial := by
  rw [Fintype.card_congr (coordinateLogFiberEquiv C n 1 endpoint)]
  rw [card_admissibleLogs_rank C 1 (by omega) C.rank_pos]
  simp

/-- Surviving initial boundaries visible in a rank-`s` endpoint. -/
abbrev SurvivingBoundaryChoices (C : MarkedCircle α) (s : ℕ) :=
  {survivors : Finset C.boundaries // survivors.card = s}

theorem card_survivingBoundaryChoices (C : MarkedCircle α) (s : ℕ) :
    Fintype.card (SurvivingBoundaryChoices C s) = Nat.choose C.rank s := by
  rw [Fintype.card_finset_len, Fintype.card_coe, C.card_boundaries]

/-- Literal-endpoint parameters are defined only for visible rank `s ≥ 2`.
The source-boundary subset is recoverable from packet identities in a literal
endpoint; it is not part of the rank-one coordinate observation. -/
abbrev RankedEndpointChoices (C : MarkedCircle α) (n s : ℕ)
    (_rankVisible : 2 ≤ s) (_rankAvailable : s ≤ C.rank) :=
  SurvivingBoundaryChoices C s × EndpointChoices n s

theorem card_rankedEndpointChoices (C : MarkedCircle α) (n s : ℕ)
    (rankVisible : 2 ≤ s) (rankAvailable : s ≤ C.rank) :
    Fintype.card (RankedEndpointChoices C n s rankVisible rankAvailable) =
      Fintype.card (SurvivingBoundaryChoices C s) * (s * Nat.choose n s) := by
  classical
  rw [Fintype.card_prod, card_survivingBoundaryChoices, card_endpointChoices]

theorem card_rankedEndpointChoices_formula (C : MarkedCircle α) (n s : ℕ)
    (rankVisible : 2 ≤ s) (rankAvailable : s ≤ C.rank) :
    Fintype.card (RankedEndpointChoices C n s rankVisible rankAvailable) =
      Nat.choose C.rank s * (s * Nat.choose n s) := by
  rw [card_rankedEndpointChoices, card_survivingBoundaryChoices]

/-- Rank one has no visible surviving boundary: only its physical phase is
recorded. The last undeleted boundary remains part of the history fibre. -/
abbrev RankOneEndpointChoices (n : ℕ) := EndpointChoices n 1

theorem card_rankOneEndpointChoices (n : ℕ) :
    Fintype.card (RankOneEndpointChoices n) = n := by
  change Fintype.card (EndpointChoices n 1) = n
  rw [card_endpointChoices]
  simp

end FusionLogEnumeration
