import RegisteredAbsorptionChains.CleanCodeInduction
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem CheckpointSourceFrontier.carrier_eq_compl_remaining
    (f : CheckpointSourceFrontier n) : f.carrier = f.remainingᶜ := by
  ext a
  rw [Finset.mem_compl]
  have h := f.not_mem_carrier_iff_remaining a
  tauto

theorem CheckpointSourceFrontier.carrier_card
    (f : CheckpointSourceFrontier n) : f.carrier.card = f.absorbed + 2 := by
  rw [f.carrier_eq_compl_remaining, Finset.card_compl, f.remaining_card]
  have htotal := f.remaining_plus_absorbed
  rw [f.remaining_card] at htotal
  simp only [ZMod.card]
  have hn : 2 ≤ n := le_trans f.lo_valid (le_trans f.noncrossing f.hi_valid)
  have hlo := f.lo_valid
  have hmid := f.noncrossing
  have hhi := f.hi_valid
  omega

/-- The accumulated source size and the ordered parent port are observable
from one actual-format symbolic absorption record. -/
def checkpointKey (rho : FusionRecord (ZMod n)) : ℕ × Bool :=
  (rho.result.card - 2, 0 ∈ rho.left)

theorem CheckpointSourceFrontier.checkpointKey_R
    (f : CheckpointSourceFrontier n) (bNext : ℕ)
    (hnext : f.absorbed < bNext) (hmax : bNext ≤ n - 2) :
    checkpointKey (checkpointRecord true f.carrier
      (f.partnerR (bNext - f.absorbed))) = (bNext, true) := by
  have hgap := f.checkpoint_gap bNext hnext hmax
  have hcard : (f.carrier ∪ f.partnerR (bNext - f.absorbed)).card =
      bNext + 2 := by
    rw [← f.carrier_nextR (bNext - f.absorbed) hgap.2]
    rw [(f.nextR (bNext - f.absorbed) hgap.2).carrier_card,
      f.nextR_checkpoint bNext hnext hmax]
  have hzero : (0 : ZMod n) ∈ f.carrier := by
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  simp [checkpointKey, checkpointRecord, hcard, hzero]

theorem CheckpointSourceFrontier.checkpointKey_L
    (f : CheckpointSourceFrontier n) (bNext : ℕ)
    (hnext : f.absorbed < bNext) (hmax : bNext ≤ n - 2) :
    checkpointKey (checkpointRecord false f.carrier
      (f.partnerL (bNext - f.absorbed))) = (bNext, false) := by
  have hgap := f.checkpoint_gap bNext hnext hmax
  have hcard : (f.carrier ∪ f.partnerL (bNext - f.absorbed)).card =
      bNext + 2 := by
    rw [← f.carrier_nextL (bNext - f.absorbed) hgap.2]
    rw [(f.nextL (bNext - f.absorbed) hgap.2).carrier_card,
      f.nextL_checkpoint bNext hnext hmax]
  have hzero : (0 : ZMod n) ∈ f.carrier := by
    simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hnot : (0 : ZMod n) ∉ f.partnerL (bNext - f.absorbed) := by
    intro hmem
    exact Finset.disjoint_left.mp (f.partnerL_disjoint_carrier
      (bNext - f.absorbed) hgap.2) hmem hzero
  simp [checkpointKey, checkpointRecord, Finset.union_comm, hcard, hnot]

/-- The nonzero code positions, with their 1-based checkpoint number and
port orientation, in chronological order. -/
def codeKeysPrefix (c : Code (n - 2)) :
    (j : ℕ) → j ≤ n - 2 → List (ℕ × Bool)
  | 0, _ => []
  | j + 1, hj =>
      let prior := codeKeysPrefix c j (by omega)
      match c ⟨j, by omega⟩ with
      | none => prior
      | some side => prior ++ [(j + 1, side)]

theorem decodeCodePrefix_keys (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∀ (j : ℕ) (hj : j ≤ n - 2),
      (decodeCodePrefix c hn j hj).chain.map checkpointKey =
        codeKeysPrefix c j hj := by
  intro j
  induction j with
  | zero =>
      intro hj
      simp [decodeCodePrefix, codeKeysPrefix, DecodedCodePrefix.initial]
  | succ j ih =>
      intro hj
      have hj' : j ≤ n - 2 := by omega
      let f := (decodeCodePrefix c hn j hj').frontier
      let i : Fin (n - 2) := ⟨j, by omega⟩
      cases hsymbol : c i with
      | none =>
          simpa [decodeCodePrefix, DecodedCodePrefix.advance,
            codeKeysPrefix, i, hsymbol] using ih hj'
      | some side =>
          have hnext : f.absorbed < j + 1 := by
            have := (decodeCodePrefix c hn j hj').bound
            dsimp [f] at *
            omega
          cases side with
          | false =>
              simpa [decodeCodePrefix, DecodedCodePrefix.advance,
                codeKeysPrefix, i, hsymbol, List.map_append] using
                And.intro (ih hj') (f.checkpointKey_L (j + 1) hnext hj)
          | true =>
              simpa [decodeCodePrefix, DecodedCodePrefix.advance,
                codeKeysPrefix, i, hsymbol, List.map_append] using
                And.intro (ih hj') (f.checkpointKey_R (j + 1) hnext hj)

omit [NeZero n] in
theorem codeKeysPrefix_bound (c : Code (n - 2)) :
    ∀ (j : ℕ) (hj : j ≤ n - 2) (key : ℕ × Bool),
      key ∈ codeKeysPrefix c j hj → key.1 ≤ j := by
  intro j
  induction j with
  | zero =>
      intro hj key hmem
      simp [codeKeysPrefix] at hmem
  | succ j ih =>
      intro hj key hmem
      have hj' : j ≤ n - 2 := by omega
      let i : Fin (n - 2) := ⟨j, by omega⟩
      cases hsymbol : c i with
      | none =>
          have hprior : key ∈ codeKeysPrefix c j hj' := by
            simpa [codeKeysPrefix, i, hsymbol] using hmem
          have := ih hj' key hprior
          omega
      | some side =>
          have hcases : key ∈ codeKeysPrefix c j hj' ∨
              key = (j + 1, side) := by
            simpa [codeKeysPrefix, i, hsymbol] using hmem
          rcases hcases with hprior | rfl
          · have := ih hj' key hprior
            omega
          · simp

omit [NeZero n] in
theorem codeKeysPrefix_mem_iff (c : Code (n - 2)) :
    ∀ (j : ℕ) (hj : j ≤ n - 2) (i : Fin (n - 2))
      (_hi : i.val < j) (side : Bool),
      (i.val + 1, side) ∈ codeKeysPrefix c j hj ↔ c i = some side := by
  intro j
  induction j with
  | zero =>
      intro hj i hi side
      omega
  | succ j ih =>
      intro hj i hi side
      have hj' : j ≤ n - 2 := by omega
      let last : Fin (n - 2) := ⟨j, by omega⟩
      by_cases hbefore : i.val < j
      · cases hsymbol : c last with
        | none =>
            simpa [codeKeysPrefix, last, hsymbol] using
              ih hj' i hbefore side
        | some lastSide =>
            have hne : (i.val + 1, side) ≠ (j + 1, lastSide) := by
              intro heq
              have := congrArg Prod.fst heq
              omega
            simpa [codeKeysPrefix, last, hsymbol, hne] using
              ih hj' i hbefore side
      · have hlast : i.val = j := by omega
        have hieq : i = last := Fin.ext hlast
        rw [hieq]
        have hprior : (j + 1, side) ∉ codeKeysPrefix c j hj' := by
          intro hmem
          have hbound := codeKeysPrefix_bound c j hj' _ hmem
          omega
        cases hsymbol : c last with
        | none =>
            simp [codeKeysPrefix, last, hsymbol, hprior]
        | some lastSide =>
            simp [codeKeysPrefix, last, hsymbol, hprior,
              Prod.mk.injEq]
            exact ⟨Eq.symm, Eq.symm⟩

omit [NeZero n] in
theorem codeKeysPrefix_injective (c₁ c₂ : Code (n - 2))
    (hkeys : codeKeysPrefix c₁ (n - 2) (le_refl _) =
      codeKeysPrefix c₂ (n - 2) (le_refl _)) : c₁ = c₂ := by
  funext i
  have hsame (side : Bool) : c₁ i = some side ↔ c₂ i = some side := by
    constructor
    · intro hc
      have hmem := (codeKeysPrefix_mem_iff c₁ (n - 2) (le_refl _)
        i i.isLt side).mpr hc
      rw [hkeys] at hmem
      exact (codeKeysPrefix_mem_iff c₂ (n - 2) (le_refl _)
        i i.isLt side).mp hmem
    · intro hc
      have hmem := (codeKeysPrefix_mem_iff c₂ (n - 2) (le_refl _)
        i i.isLt side).mpr hc
      rw [← hkeys] at hmem
      exact (codeKeysPrefix_mem_iff c₁ (n - 2) (le_refl _)
        i i.isLt side).mp hmem
  cases h₁ : c₁ i with
  | none =>
      cases h₂ : c₂ i with
      | none => rfl
      | some side =>
          have hcontra := (hsame side).mpr h₂
          simp [h₁] at hcontra
  | some side =>
      exact ((hsame side).mp h₁).symm

/-- Distinct ternary codes have distinct ordered source-addressed chains.
Each event exposes its cumulative absorbed count and its carrier port, so
forgetting zero positions does not identify different codes. -/
theorem decodeChain_injective (hn : 2 ≤ n) :
    Function.Injective (fun c : Code (n - 2) => decodeChain c hn) := by
  intro c₁ c₂ hchain
  have hkeys : codeKeysPrefix c₁ (n - 2) (le_refl _) =
      codeKeysPrefix c₂ (n - 2) (le_refl _) := by
    calc
      codeKeysPrefix c₁ (n - 2) (le_refl _) =
          (decodeCode c₁ hn).chain.map checkpointKey :=
        (decodeCodePrefix_keys c₁ hn (n - 2) (le_refl _)).symm
      _ = (decodeCode c₂ hn).chain.map checkpointKey :=
        congrArg (List.map checkpointKey) hchain
      _ = codeKeysPrefix c₂ (n - 2) (le_refl _) :=
        decodeCodePrefix_keys c₂ hn (n - 2) (le_refl _)
  exact codeKeysPrefix_injective c₁ c₂ hkeys

end RegisteredAbsorptionChains
