import RSR2History.LowerExtractionLifting
import RSR2History.UpperAllRSuffix
import RSR2History.AllRHistoryPremiumExact

/-!
Attaining the delayed-chain lower bound. The auxiliary optimum is realized
without a pre-existing physical witness, then the frozen all-R core is
lifted to the upper layer with the exact transfer-order atom names.
-/

namespace RSR2History
open RSR2.Parametric

def delayedChainEndpoint (q : Fin n) : Placement n := fun _ => (true, q)

def upperCoreWord (n : Nat) : List Letter :=
  (AllRTransfer.allRCore n).map (layerLetter true)

private theorem reconstruct_reindexed_ordered {n : Nat} [NeZero n]
    (e : Fin n ≃ Fin n) (carrier : Finset (Fin n)) (z : List (Fin n)) :
    (AllRTransfer.lowerLog
      ((orderedUpperFusionLog carrier z).map (UpperAllR.reindexEvent e))).map
        AllRTransfer.lowerEvent =
      (orderedUpperFusionLog carrier z).map (UpperAllR.reindexEvent e) := by
  induction z generalizing carrier with
  | nil => rfl
  | cons a rest ih =>
      simp only [orderedUpperFusionLog, List.map_cons, UpperAllR.reindexEvent,
        Bool.not_true, AllRTransfer.lowerLog, List.filterMap_cons,
        AllRTransfer.lowerEvent, AllRTransfer.packetToFin_toZMod]
      exact congrArg (List.cons _) (ih (carrier ∪ {a}))

theorem delayed_log_reindexed_events {n : Nat} [NeZero n]
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup) (hn : 1 < n) :
    (delayedUpperFusionLog z).map
        (UpperAllR.reindexEvent (UpperAllR.orderEquiv z hlen hnodup)) =
      (FusionLogAllR.allRLog n).map AllRTransfer.lowerEvent := by
  have he := UpperAllR.delayed_log_reindex z hlen hnodup hn
  rw [← he]
  cases z with
  | nil => rfl
  | cons a rest => exact (reconstruct_reindexed_ordered _ {a} rest).symm

private theorem lowerCore_run {n : Nat} [NeZero n] (hn : 3 ≤ n) :
    runLogged n (by omega) (seed n) (AllRTransfer.lowerLift (AllRTransfer.allRCore n)) =
      some ((fun _ => (false, site0 n (by omega))),
        (FusionLogAllR.allRLog n).map AllRTransfer.lowerEvent) := by
  obtain ⟨hlog, hplaced⟩ := AllRTransfer.allRCore_spec hn
  obtain ⟨P, hp, hview, hall⟩ := AllRTransfer.lowerLift_simulation (by omega)
    (FusionLogAllR.allRSelectedPair n) (seed n) (AllRTransfer.allLower_seed n)
    (RegisteredAbsorptionChains.singletonExecution n)
    AllRTransfer.lowerView_seed.symm (AllRTransfer.allRCore n)
  rw [hlog] at hp
  have hP : P = fun _ => (false, site0 n (by omega)) := by
    have hz : AllRTransfer.lowerView P 0 = some Finset.univ := by
      rw [hview, hplaced]; simp
    have hpacket : packetAt P false (site0 n (by omega)) = Finset.univ := by
      have he := congrArg (fun opt => opt.map AllRTransfer.packetToFin) hz
      have hu : AllRTransfer.packetToFin (Finset.univ : Finset (ZMod n)) = Finset.univ := by
        ext a
        simp [AllRTransfer.packetToFin]
      have hh : packetAt P false (site0 n (by omega)) ≠ ∅ ∧
          packetAt P false (site0 n (by omega)) = AllRTransfer.packetToFin Finset.univ := by
        simpa [AllRTransfer.lowerView, layerView, site0] using he
      exact hh.2.trans hu
    funext a
    exact (mem_packetAt _ _ _ _).mp (by rw [hpacket]; simp)
  simpa [hP] using hp

/-- Lift the canonical core to the actual upper layer in the specified atom
order. The complete ordered fusion log is preserved, not just the endpoint. -/
theorem upperCore_run {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup)
    {P : Placement n}
    (packed : ∀ i : Fin n, P (z[i.val]'(by omega)) = (true, i)) :
    runLogged n (by omega) P (upperCoreWord n) =
      some (delayedChainEndpoint (site0 n (by omega)), delayedUpperFusionLog z) := by
  let e := UpperAllR.orderEquiv z hlen hnodup
  have hsource : UpperAllR.asLower e P = seed n := by
    funext i
    have hp := packed i
    change P (e i) = (true, i) at hp
    simp [UpperAllR.asLower, hp, seed]
  have hword : (upperCoreWord n).map UpperAllR.flipLetter =
      AllRTransfer.lowerLift (AllRTransfer.allRCore n) := by
    simp only [upperCoreWord, AllRTransfer.lowerLift, List.map_map]
    apply List.map_congr_left
    intro letter _
    cases letter <;> rfl
  have hnov : .v ∉ upperCoreWord n := by
    simp only [upperCoreWord, List.mem_map]
    rintro ⟨letter, _, he⟩
    cases letter <;> cases he
  apply UpperAllR.runLogged_asLower_reverse (by omega) e hnov
  rw [hsource, hword, delayed_log_reindexed_events hlen hnodup (by omega)]
  have htarget : UpperAllR.asLower e (delayedChainEndpoint (site0 n (by omega))) =
      fun _ => (false, site0 n (by omega)) := rfl
  rw [htarget]
  exact lowerCore_run hn

private theorem phaseShift_fullPacket (n : Nat) [NeZero n]
    (q : Fin n) :
    phaseShift (delayedChainEndpoint (site0 n (Nat.pos_of_ne_zero (NeZero.ne n)))) true
        (q.val : ZMod n) = delayedChainEndpoint q := by
  have hsite : zsite (((site0 n (Nat.pos_of_ne_zero (NeZero.ne n))).val : ZMod n) +
      (q.val : ZMod n)) = q := by
    apply Fin.ext
    simp [zsite, site0, ZMod.val_natCast, Nat.mod_eq_of_lt q.isLt]
  funext a
  simp [phaseShift, delayedChainEndpoint, hsite]

/-! An optimal auxiliary lower extraction can be followed by the canonical
upper all-R suffix.  This is the first fully guarded attaining construction
for the delayed-chain family; the lower optimum is obtained independently of
any previously supplied delayed-chain execution. -/
theorem delayedChain_attained
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup)
    (q : Fin n) :
    ∃ word,
      runLogged n (by omega) (seed n) word =
        some (delayedChainEndpoint q, delayedUpperChainLog z) ∧
      word.length = lowerExtractionCost n (by omega) z +
        (5 * n * (n - 1)) / 2 + q.val := by
  obtain ⟨load, P, hload, hpacked, hloadLen⟩ :=
    lowerExtraction_optimal_guarded_loading (hn := by omega) hlen hnodup
  have hcore := upperCore_run hn hlen hnodup hpacked
  have hloadcore :
      runLogged n (by omega) (seed n) (load ++ upperCoreWord n) =
        some (delayedChainEndpoint (site0 n (by omega)),
          delayedUpperChainLog z) := by
    rw [runLogged_append, hload]
    simp only [Option.bind_some]
    rw [hcore]
    simp [delayedUpperChainLog]
  have hphase := runLogged_pWord (by omega)
    (delayedChainEndpoint (site0 n (by omega))) true q.val
  let word := load ++ upperCoreWord n ++ pWord true q.val
  refine ⟨word, ?_, ?_⟩
  · rw [show word = (load ++ upperCoreWord n) ++ pWord true q.val by
      simp [word, List.append_assoc], runLogged_append, hloadcore]
    simp only [Option.bind_some]
    rw [hphase]
    rw [phaseShift_fullPacket]
    simp
  · have hcoreLen : (AllRTransfer.allRCore n).length =
        (3 * n * (n - 1)) / 2 - n := by
      have hc := AllRTransfer.allRHistoryWord_length n hn
      simp only [AllRTransfer.allRHistoryWord, AllRTransfer.lowerLift_length,
        List.length_append, List.length_singleton,
        AllRTransfer.allRHistoryMinimumLength] at hc
      omega
    simp only [word, List.length_append, RSR2.Parametric.pWord,
      List.length_replicate]
    rw [show (upperCoreWord n).length = (AllRTransfer.allRCore n).length by
      simp [upperCoreWord]]
    rw [hcoreLen]
    rw [hloadLen]
    have hprod : 2 ∣ n * (n - 1) := n.even_mul_pred_self.two_dvd
    have h3 : 3 * n * (n - 1) / 2 = 3 * (n * (n - 1) / 2) := by
      rw [show 3 * n * (n - 1) = 3 * (n * (n - 1)) by ring,
        Nat.mul_div_assoc _ hprod]
    have h5 : 5 * n * (n - 1) / 2 = 5 * (n * (n - 1) / 2) := by
      rw [show 5 * n * (n - 1) = 5 * (n * (n - 1)) by ring,
        Nat.mul_div_assoc _ hprod]
    have hpred : n - 1 + 1 = n := by omega
    have hnprod : n * n = n * (n - 1) + n := by
      calc
        n * n = n * (n - 1 + 1) := by rw [hpred]
        _ = n * (n - 1) + n := by ring
    have hhalf : 2 * (n * (n - 1) / 2) = n * (n - 1) :=
      Nat.mul_div_cancel' hprod
    have hnsq : n * n = 2 * (n * (n - 1) / 2) + n := by
      rw [hnprod, hhalf]
    have hnd : n ≤ n * (n - 1) / 2 := by
      apply (Nat.le_div_iff_mul_le (by decide : 0 < 2)).2
      nlinarith [hn]
    have hle : n ≤ 3 * (n * (n - 1) / 2) := by omega
    rw [h3, h5, hnprod]
    rw [← hhalf]
    omega

/-- A literal full-packet endpoint has the one-block upper cyclic signature. -/
theorem delayedChainEndpoint_signature
    {n : Nat} [NeZero n] (q : Fin n) :
    cyclicSignature (delayedChainEndpoint q) true = [Finset.univ] := by
  have huniv : (Finset.univ : Finset (Fin n)) ≠ ∅ := Finset.univ_nonempty.ne_empty
  have hpacket : ∀ r : Fin n, packetAt (delayedChainEndpoint q) true r =
      if r = q then Finset.univ else ∅ := by
    intro r
    ext a
    by_cases hr : r = q
    · simp [packetAt, delayedChainEndpoint, hr]
    · simp [packetAt, delayedChainEndpoint, hr, Ne.symm hr]
  have hoccupied : occupiedSites (delayedChainEndpoint q) true = [q] := by
    unfold occupiedSites
    have hp : (fun r : Fin n => packetAt (delayedChainEndpoint q) true r != ∅) =
        (fun r : Fin n => decide (r = q)) := by
      funext r
      rw [hpacket]
      by_cases hr : r = q <;> simp [hr, huniv]
    rw [hp, List.filter_eq, List.count_eq_one_of_mem
      (List.nodup_finRange n) (List.mem_finRange q)]
    rfl
  rw [signature_eq_occupied_map, hoccupied]
  simp [hpacket]

/-- Exact raw-word minimum for a fixed full singleton-transfer order, ordered
upper fusion chain, and final upper phase. -/
theorem delayedChain_exact_cost
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup)
    (q : Fin n) :
    (∃ word,
      runLogged n (by omega) (seed n) word =
        some (delayedChainEndpoint q, delayedUpperChainLog z) ∧
      word.length = lowerExtractionCost n (by omega) z +
        (5 * n * (n - 1)) / 2 + q.val) ∧
    ∀ word,
      runLogged n (by omega) (seed n) word =
        some (delayedChainEndpoint q, delayedUpperChainLog z) →
      lowerExtractionCost n (by omega) z +
        (5 * n * (n - 1)) / 2 + q.val ≤ word.length := by
  refine ⟨delayedChain_attained hn hlen hnodup q, ?_⟩
  intro word hexec
  have hterminal := delayedChainEndpoint_signature q
  have hQ : ∀ atom, delayedChainEndpoint q atom = (true, q) := by
    intro atom
    rfl
  cases z with
  | nil => simp at hlen; omega
  | cons a rest =>
      cases rest with
      | nil => simp at hlen; omega
      | cons b rest =>
          exact delayedChain_cost_lower_bound_closed hn hlen hnodup hterminal q hQ hexec

theorem delayedChain_attainable
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup)
    (q : Fin n) :
    ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint q, delayedUpperChainLog z) := by
  obtain ⟨word, hrun, _⟩ := delayedChain_attained hn hlen hnodup q
  exact ⟨word, hrun⟩

/-- The minimum is the one already defined on actual five-letter words;
this is not a separate abstract-plan optimization. -/
theorem delayedChain_history_distance_exact
    {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {z : List (Fin n)} (hlen : z.length = n) (hnodup : z.Nodup)
    (q : Fin n)
    (attain : ∃ word, runLogged n (by omega) (seed n) word =
      some (delayedChainEndpoint q, delayedUpperChainLog z)) :
    AllRTransfer.historyDistance n (by omega) (delayedChainEndpoint q)
      (delayedUpperChainLog z) attain = lowerExtractionCost n (by omega) z +
        (5 * n * (n - 1)) / 2 + q.val := by
  obtain ⟨witness, lower⟩ := delayedChain_exact_cost hn hlen hnodup q
  exact AllRTransfer.minimumWordLength_eq _ attain _ witness lower

end RSR2History
