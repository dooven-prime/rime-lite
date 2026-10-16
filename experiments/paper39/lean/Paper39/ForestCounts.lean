import Std

namespace Paper39

/-- The single defect label is implicit; ports and event target remain explicit. -/
inductive FusionTree (Atom Q : Type) where
  | leaf : Atom → FusionTree Atom Q
  | fuse : Q → Q → Q → FusionTree Atom Q → FusionTree Atom Q → FusionTree Atom Q

namespace FusionTree

def leafCount : FusionTree Atom Q → Nat
  | .leaf _ => 1
  | .fuse _ _ _ left right => leafCount left + leafCount right

def fusionCount : FusionTree Atom Q → Nat
  | .leaf _ => 0
  | .fuse _ _ _ left right => fusionCount left + fusionCount right + 1

def nodeCount : FusionTree Atom Q → Nat
  | .leaf _ => 1
  | .fuse _ _ _ left right => nodeCount left + nodeCount right + 1

theorem leaf_eq_fusion_add_one (tree : FusionTree Atom Q) :
    tree.leafCount = tree.fusionCount + 1 := by
  induction tree with
  | leaf => rfl
  | fuse _ _ _ _ _ ihl ihr =>
    simp only [leafCount, fusionCount]
    omega

theorem node_eq_leaf_add_fusion (tree : FusionTree Atom Q) :
    tree.nodeCount = tree.leafCount + tree.fusionCount := by
  induction tree with
  | leaf => rfl
  | fuse _ _ _ _ _ ihl ihr =>
    simp only [nodeCount, leafCount, fusionCount]
    omega

end FusionTree

def forestLeaves (roots : List (FusionTree Atom Q)) : Nat :=
  (roots.map FusionTree.leafCount).sum

def forestFusions (roots : List (FusionTree Atom Q)) : Nat :=
  (roots.map FusionTree.fusionCount).sum

def forestNodes (roots : List (FusionTree Atom Q)) : Nat :=
  (roots.map FusionTree.nodeCount).sum

theorem forest_leaf_fusion_identity (roots : List (FusionTree Atom Q)) :
    forestLeaves roots = forestFusions roots + roots.length := by
  induction roots with
  | nil => rfl
  | cons tree rest ih =>
    have count := tree.leaf_eq_fusion_add_one
    simp only [forestLeaves, forestFusions, List.map_cons, List.sum_cons, List.length_cons] at *
    omega

theorem forest_node_identity (roots : List (FusionTree Atom Q)) :
    forestNodes roots + roots.length = 2 * forestLeaves roots := by
  induction roots with
  | nil => rfl
  | cons tree rest ih =>
    have first := tree.leaf_eq_fusion_add_one
    have second := tree.node_eq_leaf_add_fusion
    simp only [forestNodes, forestLeaves, List.map_cons, List.sum_cons, List.length_cons] at *
    omega

theorem forest_node_bound (roots : List (FusionTree Atom Q)) (nonempty : 0 < roots.length) :
    forestNodes roots ≤ 2 * forestLeaves roots - 1 := by
  have identity := forest_node_identity roots
  omega

end Paper39
