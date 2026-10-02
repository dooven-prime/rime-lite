import Mathlib.Data.Finset.Card
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Prod
import Mathlib.Data.Nat.Choose.Basic

/-!
# Survivor-product frontier

The complete one-lane survivor theorem separates branch-dependent linear
orders from a free choice of three survivor coordinates. This file checks the
product type, its exact cardinality, and the one-way complete-invariant
consequence. It makes no minimality or converse claim.
-/

namespace Rime.Paper35

universe u v w x y

def coordinateTriples [DecidableEq Coord] (available : Finset Coord) :
    Finset (Finset Coord) :=
  available.powersetCard 3

/-- The formal product `M_a(F) × binom(available, 3)`. -/
def survivorFrontier
    [DecidableEq Order] [DecidableEq Coord]
    (allowedOrders : Finset Order) (available : Finset Coord) :
    Finset (Order × Finset Coord) :=
  allowedOrders ×ˢ coordinateTriples available

@[simp] theorem mem_survivorFrontier
    [DecidableEq Order] [DecidableEq Coord]
    {allowedOrders : Finset Order} {available : Finset Coord}
    {order : Order} {coordinates : Finset Coord} :
    (order, coordinates) ∈ survivorFrontier allowedOrders available ↔
      order ∈ allowedOrders ∧
        coordinates ⊆ available ∧ coordinates.card = 3 := by
  simp [survivorFrontier, coordinateTriples]

theorem survivorFrontier_card
    [DecidableEq Order] [DecidableEq Coord]
    (allowedOrders : Finset Order) (available : Finset Coord) :
    (survivorFrontier allowedOrders available).card =
      allowedOrders.card * Nat.choose available.card 3 := by
  simp [survivorFrontier, coordinateTriples, Finset.card_product,
    Finset.card_powersetCard]

/-- The manuscript count `m_a(F) * choose (n - 2) 3`. -/
theorem survivorFrontier_card_of_available_card
    [DecidableEq Order] [DecidableEq Coord]
    (allowedOrders : Finset Order) (available : Finset Coord) {n : Nat}
    (havailable : available.card = n - 2) :
    (survivorFrontier allowedOrders available).card =
      allowedOrders.card * Nat.choose (n - 2) 3 := by
  rw [survivorFrontier_card, havailable]

/-- Abstract factorization of the complete frontier through a branch
signature. `allowedOrders` contains all branch-dependent information. -/
structure FrontierModel
    (Branch : Type u) (Signature : Type v) (Pair : Type w)
    (Order : Type x) (Coord : Type y)
    [DecidableEq Order] [DecidableEq Coord] where
  signature : Branch → Signature
  allowedOrders : Signature → Pair → Finset Order
  available : Finset Coord

namespace FrontierModel

variable {Branch : Type u} {Signature : Type v} {Pair : Type w}
variable {Order : Type x} {Coord : Type y}
variable [DecidableEq Order] [DecidableEq Coord]

def frontier
    (model : FrontierModel Branch Signature Pair Order Coord)
    (branch : Branch) (pair : Pair) : Finset (Order × Finset Coord) :=
  survivorFrontier (model.allowedOrders (model.signature branch) pair)
    model.available

/-- Equal pattern signatures determine equal survivor frontiers. The converse
and minimality are deliberately absent. -/
theorem frontier_eq_of_signature_eq
    (model : FrontierModel Branch Signature Pair Order Coord)
    {left right : Branch}
    (hsignature : model.signature left = model.signature right)
    (pair : Pair) :
    model.frontier left pair = model.frontier right pair := by
  simp [frontier, hsignature]

theorem frontier_card
    (model : FrontierModel Branch Signature Pair Order Coord)
    (branch : Branch) (pair : Pair) :
    (model.frontier branch pair).card =
      (model.allowedOrders (model.signature branch) pair).card *
        Nat.choose model.available.card 3 := by
  exact survivorFrontier_card _ _

end FrontierModel

end Rime.Paper35
