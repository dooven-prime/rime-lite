import Paper44.TerminalPrefixEncoding
import RegisteredAbsorptionChains.ActualFiberNormalForm
import RegisteredAbsorptionChains.OriginClassification

/-! # Exact decoder interfaces for terminal prefix labels

These lemmas connect sparse checkpoints to complete ordered fusion records.
In particular a retained prefix is itself an exact decoded sparse code,
not just a list with the same checkpoint sizes.
-/

namespace Paper44

open RegisteredAbsorptionChains

def prefixSupport {N : ℕ} (c : Code N) (k : ℕ) : Finset (Fin N) :=
  (support c).filter (fun i => i.val < k)

theorem prefixSupport_succ {N : ℕ} (c : Code N) (k : ℕ) (hk : k < N) :
    prefixSupport c (k + 1) =
      if c ⟨k, hk⟩ = none then prefixSupport c k
      else insert ⟨k, hk⟩ (prefixSupport c k) := by
  classical
  ext i
  by_cases hi : i.val = k
  · have hieq : i = ⟨k, hk⟩ := Fin.ext hi
    subst i
    by_cases hc : c ⟨k, hk⟩ = none <;> simp [prefixSupport, support, hc]
  · by_cases hc : c ⟨k, hk⟩ = none <;>
      simp [prefixSupport, support, hc, Fin.ext_iff, hi]
    all_goals omega

variable {n : ℕ} [NeZero n]

theorem decodePrefix_length (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∀ k (hk : k ≤ n - 2),
      (decodeCodePrefix c hn k hk).chain.length = (prefixSupport c k).card := by
  intro k
  induction k with
  | zero => intro hk; simp [decodeCodePrefix, DecodedCodePrefix.initial, prefixSupport]
  | succ k ih =>
      intro hk
      have hk' : k < n - 2 := by omega
      rw [prefixSupport_succ c k hk']
      have hnot : (⟨k, hk'⟩ : Fin (n - 2)) ∉ prefixSupport c k := by
        simp [prefixSupport]
      cases hc : c ⟨k, hk'⟩ with
      | none => simpa [decodeCodePrefix, DecodedCodePrefix.advance, hc] using ih (by omega)
      | some side =>
          cases side <;> simp [decodeCodePrefix, DecodedCodePrefix.advance, hc,
            Finset.card_insert_of_notMem hnot, ih]

theorem decodeChain_length (c : Code (n - 2)) (hn : 2 ≤ n) :
    (decodeChain c hn).length = (support c).card := by
  have hp : prefixSupport c (n - 2) = support c := by
    ext i; simp [prefixSupport]
  simpa [decodeChain, decodeCode, hp] using decodePrefix_length c hn (n - 2) (le_refl _)

def truncateCode (c : Code (n - 2)) (k : ℕ) : Code (n - 2) :=
  fun i => if i.val < k then c i else none

theorem decodeChain_truncate (c : Code (n - 2)) (hn : 2 ≤ n)
    (k : ℕ) (hk : k ≤ n - 2) :
    decodeChain (truncateCode c k) hn = (decodeCodePrefix c hn k hk).chain := by
  have hc := decodeCodePrefix_congr (truncateCode c k) c hn k hk (by
    intro i hi; simp [truncateCode, hi])
  have hs := decodeCodePrefix_skip (truncateCode c k) hn k hk (n - 2)
    (le_refl _) hk (by intro i hi _; simp [truncateCode, show ¬ i.val < k by omega])
  exact hs.2.trans (congrArg DecodedCodePrefix.chain hc)

/-- Taking records stops at an actual checkpoint; it never splits an event. -/
theorem decoded_take_is_prefix (c : Code (n - 2)) (hn : 2 ≤ n) (depth : ℕ) :
    ∀ k (hk : k ≤ n - 2), ∃ (l : ℕ) (hl : l ≤ n - 2),
      (decodeCodePrefix c hn l hl).chain =
        ((decodeCodePrefix c hn k hk).chain).take depth := by
  intro k
  induction k with
  | zero => intro hk; exact ⟨0, by omega, by simp [decodeCodePrefix, DecodedCodePrefix.initial]⟩
  | succ k ih =>
      intro hk
      have hk' : k ≤ n - 2 := by omega
      let i : Fin (n - 2) := ⟨k, by omega⟩
      cases hc : c i with
      | none => simpa [decodeCodePrefix, DecodedCodePrefix.advance, i, hc] using ih hk'
      | some side =>
          by_cases hdepth : depth ≤ (decodeCodePrefix c hn k hk').chain.length
          · obtain ⟨l, hl, htake⟩ := ih hk'
            refine ⟨l, hl, ?_⟩
            cases side <;> simpa [decodeCodePrefix, DecodedCodePrefix.advance,
              i, hc, List.take_append_of_le_length hdepth] using htake
          · refine ⟨k + 1, hk, (List.take_of_length_le ?_).symm⟩
            cases side <;> simp [decodeCodePrefix, DecodedCodePrefix.advance, i, hc]
            all_goals omega

theorem take_decodeChain_in_range (c : Code (n - 2)) (hn : 2 ≤ n) (depth : ℕ) :
    ∃ d : Code (n - 2), decodeChain d hn = (decodeChain c hn).take depth := by
  obtain ⟨l, hl, heq⟩ := decoded_take_is_prefix c hn depth (n - 2) (le_refl _)
  exact ⟨truncateCode c l, (decodeChain_truncate c hn l hl).trans heq⟩

def lastCheckpoint (hn : 3 ≤ n) : Fin (n - 2) := ⟨n - 3, by omega⟩

theorem decodePrefix_index (c : Code (n - 2)) (hn : 2 ≤ n)
    {a b : ℕ} (ha : a ≤ n - 2) (hb : b ≤ n - 2) (hab : a = b) :
    (decodeCodePrefix c hn a ha).frontier.absorbed =
      (decodeCodePrefix c hn b hb).frontier.absorbed := by
  subst b
  rfl

theorem decodePrefix_chain_index (c : Code (n - 2)) (hn : 2 ≤ n)
    {a b : ℕ} (ha : a ≤ n - 2) (hb : b ≤ n - 2) (hab : a = b) :
    (decodeCodePrefix c hn a ha).chain = (decodeCodePrefix c hn b hb).chain := by
  subst b
  rfl

/-- An unfinished prefix can be completed by one event at the last checkpoint.
The old complete ordered records are retained literally. -/
theorem complete_sparse_prefix (c : Code (n - 2)) (hn : 3 ≤ n)
    (hc : c (lastCheckpoint hn) = none) :
    ∃ (d : Code (n - 2)) (rho : FusionRecord (ZMod n)),
      d (lastCheckpoint hn) ≠ none ∧
        decodeChain d (by omega) = decodeChain c (by omega) ++ [rho] := by
  let hn2 : 2 ≤ n := by omega
  let d := Function.update c (lastCheckpoint hn) (some false)
  have hd : d (lastCheckpoint hn) = some false := by simp [d]
  have hprior := decodeCodePrefix_congr d c hn2 (n - 3) (by omega) (by
    intro i hi
    have hne : i ≠ lastCheckpoint hn := by
      intro h; have heq := congrArg Fin.val h; simp [lastCheckpoint] at heq; omega
    simp [d, Function.update_of_ne hne])
  have hN : n - 2 = n - 3 + 1 := by omega
  have hcstep := decodePrefix_chain_index c hn2 (le_refl _) (by omega) hN
  have hdstep := decodePrefix_chain_index d hn2 (le_refl _) (by omega) hN
  simp only [decodeCodePrefix, DecodedCodePrefix.advance] at hcstep hdstep
  rw [show c ⟨n - 3, by omega⟩ = none from hc] at hcstep
  rw [show d ⟨n - 3, by omega⟩ = some false from hd] at hdstep
  simp only at hcstep hdstep
  rw [hprior] at hdstep
  let f := (decodeCodePrefix c hn2 (n - 3) (by omega)).frontier
  let rho := checkpointRecord false f.carrier (f.partnerL (n - 3 + 1 - f.absorbed))
  refine ⟨d, rho, by simp [hd], ?_⟩
  exact hdstep.trans (congrArg (· ++ [rho]) hcstep.symm)

theorem decodedCarrier_full_iff_last (c : Code (n - 2)) (hn : 3 ≤ n) :
    decodedCarrier c (by omega) = (Finset.univ : Finset (ZMod n)) ↔
      c (lastCheckpoint hn) ≠ none := by
  let hn2 : 2 ≤ n := by omega
  have hcard := (decodeCode c hn2).frontier.carrier_card
  have habs := decodeCodePrefix_absorbed c hn2 (n - 2) (le_refl _)
  have hN : n - 2 = (n - 3) + 1 := by omega
  cases hc : c (lastCheckpoint hn) with
  | none =>
      have hbound := (decodeCodePrefix c hn2 (n - 3) (by omega)).bound
      have heq : (decodeCode c hn2).frontier.absorbed =
          (decodeCodePrefix c hn2 (n - 3) (by omega)).frontier.absorbed := by
        have heq' : (decodeCodePrefix c hn2 (n - 3 + 1) (by omega)).frontier.absorbed =
            (decodeCodePrefix c hn2 (n - 3) (by omega)).frontier.absorbed := by
          simp only [decodeCodePrefix, DecodedCodePrefix.advance]
          rw [show c ⟨n - 3, by omega⟩ = none from hc]
        exact (decodePrefix_index c hn2 (le_refl _) (by omega) hN).trans heq'
      constructor
      · intro hfull
        have hsize := congrArg Finset.card hfull
        simp only [Finset.card_univ, ZMod.card] at hsize
        change ((decodeCode c hn2).frontier.carrier).card = n at hsize
        omega
      · simp
  | some side =>
      have ha : (decodeCode c hn2).frontier.absorbed = n - 2 := by
        have ha' := decodeCodePrefix_absorbed c hn2 (n - 3 + 1) (by omega)
        simp only [lastCodeCheckpoint] at ha'
        rw [show c ⟨n - 3, by omega⟩ = some side from hc] at ha'
        exact (decodePrefix_index c hn2 (le_refl _) (by omega) hN).trans (by simpa [hN] using ha')
      constructor
      · intro _; simp
      · intro _
        apply Finset.eq_univ_of_card
        simpa [decodedCarrier, ha, ZMod.card, Nat.sub_add_cancel (by omega : 2 ≤ n)] using hcard

end Paper44
