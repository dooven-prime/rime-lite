import converse.ActualTrace

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem keys_mem_iff {m : ℕ} (v : Code m) (i : Fin m) (side : Bool) :
    (i.val+1, side) ∈ keys v m le_rfl ↔ v i=some side := by
  let i' : Fin (m+2-2) := ⟨i.val, by have := i.isLt; omega⟩
  simpa [keys, i'] using codeKeysPrefix_mem_iff (n := m+2)
    (fun j => v ⟨j.val, by have := j.isLt; omega⟩) m (by omega) i' i.isLt side

omit [NeZero n] in
theorem keys_bounds {m : ℕ} (v : Code m) : ∀ j (hj : j ≤ m) (key : ℕ × Bool),
    key ∈ keys v j hj → 1 ≤ key.1 ∧ key.1 ≤ j := by
  intro j
  induction j with
  | zero => intro hj key h; simp [keys_zero] at h
  | succ j ih =>
      intro hj key h
      rw [keys_succ] at h
      cases hs : v ⟨j, by omega⟩ with
      | none =>
          have hprior : key ∈ keys v j (by omega) := by simpa [hs] using h
          have hb := ih (by omega) key hprior
          exact ⟨hb.1, by omega⟩
      | some side =>
          have hcases : key ∈ keys v j (by omega) ∨ key=(j+1,side) := by simpa [hs] using h
          rcases hcases with hprior | rfl
          · have hb := ih (by omega) key hprior
            exact ⟨hb.1, by omega⟩
          · simp

omit [NeZero n] in
theorem keys_strict {m : ℕ} (v : Code m) : ∀ j (hj : j ≤ m),
    List.Pairwise (fun a b : ℕ × Bool => a.1 < b.1) (keys v j hj) := by
  intro j
  induction j with
  | zero => intro hj; simp [keys_zero]
  | succ j ih =>
      intro hj
      rw [keys_succ]
      cases hs : v ⟨j, by omega⟩ with
      | none => simpa [hs] using ih (by omega)
      | some side =>
          simp only [hs]
          apply List.pairwise_append.mpr
          refine ⟨ih (by omega), by simp, ?_⟩
          intro a ha b hb
          have hbeq : b=(j+1,side) := by simpa using hb
          subst b
          have hbound := keys_bounds v j (by omega) a ha
          exact lt_of_le_of_lt hbound.2 (Nat.lt_succ_self j)

/-- An explicit encoder reads only the actual records. Actual histories have
one key at each checkpoint; the first test detects the left-port carrier. -/
def encodeChain (c : ZMod n) (r : ℕ) (A : List (FusionRecord (ZMod n))) : Code (n-r) :=
  fun i => if (i.val+1,true) ∈ A.map (recordKeyAt c r) then some true
    else if (i.val+1,false) ∈ A.map (recordKeyAt c r) then some false else none

theorem encodeChain_decodeChain (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) : encodeChain c r (decodeChain c hr v)=v := by
  funext i
  simp only [encodeChain, decodeChain_keys, keys_mem_iff]
  cases hv : v i with
  | none => simp
  | some side => cases side <;> simp

/-- The equality is of full ordered source-addressed records, including both
parents and their result, on an arbitrary registered actual history. -/
theorem actual_chain_decode_encode (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter)
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true) :
    decodeChain c ⟨hr.1, hr.2.le⟩
      (encodeChain c r (run (arc c r) (singletonExecution n) word).chain)=
      (run (arc c r) (singletonExecution n) word).chain := by
  obtain ⟨v, hv⟩ := actual_chain_in_decode_range c hr word registered
  rw [hv, encodeChain_decodeChain]

/-- The actual chronological checkpoint sequence is strictly increasing and
lies in `1,...,n-r`. Outside-only mergers need not be absent. -/
theorem actual_chain_checkpoint_strict (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter)
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true) :
    List.Pairwise (· < ·)
      ((run (arc c r) (singletonExecution n) word).chain.map (fun rho => rho.result.card-r)) ∧
    (∀ rho ∈ (run (arc c r) (singletonExecution n) word).chain,
      1 ≤ rho.result.card-r ∧ rho.result.card-r ≤ n-r) := by
  obtain ⟨v, hv⟩ := actual_chain_in_decode_range c hr word registered
  rw [hv]
  constructor
  · have hk := keys_strict v (n-r) le_rfl
    rw [← decodeChain_keys c ⟨hr.1, hr.2.le⟩ v] at hk
    simpa only [List.pairwise_map, recordKeyAt] using hk
  · intro rho hmem
    have hkey : recordKeyAt c r rho ∈ keys v (n-r) le_rfl := by
      rw [← decodeChain_keys c ⟨hr.1, hr.2.le⟩ v]
      exact List.mem_map.mpr ⟨rho, hmem, rfl⟩
    exact keys_bounds v (n-r) le_rfl (recordKeyAt c r rho) hkey

theorem actual_chain_unique_code (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (word : List Letter)
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true) :
    ∃! v : Code (n-r), (run (arc c r) (singletonExecution n) word).chain=
      decodeChain c ⟨hr.1, hr.2.le⟩ v := by
  refine ⟨encodeChain c r (run (arc c r) (singletonExecution n) word).chain,
    (actual_chain_decode_encode c hr word registered).symm, ?_⟩
  intro v hv
  rw [hv, encodeChain_decodeChain]

/-- The fixed-origin chain bijection uses the explicit encoder in its forward
map and the already frozen real-history embedding in its inverse map. -/
noncomputable def actualSelectedChainsEquivCode (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) :
    ActualSelectedChains c r (t.val+1) ≃ Code (n-r) where
  toFun A := encodeChain c r A.val
  invFun := codeEmbeddingActualSelectedChains c hr t
  left_inv A := by
    apply Subtype.ext
    obtain ⟨word, ho, hc⟩ := A.property
    have hreg : (run (arc c r) (singletonExecution n) word).origin.isSome=true := by rw [ho]; rfl
    simpa only [codeEmbeddingActualSelectedChains_val, hc] using
      actual_chain_decode_encode c hr word hreg
  right_inv v := encodeChain_decodeChain c ⟨hr.1, hr.2.le⟩ v

theorem actualSelectedChainsEquivCode_apply (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (A : ActualSelectedChains c r (t.val+1)) :
    actualSelectedChainsEquivCode c hr t A=encodeChain c r A.val := rfl

theorem actualSelectedChainsEquivCode_symm_val (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r)) :
    ((actualSelectedChainsEquivCode c hr t).symm v).val=decodeChain c ⟨hr.1, hr.2.le⟩ v := rfl

theorem card_actualSelectedChains (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) :
    Nat.card (ActualSelectedChains c r (t.val+1))=3^(n-r) := by
  rw [Nat.card_congr (actualSelectedChainsEquivCode c hr t), Nat.card_eq_fintype_card, card_code]

end ProperArc.Chains
