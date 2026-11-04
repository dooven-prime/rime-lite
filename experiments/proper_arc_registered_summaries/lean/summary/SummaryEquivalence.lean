import summary.SummaryTypes

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem encodeSummary_placement_readback (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    (codePlacementFibreEquiv c hr (encodeSummary c hr s).1 (encodeSummary c hr s).2.1
      (encodeSummary c hr s).2.2).val=s.val.placed := by
  change ((codePlacementFibreEquiv c hr (summaryOriginIndex c hr s) (encodeChain c r s.val.chain))
    ((codePlacementFibreEquiv c hr (summaryOriginIndex c hr s) (encodeChain c r s.val.chain)).symm
      (summaryPlacementInFibre c hr s))).val=s.val.placed
  rw [Equiv.apply_symm_apply]
  rfl

/-- Decoding the recovered dependent tuple restores all three literal fields
of the very same actual summary. -/
theorem decodeSummary_encodeSummary (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) : decodeSummary c hr (encodeSummary c hr s)=s := by
  apply Subtype.ext
  apply execution_ext_fields
  · exact encodeSummary_placement_readback c hr s
  · exact (summaryOriginIndex_spec c hr s).symm
  · exact (summaryCode_spec c hr s).symm

/-- Origin, full selected records and literal terminal placement successively
identify the origin index, code and code-dependent placement parameter. -/
theorem decodeSummary_injective (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n) :
    Function.Injective (decodeSummary c hr) := by
  rintro ⟨t,v,p⟩ ⟨u,w,q⟩ h
  have hs := congrArg Subtype.val h
  have ho : some (originRecord c r (t.val+1))=some (originRecord c r (u.val+1)) :=
    congrArg Execution.origin hs
  have htu : t=u := originRecord_injective c r hr.2.le (Option.some.inj ho)
  subst u
  have hc : decodeChain c ⟨hr.1,hr.2.le⟩ v=decodeChain c ⟨hr.1,hr.2.le⟩ w :=
    congrArg Execution.chain hs
  have hvw : v=w := decodeChain_injective c ⟨hr.1,hr.2.le⟩ hc
  subst w
  have hP : codePlacementFibreEquiv c hr t v p=codePlacementFibreEquiv c hr t v q :=
    Subtype.ext (congrArg Execution.placed hs)
  have hpq := (codePlacementFibreEquiv c hr t v).injective hP
  subst q
  rfl

theorem encodeSummary_decodeSummary (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) : encodeSummary c hr (decodeSummary c hr p)=p := by
  apply decodeSummary_injective c hr
  exact decodeSummary_encodeSummary c hr (decodeSummary c hr p)

/-- Theorem 5.3, with the fixed F carried as a type index. This is an
equivalence of actual summaries, not of execution words or sample states. -/
noncomputable def actualRegisteredSummariesEquivParams (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) : ActualRegisteredSummaries c r ≃ SummaryParams ⟨hr.1,hr.2.le⟩ where
  toFun := encodeSummary c hr
  invFun := decodeSummary c hr
  left_inv := decodeSummary_encodeSummary c hr
  right_inv := encodeSummary_decodeSummary c hr

theorem actualRegisteredSummariesEquivParams_apply (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (s : ActualRegisteredSummaries c r) :
    actualRegisteredSummariesEquivParams c hr s=encodeSummary c hr s := rfl

theorem actualRegisteredSummariesEquivParams_symm (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (p : SummaryParams ⟨hr.1,hr.2.le⟩) :
    (actualRegisteredSummariesEquivParams c hr).symm p=decodeSummary c hr p := rfl

theorem actualSummary_unique_params (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    ∃! p : SummaryParams ⟨hr.1,hr.2.le⟩, decodeSummary c hr p=s := by
  refine ⟨encodeSummary c hr s,decodeSummary_encodeSummary c hr s,?_⟩
  intro p hp
  exact decodeSummary_injective c hr (hp.trans (decodeSummary_encodeSummary c hr s).symm)

/-- One actual chronological word jointly realizes the origin, complete
ordered selected chain and literal placement read from the parameter tuple. -/
theorem decodeSummary_same_word (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) :
    ∃ word : List Letter,
      let s := run (arc c r) (singletonExecution n) word
      s=(decodeSummary c hr p).val ∧
      s.origin=some (originRecord c r (p.1.val+1)) ∧
      s.chain=decodeChain c ⟨hr.1,hr.2.le⟩ p.2.1 ∧
      s.placed=(codePlacementFibreEquiv c hr p.1 p.2.1 p.2.2).val := by
  obtain ⟨word,hw,_⟩ := (decodeSummary c hr p).property
  refine ⟨word,?_⟩
  dsimp only
  rw [hw]
  exact ⟨rfl,decodeSummary_origin c hr p,decodeSummary_chain c hr p,decodeSummary_placed c hr p⟩

end ProperArc.Chains
