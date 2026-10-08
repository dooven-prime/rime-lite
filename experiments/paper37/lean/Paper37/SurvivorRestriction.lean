import Mathlib.GroupTheory.SpecificGroups.Alternating
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Exact survivor restriction on five positions

Fin 5 is the within-lane index type, not the normalized physical carrier E.
The two kernel indices are 0 and 1. Physical multiplication by Delta and
the actual terminal-placement theorem remain manuscript inputs.
-/

namespace Rime.Paper37

open scoped Classical

abbrev FivePerm := Equiv.Perm (Fin 5)

def kernelIndices : Finset (Fin 5) := {0, 1}

def kernelSwap : FivePerm := Equiv.swap 0 1

def TerminalCondition (F : Finset (Fin 5)) (eta : FivePerm) : Prop :=
  F.image eta = kernelIndices

def survivorRestriction (F : Finset (Fin 5)) (eta : FivePerm) :
    {i : Fin 5 // i ∉ F} → Fin 5 :=
  fun i => eta i.val

theorem perm_eq_one_or_swap_of_fixes_complement
    {X : Type*} [DecidableEq X] (tau : Equiv.Perm X) (a b : X)
    (hab : a ≠ b) (hfix : ∀ q, q ≠ a → q ≠ b → tau q = q) :
    tau = 1 ∨ tau = Equiv.swap a b := by
  have hclosed (q : X) (hq : q = a ∨ q = b) : tau q = a ∨ tau q = b := by
    by_contra h
    push Not at h
    have hback : tau q = q := tau.injective (hfix (tau q) h.1 h.2)
    rcases hq with rfl | rfl
    · exact h.1 hback
    · exact h.2 hback
  rcases hclosed a (Or.inl rfl) with hta | hta
  · have htb : tau b = b := by
      rcases hclosed b (Or.inr rfl) with htb | htb
      · exact False.elim (hab (tau.injective (htb.trans hta.symm)).symm)
      · exact htb
    left
    ext q
    by_cases hqa : q = a
    · subst q; simpa using hta
    by_cases hqb : q = b
    · subst q; simpa using htb
    simpa using hfix q hqa hqb
  · have htb : tau b = a := by
      rcases hclosed b (Or.inr rfl) with htb | htb
      · exact htb
      · exact False.elim (hab (tau.injective (htb.trans hta.symm)).symm)
    right
    ext q
    by_cases hqa : q = a
    · subst q; simpa [hab] using hta
    by_cases hqb : q = b
    · subst q; simpa [hab] using htb
    simpa [Equiv.swap_apply_def, hqa, hqb] using hfix q hqa hqb

theorem survivor_image_not_kernel
    {F : Finset (Fin 5)} {eta : FivePerm} (hterminal : TerminalCondition F eta)
    (i : {i : Fin 5 // i ∉ F}) :
    eta i.val ≠ 0 ∧ eta i.val ≠ 1 := by
  have hnot : eta i.val ∉ kernelIndices := by
    intro hmem
    rw [← hterminal] at hmem
    rcases Finset.mem_image.mp hmem with ⟨j, hj, heq⟩
    have hji : j = i.val := eta.injective heq
    exact i.property (hji ▸ hj)
  simpa [kernelIndices] using hnot

theorem terminal_kernelSwap_mul
    {F : Finset (Fin 5)} {eta : FivePerm} (hterminal : TerminalCondition F eta) :
    TerminalCondition F (kernelSwap * eta) := by
  change F.image (kernelSwap * eta) = kernelIndices
  have himage : F.image (kernelSwap * eta) = (F.image eta).image kernelSwap := by
    simp [Finset.image_image, Function.comp_def]
  rw [himage, hterminal]
  simp [kernelIndices, kernelSwap, Finset.pair_comm]

theorem survivorRestriction_kernelSwap_mul
    {F : Finset (Fin 5)} {eta : FivePerm} (hterminal : TerminalCondition F eta) :
    survivorRestriction F (kernelSwap * eta) = survivorRestriction F eta := by
  funext i
  obtain ⟨hzero, hone⟩ := survivor_image_not_kernel hterminal i
  simp [survivorRestriction, kernelSwap, Equiv.Perm.mul_apply,
    Equiv.swap_apply_def, hzero, hone]

/-- The kernel swap is the only possible loss under survivor restriction. -/
theorem survivorRestriction_eq_iff
    {F : Finset (Fin 5)} {eta theta : FivePerm}
    (hterminal : TerminalCondition F eta) :
    survivorRestriction F theta = survivorRestriction F eta ↔
      theta = eta ∨ theta = kernelSwap * eta := by
  constructor
  · intro hrestriction
    let tau := theta * eta⁻¹
    have hfix : ∀ q : Fin 5, q ≠ 0 → q ≠ 1 → tau q = q := by
      intro q hzero hone
      have hnot : eta⁻¹ q ∉ F := by
        intro hmem
        have himage : q ∈ F.image eta :=
          Finset.mem_image.mpr ⟨eta⁻¹ q, hmem, by simp⟩
        rw [hterminal] at himage
        simp [kernelIndices, hzero, hone] at himage
      have hread := congrFun hrestriction ⟨eta⁻¹ q, hnot⟩
      simpa [tau, survivorRestriction, Equiv.Perm.mul_apply] using hread
    rcases perm_eq_one_or_swap_of_fixes_complement tau 0 1 (by decide) hfix
        with hone | hswap
    · left
      have heq : theta * eta⁻¹ = 1 := hone
      simpa using mul_inv_eq_iff_eq_mul.mp heq
    · right
      have heq : theta * eta⁻¹ = kernelSwap := hswap
      exact mul_inv_eq_iff_eq_mul.mp heq
  · rintro (rfl | rfl)
    · rfl
    · exact survivorRestriction_kernelSwap_mul hterminal

theorem kernelSwap_ne_one : kernelSwap ≠ 1 := by
  intro h
  have hzero := congrArg (fun p : FivePerm => p 0) h
  simp [kernelSwap] at hzero

theorem kernelSwap_mul_ne (eta : FivePerm) : kernelSwap * eta ≠ eta := by
  intro h
  apply kernelSwap_ne_one
  exact mul_right_cancel (h.trans (one_mul eta).symm)

noncomputable def terminalPermutations (K : Subgroup FivePerm)
    (F : Finset (Fin 5)) : Finset FivePerm := by
  classical
  exact Finset.univ.filter fun eta => eta ∈ K ∧ TerminalCondition F eta

@[simp] theorem mem_terminalPermutations (K : Subgroup FivePerm)
    (F : Finset (Fin 5)) (eta : FivePerm) :
    eta ∈ terminalPermutations K F ↔ eta ∈ K ∧ TerminalCondition F eta := by
  classical
  simp [terminalPermutations]

noncomputable def survivorFrontier (K : Subgroup FivePerm)
    (F : Finset (Fin 5)) : Finset ({i : Fin 5 // i ∉ F} → Fin 5) := by
  classical
  exact (terminalPermutations K F).image (survivorRestriction F)

noncomputable def restrictionFiber (K : Subgroup FivePerm)
    (F : Finset (Fin 5)) (eta : FivePerm) : Finset FivePerm := by
  classical
  exact (terminalPermutations K F).filter fun theta =>
    survivorRestriction F theta = survivorRestriction F eta

theorem restrictionFiber_eq_pair
    {K : Subgroup FivePerm} {F : Finset (Fin 5)} {eta : FivePerm}
    (heta : eta ∈ terminalPermutations K F) (hswap : kernelSwap ∈ K) :
    restrictionFiber K F eta = {eta, kernelSwap * eta} := by
  classical
  obtain ⟨hetaK, hterminal⟩ := (mem_terminalPermutations K F eta).mp heta
  ext theta
  simp only [restrictionFiber, Finset.mem_filter, mem_terminalPermutations,
    Finset.mem_insert, Finset.mem_singleton]
  constructor
  · rintro ⟨⟨_, _⟩, hrestriction⟩
    exact (survivorRestriction_eq_iff hterminal).mp hrestriction
  · rintro (rfl | rfl)
    · exact ⟨⟨hetaK, hterminal⟩, rfl⟩
    · exact ⟨⟨K.mul_mem hswap hetaK, terminal_kernelSwap_mul hterminal⟩,
        survivorRestriction_kernelSwap_mul hterminal⟩

theorem restrictionFiber_eq_singleton
    {K : Subgroup FivePerm} {F : Finset (Fin 5)} {eta : FivePerm}
    (heta : eta ∈ terminalPermutations K F) (hswap : kernelSwap ∉ K) :
    restrictionFiber K F eta = {eta} := by
  classical
  obtain ⟨hetaK, hterminal⟩ := (mem_terminalPermutations K F eta).mp heta
  ext theta
  simp only [restrictionFiber, Finset.mem_filter, mem_terminalPermutations,
    Finset.mem_singleton]
  constructor
  · rintro ⟨⟨hthetaK, _⟩, hrestriction⟩
    rcases (survivorRestriction_eq_iff hterminal).mp hrestriction with heq | heq
    · exact heq
    · have hproduct := K.mul_mem hthetaK (K.inv_mem hetaK)
      have hswapK : kernelSwap ∈ K := by
        simpa [heq, mul_assoc] using hproduct
      exact False.elim (hswap hswapK)
  · intro heq
    subst theta
    exact ⟨⟨hetaK, hterminal⟩, rfl⟩

theorem restrictionFiber_card
    {K : Subgroup FivePerm} {F : Finset (Fin 5)} {eta : FivePerm}
    (heta : eta ∈ terminalPermutations K F) :
    (restrictionFiber K F eta).card = if kernelSwap ∈ K then 2 else 1 := by
  classical
  by_cases hswap : kernelSwap ∈ K
  · rw [restrictionFiber_eq_pair heta hswap]
    simp [hswap, (kernelSwap_mul_ne eta).symm]
  · rw [restrictionFiber_eq_singleton heta hswap]
    simp [hswap]

/-- Corollary 5.3's exact multiplicity law, without a nonempty-fiber assumption. -/
theorem terminal_card_eq_frontier_card_mul
    (K : Subgroup FivePerm) (F : Finset (Fin 5)) :
    (terminalPermutations K F).card =
      (survivorFrontier K F).card * (if kernelSwap ∈ K then 2 else 1) := by
  classical
  rw [Finset.card_eq_sum_card_image (survivorRestriction F)]
  have hcount : ∀ s ∈ survivorFrontier K F,
      ((terminalPermutations K F).filter
        (fun eta => survivorRestriction F eta = s)).card =
          if kernelSwap ∈ K then 2 else 1 := by
    intro s hs
    obtain ⟨eta, heta, hrestriction⟩ := Finset.mem_image.mp hs
    rw [← hrestriction]
    exact restrictionFiber_card heta
  calc
    _ = ∑ s ∈ survivorFrontier K F, (if kernelSwap ∈ K then 2 else 1) := by
      apply Finset.sum_congr rfl
      intro s hs
      exact hcount s hs
    _ = _ := by
      by_cases hswap : kernelSwap ∈ K <;> simp [hswap]

theorem kernelSwap_mul_mem_alternating_of_not {eta : FivePerm}
    (hodd : eta ∉ alternatingGroup (Fin 5)) :
    kernelSwap * eta ∈ alternatingGroup (Fin 5) := by
  have hsign : Equiv.Perm.sign eta = -1 := by
    rcases Int.units_eq_one_or (Equiv.Perm.sign eta) with h | h
    · exact False.elim (hodd (Equiv.Perm.mem_alternatingGroup.mpr h))
    · exact h
  simp [Equiv.Perm.mem_alternatingGroup, kernelSwap, map_mul,
    Equiv.Perm.sign_swap (show (0 : Fin 5) ≠ 1 by decide), hsign]

theorem survivorFrontier_card_eq_div
    (K : Subgroup FivePerm) (F : Finset (Fin 5)) :
    (survivorFrontier K F).card =
      (terminalPermutations K F).card / (if kernelSwap ∈ K then 2 else 1) := by
  classical
  rw [terminal_card_eq_frontier_card_mul]
  by_cases hswap : kernelSwap ∈ K <;> simp [hswap]

/-- Theorem 6.3's projection equality: A5 keeps one of the two
kernel extensions, while S5 keeps both. Concrete group generation and
physical guarded reachability are not inputs to this algebraic result. -/
theorem alternating_survivorFrontier_eq_full (F : Finset (Fin 5)) :
    survivorFrontier (alternatingGroup (Fin 5)) F =
      survivorFrontier (⊤ : Subgroup FivePerm) F := by
  classical
  ext s
  constructor
  · intro hs
    obtain ⟨eta, heta, hrestriction⟩ := Finset.mem_image.mp hs
    obtain ⟨_, hterminal⟩ :=
      (mem_terminalPermutations (alternatingGroup (Fin 5)) F eta).mp heta
    exact Finset.mem_image.mpr ⟨eta,
      (mem_terminalPermutations ⊤ F eta).mpr ⟨Subgroup.mem_top eta, hterminal⟩,
      hrestriction⟩
  · intro hs
    obtain ⟨eta, heta, hrestriction⟩ := Finset.mem_image.mp hs
    obtain ⟨_, hterminal⟩ := (mem_terminalPermutations ⊤ F eta).mp heta
    by_cases heven : eta ∈ alternatingGroup (Fin 5)
    · exact Finset.mem_image.mpr ⟨eta,
        (mem_terminalPermutations _ F eta).mpr ⟨heven, hterminal⟩, hrestriction⟩
    · refine Finset.mem_image.mpr ⟨kernelSwap * eta,
        (mem_terminalPermutations _ F _).mpr
          ⟨kernelSwap_mul_mem_alternating_of_not heven,
            terminal_kernelSwap_mul hterminal⟩, ?_⟩
      exact (survivorRestriction_kernelSwap_mul hterminal).trans hrestriction

end Rime.Paper37
