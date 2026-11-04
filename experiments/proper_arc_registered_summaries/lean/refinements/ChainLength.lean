import converse.ActualChainConverse
import counting.LastCheckpointCount
import RegisteredAbsorptionChains.FiberParameters

namespace ProperArc.Chains

open RegisteredAbsorptionChains

/-- A chosen checkpoint set together with its independent port directions. -/
abbrev ColoredCheckpoints (m j : ℕ) :=
  (S : Select m j) × (S.val → Bool)

def codeOfColors {m : ℕ} (S : Finset (Fin m)) (color : S → Bool) : Code m :=
  fun i => if hi : i ∈ S then some (color ⟨i,hi⟩) else none

theorem support_codeOfColors {m : ℕ} (S : Finset (Fin m)) (color : S → Bool) :
    support (codeOfColors S color)=S := by
  ext i
  simp [support,codeOfColors]

theorem codeOfColors_readback {m : ℕ} (v : Code m) :
    codeOfColors (support v) (fun i => (v i.val).getD false)=v := by
  funext i
  cases hv : v i with
  | none => simp [codeOfColors,support,hv]
  | some side => simp [codeOfColors,support,hv]

noncomputable def coloredCheckpointsEquivCodes (m j : ℕ) :
    ColoredCheckpoints m j ≃ {v : Code m // (support v).card=j} := by
  apply Equiv.ofBijective (fun p =>
    (⟨codeOfColors p.1.val p.2,by rw [support_codeOfColors]; exact p.1.property⟩ :
      {v : Code m // (support v).card=j}))
  constructor
  · rintro ⟨S,color⟩ ⟨T,other⟩ h
    have hc := congrArg Subtype.val h
    have hST : S=T := Subtype.ext (by
      simpa only [support_codeOfColors] using congrArg support hc)
    subst T
    have hcolor : color=other := by
      funext i
      have hi := congrFun hc i.val
      simpa only [codeOfColors,dif_pos i.property,Option.some.injEq] using hi
    subst other
    rfl
  · intro v
    exact ⟨⟨⟨support v.val,v.property⟩,fun i => (v.val i.val).getD false⟩,
      Subtype.ext (codeOfColors_readback v.val)⟩

theorem card_codes_by_support (m j : ℕ) :
    Nat.card {v : Code m // (support v).card=j}=m.choose j*2^j := by
  classical
  rw [Nat.card_congr (coloredCheckpointsEquivCodes m j).symm]
  rw [Nat.card_eq_fintype_card]
  simp only [ColoredCheckpoints,Fintype.card_sigma,Fintype.card_fun,
    Fintype.card_bool,Fintype.card_coe]
  have hc (S : Select m j) : S.val.card=j := S.property
  simp only [hc,Finset.sum_const,Finset.card_univ,card_select,smul_eq_mul]

theorem support_card_snoc {m : ℕ} (v : Code m) (s : Symbol) :
    (support (Fin.snoc v s)).card=(support v).card+(if s=none then 0 else 1) := by
  classical
  have hcard {l : ℕ} (w : Code l) :
      (support w).card=∑ i : Fin l, if w i ≠ none then 1 else 0 := by
    simp only [support,Finset.sum_boole,Nat.cast_id]
  rw [hcard,Fin.sum_univ_castSucc]
  simp only [Fin.snoc_castSucc,Fin.snoc_last,← hcard]
  cases s <;> simp

theorem keys_snoc_prefix {m : ℕ} (v : Code m) (s : Symbol) :
    ∀ j (hj : j ≤ m), keys (Fin.snoc v s) j (by omega)=keys v j hj := by
  intro j
  induction j with
  | zero => intro hj; rfl
  | succ j ih =>
      intro hj
      have he : (⟨j,by omega⟩ : Fin (m+1))=(⟨j,by omega⟩ : Fin m).castSucc := rfl
      rw [keys_succ,keys_succ,ih (by omega)]
      simp only [he,Fin.snoc_castSucc]

theorem keys_length_support (m : ℕ) (v : Code m) :
    (keys v m le_rfl).length=(support v).card := by
  induction m with
  | zero => simp [keys_zero,support]
  | succ m ih =>
      obtain ⟨p,hp⟩ := (codeSnocEquiv m).symm.surjective v
      change Fin.snoc p.1 p.2=v at hp
      rw [← hp,keys_succ,keys_snoc_prefix p.1 p.2 m le_rfl,
        support_card_snoc,List.length_append,ih]
      have he : (⟨m,by omega⟩ : Fin (m+1))=Fin.last m := rfl
      simp only [he,Fin.snoc_last]
      cases p.2 <;> simp

variable {n : ℕ} [NeZero n]

theorem decodeChain_length (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) : (decodeChain c hr v).length=(support v).card := by
  have h := congrArg List.length (decodeChain_keys c hr v)
  simpa only [List.length_map,keys_length_support] using h

/-- Restrict the frozen actual-chain equivalence by the literal record count. -/
noncomputable def actualChainsLengthEquivCodes (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (j : ℕ) :
    {A : ActualSelectedChains c r (t.val+1) // A.val.length=j} ≃
      {v : Code (n-r) // (support v).card=j} := by
  apply (actualSelectedChainsEquivCode c hr t).subtypeEquiv
  intro A
  have h := (actualSelectedChainsEquivCode c hr t).symm_apply_apply A
  have hlength := congrArg (fun B => B.val.length) h
  rw [actualSelectedChainsEquivCode_symm_val,decodeChain_length] at hlength
  exact hlength.symm ▸ Iff.rfl

/-- Theorem 4.2: exactly j actual selected absorptions at each fixed origin. -/
theorem card_actualSelectedChains_length (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (j : ℕ) :
    Nat.card {A : ActualSelectedChains c r (t.val+1) // A.val.length=j}=
      (n-r).choose j*2^j := by
  rw [Nat.card_congr (actualChainsLengthEquivCodes c hr t j),card_codes_by_support]

end ProperArc.Chains
