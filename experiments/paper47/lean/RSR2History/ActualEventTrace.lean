import RSR2History.CyclicEventPath

namespace RSR2History
open RSR2.Parametric

/-- A real run cut at its effective events. Silent words and every physical
event boundary are retained, so this is stronger data than `CyclicEventPath`. -/
inductive ActualEventTrace (n : Nat) (hn : 1 < n) :
    Placement n → List (EffectiveEvent n) → Placement n → Type where
  | done {P Q : Placement n} (tail : List Letter)
      (run : runLogged n hn P tail = some (Q, [])) :
      ActualEventTrace n hn P [] Q
  | cons {P R S Q : Placement n} {event : EffectiveEvent n}
      {events : List (EffectiveEvent n)}
      (before : List Letter)
      (silent : runLogged n hn P before = some (R, []))
      (letter : Letter)
      (eventStep : EventStep n hn R S letter event)
      (rest : ActualEventTrace n hn S events Q) :
      ActualEventTrace n hn P (event :: events) Q

def ActualEventTrace.word {n : Nat} {hn : 1 < n} {P Q : Placement n}
    {events : List (EffectiveEvent n)} : ActualEventTrace n hn P events Q → List Letter
  | .done tail _ => tail
  | .cons before _ letter _ rest => before ++ letter :: rest.word

theorem EventStep.transfer_letter {n : Nat} {hn : 1 < n}
    {P R : Placement n} {letter : Letter} {packet : Finset (Fin n)}
    (h : EventStep n hn P R letter (.transfer packet)) : letter = .v := by
  cases letter with
  | p layer => simp [EventStep, emittedEvents] at h
  | d layer =>
      by_cases hb : occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn)
      · simp [EventStep, emittedEvents, hb] at h
      · simp [EventStep, emittedEvents, hb] at h
  | v => rfl

theorem EventStep.transfer_source {n : Nat} {hn : 1 < n}
    {P R : Placement n} {packet : Finset (Fin n)}
    (h : EventStep n hn P R .v (.transfer packet)) :
    packetAt P false (site0 n (by omega)) = packet := by
  have he : EffectiveEvent.transfer (packetAt P false (site0 n (by omega))) =
      .transfer packet := by
    simpa [EventStep, emittedEvents] using h.2
  cases he
  rfl

theorem EventStep.upperFusion_letter {n : Nat} {hn : 1 < n}
    {P R : Placement n} {letter : Letter} {A B C : Finset (Fin n)}
    (h : EventStep n hn P R letter (.fusion true A B C)) :
    letter = .d true := by
  cases letter with
  | p layer => simp [EventStep, emittedEvents] at h
  | d layer =>
      cases layer with
      | false =>
          by_cases hb : occupiedAt P false (site0 n (by omega)) ∧
              occupiedAt P false (site1 n hn)
          · simp [EventStep, emittedEvents, hb] at h
          · simp [EventStep, emittedEvents, hb] at h
      | true => rfl
  | v => simp [EventStep, emittedEvents] at h

theorem EventStep.upperFusion_ports {n : Nat} {hn : 1 < n}
    {P R : Placement n} {A B C : Finset (Fin n)}
    (h : EventStep n hn P R (.d true) (.fusion true A B C)) :
    packetAt P true (site0 n (by omega)) = A ∧
      packetAt P true (site1 n hn) = B := by
  by_cases hb : occupiedAt P true (site0 n (by omega)) ∧
      occupiedAt P true (site1 n hn)
  · have he : EffectiveEvent.fusion true
        (packetAt P true (site0 n (by omega)))
        (packetAt P true (site1 n hn))
        (packetAt P true (site0 n (by omega)) ∪ packetAt P true (site1 n hn)) =
          .fusion true A B C := by
        simpa [EventStep, emittedEvents, hb] using h.2
    cases he
    exact ⟨rfl, rfl⟩
  · simp [EventStep, emittedEvents, hb] at h

/-- Read the actual silent prefix and physical letter for the first event. -/
structure ActualEventTraceHead (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {event : EffectiveEvent n} {events : List (EffectiveEvent n)} where
  beforeState : Placement n
  afterState : Placement n
  before : List Letter
  letter : Letter
  rest : ActualEventTrace n hn afterState events Q
  silent : runLogged n hn P before = some (beforeState, [])
  eventStep : EventStep n hn beforeState afterState letter event

def ActualEventTrace.first {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {event : EffectiveEvent n} {events : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P (event :: events) Q) :
    ActualEventTraceHead n hn (P := P) (Q := Q) (event := event) (events := events) := by
  cases trace with
  | cons before hbefore letter hstep rest => exact ⟨_, _, before, letter, rest, hbefore, hstep⟩

theorem ActualEventTrace.runLogged {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {events : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P events Q) :
    runLogged n hn P trace.word = some (Q, events) := by
  induction trace with
  | done tail htail => exact htail
  | cons before hbefore letter hevent rest ih =>
      rw [ActualEventTrace.word]
      have hword : before ++ letter :: rest.word =
          before ++ ([letter] ++ rest.word) := by simp
      rw [hword, runLogged_append, hbefore]
      simp only [Option.bind_some]
      rw [runLogged_append, hevent.runLogged]
      simpa using ih

/-- Extend the leading silent segment while preserving the same event trace. -/
def ActualEventTrace.prependSilent {n : Nat} {hn : 1 < n}
    {P R Q : Placement n} {events : List (EffectiveEvent n)}
    (letter : Letter) (hstep : SilentStep n hn P R letter)
    (trace : ActualEventTrace n hn R events Q) :
    ActualEventTrace n hn P events Q := by
  cases trace with
  | done tail htail =>
      exact .done (letter :: tail) (by
        rw [show letter :: tail = [letter] ++ tail by rfl, runLogged_append]
        simp [RSR2History.runLogged, hstep.1, hstep.2, htail])
  | cons before hbefore next hevent rest =>
      exact .cons (letter :: before) (by
        rw [show letter :: before = [letter] ++ before by rfl, runLogged_append]
        simp [RSR2History.runLogged, hstep.1, hstep.2, hbefore]) next hevent rest

@[simp] theorem ActualEventTrace.prependSilent_word {n : Nat} {hn : 1 < n}
    {P R Q : Placement n} {events : List (EffectiveEvent n)}
    (letter : Letter) (hstep : SilentStep n hn P R letter)
    (trace : ActualEventTrace n hn R events Q) :
    (trace.prependSilent letter hstep).word = letter :: trace.word := by
  cases trace <;> rfl

/-- Keep the physical silent tail after the last event in the same trace. -/
noncomputable def ActualEventTrace.appendSilent {n : Nat} {hn : 1 < n}
    {P R Q : Placement n} {events : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P events R) (after : List Letter)
    (silent : RSR2History.runLogged n hn R after = some (Q, [])) :
    ActualEventTrace n hn P events Q := by
  induction trace with
  | done tail htail =>
      exact .done (tail ++ after) (by simp [runLogged_append, htail, silent])
  | cons before hbefore letter hevent rest ih =>
      exact .cons before hbefore letter hevent (ih silent)

@[simp] theorem ActualEventTrace.appendSilent_word {n : Nat} {hn : 1 < n}
    {P R Q : Placement n} {events : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P events R) (after : List Letter)
    (silent : RSR2History.runLogged n hn R after = some (Q, [])) :
    (trace.appendSilent after silent).word = trace.word ++ after := by
  induction trace with
  | done tail htail => rfl
  | cons before hbefore letter hevent rest ih =>
      simpa [ActualEventTrace.appendSilent, ActualEventTrace.word, List.append_assoc] using
        congrArg (fun t => before ++ letter :: t) (ih silent)

/-- Decompose any successful logged execution into its actual silent segments
and the physical letter that emitted each specified event. -/
theorem actualEventTrace_of_runLogged (n : Nat) (hn : 1 < n)
    (word : List Letter) {P Q : Placement n} {events : List (EffectiveEvent n)}
    (run : runLogged n hn P word = some (Q, events)) :
    ∃ trace : ActualEventTrace n hn P events Q, trace.word = word := by
  induction word generalizing P Q events with
  | nil =>
      have h : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using run
      rcases h with ⟨rfl, rfl⟩
      exact ⟨.done [] rfl, rfl⟩
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at run
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at run
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, hr] using run
              cases he.1
              obtain ⟨tail, htailWord⟩ := ih hr
              rcases emittedEvents_nil_or_singleton n hn P letter with hsilent | ⟨event, hevent⟩
              · have hlog : later = events := by simpa [hsilent] using he.2
                subst events
                have hstep : SilentStep n hn P R letter := ⟨hs, hsilent⟩
                exact ⟨tail.prependSilent letter hstep,
                  by simpa [ActualEventTrace.prependSilent_word] using congrArg (List.cons letter) htailWord⟩
              · have hlog : event :: later = events := by
                  simpa [hevent] using he.2
                subst events
                have hstep : EventStep n hn P R letter event := ⟨hs, hevent⟩
                refine ⟨.cons [] (by rfl) letter hstep tail, ?_⟩
                simpa [ActualEventTrace.word] using congrArg (List.cons letter) htailWord

/-- Split an actual event trace at a specified event boundary. -/
def ActualEventTrace.split {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {early late : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P (early ++ late) Q) :
    Σ R : Placement n, ActualEventTrace n hn P early R ×
      ActualEventTrace n hn R late Q := by
  induction early generalizing P with
  | nil => exact ⟨P, .done [] rfl, trace⟩
  | cons event rest ih =>
      cases trace with
      | cons before hbefore letter hstep tail =>
          obtain ⟨R, h₁, h₂⟩ := ih tail
          exact ⟨R, .cons before hbefore letter hstep h₁, h₂⟩

theorem ActualEventTrace.split_word {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {early late : List (EffectiveEvent n)}
    (trace : ActualEventTrace n hn P (early ++ late) Q) :
    (trace.split.2.1.word ++ trace.split.2.2.word) = trace.word := by
  induction early generalizing P with
  | nil => rfl
  | cons event rest ih =>
      cases trace with
      | cons before hbefore letter hstep tail =>
          have h := ih tail
          simpa [ActualEventTrace.split, ActualEventTrace.word,
            List.append_assoc] using h

def singletonTransferLog (z : List (Fin n)) : List (EffectiveEvent n) :=
  z.map fun a => .transfer ({a} : Finset (Fin n))

def orderedUpperFusionLog (carrier : Finset (Fin n)) :
    List (Fin n) → List (EffectiveEvent n)
  | [] => []
  | a :: rest =>
      .fusion true carrier {a} (carrier ∪ {a}) ::
        orderedUpperFusionLog (carrier ∪ {a}) rest

def delayedUpperFusionLog (z : List (Fin n)) : List (EffectiveEvent n) :=
  match z with
  | [] => []
  | a :: rest => orderedUpperFusionLog {a} rest

/-- The delayed-chain contract: every singleton is transferred in `z` order,
then the upper carrier absorbs the remaining singleton packets in that same
order. -/
def delayedUpperChainLog (z : List (Fin n)) : List (EffectiveEvent n) :=
  singletonTransferLog z ++ delayedUpperFusionLog z

structure DelayedChainActualCut (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) (word : List Letter) (Q : Placement n) where
  packed : Placement n
  trace : ActualEventTrace n hn (seed n) (delayedUpperChainLog z) Q
  trace_word : trace.word = word
  loading : ActualEventTrace n hn (seed n) (singletonTransferLog z) packed
  fusion : ActualEventTrace n hn packed (delayedUpperFusionLog z) Q
  segments_word : loading.word ++ fusion.word = word

theorem delayedChainActualCut_of_runLogged (n : Nat) (hn : 1 < n)
    (z : List (Fin n)) {word : List Letter} {Q : Placement n}
    (run : runLogged n hn (seed n) word = some (Q, delayedUpperChainLog z)) :
    Nonempty (DelayedChainActualCut n hn z word Q) := by
  obtain ⟨trace, hword⟩ := actualEventTrace_of_runLogged n hn word run
  change ActualEventTrace n hn (seed n)
    (singletonTransferLog z ++ delayedUpperFusionLog z) Q at trace
  let hsplit := @ActualEventTrace.split n hn (seed n) Q
    (singletonTransferLog z) (delayedUpperFusionLog z) trace
  refine ⟨⟨hsplit.1, trace, hword, hsplit.2.1, hsplit.2.2, ?_⟩⟩
  simpa [hsplit] using (trace.split_word.trans hword)

structure DelayedFirstTransfer (n : Nat) (hn : 1 < n)
    {a : Fin n} {z : List (Fin n)} {packed : Placement n} where
  loading : ActualEventTrace n hn (seed n) (singletonTransferLog (a :: z)) packed
  beforeState : Placement n
  afterState : Placement n
  before : List Letter
  rest : ActualEventTrace n hn afterState (singletonTransferLog z) packed
  silent : runLogged n hn (seed n) before = some (beforeState, [])
  transfer : EventStep n hn beforeState afterState .v (.transfer {a})
  sourcePacket : packetAt beforeState false (site0 n (by omega)) = {a}
  loading_eq : loading = .cons before silent .v transfer rest

structure DelayedFirstUpperFusion (n : Nat) (hn : 1 < n)
    {a b : Fin n} {z : List (Fin n)} {packed Q : Placement n} where
  fusionTrace : ActualEventTrace n hn packed
    (orderedUpperFusionLog {a} (b :: z)) Q
  beforeState : Placement n
  afterState : Placement n
  before : List Letter
  rest : ActualEventTrace n hn afterState (orderedUpperFusionLog ({a, b}) z) Q
  silent : runLogged n hn packed before = some (beforeState, [])
  fusion : EventStep n hn beforeState afterState (.d true)
    (.fusion true {a} {b} ({a, b} : Finset (Fin n)))
  leftAtPort : packetAt beforeState true (site0 n (by omega)) = {a}
  rightAtPort : packetAt beforeState true (site1 n hn) = {b}
  fusion_eq : fusionTrace = .cons before silent (.d true) fusion rest

theorem DelayedChainActualCut.firstTransfer {n : Nat} {hn : 1 < n}
    {a : Fin n} {z : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedChainActualCut n hn (a :: z) word Q) :
    Nonempty (DelayedFirstTransfer n hn (a := a) (z := z) (packed := cut.packed)) := by
  have hload : ActualEventTrace n hn (seed n)
      (.transfer ({a} : Finset (Fin n)) :: singletonTransferLog z) cut.packed := by
    simpa [singletonTransferLog] using cut.loading
  cases hload' : cut.loading with
  | cons before hbefore letter hevent rest =>
      have hletter := hevent.transfer_letter
      subst letter
      refine ⟨⟨cut.loading, _, _, before, rest, hbefore, hevent,
        hevent.transfer_source, ?_⟩⟩
      rw [hload']

theorem DelayedChainActualCut.firstUpperFusion {n : Nat} {hn : 1 < n}
    {a b : Fin n} {z : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedChainActualCut n hn (a :: b :: z) word Q) :
    Nonempty (DelayedFirstUpperFusion n hn (a := a) (b := b) (z := z)
      (packed := cut.packed) (Q := Q)) := by
  have hfusion : ActualEventTrace n hn cut.packed
      (.fusion true ({a} : Finset (Fin n)) {b} ({a, b} : Finset (Fin n)) ::
        orderedUpperFusionLog ({a, b}) z) Q := by
    simpa [delayedUpperFusionLog, orderedUpperFusionLog] using cut.fusion
  cases hfusion' : cut.fusion with
  | cons before hbefore letter hevent rest =>
      have hletter := hevent.upperFusion_letter
      subst letter
      refine ⟨⟨cut.fusion, _, _, before, rest, hbefore, hevent,
        hevent.upperFusion_ports.1, hevent.upperFusion_ports.2, ?_⟩⟩
      rw [hfusion']

end RSR2History
