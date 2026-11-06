import RegisteredAbsorptionChains.FiberParameters

namespace RegisteredAbsorptionChains

/-- Symbolic chains with exactly `t` registered checkpoints. -/
abbrev RankedCode (m t : ℕ) := {c : Code m // (support c).card = t}

def rankedEquiv (m t : ℕ) :
    RankedCode m t ≃ (s : Select m t) × (s.1 → Side) where
  toFun c :=
    ⟨⟨support c.1, c.2⟩, fun i => (c.1 i.1).getD false⟩
  invFun sf :=
    ⟨fun i => if hi : i ∈ sf.1.1 then some (sf.2 ⟨i, hi⟩) else none, by
      have hs : support (fun i : Fin m =>
          if hi : i ∈ sf.1.1 then some (sf.2 ⟨i, hi⟩) else none) = sf.1.1 := by
        ext i
        simp [support]
      rw [hs]
      exact sf.1.2⟩
  left_inv := by
    intro c
    apply Subtype.ext
    funext i
    by_cases hi : i ∈ support c.1
    · have hc : c.1 i ≠ none := by simpa [support] using hi
      cases h : c.1 i with
      | none => exact False.elim (hc h)
      | some b => simp [hi, h]
    · have hc : c.1 i = none := by
        by_contra hn
        exact hi (by simp [support, hn])
      simp [hi, hc]
  right_inv := by
    intro ⟨s, f⟩
    have hs : (⟨support (fun i : Fin m =>
        if hi : i ∈ s.1 then some (f ⟨i, hi⟩) else none), by
          have hh : support (fun i : Fin m =>
              if hi : i ∈ s.1 then some (f ⟨i, hi⟩) else none) = s.1 := by
            ext i
            simp [support]
          rw [hh]
          exact s.2⟩ : Select m t) = s := by
      apply Subtype.ext
      ext i
      simp [support]
    apply Sigma.ext hs
    apply Function.hfunext (congrArg (fun a : Select m t => ↥a.1) hs)
    intro i i' hii
    have hval : i.1 = i'.1 := (Subtype.heq_iff_coe_eq (by
      intro x
      simp [support])).mp hii
    apply heq_of_eq
    simp only [hval]
    simp

noncomputable instance (m t : ℕ) : Fintype (RankedCode m t) :=
  Fintype.ofEquiv ((s : Select m t) × (s.1 → Side)) (rankedEquiv m t).symm

/-- The symbolic length stratum in equation (3.3). -/
theorem card_rankedCode (m t : ℕ) :
    Fintype.card (RankedCode m t) = 2 ^ t * m.choose t := by
  classical
  rw [Fintype.card_congr (rankedEquiv m t)]
  simp only [Fintype.card_sigma, Fintype.card_fun]
  have h : ∀ s : Select m t, Fintype.card Side ^ Fintype.card s.1 = 2 ^ t := by
    intro s
    simp [Side, Fintype.card_coe, s.2]
  simp only [h, Finset.sum_const, Finset.card_univ, Nat.nsmul_eq_mul]
  rw [card_select]
  ac_rfl

end RegisteredAbsorptionChains
