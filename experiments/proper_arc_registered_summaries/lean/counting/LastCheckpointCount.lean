import chains.Decoder
import Mathlib.Algebra.BigOperators.Option
import Mathlib.Algebra.BigOperators.Intervals

namespace ProperArc.Chains

open RegisteredAbsorptionChains

/-- Split off the final symbol, retaining the chronological code prefix. -/
def codeSnocEquiv (m : ℕ) : Code (m+1) ≃ Code m × Symbol where
  toFun v := (fun i => v i.castSucc, v (Fin.last m))
  invFun p := Fin.snoc p.1 p.2
  left_inv v := by
    funext i
    refine Fin.lastCases ?_ (fun j => ?_) i
    · simp
    · simp
  right_inv p := by
    rcases p with ⟨v,s⟩
    simp

theorem lastCheckpoint_le {m : ℕ} (v : Code m) :
    ∀ j (hj : j ≤ m), lastCheckpoint v j hj ≤ j := by
  intro j
  induction j with
  | zero => intro hj; simp [lastCheckpoint]
  | succ j ih =>
      intro hj
      cases hs : v ⟨j,by omega⟩ with
      | none => simpa [lastCheckpoint,hs] using Nat.le_succ_of_le (ih (by omega))
      | some s => simp [lastCheckpoint,hs]

theorem lastCheckpoint_snoc_prefix {m : ℕ} (v : Code m) (s : Symbol) :
    ∀ j (hj : j ≤ m),
      lastCheckpoint (Fin.snoc v s) j (by omega)=lastCheckpoint v j hj := by
  intro j
  induction j with
  | zero => intro hj; rfl
  | succ j ih =>
      intro hj
      have he : (⟨j,by omega⟩ : Fin (m+1))=(⟨j,by omega⟩ : Fin m).castSucc := rfl
      simp only [lastCheckpoint,he,Fin.snoc_castSucc]
      cases v ⟨j,by omega⟩ with
      | none => exact ih (by omega)
      | some side => rfl

theorem lastCheckpoint_snoc {m : ℕ} (v : Code m) (s : Symbol) :
    lastCheckpoint (Fin.snoc v s) (m+1) le_rfl=
      match s with | none => lastCheckpoint v m le_rfl | some _ => m+1 := by
  have he : (⟨m,by omega⟩ : Fin (m+1))=Fin.last m := rfl
  simp only [lastCheckpoint,he,Fin.snoc_last]
  cases s with
  | none => exact lastCheckpoint_snoc_prefix v none m le_rfl
  | some side => rfl

/-- Weighted last-checkpoint enumeration; the zero code contributes once. -/
theorem sum_codes_by_last_checkpoint (m : ℕ) (f : ℕ → ℕ) :
    (∑ v : Code m, f (lastCheckpoint v m le_rfl))=
      f 0+2*∑ b ∈ Finset.range m, 3^b*f (b+1) := by
  induction m with
  | zero => simp [Code,lastCheckpoint]
  | succ m ih =>
      rw [← (codeSnocEquiv m).symm.sum_comp]
      simp only [codeSnocEquiv,Equiv.coe_fn_symm_mk,Fintype.sum_prod_type,
        lastCheckpoint_snoc]
      simp only [Symbol,Side,Fintype.sum_option,Fintype.sum_bool]
      simp only [Finset.sum_add_distrib,Finset.sum_const,Finset.card_univ,
        card_code,smul_eq_mul]
      rw [ih,Finset.sum_range_succ]
      ring

/-- C2: each positive last checkpoint has two sides and an arbitrary prefix. -/
theorem card_codes_by_last_checkpoint (m b : ℕ) :
    Nat.card {v : Code m // lastCheckpoint v m le_rfl=b}=
      if b=0 then 1 else if b ≤ m then 2*3^(b-1) else 0 := by
  classical
  rw [Nat.card_eq_fintype_card,Fintype.card_subtype]
  have hcard : (∑ v : Code m, if lastCheckpoint v m le_rfl=b then 1 else 0)=
      ({v : Code m | lastCheckpoint v m le_rfl=b} : Finset (Code m)).card := by simp
  rw [← hcard]
  rw [sum_codes_by_last_checkpoint m (fun j => if j=b then 1 else 0)]
  by_cases hb : b=0
  · subst b
    simp
  · by_cases hbm : b ≤ m
    · obtain ⟨a,rfl⟩ := Nat.exists_eq_succ_of_ne_zero hb
      have ha : a < m := by omega
      have hsum : (∑ j ∈ Finset.range m, 3^j*(if j+1=a+1 then 1 else 0))=3^a := by
        simp [ha]
      simp only [Nat.succ_eq_add_one,Nat.zero_ne_add_one,if_false,hsum,
        Nat.add_sub_cancel,zero_add,hbm,if_true,Nat.add_one_ne_zero]
    · have hz : (∑ j ∈ Finset.range m, 3^j*(if j+1=b then 1 else 0))=0 := by
        apply Finset.sum_eq_zero
        intro j hj
        have hne : j+1 ≠ b := by have := Finset.mem_range.mp hj; omega
        simp [hne]
      simp only [hb,Ne.symm hb,hbm,if_false,hz,mul_zero,add_zero]

end ProperArc.Chains
