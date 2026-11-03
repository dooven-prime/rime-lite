import FutureEvent.RegisterableData

namespace FutureEvent

open RegisteredAbsorptionChains

def addInitialCut {N t : ℕ} (s : Select N t) : InitialCutSelect (N + 1) (t + 1) := by
  let T := insert (0 : Fin (N + 1)) (s.val.map (Fin.succEmb N))
  have hnot : (0 : Fin (N + 1)) ∉ s.val.map (Fin.succEmb N) := by simp
  exact ⟨⟨T, by simp [T, hnot, s.property]⟩, 0, by simp [T], rfl⟩

theorem addInitialCut_injective {N t : ℕ} : Function.Injective (addInitialCut (N := N) (t := t)) := by
  intro s v h
  apply Subtype.ext
  ext i
  have he := congrArg (fun S : InitialCutSelect (N + 1) (t + 1) => i.succ ∈ S.val.val) h
  simpa [addInitialCut] using he

theorem addInitialCut_surjective {N t : ℕ} : Function.Surjective (addInitialCut (N := N) (t := t)) := by
  intro T
  let S := Finset.univ.filter (fun i : Fin N => i.succ ∈ T.val.val)
  have hzero : (0 : Fin (N + 1)) ∈ T.val.val := by
    obtain ⟨i, hi, hv⟩ := T.property
    have he : i = 0 := Fin.ext hv
    exact he ▸ hi
  have heq : insert (0 : Fin (N + 1)) (S.map (Fin.succEmb N)) = T.val.val := by
    ext i
    refine Fin.cases ?_ (fun j => ?_) i
    · simp [hzero]
    · simp [S]
  have hnot : (0 : Fin (N + 1)) ∉ S.map (Fin.succEmb N) := by simp
  have hc : S.card = t := by
    have hh := congrArg Finset.card heq
    simp only [Finset.card_insert_of_notMem hnot, Finset.card_map, T.val.property] at hh
    omega
  exact ⟨⟨S, hc⟩, Subtype.ext (Subtype.ext heq)⟩

noncomputable def initialCutEquiv (N t : ℕ) : Select N t ≃ InitialCutSelect (N + 1) (t + 1) :=
  Equiv.ofBijective addInitialCut ⟨addInitialCut_injective, addInitialCut_surjective⟩

noncomputable def registerableNativeEquiv (n : ℕ) (hn : 3 ≤ n) :
    RegisterableParams n ≃ RegisterableNativeParams n := by
  apply Equiv.sigmaCongrRight
  intro i
  have hN : n - 3 + 1 = n - 1 - 1 := by omega
  have ht : i.val + 1 - 1 = i.val := by omega
  change (Fin n × Select (n - 3) (i.val + 1 - 1) × Select (n - 1) (i.val + 1 + 1)) ≃ _
  rw [ht]
  exact Equiv.prodCongr (Equiv.refl _) (Equiv.prodCongr
    ((initialCutEquiv (n - 3) i.val).trans (Equiv.cast (by rw [hN]))) (Equiv.refl _))

end FutureEvent
