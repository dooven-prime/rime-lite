import RSR2History.HistoryCompressionBudget

/-!
Exact resource identities for the existing complete effective-event contract.
Mass is read from the literal packet stored in each successful transfer event.
The executor, event fields, guards and earlier H3 budgets are unchanged.
-/
namespace RSR2History
open RSR2.Parametric
open scoped BigOperators

/-- Number of effective fusion events, on either layer. -/
def logFusionCount (events : List (EffectiveEvent n)) : Nat :=
  (events.map (fun | .fusion _ _ _ _ => 1 | .transfer _ => 0)).sum

/-- Effective fusions on the specified layer, read from the same log. -/
def logLayerFusionCount (layer : Layer) (events : List (EffectiveEvent n)) : Nat :=
  (events.map (fun
    | .fusion l _ _ _ => if l = layer then 1 else 0
    | .transfer _ => 0)).sum

/-- Number of successful whole-packet transfers. -/
def logTransferCount (events : List (EffectiveEvent n)) : Nat :=
  (events.map (fun | .fusion _ _ _ _ => 0 | .transfer _ => 1)).sum

/-- Atom mass of all successful transfers, using their actual recorded packets. -/
def logTransferMass (events : List (EffectiveEvent n)) : Nat :=
  (events.map (fun | .fusion _ _ _ _ => 0 | .transfer packet => packet.card)).sum

/-- Extra atom mass beyond one atom for each transfer. -/
def logTransferExcess (events : List (EffectiveEvent n)) : Nat :=
  (events.map (fun | .fusion _ _ _ _ => 0 | .transfer packet => packet.card-1)).sum

@[simp] theorem logFusionCount_append (xs ys : List (EffectiveEvent n)) :
    logFusionCount (xs++ys) = logFusionCount xs + logFusionCount ys := by
  simp [logFusionCount]

@[simp] theorem logLayerFusionCount_append (layer : Layer)
    (xs ys : List (EffectiveEvent n)) :
    logLayerFusionCount layer (xs++ys) =
      logLayerFusionCount layer xs + logLayerFusionCount layer ys := by
  simp [logLayerFusionCount]

theorem logFusionCount_layer_split (events : List (EffectiveEvent n)) :
    logFusionCount events =
      logLayerFusionCount false events + logLayerFusionCount true events := by
  induction events with
  | nil => rfl
  | cons event rest ih =>
      cases event with
      | fusion layer A B C =>
          cases layer <;> simp [logFusionCount, logLayerFusionCount] at * <;> omega
      | transfer packet => simpa [logFusionCount, logLayerFusionCount] using ih

@[simp] theorem logTransferCount_append (xs ys : List (EffectiveEvent n)) :
    logTransferCount (xs++ys) = logTransferCount xs + logTransferCount ys := by
  simp [logTransferCount]

@[simp] theorem logTransferMass_append (xs ys : List (EffectiveEvent n)) :
    logTransferMass (xs++ys) = logTransferMass xs + logTransferMass ys := by
  simp [logTransferMass]

@[simp] theorem logTransferExcess_append (xs ys : List (EffectiveEvent n)) :
    logTransferExcess (xs++ys) = logTransferExcess xs + logTransferExcess ys := by
  simp [logTransferExcess]

theorem log_event_count_split (events : List (EffectiveEvent n)) :
    logFusionCount events + logTransferCount events = events.length := by
  induction events with
  | nil => rfl
  | cons event rest ih =>
      cases event <;> simp only [logFusionCount, logTransferCount, List.map_cons,
        List.sum_cons, List.length_cons] at * <;> omega

theorem packetAtomMass_eq_card (P : Placement n) (layer : Layer) (q : Fin n) :
    packetAtomMass P layer q = (packetAt P layer q).card := by
  have h := (List.nodup_finRange n).card_eq_countP (P := fun a => P a = (layer, q))
  simpa [packetAtomMass, packetAt] using h.symm

private theorem emitted_fusion_count (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logFusionCount (emittedEvents n hn P letter) =
      lowerFusionCharge n hn P letter + upperFusionCharge n hn P letter := by
  classical
  cases letter with
  | p layer => simp [emittedEvents, logFusionCount, lowerFusionCharge, upperFusionCharge]
  | d layer =>
      cases layer with
      | false =>
          by_cases hb : occupiedAt P false (site0 n (by omega)) ∧
              occupiedAt P false (site1 n hn) <;>
            simp [emittedEvents, logFusionCount, lowerFusionCharge, upperFusionCharge, hb]
      | true =>
          by_cases hb : occupiedAt P true (site0 n (by omega)) ∧
              occupiedAt P true (site1 n hn) <;>
            simp [emittedEvents, logFusionCount, lowerFusionCharge, upperFusionCharge, hb]
  | v => simp [emittedEvents, logFusionCount, lowerFusionCharge, upperFusionCharge]

private theorem emitted_transfer_mass (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logTransferMass (emittedEvents n hn P letter) = transferLetterMass n hn P letter := by
  classical
  cases letter with
  | p layer => rfl
  | d layer =>
      simp only [emittedEvents]
      split <;> simp [logTransferMass, transferLetterMass]
  | v => simp [logTransferMass, emittedEvents, transferLetterMass, packetAtomMass_eq_card]

private theorem emitted_transfer_split (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hs : step n hn P letter = some Q) :
    logTransferMass (emittedEvents n hn P letter) =
      logTransferCount (emittedEvents n hn P letter) +
        logTransferExcess (emittedEvents n hn P letter) := by
  classical
  cases letter with
  | p layer => rfl
  | d layer =>
      simp only [emittedEvents]
      split <;> simp [logTransferMass, logTransferCount, logTransferExcess]
  | v =>
      obtain ⟨hg, _⟩ := (step_v_eq_some_iff n hn P Q).mp hs
      have hpos := Finset.card_pos.mpr ((packetAt_nonempty P false (site0 n (by omega))).mpr hg.1)
      simp only [emittedEvents, logTransferMass, logTransferCount, logTransferExcess,
        List.map_cons, List.map_nil, List.sum_cons, List.sum_nil, Nat.add_zero]
      omega

/-- Exact packet-rank balance, atom-mass balance and transfer-mass split
along one successful raw execution, from an arbitrary typed initial state. -/
theorem runLogged_resource_balance (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    totalPacketCount Q + logFusionCount events = totalPacketCount P ∧
      lowerAtomMass Q + logTransferMass events = lowerAtomMass P ∧
      logTransferMass events = logTransferCount events + logTransferExcess events := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.1, he.2, logFusionCount, logTransferMass, logTransferCount, logTransferExcess]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              obtain ⟨hf, hm, hx⟩ := ih (by simpa [he.1] using hr)
              have hrank := step_totalPacketCount_balance n hn P R letter hs
              have hmass := step_transferMass_balance n hn P R letter hs
              have hP := upperAtomMass_add_lowerAtomMass P
              have hR := upperAtomMass_add_lowerAtomMass R
              have hcf := emitted_fusion_count n hn P letter
              have hcm := emitted_transfer_mass n hn P letter
              have hcx := emitted_transfer_split n hn P R letter hs
              rw [← he.2, logFusionCount_append, logTransferMass_append,
                logTransferCount_append, logTransferExcess_append]
              omega

/-- Additive form avoids any ambiguity from natural-number subtraction. -/
theorem runLogged_event_potential_exact (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    eventPotential Q + events.length + logTransferExcess events = eventPotential P := by
  obtain ⟨hf, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  have hlen := log_event_count_split events
  unfold eventPotential
  omega

/-- Seed specialization: endpoint rank and transferred atom mass are read
from the same complete effective-event log. -/
theorem singleton_log_resource_balance (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    totalPacketCount Q = n-logFusionCount events ∧
      lowerAtomMass Q = n-logTransferMass events ∧
      logTransferMass events = logTransferCount events + logTransferExcess events := by
  obtain ⟨hf, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  have hmass := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hmass
  rw [seed_totalPacketCount] at hf
  omega

@[simp] theorem seed_eventPotential (n : Nat) : eventPotential (seed n) = 2*n := by
  have hmass := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hmass
  simp only [eventPotential, seed_totalPacketCount]
  omega

/-- The potential-inequality slack is exactly extra mass moved by whole packets. -/
theorem singleton_event_potential_slack (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    2*n-eventPotential Q-events.length = logTransferMass events-logTransferCount events ∧
      logTransferMass events-logTransferCount events = logTransferExcess events := by
  have h := runLogged_event_potential_exact n hn word hexec
  rw [seed_eventPotential] at h
  have hx := (runLogged_resource_balance n hn word hexec).2.2
  omega

/-- The universal `2n-1` event-count slack has two contributions: the final
potential above one and excess transferred mass. It is not just the latter. -/
theorem singleton_event_count_slack (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    2*n-1-events.length = (eventPotential Q-1)+logTransferExcess events := by
  have h := runLogged_event_potential_exact n hn word hexec
  rw [seed_eventPotential] at h
  have hp := eventPotential_pos n (by omega) Q
  omega

/-- Sum of internal atom excess in the terminal lower packets. Empty sites
contribute zero; each nonempty literal packet occurs at exactly one site. -/
def lowerPacketExcess (P : Placement n) : Nat :=
  ∑ q : Fin n, ((packetAt P false q).card - 1)

theorem lowerAtomMass_eq_sum_packet_card (P : Placement n) :
    lowerAtomMass P = ∑ q : Fin n, (packetAt P false q).card := by
  classical
  have hc := (List.nodup_finRange n).card_eq_countP (P := fun a => (P a).1 = false)
  have hmass : lowerAtomMass P =
      (Finset.univ.filter (fun a => (P a).1 = false)).card := by
    simpa [lowerAtomMass, Bool.not_eq_true] using hc.symm
  rw [hmass]
  calc
    _ = ∑ q : Fin n,
        ((Finset.univ.filter (fun a => (P a).1 = false)).filter
          (fun a => (P a).2 = q)).card :=
      Finset.card_eq_sum_card_fiberwise (by intro a ha; simp)
    _ = _ := by
      apply Finset.sum_congr rfl
      intro q _
      congr 1
      ext a
      simp [packetAt, Prod.ext_iff]

theorem lowerAtomMass_eq_packetCount_add_excess (P : Placement n) :
    lowerAtomMass P = lowerPacketCount P + lowerPacketExcess P := by
  classical
  have hc := (List.nodup_finRange n).card_eq_countP (P := fun q => occupiedAt P false q)
  have hrank : lowerPacketCount P =
      ∑ q : Fin n, if occupiedAt P false q then 1 else 0 := by
    calc
      _ = (Finset.univ.filter (fun q => occupiedAt P false q)).card := by
        simpa [lowerPacketCount] using hc.symm
      _ = _ := by simp
  rw [lowerAtomMass_eq_sum_packet_card, hrank, lowerPacketExcess, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro q _
  by_cases hq : occupiedAt P false q
  · have hpos := Finset.card_pos.mpr ((packetAt_nonempty P false q).mpr hq)
    simp only [hq, ↓reduceIte]
    omega
  · have hz : packetAt P false q = ∅ := by
      apply Finset.not_nonempty_iff_eq_empty.mp
      simpa only [packetAt_nonempty] using hq
    simp [hq, hz]

private theorem emitted_lower_fusion_count (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logLayerFusionCount false (emittedEvents n hn P letter) =
      lowerFusionCharge n hn P letter := by
  classical
  cases letter with
  | p layer => simp [emittedEvents, logLayerFusionCount, lowerFusionCharge]
  | d layer =>
      cases layer <;> simp only [emittedEvents]
      all_goals split <;> simp_all [logLayerFusionCount, lowerFusionCharge]
  | v => simp [emittedEvents, logLayerFusionCount, lowerFusionCharge]

private theorem emitted_transfer_count (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logTransferCount (emittedEvents n hn P letter) = if letter = .v then 1 else 0 := by
  classical
  cases letter with
  | p layer => rfl
  | d layer => simp only [emittedEvents]; split <;> simp [logTransferCount]
  | v => rfl

/-- The lower packet ledger expressed directly in the complete event log. -/
theorem runLogged_lower_packet_balance (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    lowerPacketCount Q + logLayerFusionCount false events + logTransferCount events =
      lowerPacketCount P := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.1, he.2, logLayerFusionCount, logTransferCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              have hi := ih (by simpa [he.1] using hr)
              have hsbal := step_lowerPacketCount_balance n hn P R letter hs
              have hf := emitted_lower_fusion_count n hn P letter
              have hv := emitted_transfer_count n hn P letter
              rw [← he.2, logLayerFusionCount_append, logTransferCount_append]
              omega

/-- Every lower fusion is accounted for either by excess mass in a later
whole-packet transfer or by internal excess still present below. -/
theorem singleton_lower_fusion_decomposition (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    logLayerFusionCount false events = logTransferExcess events + lowerPacketExcess Q := by
  have hl := runLogged_lower_packet_balance n hn word hexec
  rw [seed_lowerPacketCount] at hl
  obtain ⟨_, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  have hs := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hs
  have he := lowerAtomMass_eq_packetCount_add_excess Q
  omega

theorem singleton_lower_fusion_eq_excess_of_empty (n : Nat) (hn : 1 < n)
    (word : List Letter) {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hempty : lowerAtomMass Q = 0) :
    logLayerFusionCount false events = logTransferExcess events := by
  have h := singleton_lower_fusion_decomposition n hn word hexec
  have he := lowerAtomMass_eq_packetCount_add_excess Q
  omega

private theorem emitted_transfer_nonempty (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hs : step n hn P letter = some Q)
    {packet : Finset (Fin n)} (hmem : .transfer packet ∈ emittedEvents n hn P letter) :
    packet.Nonempty := by
  cases letter with
  | p layer => simp [emittedEvents] at hmem
  | d layer =>
      simp only [emittedEvents] at hmem
      split at hmem <;> simp at hmem
  | v =>
      have he : packet = packetAt P false (site0 n (by omega)) := by
        simpa [emittedEvents] using hmem
      rw [he, packetAt_nonempty]
      exact ((step_v_eq_some_iff n hn P Q).mp hs).1.1

theorem runLogged_transfer_nonempty (n : Nat) (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    ∀ packet, .transfer packet ∈ events → packet.Nonempty := by
  induction word generalizing P events with
  | nil =>
      have he : events = [] := by simpa [runLogged] using (congrArg (Option.map Prod.snd) hexec).symm
      simp [he]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using hexec
              intro packet hmem
              rw [← he.2] at hmem
              rcases List.mem_append.mp hmem with hfirst | hlater
              · exact emitted_transfer_nonempty n hn P R letter hs hfirst
              · exact ih (by simpa [he.1] using hr) packet hlater

/-- Nonempty transfers have zero excess exactly when each transfers one atom.
Nonemptiness is essential: this statement is not asserted for arbitrary
ill-formed event lists containing empty transfer packets. -/
theorem logTransferExcess_eq_zero_iff_singleton_transfers
    (events : List (EffectiveEvent n))
    (hvalid : ∀ packet, .transfer packet ∈ events → packet.Nonempty) :
    logTransferExcess events = 0 ↔
      ∀ packet, .transfer packet ∈ events → packet.card = 1 := by
  induction events with
  | nil => simp [logTransferExcess]
  | cons event rest ih =>
      have hrest : ∀ packet, .transfer packet ∈ rest → packet.Nonempty := by
        intro packet hmem
        exact hvalid packet (List.mem_cons_of_mem _ hmem)
      cases event with
      | fusion layer A B C =>
          simpa [logTransferExcess] using ih hrest
      | transfer packet =>
          have hpos := Finset.card_pos.mpr (hvalid packet (by simp))
          have hi := ih hrest
          simp only [logTransferExcess, List.map_cons, List.sum_cons] at *
          constructor
          · intro h B hB
            have he : packet.card = 1 := by omega
            have hr : ∀ B, .transfer B ∈ rest → B.card = 1 := hi.mp (by omega)
            rcases List.mem_cons.mp hB with hsame | hlater
            · simpa using (EffectiveEvent.transfer.inj hsame) ▸ he
            · exact hr B hlater
          · intro h
            have he := h packet (by simp)
            have hr := hi.mpr (by intro B hB; exact h B (List.mem_cons_of_mem _ hB))
            omega

theorem eventPotential_eq_one_iff (n : Nat) (P : Placement n) :
    eventPotential P = 1 ↔ lowerAtomMass P = 0 ∧ upperPacketCount P = 1 := by
  classical
  constructor
  · intro h
    have hl : lowerAtomMass P = 0 := by
      by_contra hne
      obtain ⟨a, _, ha⟩ := List.one_le_countP_iff.mp
        (show 1 ≤ (List.finRange n).countP (fun a => !(P a).1) by
          change 1 ≤ lowerAtomMass P
          omega)
      have ha' : (P a).1 = false := by simpa using ha
      have hoc : occupiedAt P false (P a).2 := ⟨a, Prod.ext ha' rfl⟩
      have hk : 1 ≤ lowerPacketCount P := by
        apply List.one_le_countP_iff.mpr
        exact ⟨(P a).2, List.mem_finRange _, by simp [hoc]⟩
      unfold eventPotential totalPacketCount at h
      omega
    have hk := lowerAtomMass_eq_packetCount_add_excess P
    unfold eventPotential totalPacketCount at h
    omega
  · rintro ⟨hl, hu⟩
    have hk := lowerAtomMass_eq_packetCount_add_excess P
    unfold eventPotential totalPacketCount
    omega

/-- Potential one is a literal all-upper single-packet endpoint, at some
physical site. Its phase is not fixed by the event-count equality. -/
theorem eventPotential_one_upper_packet (n : Nat) (P : Placement n)
    (h : eventPotential P = 1) :
    ∃ q : Fin n, ∀ a : Fin n, P a = (true, q) := by
  classical
  obtain ⟨hl, hu⟩ := (eventPotential_eq_one_iff n P).mp h
  have hupper : ∀ a, (P a).1 = true := by
    intro a
    have ha := List.countP_eq_zero.mp hl a (List.mem_finRange _)
    cases hPa : (P a).1 <;> simp_all
  have hc := (List.nodup_finRange n).card_eq_countP (P := fun q => occupiedAt P true q)
  rw [upperPacketCount_eq_countP] at hu
  have hcard : (Finset.univ.filter (fun q => occupiedAt P true q)).card = 1 := by
    simpa using hc.trans hu
  obtain ⟨q, hq⟩ := Finset.card_eq_one.mp hcard
  refine ⟨q, ?_⟩
  intro a
  have hoc : occupiedAt P true (P a).2 := ⟨a, Prod.ext (hupper a) rfl⟩
  have hmem : (P a).2 ∈ Finset.univ.filter (fun q => occupiedAt P true q) := by simp [hoc]
  rw [hq, Finset.mem_singleton] at hmem
  exact Prod.ext (hupper a) hmem

/-- Equality in the uniform event bound, for the same actual seed history. -/
theorem singleton_max_event_count_iff (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events)) :
    events.length = 2*n-1 ↔ eventPotential Q = 1 ∧ logTransferExcess events = 0 := by
  have h := runLogged_event_potential_exact n hn word hexec
  rw [seed_eventPotential] at h
  have hp := eventPotential_pos n (by omega) Q
  omega

/-- Extremal event histories use only singleton transfers, fuse exclusively
above, and end in one upper packet. No silent-letter cost bound is inferred. -/
theorem singleton_max_event_count_structure (n : Nat) (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn (seed n) word = some (Q, events))
    (hmax : events.length = 2*n-1) :
    logTransferCount events = n ∧
      logLayerFusionCount false events = 0 ∧
      logLayerFusionCount true events = n-1 ∧
      (∃ q : Fin n, ∀ a : Fin n, Q a = (true, q)) ∧
      (∀ packet, .transfer packet ∈ events → packet.card = 1) := by
  obtain ⟨hpot, he⟩ := (singleton_max_event_count_iff n hn word hexec).mp hmax
  obtain ⟨hl, _⟩ := (eventPotential_eq_one_iff n Q).mp hpot
  have hzero := singleton_lower_fusion_eq_excess_of_empty n hn word hexec hl
  obtain ⟨_, hm, hx⟩ := runLogged_resource_balance n hn word hexec
  have hs := upperAtomMass_add_lowerAtomMass (seed n)
  rw [seed_upperAtomMass] at hs
  have hlen := log_event_count_split events
  have hf := logFusionCount_layer_split events
  refine ⟨by omega, by omega, by omega, eventPotential_one_upper_packet n Q hpot, ?_⟩
  exact (logTransferExcess_eq_zero_iff_singleton_transfers events
    (runLogged_transfer_nonempty n hn word hexec)).mp he

end RSR2History
