import RegisteredAbsorptionChains.OneCutAssembly
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n t : ℕ} [NeZero n]

/-- Interior cut positions in absolute source addresses. Translating by
`-u` gives the usual boundaries in `{1,...,v-u-1}`. -/
noncomputable def targetCutBoundaries
    (data : ValidFiberPlacement n t) : Finset ℕ :=
  Finset.univ.image (fun i : Fin (t - 1) =>
    data.cut ⟨i.val + 1, by omega⟩)

theorem targetCutBoundaries_internal
    (data : ValidFiberPlacement n t) (b : ℕ)
    (hb : b ∈ targetCutBoundaries data) :
    data.u < b ∧ b < data.v := by
  obtain ⟨i, _, rfl⟩ := Finset.mem_image.mp hb
  have hzero : (⟨0, Nat.zero_lt_succ t⟩ : Fin (t + 1)) <
      ⟨i.val + 1, by omega⟩ := Fin.mk_lt_mk.mpr (by omega)
  have hlast : (⟨i.val + 1, by omega⟩ : Fin (t + 1)) <
      ⟨t, Nat.lt_succ_self t⟩ := Fin.mk_lt_mk.mpr (by omega)
  have hlow := data.cut_strict hzero
  have hhigh := data.cut_strict hlast
  rw [data.cut_zero] at hlow
  rw [data.cut_last] at hhigh
  omega

theorem targetCutBoundaries_card (data : ValidFiberPlacement n t) :
    (targetCutBoundaries data).card = t - 1 := by
  unfold targetCutBoundaries
  rw [Finset.card_image_iff.mpr]
  · simp
  · intro i _ j _ hij
    change data.cut ⟨i.val + 1, by omega⟩ =
      data.cut ⟨j.val + 1, by omega⟩ at hij
    have hidx := data.cut_strict.injective hij
    have hijVal : i.val + 1 = j.val + 1 := congrArg Fin.val hidx
    exact Fin.ext (by omega)

/-- A legal abstract deletion preserves every target boundary. Its index
counts deletions, not literal `p,d` letters. -/
inductive CutBoundaryPlan (D : Finset ℕ) :
    Finset ℕ → ℕ → Prop where
  | done : CutBoundaryPlan D D 0
  | erase {E : Finset ℕ} {cost : ℕ} (b : ℕ)
      (hb : b ∈ E \ D)
      (tail : CutBoundaryPlan D (E.erase b) cost) :
      CutBoundaryPlan D E (cost + 1)

theorem CutBoundaryPlan.exists_of_subset
    (D E : Finset ℕ) (hDE : D ⊆ E) :
    CutBoundaryPlan D E (E \ D).card := by
  have aux : ∀ m : ℕ, ∀ E : Finset ℕ,
      (E \ D).card = m → D ⊆ E →
      CutBoundaryPlan D E (E \ D).card := by
    intro m
    induction m using Nat.strong_induction_on with
    | h m ih =>
        intro E hcard hsub
        by_cases heq : E = D
        · subst E
          simpa using (CutBoundaryPlan.done (D := D))
        · have hnonempty : (E \ D).Nonempty := by
            by_contra h
            have hempty : E \ D = ∅ := Finset.not_nonempty_iff_eq_empty.mp h
            exact heq (Finset.sdiff_eq_empty_iff_subset.mp hempty |>.antisymm hsub)
          obtain ⟨b, hb⟩ := hnonempty
          have hbE : b ∈ E := (Finset.mem_sdiff.mp hb).1
          have hbD : b ∉ D := (Finset.mem_sdiff.mp hb).2
          have hsub' : D ⊆ E.erase b := by
            intro x hx
            exact Finset.mem_erase.mpr ⟨by intro h; subst x; exact hbD hx,
              hsub hx⟩
          have hdrop : ((E.erase b) \ D).card < m := by
            have hsame : (E.erase b) \ D = (E \ D).erase b := by
              ext x
              simp only [Finset.mem_sdiff, Finset.mem_erase]
              tauto
            rw [hsame, Finset.card_erase_of_mem hb, hcard]
            have : 0 < m := by
              rw [← hcard]
              exact Finset.card_pos.mpr ⟨b, hb⟩
            omega
          have htail := ih _ hdrop (E.erase b) rfl hsub'
          have hcost : (E \ D).card = ((E.erase b) \ D).card + 1 := by
            have hsame : (E.erase b) \ D = (E \ D).erase b := by
              ext x
              simp only [Finset.mem_sdiff, Finset.mem_erase]
              tauto
            rw [hsame, Finset.card_erase_of_mem hb]
            omega
          rw [hcost]
          exact CutBoundaryPlan.erase b hb htail
  exact aux _ E rfl hDE

/-- Every target cut is obtained from the clean singleton partition by
exactly `k-t` abstract boundary deletions. Real-word lifting of each
deletion remains a separate obligation. -/
theorem targetCutBoundaryPlan (data : ValidFiberPlacement n t) :
    CutBoundaryPlan (targetCutBoundaries data)
      (Finset.Ioo data.u data.v)
      (data.v - data.u - t) := by
  let D := targetCutBoundaries data
  let E := Finset.Ioo data.u data.v
  have hsub : D ⊆ E := by
    intro b hb
    have h := targetCutBoundaries_internal data b hb
    simp [E, h.1, h.2]
  have hplan := CutBoundaryPlan.exists_of_subset D E hsub
  have hD : D.card = t - 1 := targetCutBoundaries_card data
  have hE : E.card = data.v - data.u - 1 := by
    simp [E]
  have hcard : (E \ D).card = data.v - data.u - t := by
    rw [Finset.card_sdiff, Finset.inter_eq_left.mpr hsub, hD, hE]
    have hvt : t ≤ data.v - data.u := by
      have hle := Finset.card_le_card hsub
      rw [hD, hE] at hle
      have := data.ht
      have := data.huv
      omega
    have := data.ht
    omega
  rw [← hcard]
  exact hplan

end RegisteredAbsorptionChains
