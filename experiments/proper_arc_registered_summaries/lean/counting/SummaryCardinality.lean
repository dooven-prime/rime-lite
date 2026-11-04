import summary.SummaryEquivalence
import counting.LastCheckpointCount

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

instance codeFiberParams_finite {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    Finite (CodeFiberParams hr v) := by
  unfold CodeFiberParams
  split_ifs <;> infer_instance

/-- C1: cardinality transport starts at actual registered seed histories. -/
theorem card_summary_sigma (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) :
    Nat.card (ActualRegisteredSummaries c r)=
      ∑ _t : Fin (r-1), ∑ v : Code (n-r),
        Nat.card (CodeFiberParams ⟨hr.1,hr.2.le⟩ v) := by
  rw [Nat.card_congr (actualRegisteredSummariesEquivParams c hr)]
  simp only [SummaryParams,Nat.card_sigma]

/-- The inherited actual-fibre count also covers the independent k=0 phase branch. -/
theorem card_code_fibre (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r)) :
    Nat.card (CodeFiberParams ⟨hr.1,hr.2.le⟩ v)=
      n*(n+(n-r)-lastCheckpoint v (n-r) le_rfl-2).choose
        (n-r-lastCheckpoint v (n-r) le_rfl) := by
  rw [Nat.card_congr (codePlacementFibreEquiv c hr t v),card_actualCodePlacements,
    outsideCount_eq]
  have hb := lastCheckpoint_le v (n-r) le_rfl
  congr 2
  omega

/-- The endpoint layer b=m retains n single-packet phases for every code. -/
theorem card_code_fibre_full (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r))
    (hb : lastCheckpoint v (n-r) le_rfl=n-r) :
    Nat.card (CodeFiberParams ⟨hr.1,hr.2.le⟩ v)=n := by
  rw [card_code_fibre c hr t v,hb]
  simp

theorem sum_range_shift_Icc (m : ℕ) (f : ℕ → ℕ) :
    (∑ b ∈ Finset.range m, f (b+1))=∑ b ∈ Finset.Icc 1 m, f b := by
  rw [← Finset.Ico_add_one_right_eq_Icc,Finset.sum_Ico_eq_sum_range]
  simp [Nat.add_comm]

/-- C3: one origin's dependent fibres, grouped by their last checkpoint. -/
theorem card_code_fibre_sum (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) :
    (∑ v : Code (n-r), Nat.card (CodeFiberParams ⟨hr.1,hr.2.le⟩ v))=
      n*((n+(n-r)-2).choose (n-r)+
        2*∑ b ∈ Finset.Icc 1 (n-r),
          3^(b-1)*(n+(n-r)-b-2).choose (n-r-b)) := by
  simp_rw [card_code_fibre c hr t]
  rw [sum_codes_by_last_checkpoint (n-r)
    (fun b => n*(n+(n-r)-b-2).choose (n-r-b))]
  simp only [Nat.sub_zero]
  have hshift := sum_range_shift_Icc (n-r)
    (fun b => 3^(b-1)*(n+(n-r)-b-2).choose (n-r-b))
  simp only [Nat.add_sub_cancel] at hshift
  rw [show (∑ b ∈ Finset.range (n-r),
      3^b*(n*(n+(n-r)-(b+1)-2).choose (n-r-(b+1))))=
      n*∑ b ∈ Finset.range (n-r),
        3^b*(n+(n-r)-(b+1)-2).choose (n-r-(b+1)) by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro b hb
    ring]
  rw [hshift]
  ring

/-- Theorem 6.1: complete actual registered summaries, for every proper arc. -/
theorem card_actual_registered_summaries (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) :
    Nat.card (ActualRegisteredSummaries c r)=
      (r-1)*n*((n+(n-r)-2).choose (n-r)+
        2*∑ b ∈ Finset.Icc 1 (n-r),
          3^(b-1)*(n+(n-r)-b-2).choose (n-r-b)) := by
  rw [card_summary_sigma c hr]
  simp_rw [card_code_fibre_sum c hr ⟨0,by omega⟩]
  simp only [Finset.sum_const,Finset.card_univ,Fintype.card_fin,smul_eq_mul]
  ring

/-- Shortest nonempty complement: m=1, including both L/R full-carrier codes. -/
theorem card_actual_registered_summaries_short_complement (c : ZMod n) (hn : 3 ≤ n) :
    Nat.card (ActualRegisteredSummaries c (n-1))=(n-2)*n*(n+1) := by
  have hr : 2 ≤ n-1 ∧ n-1 < n := by omega
  rw [card_actual_registered_summaries c hr]
  have hm : n-(n-1)=1 := by omega
  have hcut : n-1-1=n-2 := by omega
  have htop : n+1-2=n-1 := by omega
  simp only [hm,hcut,htop,Finset.Icc_self,Finset.sum_singleton,Nat.sub_self,
    pow_zero,Nat.choose_zero_right,Nat.choose_one_right,one_mul]
  have hbracket : n-1+2*1=n+1 := by omega
  rw [hbracket]

end ProperArc.Chains
