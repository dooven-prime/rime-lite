import Std

/-!
# Paper XXVIII: exact credit spine

These are the data-independent arithmetic implications of Proposition 4.1.
No theorem here constructs an exact receipt or proves its membership in a
declared lift fiber.
-/

namespace Rime.Paper28

structure Receipt (Context : Type u) where
  source : Context
  target : Context
  length : Nat
  surplus : Int

def Budget (top : Int) (maturity : Context → Int) (context : Context) : Int :=
  top - maturity context

def SurplusLaw (maturity : Context → Int) (x : Receipt Context) : Prop :=
  x.surplus = maturity x.target - maturity x.source - (x.length : Int)

def CreditLaw (budget : Context → Int) (x : Receipt Context) : Prop :=
  budget x.source = (x.length : Int) + x.surplus + budget x.target

/-- A corridor surplus equation implies the exact budget identity. -/
theorem credit_of_surplus
    (top : Int) (maturity : Context → Int) (x : Receipt Context)
    (h : SurplusLaw maturity x) :
    CreditLaw (Budget top maturity) x := by
  unfold SurplusLaw at h
  unfold CreditLaw Budget
  omega

/-- Composition is conditional on an existing compatible exact composite. -/
theorem credit_of_composite
    (budget : Context → Int) (x y composite : Receipt Context)
    (hxy : x.target = y.source)
    (hx : CreditLaw budget x) (hy : CreditLaw budget y)
    (hsource : composite.source = x.source)
    (htarget : composite.target = y.target)
    (hlength : composite.length = x.length + y.length)
    (hsurplus : composite.surplus = x.surplus + y.surplus) :
    CreditLaw budget composite := by
  unfold CreditLaw at hx hy ⊢
  rw [hsource, htarget, hlength, hsurplus]
  rw [hxy] at hx
  omega

end Rime.Paper28
