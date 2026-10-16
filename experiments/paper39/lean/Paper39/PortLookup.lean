import Std

namespace Paper39

variable {Q Tree : Type} [DecidableEq Q]

/-- A storage list denotes a position-indexed partial function. -/
def lookup (roots : List (Q × Tree)) (q : Q) : Option Tree :=
  match roots with
  | [] => none
  | (position, tree) :: rest => if position = q then some tree else lookup rest q

def KeyFunctional (roots : List (Q × Tree)) : Prop :=
  ∀ q x y, (q, x) ∈ roots → (q, y) ∈ roots → x = y

theorem lookup_some_mem {roots : List (Q × Tree)} {q : Q} {tree : Tree}
    (h : lookup roots q = some tree) : (q, tree) ∈ roots := by
  induction roots with
  | nil => simp [lookup] at h
  | cons entry rest ih =>
    rcases entry with ⟨position, value⟩
    simp only [lookup] at h
    split at h
    · rename_i hp
      cases hp
      cases Option.some.inj h
      exact List.mem_cons_self
    · exact List.mem_cons_of_mem _ (ih h)

theorem lookup_of_mem {roots : List (Q × Tree)} (unique : KeyFunctional roots)
    {q : Q} {tree : Tree} (member : (q, tree) ∈ roots) : lookup roots q = some tree := by
  induction roots with
  | nil => simp at member
  | cons entry rest ih =>
    rcases entry with ⟨position, value⟩
    simp only [lookup]
    by_cases hp : position = q
    · rw [if_pos hp]
      cases hp
      exact congrArg some (unique q value tree List.mem_cons_self member)
    · rw [if_neg hp]
      apply ih
      · intro p x y hx hy
        exact unique p x y (List.mem_cons_of_mem _ hx) (List.mem_cons_of_mem _ hy)
      · rcases List.mem_cons.mp member with heq | htail
        · exact False.elim (hp (congrArg Prod.fst heq).symm)
        · exact htail

omit [DecidableEq Q] in
theorem keyFunctional_perm {xs ys : List (Q × Tree)} (permutation : xs.Perm ys)
    (unique : KeyFunctional xs) : KeyFunctional ys := by
  intro q x y hx hy
  exact unique q x y (permutation.mem_iff.mpr hx) (permutation.mem_iff.mpr hy)

theorem lookup_perm {xs ys : List (Q × Tree)} (permutation : xs.Perm ys)
    (unique : KeyFunctional xs) (q : Q) : lookup xs q = lookup ys q := by
  have other := keyFunctional_perm permutation unique
  cases hx : lookup xs q with
  | some tree =>
    exact (lookup_of_mem other (permutation.mem_iff.mp (lookup_some_mem hx))).symm
  | none =>
    cases hy : lookup ys q with
    | none => rfl
    | some tree =>
      have impossible := lookup_of_mem unique (permutation.mem_iff.mpr (lookup_some_mem hy))
      simp [hx] at impossible

/-- Children are selected by fixed ports, not by incoming list order. -/
def collisionChildren (roots : List (Q × Tree)) (k0 k1 : Q) : Option (Tree × Tree) := do
  let left ← lookup roots k0
  let right ← lookup roots k1
  pure (left, right)

theorem collisionChildren_perm {xs ys : List (Q × Tree)} (permutation : xs.Perm ys)
    (unique : KeyFunctional xs) (k0 k1 : Q) :
    collisionChildren xs k0 k1 = collisionChildren ys k0 k1 := by
  simp only [collisionChildren, lookup_perm permutation unique]

theorem reversed_two_root_ports :
    collisionChildren [(1, 11), (0, 7)] 0 1 = some (7, 11) := by decide

end Paper39
