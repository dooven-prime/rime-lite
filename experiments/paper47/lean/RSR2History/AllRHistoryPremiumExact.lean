import RSR2History.AllRTransferBridge
import FusionLogAllR.RawAllRUniqueness
import RSR2.PortCostSharpness

/-!
An exact history-preservation premium at a fixed, cheap literal endpoint.
All words use the original guarded executor. Equality in the erasure bridge
removes every upper letter and the post-transfer tail; single-ring all-R
uniqueness then determines the entire five-letter word.
-/
namespace RSR2History.AllRTransfer

open RSR2.Parametric

/-- Embed each single-ring letter as its actual lower-layer letter. -/
def lowerLift (word : List RegisteredAbsorptionChains.Letter) : List Letter :=
  word.map (layerLetter false)

@[simp] theorem lowerWord_lowerLift (word : List RegisteredAbsorptionChains.Letter) :
    lowerWord (lowerLift word) = word := by
  induction word with
  | nil => rfl
  | cons letter rest ih =>
      cases letter <;> simpa [lowerLift, lowerWord, layerLetter] using ih

@[simp] theorem lowerLift_length (word : List RegisteredAbsorptionChains.Letter) :
    (lowerLift word).length = word.length := List.length_map _

theorem lowerLift_of_length_eq {word : List Letter}
    (hlen : (lowerWord word).length = word.length) :
    lowerLift (lowerWord word) = word := by
  induction word with
  | nil => rfl
  | cons letter rest ih =>
      have hle := lowerWord_length_le rest
      cases letter with
      | p layer =>
          cases layer with
          | false =>
              have ht : (lowerWord rest).length = rest.length := by
                simpa [lowerWord] using hlen
              simpa [lowerWord, lowerLift, layerLetter] using congrArg (List.cons (.p false)) (ih ht)
          | true => change (lowerWord rest).length = rest.length + 1 at hlen; omega
      | d layer =>
          cases layer with
          | false =>
              have ht : (lowerWord rest).length = rest.length := by
                simpa [lowerWord] using hlen
              simpa [lowerWord, lowerLift, layerLetter] using congrArg (List.cons (.d false)) (ih ht)
          | true => change (lowerWord rest).length = rest.length + 1 at hlen; omega
      | v => change (lowerWord rest).length = rest.length + 1 at hlen; omega

private theorem lower_emitted_reconstruct {n : Nat} [NeZero n] (hn : 1 < n)
    (P : Placement n) (letter : RegisteredAbsorptionChains.Letter) :
    (lowerLog (emittedEvents n hn P (layerLetter false letter))).map lowerEvent =
      emittedEvents n hn P (layerLetter false letter) := by
  cases letter with
  | p => rfl
  | d =>
      simp only [layerLetter, emittedEvents]
      split <;> simp [lowerLog, lowerEvent, -packetToZMod_union]

/-- Reverse of lower erasure: lift any single-ring word while preserving
its exact ordered event tuples and literal lower placement. -/
theorem lowerLift_simulation {n : Nat} [NeZero n] (hn : 1 < n)
    (F : Finset (ZMod n)) (P : Placement n) (all : AllLower P)
    (s : RegisteredAbsorptionChains.Execution n (ZMod n))
    (source : s.placed = lowerView P) (word : List RegisteredAbsorptionChains.Letter) :
    ∃ Q, runLogged n hn P (lowerLift word) =
        some (Q, (FusionLogAllR.completeFusionLog F s word).map lowerEvent) ∧
      lowerView Q = (RegisteredAbsorptionChains.run F s word).placed ∧ AllLower Q := by
  induction word generalizing P s with
  | nil => exact ⟨P, rfl, source.symm, all⟩
  | cons letter rest ih =>
      let Q := match letter with
        | .p => rotate n (by omega) P false
        | .d => collapse n hn P false
      have hs : step n hn P (layerLetter false letter) = some Q := by
        cases letter <;> simp [layerLetter, Q, step]
      have hsingle : runLogged n hn P [layerLetter false letter] =
          some (Q, emittedEvents n hn P (layerLetter false letter)) := by
        simp [runLogged, hs]
      have hnov : .v ∉ [layerLetter false letter] := by
        cases letter <;> simp [layerLetter]
      obtain ⟨hv, hl, ha⟩ := lowerWord_simulation hn F all hnov hsingle s source
      have hw : lowerWord [layerLetter false letter] = [letter] := by
        cases letter <;> rfl
      rw [hw] at hv hl
      have hview : (RegisteredAbsorptionChains.step F s letter).placed = lowerView Q := by
        simpa [RegisteredAbsorptionChains.run] using hv
      have hevents : emittedEvents n hn P (layerLetter false letter) =
          (FusionLogAllR.completeFusionLog F s [letter]).map lowerEvent := by
        rw [hl, lower_emitted_reconstruct]
      obtain ⟨R, hr, hrview, hra⟩ := ih Q ha (RegisteredAbsorptionChains.step F s letter) hview
      refine ⟨R, ?_, ?_, hra⟩
      · have hlog := FusionLogAllR.completeFusionLog_append F s [letter] rest
        have htotal : FusionLogAllR.completeFusionLog F s (letter :: rest) =
            FusionLogAllR.completeFusionLog F s [letter] ++
              FusionLogAllR.completeFusionLog F (RegisteredAbsorptionChains.step F s letter) rest := by
          simpa [RegisteredAbsorptionChains.run] using hlog
        change runLogged n hn P (layerLetter false letter :: lowerLift rest) = _
        simp only [runLogged, hs, Option.bind_some, hr, Option.map_some, hevents,
          htotal, List.map_append]
      · simpa [RegisteredAbsorptionChains.run] using hrview

/-- The all-R canonical word before its final phase-only tail. -/
def allRCore (n : Nat) : List RegisteredAbsorptionChains.Letter :=
  [.d] ++ FusionLogAllR.allRStages n (n - 2)

theorem allRCanonicalWord_split (n : Nat) :
    FusionLogAllR.allRCanonicalWord n =
      allRCore n ++ RegisteredAbsorptionChains.pWord (n - 1) := rfl

def allRHistoryWord (n : Nat) : List Letter := lowerLift (allRCore n) ++ [.v]

def allRHistoryMinimumLength (n : Nat) : Nat := (3 * n * (n - 1)) / 2 - n + 1

theorem allRCore_spec {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    FusionLogAllR.completeFusionLog (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n) (allRCore n) =
        FusionLogAllR.allRLog n ∧
      (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n) (allRCore n)).placed =
        (fun q => if q = 0 then some Finset.univ else none) := by
  have hreal := FusionLogAllR.allRCanonicalWord_realizes (n := n) hn
  have hlog := hreal.log_eq
  rw [allRCanonicalWord_split, FusionLogAllR.completeFusionLog_append] at hlog
  have htail := (FusionLogAllR.completeFusionLog_eq_nil_iff_fusionFree
    (FusionLogAllR.allRSelectedPair n)
    (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
      (RegisteredAbsorptionChains.singletonExecution n) (allRCore n))
    (RegisteredAbsorptionChains.pWord (n - 1))).mpr
      (RegisteredAbsorptionChains.fusionFree_pWord _ _ _)
  refine ⟨by simpa [htail] using hlog, ?_⟩
  have hp := FusionLogAllR.allRStages_placed hn (Nat.le_refl (n - 2))
    (FusionLogAllR.allRSelectedPair n)
  have hpre : RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
      (RegisteredAbsorptionChains.singletonExecution n) (allRCore n) =
      RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        FusionLogAllR.allRRegistered (FusionLogAllR.allRStages n (n - 2)) := by
    rw [allRCore, RegisteredAbsorptionChains.run_append]
    rfl
  rw [hpre, hp]
  have hfull : FusionLogAllR.allRCarrier n (n - 2 + 1) = Finset.univ := by
    ext a
    simp only [FusionLogAllR.allRCarrier, Finset.mem_filter, Finset.mem_univ, true_and,
      iff_true]
    have he : n - 2 + 1 = n - 1 := by omega
    rw [he]
    exact Nat.le_pred_of_lt (ZMod.val_lt a)
  funext q
  have hq : q.val ≤ n - 2 + 1 := by have := ZMod.val_lt q; omega
  simp [FusionLogAllR.allRBoundaryPlaced, hfull, hq]

theorem allRHistoryWord_length (n : Nat) (hn : 3 ≤ n) :
    (allRHistoryWord n).length = allRHistoryMinimumLength n := by
  have h := FusionLogAllR.allRCanonicalWord_length hn
  rw [allRCanonicalWord_split] at h
  simp only [List.length_append, FusionLogCompression.pWord_length] at h
  have hcore : 1 ≤ (allRCore n).length := by simp [allRCore]
  simp only [allRHistoryWord, List.length_append, lowerLift_length, List.length_singleton,
    allRHistoryMinimumLength]
  omega

/-- The explicit attaining word has the prescribed complete history and
the exact same cheap upper full-packet endpoint used by endpoint-only optimization. -/
theorem allRHistoryWord_run {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    runLogged n (by omega) (seed n) (allRHistoryWord n) =
      some (upperFullPacket n (by omega), allRHistory n) := by
  obtain ⟨hlog, hplaced⟩ := allRCore_spec hn
  obtain ⟨P, hp, hview, hall⟩ := lowerLift_simulation (by omega)
    (FusionLogAllR.allRSelectedPair n) (seed n) (allLower_seed n)
    (RegisteredAbsorptionChains.singletonExecution n) lowerView_seed.symm (allRCore n)
  rw [hlog] at hp
  have hP : P = fun _ => (false, site0 n (by omega)) := by
    have hz : lowerView P 0 = some Finset.univ := by rw [hview, hplaced]; simp
    have hpacket : packetAt P false (site0 n (by omega)) = Finset.univ := by
      have he := congrArg (fun opt => opt.map packetToFin) hz
      have hu : packetToFin (Finset.univ : Finset (ZMod n)) = Finset.univ := by
        ext a
        simp [packetToFin]
      have hh : packetAt P false (site0 n (by omega)) ≠ ∅ ∧
          packetAt P false (site0 n (by omega)) = packetToFin Finset.univ := by
        simpa [lowerView, layerView, site0] using he
      exact hh.2.trans hu
    funext a
    exact (mem_packetAt _ _ _ _).mp (by rw [hpacket]; simp)
  have hguard : liftGuard n (by omega) P := by
    rw [hP]
    exact ⟨⟨⟨0, by omega⟩, rfl⟩, by rintro ⟨a, ha⟩; cases ha⟩
  have hafter : liftPacket n (by omega) P = upperFullPacket n (by omega) := by
    rw [hP]
    rfl
  have hpacket : packetAt P false (site0 n (by omega)) = Finset.univ := by
    ext a
    simp [packetAt, hP]
  simp [allRHistoryWord, runLogged_append, hp, runLogged, step, hguard,
    hafter, emittedEvents, hpacket, allRHistory, lowerTransferHistory]

/-- Equality leaves no room for erased upper letters or a post-transfer
tail, and the projected word attains the single-ring all-R minimum. -/
theorem UniqueTransferPrefix.minimum_rigidity {n : Nat} [NeZero n]
    (hn : 3 ≤ n) {word : List Letter} {Q : Placement n}
    (cut : UniqueTransferPrefix (by omega) word Q (FusionLogAllR.allRLog n))
    (hlen : word.length = allRHistoryMinimumLength n) :
    (lowerWord cut.pre).length = cut.pre.length ∧ cut.post = [] ∧
      lowerWord cut.pre = allRCore n := by
  have hsingle := cut.to_allR
  have hmin : (FusionLogAllR.allRCanonicalWord n).length ≤
      (lowerWord cut.pre ++ RegisteredAbsorptionChains.pWord (n - 1)).length := by
    rw [FusionLogAllR.allRCanonicalWord_length hn]
    exact hsingle.word_length_lower_bound hn
  have hcanonical := FusionLogAllR.allRCanonicalWord_length hn
  have hcost : (allRCore n).length + 1 = allRHistoryMinimumLength n := by
    simpa [allRHistoryWord] using allRHistoryWord_length n hn
  have hraw := congrArg List.length cut.word_eq
  have herase := lowerWord_length_le cut.pre
  rw [allRCanonicalWord_split] at hmin hcanonical
  simp only [List.length_append, FusionLogCompression.pWord_length] at hmin hcanonical
  simp only [List.length_append, List.length_cons] at hraw
  have hpre : (lowerWord cut.pre).length = cut.pre.length := by omega
  have hpost : cut.post = [] := List.eq_nil_of_length_eq_zero (by omega)
  have hprojected :
      (lowerWord cut.pre ++ RegisteredAbsorptionChains.pWord (n - 1)).length =
        (FusionLogAllR.allRCanonicalWord n).length := by
    rw [allRCanonicalWord_split]
    simp only [List.length_append, FusionLogCompression.pWord_length]
    omega
  have hword := hsingle.minimal_word_unique hn hprojected
  rw [allRCanonicalWord_split] at hword
  exact ⟨hpre, hpost, List.append_cancel_right hword⟩

/-- Literal uniqueness for every competing word at the history lower bound.
Even the final endpoint need not be supplied to obtain this rigidity. -/
theorem allRHistory_minimal_word_unique {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} {Q : Placement n}
    (hexec : runLogged n (by omega) (seed n) word = some (Q, allRHistory n))
    (hlen : word.length = allRHistoryMinimumLength n) : word = allRHistoryWord n := by
  obtain ⟨cut⟩ := uniqueTransferPrefix_of_runLogged (by omega) hexec
  obtain ⟨hpre, hpost, hcore⟩ := cut.minimum_rigidity hn hlen
  have hlift := lowerLift_of_length_eq hpre
  rw [hcore] at hlift
  rw [cut.word_eq, hpost, ← hlift]
  rfl

theorem allRHistory_exact_minimum {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    runLogged n (by omega) (seed n) (allRHistoryWord n) =
        some (upperFullPacket n (by omega), allRHistory n) ∧
      (allRHistoryWord n).length = allRHistoryMinimumLength n ∧
      ∀ (word : List Letter) (Q : Placement n),
        runLogged n (by omega) (seed n) word = some (Q, allRHistory n) →
          allRHistoryMinimumLength n ≤ word.length ∧
            (word.length = allRHistoryMinimumLength n ↔ word = allRHistoryWord n) := by
  refine ⟨allRHistoryWord_run hn, allRHistoryWord_length n hn, ?_⟩
  intro word Q hexec
  refine ⟨allRHistory_word_length_lower_bound hn hexec, ?_⟩
  exact ⟨allRHistory_minimal_word_unique hn hexec,
    fun h => h ▸ allRHistoryWord_length n hn⟩

theorem allRHistory_existsUnique_minimum_word {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    ∃! word : List Letter,
      runLogged n (by omega) (seed n) word =
          some (upperFullPacket n (by omega), allRHistory n) ∧
        word.length = allRHistoryMinimumLength n := by
  exact ⟨allRHistoryWord n, ⟨allRHistoryWord_run hn, allRHistoryWord_length n hn⟩,
    fun _ h => allRHistory_minimal_word_unique hn h.1 h.2⟩

/-- The endpoint-only contract forgets the effective log, keeping the very
same literal layer, packet and site. Its exact optimum is already linear. -/
theorem allR_endpoint_exact_minimum (n : Nat) (hn : 3 ≤ n) :
    (∃ word : List Letter,
      run n (by omega) (seed n) word = some (upperFullPacket n (by omega)) ∧
        word.length = 2 * n - 2) ∧
      ∀ word : List Letter,
        run n (by omega) (seed n) word = some (upperFullPacket n (by omega)) →
          2 * n - 2 ≤ word.length := by
  obtain ⟨hrun, hlen, _, hbound⟩ := upperFullPacket_optimal n (by omega)
  exact ⟨⟨fullPacketTransferWord n, hrun, hlen⟩, fun word hw => (hbound word hw).1⟩

private theorem accepted_length_exists {accepts : List Letter → Prop}
    (attain : ∃ word, accepts word) :
    ∃ length, ∃ word, accepts word ∧ word.length = length := by
  obtain ⟨word, hw⟩ := attain
  exact ⟨word.length, word, hw, rfl⟩

/-- The least actual raw-word length of an inhabited observation fiber.
No finite approximation of the word space is used. -/
noncomputable def minimumWordLength (accepts : List Letter → Prop)
    (attain : ∃ word, accepts word) : Nat := by
  classical
  exact Nat.find (accepted_length_exists attain)

theorem minimumWordLength_spec (accepts : List Letter → Prop)
    (attain : ∃ word, accepts word) :
    ∃ word, accepts word ∧ word.length = minimumWordLength accepts attain := by
  classical
  exact Nat.find_spec (accepted_length_exists attain)

theorem minimumWordLength_le (accepts : List Letter → Prop)
    (attain : ∃ word, accepts word) {word : List Letter} (hw : accepts word) :
    minimumWordLength accepts attain ≤ word.length := by
  classical
  exact Nat.find_min' (accepted_length_exists attain) ⟨word, hw, rfl⟩

theorem minimumWordLength_eq (accepts : List Letter → Prop)
    (attain : ∃ word, accepts word) (length : Nat)
    (witness : ∃ word, accepts word ∧ word.length = length)
    (lower : ∀ word, accepts word → length ≤ word.length) :
    minimumWordLength accepts attain = length := by
  obtain ⟨word, hw, hlen⟩ := witness
  obtain ⟨best, hb, hbest⟩ := minimumWordLength_spec accepts attain
  have hle := minimumWordLength_le accepts attain hw
  have hge := lower best hb
  omega

theorem endpoint_attainable_of_logged {n : Nat} (hn : 1 < n)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    ∃ word, run n hn (seed n) word = some Q := by
  obtain ⟨word, hw⟩ := attain
  exact ⟨word, by simpa [hw] using (runLogged_project n hn (seed n) word).symm⟩

noncomputable def endpointDistance (n : Nat) (hn : 1 < n) (Q : Placement n)
    (attain : ∃ word, run n hn (seed n) word = some Q) : Nat :=
  minimumWordLength (fun word => run n hn (seed n) word = some Q) attain

noncomputable def historyDistance (n : Nat) (hn : 1 < n) (Q : Placement n)
    (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) : Nat :=
  minimumWordLength (fun word => runLogged n hn (seed n) word = some (Q, events)) attain

/-- Extra minimum raw length for preserving the effective history at the
same literal endpoint; only the observation contract is changed. -/
noncomputable def historyPremium (n : Nat) (hn : 1 < n) (Q : Placement n)
    (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) : Nat :=
  historyDistance n hn Q events attain -
    endpointDistance n hn Q (endpoint_attainable_of_logged hn attain)

theorem endpointDistance_le_historyDistance (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    endpointDistance n hn Q (endpoint_attainable_of_logged hn attain) ≤
      historyDistance n hn Q events attain := by
  obtain ⟨word, hw, hlen⟩ := minimumWordLength_spec
    (fun word => runLogged n hn (seed n) word = some (Q, events)) attain
  have hrun : run n hn (seed n) word = some Q := by
    simpa [hw] using (runLogged_project n hn (seed n) word).symm
  have hle := minimumWordLength_le
    (fun word => run n hn (seed n) word = some Q)
    (endpoint_attainable_of_logged hn attain) hrun
  simpa [endpointDistance, historyDistance, hlen] using hle

theorem historyPremium_balance (n : Nat) (hn : 1 < n)
    (Q : Placement n) (events : List (EffectiveEvent n))
    (attain : ∃ word, runLogged n hn (seed n) word = some (Q, events)) :
    endpointDistance n hn Q (endpoint_attainable_of_logged hn attain) +
        historyPremium n hn Q events attain = historyDistance n hn Q events attain := by
  exact Nat.add_sub_cancel' (endpointDistance_le_historyDistance n hn Q events attain)

theorem allRHistory_attainable {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    ∃ word, runLogged n (by omega) (seed n) word =
      some (upperFullPacket n (by omega), allRHistory n) :=
  ⟨allRHistoryWord n, allRHistoryWord_run hn⟩

theorem allR_history_distance_exact {n : Nat} [NeZero n] (hn : 3 ≤ n)
    (attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (upperFullPacket n (by omega), allRHistory n)) :
    historyDistance n (by omega) (upperFullPacket n (by omega)) (allRHistory n) attain =
      allRHistoryMinimumLength n := by
  apply minimumWordLength_eq _ attain _
  · exact ⟨allRHistoryWord n, allRHistoryWord_run hn, allRHistoryWord_length n hn⟩
  · intro word hw
    exact allRHistory_word_length_lower_bound hn hw

theorem allR_endpoint_distance_exact (n : Nat) (hn : 3 ≤ n)
    (attain : ∃ word, run n (by omega) (seed n) word =
      some (upperFullPacket n (by omega))) :
    endpointDistance n (by omega) (upperFullPacket n (by omega)) attain = 2 * n - 2 := by
  obtain ⟨witness, lower⟩ := allR_endpoint_exact_minimum n hn
  exact minimumWordLength_eq _ attain _ witness lower

private theorem allR_premium_arithmetic (n : Nat) (hn : 3 ≤ n) :
    allRHistoryMinimumLength n - (2 * n - 2) = (3 * (n - 1) * (n - 2)) / 2 := by
  have hd : 2 ∣ 3 * n * (n - 1) := by
    simpa [Nat.mul_assoc] using
      (dvd_mul_of_dvd_right (Nat.even_mul_pred_self n).two_dvd 3)
  have hd' : 2 ∣ 3 * (n - 1) * (n - 2) := by
    have he : n - 1 - 1 = n - 2 := by omega
    simpa [Nat.mul_assoc, he] using
      (dvd_mul_of_dvd_right (Nat.even_mul_pred_self (n - 1)).two_dvd 3)
  have hq := Nat.mul_div_cancel' hd
  have hq' := Nat.mul_div_cancel' hd'
  have hn1 : n - 1 + 1 = n := by omega
  have hn2 : n - 2 + 2 = n := by omega
  have he : (3 * n * (n - 1)) / 2 =
      (3 * (n - 1) * (n - 2)) / 2 + 3 * (n - 1) := by nlinarith
  unfold allRHistoryMinimumLength
  omega

/-- The exact extra cost caused by the prescribed complete all-R history
at the same literal endpoint whose endpoint-only optimum is 2n-2. -/
theorem allR_history_premium_exact {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    historyPremium n (by omega) (upperFullPacket n (by omega)) (allRHistory n)
        (allRHistory_attainable hn) = (3 * (n - 1) * (n - 2)) / 2 := by
  unfold historyPremium
  rw [allR_history_distance_exact hn, allR_endpoint_distance_exact n hn]
  exact allR_premium_arithmetic n hn

end RSR2History.AllRTransfer
