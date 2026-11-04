import fibres.PlacementEquivalence

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- F is the fixed type index. All remaining summary fields come from one
complete actual singleton-seed execution, with a registered origin. -/
def ActualRegisteredSummaries (c : ZMod n) (r : ℕ) :=
  {s : Execution n (ZMod n) // ∃ word : List Letter,
    run (arc c r) (singletonExecution n) word=s ∧ s.origin.isSome=true}

/-- Origin index, ternary code and its dependent native placement parameter.
There is no reachability requirement on the parameter side. -/
def SummaryParams {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) :=
  (_ : Fin (r-1)) × (v : Code (n-r)) × CodeFiberParams hr v

theorem execution_ext_fields (s z : Execution n (ZMod n))
    (placed : s.placed=z.placed) (origin : s.origin=z.origin) (chain : s.chain=z.chain) : s=z := by
  cases s
  cases z
  simp_all only [Execution.mk.injEq]

theorem actualSummary_reachable (c : ZMod n) (r : ℕ) (s : ActualRegisteredSummaries c r) :
    ReachableExecution (arc c r) s.val := by
  obtain ⟨word,hw,_⟩ := s.property
  exact ⟨word,hw⟩

theorem actualSummary_registered (c : ZMod n) (r : ℕ) (s : ActualRegisteredSummaries c r) :
    s.val.origin.isSome=true := by
  obtain ⟨_,_,hreg⟩ := s.property
  exact hreg

theorem summary_origin_unique (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    ∃! t : Fin (r-1), s.val.origin=some (originRecord c r (t.val+1)) := by
  apply actual_registered_origin_unique c r s.val hr (actualSummary_reachable c r s)
  intro ho
  have hreg := actualSummary_registered c r s
  simp [ho] at hreg

noncomputable def summaryOriginIndex (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) : Fin (r-1) :=
  Classical.choose (summary_origin_unique c hr s).exists

theorem summaryOriginIndex_spec (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    s.val.origin=some (originRecord c r ((summaryOriginIndex c hr s).val+1)) :=
  Classical.choose_spec (summary_origin_unique c hr s).exists

theorem summaryCode_spec (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    s.val.chain=decodeChain c ⟨hr.1,hr.2.le⟩ (encodeChain c r s.val.chain) := by
  obtain ⟨word,hw,hreg⟩ := s.property
  have hregw : (run (arc c r) (singletonExecution n) word).origin.isSome=true := by rw [hw]; exact hreg
  have h := actual_chain_decode_encode c hr word hregw
  rw [hw] at h
  exact h.symm

def summaryPlacementInFibre (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) :
    ActualCodePlacements c hr (summaryOriginIndex c hr s) (encodeChain c r s.val.chain) := by
  refine ⟨s.val.placed,?_⟩
  obtain ⟨word,hw,_⟩ := s.property
  refine ⟨word,?_⟩
  dsimp only
  rw [hw]
  exact ⟨summaryOriginIndex_spec c hr s,summaryCode_spec c hr s,rfl⟩

noncomputable def decodeSummary (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) : ActualRegisteredSummaries c r := by
  let P := codePlacementFibreEquiv c hr p.1 p.2.1 p.2.2
  refine ⟨⟨P.val,some (originRecord c r (p.1.val+1)),decodeChain c ⟨hr.1,hr.2.le⟩ p.2.1⟩,?_⟩
  obtain ⟨word,ho,hc,hP⟩ := P.property
  exact ⟨word,execution_ext_fields _ _ hP ho hc,rfl⟩

theorem decodeSummary_origin (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) :
    (decodeSummary c hr p).val.origin=some (originRecord c r (p.1.val+1)) := rfl

theorem decodeSummary_chain (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) :
    (decodeSummary c hr p).val.chain=decodeChain c ⟨hr.1,hr.2.le⟩ p.2.1 := rfl

theorem decodeSummary_placed (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (p : SummaryParams ⟨hr.1,hr.2.le⟩) :
    (decodeSummary c hr p).val.placed=(codePlacementFibreEquiv c hr p.1 p.2.1 p.2.2).val := rfl

noncomputable def encodeSummary (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) : SummaryParams ⟨hr.1,hr.2.le⟩ :=
  ⟨summaryOriginIndex c hr s,encodeChain c r s.val.chain,
    (codePlacementFibreEquiv c hr (summaryOriginIndex c hr s) (encodeChain c r s.val.chain)).symm
      (summaryPlacementInFibre c hr s)⟩

theorem encodeSummary_origin (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) : (encodeSummary c hr s).1=summaryOriginIndex c hr s := rfl

theorem encodeSummary_code (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (s : ActualRegisteredSummaries c r) : (encodeSummary c hr s).2.1=encodeChain c r s.val.chain := rfl

end ProperArc.Chains
