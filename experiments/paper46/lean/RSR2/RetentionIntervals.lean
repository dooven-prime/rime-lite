import RSR2.RetentionRouting

/-! Finite safe intervals extracted from the semantic retention predicate. -/
namespace RSR2.Parametric

def cutSite (n : Nat) (hn : 0 < n) (cut i : Fin n) : Fin n :=
  sourceAtom n hn ((cut.val : Int) + i.val)

def cutIndex (n : Nat) (hn : 0 < n) (cut a : Fin n) : Fin n :=
  nextMany n hn a (n-cut.val)

theorem cutSite_val (n : Nat) (hn : 0 < n) (cut i : Fin n) :
    (cutSite n hn cut i).val = (cut.val+i.val)%n := by
  have h := sourceAtom_val n hn ((cut.val : Int)+i.val)
  have he : ((cut.val : Int)+i.val) = ((cut.val+i.val : Nat) : Int) := by omega
  rw [he, ← Int.natCast_emod] at h
  change ((cutSite n hn cut i).val : Int) = _ at h
  omega

theorem cutIndex_cutSite (n : Nat) (hn : 0 < n) (cut i : Fin n) :
    cutIndex n hn cut (cutSite n hn cut i) = i := by
  apply Fin.ext
  rw [cutIndex, nextMany_val, cutSite_val, Nat.mod_add_mod]
  have he : cut.val+i.val+(n-cut.val) = i.val+n := by have := cut.isLt; omega
  rw [he, Nat.add_mod, Nat.mod_self, Nat.add_zero]
  simp [Nat.mod_eq_of_lt i.isLt]

theorem cutSite_cutIndex (n : Nat) (hn : 0 < n) (cut a : Fin n) :
    cutSite n hn cut (cutIndex n hn cut a) = a := by
  apply Fin.ext
  rw [cutSite_val, cutIndex, nextMany_val, Nat.add_mod_mod]
  have he : cut.val+(a.val+(n-cut.val)) = a.val+n := by have := cut.isLt; omega
  rw [he, Nat.add_mod, Nat.mod_self, Nat.add_zero]
  simp [Nat.mod_eq_of_lt a.isLt]

theorem cutSite_injective (n : Nat) (hn : 0 < n) (cut : Fin n)
    {i j : Fin n} (h : cutSite n hn cut i = cutSite n hn cut j) : i=j := by
  have := congrArg (cutIndex n hn cut) h
  simpa only [cutIndex_cutSite] using this

theorem restricted_interval_between (n : Nat) (hn : 0 < n)
    (cut : Fin n) (U B : Fin n → Prop)
    (h : ListLabelInterval B (restrictedSourceCycle n hn cut U))
    (i j k : Fin n) (hij : i ≤ j) (hjk : j ≤ k)
    (hi : B (cutSite n hn cut i)) (hk : B (cutSite n hn cut k))
    (hBU : ∀a, B a → U a) (hj : U (cutSite n hn cut j)) :
    B (cutSite n hn cut j) := by
  classical
  by_cases he : i=j
  · simpa only [he] using hi
  by_cases he' : j=k
  · simpa only [← he'] using hk
  have horder : ([i,j,k] : List (Fin n)).Pairwise (· < ·) := by
    simp
    exact ⟨⟨by omega, by omega⟩, by omega⟩
  have hsub : ([i,j,k] : List (Fin n)).Sublist (List.finRange n) := by
    let ix (a : Fin n) : Fin (List.finRange n).length :=
      ⟨a.val, by simpa using a.isLt⟩
    have ho : ([ix i,ix j,ix k]).Pairwise (· < ·) := by
      simp [ix, Fin.lt_def] at *
      exact horder
    have hs := List.map_getElem_sublist (l := List.finRange n) ho
    simpa [ix, Fin.cast] using hs
  have hf : ([i,j,k] : List (Fin n)).Sublist
      ((List.finRange n).filter (fun r => decide (U (cutSite n hn cut r)))) := by
    exact List.sublist_filter_iff.mpr ⟨[i,j,k], hsub, by
      simp [hBU _ hi, hj, hBU _ hk]⟩
  apply h _ _ _ (by
    have hs := hf.map (cutSite n hn cut)
    change ([cutSite n hn cut i,cutSite n hn cut j,cutSite n hn cut k]).Sublist
      (((List.finRange n).filter (fun r => decide (U (cutSite n hn cut r)))).map
        (cutSite n hn cut))
    exact hs) hi hk

/-- A nonempty retained block has a safe source interval after a suitable
cut. Its endpoints belong to the block; every retained atom between them
belongs to that same block. -/
theorem retention_safe_interval (n : Nat) (hn : 0 < n)
    (U : Fin n → Prop) (B : List (Fin n)) (hne : B ≠ [])
    (hBU : ∀a∈B,U a)
    (h : RestrictedCyclicInterval n hn U (· ∈ B)) :
    ∃ cut lo hi : Fin n,
      lo ≤ hi ∧ cutSite n hn cut lo ∈ B ∧ cutSite n hn cut hi ∈ B ∧
      (∀a∈B, lo ≤ cutIndex n hn cut a ∧ cutIndex n hn cut a ≤ hi) ∧
      (∀i, lo ≤ i → i ≤ hi → U (cutSite n hn cut i) →
        cutSite n hn cut i ∈ B) := by
  classical
  obtain ⟨cut,hcut⟩ := h
  let indices := B.map (fun a => (cutIndex n hn cut a).val)
  have hindices : indices ≠ [] := by simpa [indices] using hne
  have hlo := List.min_mem hindices
  have hhi := List.max_mem hindices
  have hbound : ∀i∈indices, i<n := by
    intro i hi
    obtain ⟨a,_,rfl⟩ := List.mem_map.mp hi
    exact (cutIndex n hn cut a).isLt
  let lo : Fin n := ⟨indices.min hindices, hbound _ hlo⟩
  let hi : Fin n := ⟨indices.max hindices, hbound _ hhi⟩
  have loB : cutSite n hn cut lo ∈ B := by
    obtain ⟨a,ha,he⟩ := List.mem_map.mp hlo
    have he' : cutIndex n hn cut a=lo := Fin.ext he
    rw [← he', cutSite_cutIndex]; exact ha
  have hiB : cutSite n hn cut hi ∈ B := by
    obtain ⟨a,ha,he⟩ := List.mem_map.mp hhi
    have he' : cutIndex n hn cut a=hi := Fin.ext he
    rw [← he', cutSite_cutIndex]; exact ha
  refine ⟨cut,lo,hi, List.min_le_of_mem hhi, loB,hiB, ?_, ?_⟩
  · intro a ha
    have hm : (cutIndex n hn cut a).val ∈ indices := List.mem_map.mpr ⟨a,ha,rfl⟩
    exact ⟨List.min_le_of_mem hm, List.le_max_of_mem hm⟩
  · intro i hil hih hu
    exact restricted_interval_between n hn cut U (·∈B) hcut lo i hi hil hih
      loB hiB hBU hu

end RSR2.Parametric
