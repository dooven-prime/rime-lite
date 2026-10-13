import Init

namespace AgainstSilentPromotion

theorem factors_iff_fibre_constant
    {X Y Z : Type} (q : X → Y) (h : X → Z)
    (surj : Function.Surjective q) :
    (∃ g : Y → Z, ∀ x, g (q x) = h x) ↔
      (∀ x x', q x = q x' → h x = h x') := by
  constructor
  · rintro ⟨g, hg⟩ x x' heq
    calc
      h x = g (q x) := (hg x).symm
      _ = g (q x') := congrArg g heq
      _ = h x' := hg x'
  · intro hc
    classical
    let g : Y → Z := fun y => h (Classical.choose (surj y))
    refine ⟨g, ?_⟩
    intro x
    exact hc (Classical.choose (surj (q x))) x
      (Classical.choose_spec (surj (q x)))

theorem factor_unique
    {X Y Z : Type} (q : X → Y) (h : X → Z)
    (surj : Function.Surjective q) (g₁ g₂ : Y → Z)
    (hg₁ : ∀ x, g₁ (q x) = h x)
    (hg₂ : ∀ x, g₂ (q x) = h x) : g₁ = g₂ := by
  funext y
  rcases surj y with ⟨x, rfl⟩
  exact (hg₁ x).trans (hg₂ x).symm

theorem hostile_pair_blocks_factorization
    {X Y Z : Type} (q : X → Y) (h : X → Z)
    (x x' : X) (same : q x = q x') (different : h x ≠ h x') :
    ¬ ∃ g : Y → Z, ∀ u, g (q u) = h u := by
  rintro ⟨g, hg⟩
  apply different
  calc
    h x = g (q x) := (hg x).symm
    _ = g (q x') := congrArg g same
    _ = h x' := hg x'

structure Vec2 where
  x : Int
  y : Int
deriving DecidableEq, Repr

abbrev Mat2 := Vec2 × Vec2

def zeroVec : Vec2 := ⟨0, 0⟩
def zeroMat : Mat2 := (zeroVec, zeroVec)
def e₀ : Vec2 := ⟨1, 0⟩
def e₁ : Vec2 := ⟨0, 1⟩

-- The two vectors in Mat2 are its columns.
def act (m : Mat2) (v : Vec2) : Vec2 :=
  ⟨m.1.x * v.x + m.2.x * v.y,
   m.1.y * v.x + m.2.y * v.y⟩

def mul (a b : Mat2) : Mat2 :=
  (act a (act b e₀), act a (act b e₁))

theorem mul_nonzero_iff_basis_survivor (a b : Mat2) :
    mul a b ≠ zeroMat ↔
      act a (act b e₀) ≠ zeroVec ∨ act a (act b e₁) ≠ zeroVec := by
  by_cases h₀ : act a (act b e₀) = zeroVec
  · by_cases h₁ : act a (act b e₁) = zeroVec
    · simp [mul, zeroMat, h₀, h₁]
    · simp [mul, zeroMat, h₀, h₁]
  · simp [mul, zeroMat, h₀]

def A : Mat2 := (⟨1, 0⟩, ⟨0, 0⟩)
def B₀ : Mat2 := (⟨0, 0⟩, ⟨0, 1⟩)
def B₁ : Mat2 := (⟨1, 0⟩, ⟨0, 0⟩)

def support (m : Mat2) : Bool := decide (m ≠ zeroMat)
def retained (pair : Mat2 × Mat2) : Bool × Bool :=
  (support pair.1, support pair.2)
def compositionNonzero (pair : Mat2 × Mat2) : Bool :=
  decide (mul pair.1 pair.2 ≠ zeroMat)

theorem same_boolean_support : retained (A, B₀) = retained (A, B₁) := by
  decide

theorem different_composition :
    compositionNonzero (A, B₀) ≠ compositionNonzero (A, B₁) := by
  decide

theorem support_does_not_determine_composition :
    ¬ ∃ g : Bool × Bool → Bool,
      ∀ pair : Mat2 × Mat2, g (retained pair) = compositionNonzero pair := by
  exact hostile_pair_blocks_factorization retained compositionNonzero
    (A, B₀) (A, B₁) same_boolean_support different_composition

end AgainstSilentPromotion
