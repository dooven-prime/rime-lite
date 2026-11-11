import PaperXL.C1EventBridge

/-!
# Run correspondence for the concrete C1 circular action

This module lifts the endpoint/event-code bridge to words.  It compares the
Paper XL circular state with C1's complete-log execution while deliberately
leaving registration metadata outside the interface: the common object here
is the complete effective-fusion log together with the literal placement.
-/

namespace PaperXL

open RegisteredAbsorptionChains
open FusionLogCompression

variable {n m : Nat}

def c1LetterOf : RawLetter → Letter
  | .p => .p
  | .d => .d

def c1Run [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) (word : List RawLetter) : CircularLogState n m :=
  word.foldl (CircularLogState.step E) s

def c1ExecutionOf [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) : Execution n (Fin m) :=
  { placed := c1PlacementOf E s
    origin := none
    chain := [] }

def c1LoggedExecutionOf [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) : LoggedExecution n (Fin m) :=
  { state := c1ExecutionOf E s
    fullLog := s.events.map codeFusionRecord }

theorem c1Occupied_iff [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) (q : Fin n) :
    CircularLogState.occupied s q = true ↔
      (c1PacketAt E s q).Nonempty := by
  simp only [CircularLogState.occupied, decide_eq_true_eq,
    CircularLogState.support, Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨i, hi, rfl⟩
    exact ⟨i, by simp [c1PacketAt]⟩
  · intro hq
    rcases hq with ⟨i, hi⟩
    exact ⟨i, (mem_c1PacketAt E s q i).mp hi⟩

theorem c1PlacementOf_port0_nonempty_iff [NeZero n]
    (E : CircularEnvironment n m) (s : CircularLogState n m) :
    (c1PlacementOf E s ((ZMod.finEquiv n) E.port0)).isSome ↔
      CircularLogState.occupied s E.port0 = true := by
  simpa [c1PlacementOf, c1PacketAtZMod,
    Finset.nonempty_iff_ne_empty] using (c1Occupied_iff E s E.port0).symm

theorem c1PlacementOf_port1_nonempty_iff [NeZero n]
    (E : CircularEnvironment n m) (s : CircularLogState n m) :
    (c1PlacementOf E s ((ZMod.finEquiv n) E.port1)).isSome ↔
      CircularLogState.occupied s E.port1 = true := by
  simpa [c1PlacementOf, c1PacketAtZMod,
    Finset.nonempty_iff_ne_empty] using (c1Occupied_iff E s E.port1).symm

theorem c1PlacementOf_step_d [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) :
    c1PlacementOf E (CircularLogState.step E s .d) =
      fusionPlacement (c1PlacementOf E s) := by
  have hp0 := c1_port0_zmod E h
  have hp1 := c1_port1_zmod E h
  funext q
  by_cases hq0 : q = (ZMod.finEquiv n) E.port0
  · subst q
    rw [hp0]
    unfold c1PlacementOf fusionPlacement
    rw [c1PacketAtZMod_step_d E h s]
    simp only [hp0, hp1]
    by_cases h0 : (c1PacketAtZMod E s 0).Nonempty
    · by_cases h1 : (c1PacketAtZMod E s 1).Nonempty
      · simp [h0, h1]
      · have h1e : c1PacketAtZMod E s 1 = ∅ := by
          exact Finset.not_nonempty_iff_eq_empty.mp h1
        simp [h0, h1, h1e]
    · by_cases h1 : (c1PacketAtZMod E s 1).Nonempty
      · have h0e : c1PacketAtZMod E s 0 = ∅ := by
          exact Finset.not_nonempty_iff_eq_empty.mp h0
        simp [h0, h1, h0e]
      · have h0e : c1PacketAtZMod E s 0 = ∅ := by
          exact Finset.not_nonempty_iff_eq_empty.mp h0
        have h1e : c1PacketAtZMod E s 1 = ∅ := by
          exact Finset.not_nonempty_iff_eq_empty.mp h1
        simp [h0, h1, h0e, h1e]
  · by_cases hq1 : q = (ZMod.finEquiv n) E.port1
    · subst q
      rw [hp1]
      unfold c1PlacementOf fusionPlacement
      rw [c1PacketAtZMod_step_d E h s]
      have h10 : (1 : ZMod n) ≠ 0 := by
        intro h10
        apply E.ports_ne
        apply (ZMod.finEquiv n).injective
        rw [hp0, hp1]
        exact h10.symm
      simp [hp0, hp1, hq0, h10]
    · have hq0' : q ≠ 0 := by simpa [hp0] using hq0
      have hq1' : q ≠ 1 := by simpa [hp1] using hq1
      change (if (c1PacketAtZMod E (CircularLogState.step E s .d) q).Nonempty then
          some (c1PacketAtZMod E (CircularLogState.step E s .d) q) else none) = _
      rw [c1PacketAtZMod_step_d E h s]
      simp [fusionPlacement, c1PlacementOf, hq0, hq1, hq0', hq1']

theorem c1Run_nil [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) : c1Run E s [] = s := rfl

theorem c1Run_append [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) (u v : List RawLetter) :
    c1Run E s (u ++ v) = c1Run E (c1Run E s u) v := by
  simp [c1Run, List.foldl_append]

theorem c1LoggedStep_placement_of [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (logged : LoggedExecution n (Fin m))
    (hplace : logged.state.placed = c1PlacementOf E s) (a : RawLetter) :
    (loggedStep ∅ logged (c1LetterOf a)).state.placed =
      c1PlacementOf E (CircularLogState.step E s a) := by
  cases a with
  | p =>
      rw [loggedStep_state]
      change (rotate 1 logged.state.placed) = _
      rw [hplace]
      exact (c1PlacementOf_step_p E s).symm
  | d =>
      simp only [c1LetterOf]
      rw [loggedStep_state]
      change (stepDefect ∅ logged.state).placed = _
      have hstep : (stepDefect ∅ logged.state).placed =
          fusionPlacement logged.state.placed := by
        unfold stepDefect
        cases h0 : logged.state.placed 0 <;>
          cases h1 : logged.state.placed 1 <;> simp [h0, h1]
      rw [hstep]
      rw [hplace]
      exact (c1PlacementOf_step_d E h s).symm

theorem c1LoggedStep_log_of [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (logged : LoggedExecution n (Fin m))
    (hplace : logged.state.placed = c1PlacementOf E s)
    (hlog : logged.fullLog = s.events.map codeFusionRecord) (a : RawLetter) :
    (loggedStep ∅ logged (c1LetterOf a)).fullLog =
      (CircularLogState.step E s a).events.map codeFusionRecord := by
  cases a with
  | p => simpa [c1LetterOf, hlog]
  | d =>
      change (loggedStep ∅ logged .d).fullLog = _
      have hp0 := c1_port0_zmod E h
      have hp1 := c1_port1_zmod E h
      have hp0place : logged.state.placed 0 =
          if (c1PacketAt E s E.port0).Nonempty then
            some (c1PacketAt E s E.port0) else none := by
        rw [hplace, ← hp0]
        simp [c1PlacementOf, c1PacketAtZMod]
      have hp1place : logged.state.placed 1 =
          if (c1PacketAt E s E.port1).Nonempty then
            some (c1PacketAt E s E.port1) else none := by
        rw [hplace, ← hp1]
        simp [c1PlacementOf, c1PacketAtZMod]
      rw [C1Compatible.step_d_events E s]
      by_cases p0 : (c1PacketAt E s E.port0).Nonempty
      · have o0 : CircularLogState.occupied s E.port0 = true :=
          (c1Occupied_iff E s E.port0).mpr p0
        by_cases p1 : (c1PacketAt E s E.port1).Nonempty
        · have o1 : CircularLogState.occupied s E.port1 = true :=
            (c1Occupied_iff E s E.port1).mpr p1
          simp [loggedStep, hp0place, hp1place, hlog, p0, p1, o0, o1,
            codeFusionRecord_eventCode]
          rw [c1PacketAt_port0, c1PacketAt_port1]
          simp
        · have o1 : ¬CircularLogState.occupied s E.port1 = true := by
            intro ho
            exact p1 ((c1Occupied_iff E s E.port1).mp ho)
          simp [loggedStep, hp0place, hp1place, hlog, p0, p1, o0, o1]
      · have o0 : ¬CircularLogState.occupied s E.port0 = true := by
          intro ho
          exact p0 ((c1Occupied_iff E s E.port0).mp ho)
        by_cases p1 : (c1PacketAt E s E.port1).Nonempty
        · have o1 : CircularLogState.occupied s E.port1 = true :=
            (c1Occupied_iff E s E.port1).mpr p1
          simp [loggedStep, hp0place, hp1place, hlog, p0, p1, o0, o1]
        · have o1 : ¬CircularLogState.occupied s E.port1 = true := by
            intro ho
            exact p1 ((c1Occupied_iff E s E.port1).mp ho)
          simp [loggedStep, hp0place, hp1place, hlog, p0, p1, o0, o1]

theorem c1RunCorrespondence [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (logged : LoggedExecution n (Fin m))
    (hplace : logged.state.placed = c1PlacementOf E s)
    (hlog : logged.fullLog = s.events.map codeFusionRecord)
    (word : List RawLetter) :
    (runLogged ∅ logged (word.map c1LetterOf)).state.placed =
        c1PlacementOf E (c1Run E s word) ∧
      (runLogged ∅ logged (word.map c1LetterOf)).fullLog =
        (c1Run E s word).events.map codeFusionRecord := by
  induction word generalizing s logged with
  | nil =>
      simp [c1Run, runLogged, hplace, hlog]
  | cons a rest ih =>
      have hplace' := c1LoggedStep_placement_of E h s logged hplace a
      have hlog' := c1LoggedStep_log_of E h s logged hplace hlog a
      simpa [c1Run, runLogged, c1LetterOf] using
        (ih (s := CircularLogState.step E s a)
          (logged := loggedStep ∅ logged (c1LetterOf a)) hplace' hlog')

theorem c1RunCorrespondence_initial [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (word : List RawLetter) :
    (runLogged ∅ (c1LoggedExecutionOf E s) (word.map c1LetterOf)).state.placed =
        c1PlacementOf E (c1Run E s word) ∧
      (runLogged ∅ (c1LoggedExecutionOf E s) (word.map c1LetterOf)).fullLog =
        (c1Run E s word).events.map codeFusionRecord := by
  exact c1RunCorrespondence E h s (c1LoggedExecutionOf E s) rfl rfl word

end PaperXL
