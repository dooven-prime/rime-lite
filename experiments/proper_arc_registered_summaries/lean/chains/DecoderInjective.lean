import chains.Decoder

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- One record exposes the new carrier size relative to the proper source arc,
and whether its old carrier occupied the left port. -/
def recordKey (r : ℕ) (rho : FusionRecord (ZMod n)) : ℕ × Bool :=
  (rho.result.card-r, 0 ∈ rho.left)

theorem recordKey_R (f : CheckpointSourceFrontier n) (r b : ℕ)
    (hr : 2 ≤ r) (hnext : f.absorbed < r-2+b) (hmax : r-2+b ≤ n-2) :
    recordKey r (checkpointRecord true f.carrier (f.partnerR (r-2+b-f.absorbed))) =
      (b, true) := by
  have hk := f.checkpointKey_R (r-2+b) hnext hmax
  have hc := (f.nextR _ (f.checkpoint_gap _ hnext hmax).2).carrier_card
  rw [f.nextR_checkpoint _ hnext hmax] at hc
  rw [f.carrier_nextR] at hc
  apply Prod.ext
  · change (f.carrier ∪ f.partnerR _).card-r = b
    omega
  · simpa only [recordKey, checkpointKey] using congrArg (fun p : ℕ × Bool => p.2) hk

theorem recordKey_L (f : CheckpointSourceFrontier n) (r b : ℕ)
    (hr : 2 ≤ r) (hnext : f.absorbed < r-2+b) (hmax : r-2+b ≤ n-2) :
    recordKey r (checkpointRecord false f.carrier (f.partnerL (r-2+b-f.absorbed))) =
      (b, false) := by
  have hk := f.checkpointKey_L (r-2+b) hnext hmax
  have hc := (f.nextL _ (f.checkpoint_gap _ hnext hmax).2).carrier_card
  rw [f.nextL_checkpoint _ hnext hmax] at hc
  rw [f.carrier_nextL] at hc
  apply Prod.ext
  · change (f.partnerL _ ∪ f.carrier).card-r = b
    rw [Finset.union_comm]
    omega
  · simpa only [recordKey, checkpointKey] using congrArg (fun p : ℕ × Bool => p.2) hk

omit [NeZero n] in
def keys {m : ℕ} (v : Code m) (j : ℕ) (hj : j ≤ m) : List (ℕ × Bool) :=
  codeKeysPrefix (n := m+2) (fun i => v ⟨i.val, by have := i.isLt; omega⟩) j (by omega)

omit [NeZero n] in
theorem keys_zero {m : ℕ} (v : Code m) : keys v 0 (by omega) = [] := rfl

omit [NeZero n] in
theorem keys_succ {m : ℕ} (v : Code m) (j : ℕ) (hj : j+1 ≤ m) :
    keys v (j+1) hj = keys v j (by omega) ++
      (match v ⟨j, by omega⟩ with | none => [] | some side => [(j+1, side)]) := by
  unfold keys
  rw [codeKeysPrefix]
  split <;> simp_all

omit [NeZero n] in
theorem keys_injective {m : ℕ} (v w : Code m)
    (h : keys v m le_rfl = keys w m le_rfl) : v = w := by
  funext i
  have hm : m+2-2=m := by omega
  unfold keys at h
  have hfull : codeKeysPrefix (n := m+2)
      (fun j => v ⟨j.val, by have := j.isLt; omega⟩) (m+2-2) le_rfl =
    codeKeysPrefix (n := m+2)
      (fun j => w ⟨j.val, by have := j.isLt; omega⟩) (m+2-2) le_rfl := by
    simpa only [hm] using h
  have heq := codeKeysPrefix_injective _ _ hfull
  exact congrFun heq ⟨i.val, by have := i.isLt; omega⟩

theorem decodePrefix_keys {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    ∀ j (hj : j ≤ n-r),
      (decodePrefix hr v j hj).chain.map (recordKey r) = keys v j hj := by
  intro j
  induction j with
  | zero => intro hj; rfl
  | succ j ih =>
      intro hj
      let i : Fin (n-r) := ⟨j, by omega⟩
      let f := (decodePrefix hr v j (by omega)).frontier
      have hnext : f.absorbed < r-2+(j+1) := by
        have := (decodePrefix hr v j (by omega)).bound
        dsimp [f]; omega
      have hmax : r-2+(j+1) ≤ n-2 := by omega
      rw [keys_succ]
      cases hs : v i with
      | none => simpa [decodePrefix, Prefix.advance, i, hs] using ih (by omega)
      | some side =>
          cases side with
          | false =>
              simpa [decodePrefix, Prefix.advance, i, hs, f, List.map_append, Nat.add_assoc] using
                And.intro (ih (by omega)) (recordKey_L f r (j+1) hr.1 hnext hmax)
          | true =>
              simpa [decodePrefix, Prefix.advance, i, hs, f, List.map_append, Nat.add_assoc] using
                And.intro (ih (by omega)) (recordKey_R f r (j+1) hr.1 hnext hmax)

theorem decodeCanonicalChain_injective {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) :
    Function.Injective (decodeCanonicalChain hr) := by
  intro v w h
  apply keys_injective
  rw [← decodePrefix_keys hr v, ← decodePrefix_keys hr w]
  exact congrArg (List.map (recordKey r)) h

end ProperArc.Chains
