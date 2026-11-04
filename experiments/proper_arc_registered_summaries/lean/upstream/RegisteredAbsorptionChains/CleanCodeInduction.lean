import RegisteredAbsorptionChains.CheckpointPartnerAdmission
import RegisteredAbsorptionChains.CombinatorialCore
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The pure code decoder retains the source frontier and the ordered records
in one state. Its bound says that the last consumed checkpoint lies in the
processed prefix. -/
structure DecodedCodePrefix (n j : ℕ) [NeZero n] where
  frontier : CheckpointSourceFrontier n
  chain : List (FusionRecord (ZMod n))
  bound : frontier.absorbed ≤ j

def DecodedCodePrefix.initial (n : ℕ) [NeZero n] (hn : 2 ≤ n) :
    DecodedCodePrefix n 0 where
  frontier := ⟨2, n, by omega, by omega, le_refl n⟩
  chain := []
  bound := by simp [CheckpointSourceFrontier.absorbed]

/-- Zero symbols keep the frontier; a nonzero symbol consumes all source
addresses since the previous checkpoint in one ordered absorption record. -/
def DecodedCodePrefix.advance (c : Code (n - 2))
    (i : Fin (n - 2)) (x : DecodedCodePrefix n i.val) :
    DecodedCodePrefix n (i.val + 1) := by
  match c i with
  | none =>
      exact ⟨x.frontier, x.chain, Nat.le_succ_of_le x.bound⟩
  | some side =>
      let f := x.frontier
      let bNext := i.val + 1
      have hnext : f.absorbed < bNext := by
        have hbound : f.absorbed ≤ i.val := x.bound
        dsimp [bNext]
        omega
      have hmax : bNext ≤ n - 2 := by have := i.isLt; dsimp [bNext]; omega
      let ell := bNext - f.absorbed
      let hgap := (f.checkpoint_gap bNext hnext hmax).2
      cases side with
      | false =>
          exact ⟨f.nextL ell hgap,
            x.chain ++ [checkpointRecord false f.carrier (f.partnerL ell)],
            by simpa [f, ell, hgap, bNext] using
              (f.nextL_checkpoint bNext hnext hmax).le⟩
      | true =>
          exact ⟨f.nextR ell hgap,
            x.chain ++ [checkpointRecord true f.carrier (f.partnerR ell)],
            by simpa [f, ell, hgap, bNext] using
              (f.nextR_checkpoint bNext hnext hmax).le⟩

/-- Decode a prefix using the actual checkpoint indices, not merely their
number. A zero position is skipped; its index still advances. -/
def decodeCodePrefix (c : Code (n - 2)) (hn : 2 ≤ n) :
    (j : ℕ) → j ≤ n - 2 → DecodedCodePrefix n j
  | 0, _ => DecodedCodePrefix.initial n hn
  | j + 1, hj =>
      (decodeCodePrefix c hn j (by omega)).advance c ⟨j, by omega⟩

/-- The last nonzero checkpoint among the first `j` positions, or zero if
there has not been one. Code position `i` denotes absorbed count `i+1`. -/
def lastCodeCheckpoint (c : Code (n - 2)) :
    (j : ℕ) → j ≤ n - 2 → ℕ
  | 0, _ => 0
  | j + 1, hj =>
      match c ⟨j, by omega⟩ with
      | none => lastCodeCheckpoint c j (by omega)
      | some _ => j + 1

theorem decodeCodePrefix_absorbed (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∀ (j : ℕ) (hj : j ≤ n - 2),
      (decodeCodePrefix c hn j hj).frontier.absorbed =
        lastCodeCheckpoint c j hj := by
  intro j
  induction j with
  | zero =>
      intro hj
      simp [decodeCodePrefix, lastCodeCheckpoint,
        DecodedCodePrefix.initial, CheckpointSourceFrontier.absorbed]
  | succ j ih =>
      intro hj
      have hj' : j ≤ n - 2 := by omega
      let f := (decodeCodePrefix c hn j hj').frontier
      let i : Fin (n - 2) := ⟨j, by omega⟩
      cases hsymbol : c i with
      | none =>
          simpa [decodeCodePrefix, DecodedCodePrefix.advance,
            lastCodeCheckpoint, i, hsymbol] using ih hj'
      | some side =>
          have hnext : f.absorbed < j + 1 := by
            have := (decodeCodePrefix c hn j hj').bound
            dsimp [f] at *
            omega
          cases side with
          | false =>
              simpa [decodeCodePrefix, DecodedCodePrefix.advance,
                lastCodeCheckpoint, i, hsymbol, f] using
                f.nextL_checkpoint (j + 1) hnext hj
          | true =>
              simpa [decodeCodePrefix, DecodedCodePrefix.advance,
                lastCodeCheckpoint, i, hsymbol, f] using
                f.nextR_checkpoint (j + 1) hnext hj

def decodeCode (c : Code (n - 2)) (hn : 2 ≤ n) :
    DecodedCodePrefix n (n - 2) :=
  decodeCodePrefix c hn (n - 2) (le_refl _)

def decodeChain (c : Code (n - 2)) (hn : 2 ≤ n) :
    List (FusionRecord (ZMod n)) := (decodeCode c hn).chain

def decodedCarrier (c : Code (n - 2)) (hn : 2 ≤ n) :
    Finset (ZMod n) := (decodeCode c hn).frontier.carrier

/-- One generated execution, its precise code frontier, and its complete
source-addressed record list are carried by the same prefix witness. -/
structure CleanCodePrefix (c : Code (n - 2)) (hn : 2 ≤ n)
    (j : ℕ) (hj : j ≤ n - 2)
    (state : Execution n (ZMod n)) (word : List Letter) : Prop where
  run_eq : state = run (selectedPair n) (singletonExecution n) word
  origin_eq : state.origin = (registrationExecution n).origin
  chain_eq : state.chain = (decodeCodePrefix c hn j hj).chain
  registered : state.origin.isSome = true
  inside : selectedPair n ⊆ (decodeCodePrefix c hn j hj).frontier.carrier
  clean : CleanOutside (decodeCodePrefix c hn j hj).frontier.carrier state

theorem realize_clean_code_prefix (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∀ (j : ℕ) (hj : j ≤ n - 2),
      ∃ state word, CleanCodePrefix c hn j hj state word := by
  intro j
  induction j with
  | zero =>
      intro hj
      have hbase := registration_clean (n := n) hn
      have hcarrier : (decodeCodePrefix c hn 0 hj).frontier.carrier =
          selectedPair n := by
        simp [decodeCodePrefix, DecodedCodePrefix.initial,
          CheckpointSourceFrontier.carrier, sourceInterval]
      refine ⟨registrationExecution n, [.d], rfl, rfl, ?_, ?_, ?_, ?_⟩
      · simpa [decodeCodePrefix, DecodedCodePrefix.initial] using hbase.2.2.1
      · rw [hbase.2.1]
        simp
      · rw [hcarrier]
      · rw [hcarrier]
        exact hbase.2.2.2
  | succ j ih =>
      intro hj
      have hj' : j ≤ n - 2 := by omega
      obtain ⟨s, w, prev⟩ := ih hj'
      let f := (decodeCodePrefix c hn j hj').frontier
      let i : Fin (n - 2) := ⟨j, by omega⟩
      have hreach : ReachableExecution (selectedPair n) s :=
        ⟨w, prev.run_eq.symm⟩
      have hsel : (selectedPair n).Nonempty := by
        exact ⟨0, by simp [selectedPair]⟩
      have hnext : f.absorbed < j + 1 := by
        have := (decodeCodePrefix c hn j hj').bound
        dsimp [f] at *
        omega
      have hmax : j + 1 ≤ n - 2 := hj
      cases hsymbol : c i with
      | none =>
          refine ⟨s, w, prev.run_eq, prev.origin_eq, ?_,
            prev.registered, ?_, ?_⟩
          · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i, hsymbol]
              using prev.chain_eq
          · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i, hsymbol]
              using prev.inside
          · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i, hsymbol]
              using prev.clean
      | some side =>
          cases side with
          | false =>
              obtain ⟨suffix, _, horigin, hchain, hclean⟩ :=
                f.realizeL_checkpoint (selectedPair n) s hreach
                  prev.registered hsel prev.inside prev.clean (j + 1) hnext hmax
              refine ⟨run (selectedPair n) s suffix,
                w ++ suffix, ?_, ?_, ?_, ?_, ?_, ?_⟩
              · rw [run_append, ← prev.run_eq]
              · exact horigin.trans prev.origin_eq
              · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hchain.trans (congrArg
                    (fun xs => xs ++ [checkpointRecord false f.carrier
                      (f.partnerL (j + 1 - f.absorbed))]) prev.chain_eq)
              · rw [horigin]
                exact prev.registered
              · have hinside : selectedPair n ⊆
                    (f.nextL (j + 1 - f.absorbed)
                      (f.checkpoint_gap (j + 1) hnext hmax).2).carrier := by
                    rw [f.carrier_nextL]
                    exact prev.inside.trans Finset.subset_union_left
                simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hinside
              · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hclean
          | true =>
              obtain ⟨suffix, _, horigin, hchain, hclean⟩ :=
                f.realizeR_checkpoint (selectedPair n) s hreach
                  prev.registered hsel prev.inside prev.clean (j + 1) hnext hmax
              refine ⟨run (selectedPair n) s suffix,
                w ++ suffix, ?_, ?_, ?_, ?_, ?_, ?_⟩
              · rw [run_append, ← prev.run_eq]
              · exact horigin.trans prev.origin_eq
              · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hchain.trans (congrArg
                    (fun xs => xs ++ [checkpointRecord true f.carrier
                      (f.partnerR (j + 1 - f.absorbed))]) prev.chain_eq)
              · rw [horigin]
                exact prev.registered
              · have hinside : selectedPair n ⊆
                    (f.nextR (j + 1 - f.absorbed)
                      (f.checkpoint_gap (j + 1) hnext hmax).2).carrier := by
                    rw [f.carrier_nextR]
                    exact prev.inside.trans Finset.subset_union_left
                simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hinside
              · simpa [decodeCodePrefix, DecodedCodePrefix.advance, i,
                  hsymbol, f] using hclean

/-- Every symbolic ternary code has one actual clean, registered execution
whose carrier and ordered records are its own decoder outputs. -/
theorem realize_clean_code (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∃ word : List Letter,
      let s := run (selectedPair n) (singletonExecution n) word
      s.origin = (registrationExecution n).origin ∧
      s.chain = decodeChain c hn ∧
      selectedPair n ⊆ decodedCarrier c hn ∧
      CleanOutside (decodedCarrier c hn) s := by
  obtain ⟨s, w, x⟩ := realize_clean_code_prefix c hn (n - 2) (le_refl _)
  refine ⟨w, ?_⟩
  dsimp
  rw [← x.run_eq]
  exact ⟨x.origin_eq, x.chain_eq, x.inside, x.clean⟩

/-- The decoded carrier is literally one current packet in the constructed
execution, not just an abstract set containing the registered pair. -/
theorem realize_clean_code_actual_carrier (c : Code (n - 2)) (hn : 2 ≤ n) :
    ∃ (word : List Letter) (q : ZMod n),
      let s := run (selectedPair n) (singletonExecution n) word
      s.placed q = some (decodedCarrier c hn) ∧
      s.origin = (registrationExecution n).origin ∧
      s.chain = decodeChain c hn ∧
      CleanOutside (decodedCarrier c hn) s := by
  obtain ⟨word, horigin, hchain, _, hclean⟩ := realize_clean_code c hn
  obtain ⟨q, hq⟩ := hclean.1
  exact ⟨word, q, hq, horigin, hchain, hclean⟩

end RegisteredAbsorptionChains
