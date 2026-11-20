import RSR2History.MultiRootCursorReplay

namespace RSR2History

def forestMergeMass (forest : List (UpperFusionTree n)) : Nat :=
  (forest.map (fun T => T.leaves.length-1)).sum

/-- The unordered pair sum of internal merge counts of distinct roots. -/
def forestCrossDefect : List (UpperFusionTree n) → Nat
  | [] => 0
  | T :: rest => (T.leaves.length-1)*forestMergeMass rest + forestCrossDefect rest

private theorem twice_choose_two (a : Nat) : 2*a.choose 2 = a*(a-1) := by
  obtain ⟨q,hq⟩ := Nat.even_mul_pred_self a
  rw [Nat.choose_two_right]
  omega

private theorem choose_two_add (a b : Nat) :
    (a+b).choose 2 = a.choose 2+b.choose 2+a*b := by
  by_cases ha : a=0
  · simp [ha]
  by_cases hb : b=0
  · simp [hb]
  have h1 := twice_choose_two a
  have h2 := twice_choose_two b
  have h3 := twice_choose_two (a+b)
  have hpa := Nat.sub_add_cancel (show 1≤a by omega)
  have hpb := Nat.sub_add_cancel (show 1≤b by omega)
  have hpab := Nat.sub_add_cancel (show 1≤a+b by omega)
  nlinarith

theorem forestMergeMass_balance (forest : List (UpperFusionTree n)) :
    forest.length+forestMergeMass forest = (forestLeaves forest).length := by
  induction forest with
  | nil => rfl
  | cons T rest ih =>
      have hp := T.leaves_length_pos
      simp only [List.length_cons, forestMergeMass, List.map_cons, List.sum_cons,
        forestLeaves, List.flatMap_cons, List.length_append] at ih ⊢
      omega

theorem forest_crossDefect_identity (forest : List (UpperFusionTree n)) :
    forestGapDebt forest + (forest.map UpperFusionTree.leftBranchDefect).sum +
      forestCrossDefect forest = (forestMergeMass forest).choose 2 := by
  induction forest with
  | nil => rfl
  | cons T rest ih =>
      have ht := T.gapDebt_add_defect
      have hc := choose_two_add (T.leaves.length-1) (forestMergeMass rest)
      simp only [forestGapDebt, List.map_cons, List.sum_cons, forestCrossDefect,
        forestMergeMass] at ih ⊢
      simp only [forestMergeMass] at hc
      omega

theorem forest_crossDefect_identity_of_leaf_count
    (forest : List (UpperFusionTree n)) (hlen : (forestLeaves forest).length = n) :
    forestGapDebt forest + (forest.map UpperFusionTree.leftBranchDefect).sum +
      forestCrossDefect forest = (n-forest.length).choose 2 := by
  have hb := forestMergeMass_balance forest
  have hm : forestMergeMass forest = n-forest.length := by omega
  simpa only [hm] using forest_crossDefect_identity forest

theorem forest_gapDebt_le_choose
    (forest : List (UpperFusionTree n)) (hlen : (forestLeaves forest).length = n) :
    forestGapDebt forest ≤ (n-forest.length).choose 2 := by
  have h := forest_crossDefect_identity_of_leaf_count forest hlen
  omega

end RSR2History
