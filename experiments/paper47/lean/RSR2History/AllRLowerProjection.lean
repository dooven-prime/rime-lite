import RSR2History.LayerExecutionAdapter
import RSR2History.EventResourceLedger
import FusionLogAllR.RawAllRLowerBound

/-!
Lower-ring erasure before the first transfer. Packet relabelling is explicit:
the guarded machine uses `Fin n`, while the all-R target uses `ZMod n`.
No intermediate-placement agreement with a different execution is assumed.
-/
namespace RSR2History.AllRTransfer

open RSR2.Parametric

def packetToZMod {n : Nat} [NeZero n] (A : Finset (Fin n)) : Finset (ZMod n) :=
  A.map (ZMod.finEquiv n).toEquiv.toEmbedding

def packetToFin {n : Nat} [NeZero n] (A : Finset (ZMod n)) : Finset (Fin n) :=
  A.map (ZMod.finEquiv n).toEquiv.symm.toEmbedding

@[simp] theorem packetToZMod_empty {n : Nat} [NeZero n] :
    packetToZMod (∅ : Finset (Fin n)) = ∅ := by simp [packetToZMod]

@[simp] theorem packetToZMod_union {n : Nat} [NeZero n] (A B : Finset (Fin n)) :
    packetToZMod (A ∪ B) = packetToZMod A ∪ packetToZMod B := by
  ext a
  simp [packetToZMod]

@[simp] theorem packetToZMod_eq_empty {n : Nat} [NeZero n] (A : Finset (Fin n)) :
    packetToZMod A = ∅ ↔ A = ∅ := by simp [packetToZMod]

@[simp] theorem packetToZMod_toFin {n : Nat} [NeZero n] (A : Finset (ZMod n)) :
    packetToZMod (packetToFin A) = A := by
  ext a
  simp [packetToZMod, packetToFin]

@[simp] theorem packetToFin_toZMod {n : Nat} [NeZero n] (A : Finset (Fin n)) :
    packetToFin (packetToZMod A) = A := by
  ext a
  simp [packetToZMod, packetToFin]

@[simp] theorem packetToZMod_univ {n : Nat} [NeZero n] :
    packetToZMod (Finset.univ : Finset (Fin n)) = Finset.univ := by
  ext a
  simp [packetToZMod]

/-- The physical lower layer, with sites and atom labels in the all-R convention. -/
def lowerView {n : Nat} [NeZero n] (P : Placement n) :
    RegisteredAbsorptionChains.Placement n (Finset (ZMod n)) :=
  fun q => (layerView P false q).map packetToZMod

theorem lowerView_rotate {n : Nat} [NeZero n] (hn : 1 < n) (P : Placement n) :
    lowerView (rotate n (by omega) P false) =
      RegisteredAbsorptionChains.rotate 1 (lowerView P) := by
  funext q
  simp only [lowerView]
  rw [layerView_rotate hn P false]
  rfl

theorem lowerView_collapse {n : Nat} [NeZero n] (hn : 1 < n) (P : Placement n) :
    lowerView (collapse n hn P false) =
      RegisteredAbsorptionChains.fusionPlacement (lowerView P) := by
  funext q
  simp only [lowerView, layerView_collapse, RegisteredAbsorptionChains.fusionPlacement]
  by_cases hz : q = 0
  · simp only [hz, if_pos]
    cases h0 : layerView P false 0 <;> cases h1 : layerView P false 1 <;>
      simp [packetToZMod_union]
  · simp only [if_neg hz]
    by_cases ho : q = 1 <;> simp [ho]

def AllLower (P : Placement n) : Prop := ∀ a, (P a).1 = false

theorem allLower_seed (n : Nat) : AllLower (seed n) := fun _ => rfl

theorem allLower_rotate {n : Nat} (hn : 1 < n) {P : Placement n}
    (h : AllLower P) (layer : Layer) : AllLower (rotate n (by omega) P layer) := by
  intro a
  cases layer <;> simp [rotate, h a]

theorem allLower_collapse {n : Nat} (hn : 1 < n) {P : Placement n}
    (h : AllLower P) (layer : Layer) : AllLower (collapse n hn P layer) := by
  intro a
  simp only [collapse]
  split
  · rename_i he
    simpa only [he, Prod.fst] using h a
  · exact h a

theorem allLower_upper_rotate {n : Nat} (hn : 1 < n) {P : Placement n}
    (h : AllLower P) : rotate n (by omega) P true = P := by
  funext a
  simp [rotate, h a]

theorem allLower_upper_collapse {n : Nat} (hn : 1 < n) {P : Placement n}
    (h : AllLower P) : collapse n hn P true = P := by
  funext a
  have hne : P a ≠ (true, site1 n hn) := by
    intro he
    have := congrArg Prod.fst he
    simp [h a] at this
  simp [collapse, hne]

theorem allLower_upper_unoccupied {P : Placement n} (h : AllLower P) (q : Fin n) :
    ¬ occupiedAt P true q := by
  rintro ⟨a, ha⟩
  have := congrArg Prod.fst ha
  simp [h a] at this

/-- Retain lower raw letters, without identifying silent defects with identity. -/
def lowerWord : List Letter → List RegisteredAbsorptionChains.Letter :=
  List.filterMap (fun
    | .p false => some .p
    | .d false => some .d
    | _ => none)

theorem lowerWord_length_le (word : List Letter) : (lowerWord word).length ≤ word.length :=
  List.length_filterMap_le _ _

/-- Embed a complete single-ring record as a lower effective event. -/
def lowerEvent {n : Nat} [NeZero n]
    (r : RegisteredAbsorptionChains.FusionRecord (ZMod n)) : EffectiveEvent n :=
  .fusion false (packetToFin r.left) (packetToFin r.right) (packetToFin r.result)

/-- Read lower fusion records in the all-R atom convention. -/
def lowerLog {n : Nat} [NeZero n] : List (EffectiveEvent n) →
    List (RegisteredAbsorptionChains.FusionRecord (ZMod n)) :=
  List.filterMap (fun
    | .fusion false A B C => some ⟨packetToZMod A, packetToZMod B, packetToZMod C⟩
    | _ => none)

@[simp] theorem lowerLog_append {n : Nat} [NeZero n] (xs ys : List (EffectiveEvent n)) :
    lowerLog (xs ++ ys) = lowerLog xs ++ lowerLog ys := by
  simp [lowerLog]

@[simp] theorem lowerLog_lowerEvent {n : Nat} [NeZero n]
    (records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))) :
    lowerLog (records.map lowerEvent) = records := by
  induction records with
  | nil => rfl
  | cons r rest ih =>
      simp only [List.map_cons, lowerLog, lowerEvent, List.filterMap_cons,
        packetToZMod_toFin]
      change r :: lowerLog (rest.map lowerEvent) = r :: rest
      rw [ih]

theorem lowerView_seed {n : Nat} [NeZero n] :
    lowerView (seed n) = (RegisteredAbsorptionChains.singletonExecution n).placed := by
  funext q
  let a : Fin n := ⟨q.val, ZMod.val_lt q⟩
  have hp : packetAt (seed n) false a = {a} := by
    ext b
    simp [packetAt, seed]
  have he : ZMod.finEquiv n a = q := by
    apply ZMod.val_injective
    cases n with
    | zero => exact (NeZero.ne 0 rfl).elim
    | succ n => rfl
  simp [lowerView, layerView, hp, a, packetToZMod,
    RegisteredAbsorptionChains.singletonExecution, he]

theorem lowerView_full_zero {n : Nat} [NeZero n] (hn : 1 < n)
    {P : Placement n} (hp : packetAt P false (site0 n (by omega)) = Finset.univ) :
    lowerView P = fun q => if q = 0 then some Finset.univ else none := by
  have hall (a : Fin n) : P a = (false, site0 n (by omega)) := by
    have ha : a ∈ packetAt P false (site0 n (by omega)) := by rw [hp]; simp
    exact (mem_packetAt _ _ _ _).mp ha
  funext q
  have hz : (⟨q.val, ZMod.val_lt q⟩ : Fin n) = site0 n (by omega) ↔ q = 0 := by
    rw [Fin.ext_iff]
    exact ⟨fun h => ZMod.val_injective n (by simpa [site0] using h),
      fun h => by subst q; simp [site0]⟩
  by_cases hq : q = 0
  · subst q
    simp only [lowerView, layerView, ZMod.val_zero, ite_true]
    change (if packetAt P false (site0 n (by omega)) = ∅ then none
      else some (packetAt P false (site0 n (by omega)))).map packetToZMod = some Finset.univ
    rw [hp]
    have hu : (Finset.univ : Finset (Fin n)).Nonempty := ⟨⟨0, by omega⟩, by simp⟩
    simp [hu.ne_empty]
  · have hne : site0 n (by omega) ≠ (⟨q.val, ZMod.val_lt q⟩ : Fin n) :=
      Ne.symm ((not_congr hz).mpr hq)
    have he : packetAt P false ⟨q.val, ZMod.val_lt q⟩ = ∅ := by
      ext a
      simp [packetAt, hall a, hne]
    simp [lowerView, layerView, hq, he]

private theorem lower_defect_log {n : Nat} [NeZero n] (hn : 1 < n)
    (F : Finset (ZMod n)) (P : Placement n)
    (s : RegisteredAbsorptionChains.Execution n (ZMod n)) (hv : s.placed = lowerView P) :
    FusionLogAllR.completeFusionLog F s [.d] = lowerLog (emittedEvents n hn P (.d false)) := by
  classical
  have hone : (1 : ZMod n).val = 1 := by
    have : Fact (1 < n) := ⟨hn⟩
    exact ZMod.val_one n
  have hv0 : s.placed 0 = if packetAt P false (site0 n (by omega)) = ∅ then none
      else some (packetToZMod (packetAt P false (site0 n (by omega)))) := by
    rw [hv]
    simp only [lowerView, layerView, ZMod.val_zero]
    split <;> rename_i he <;> simp_all [site0]
  have hv1 : s.placed 1 = if packetAt P false (site1 n hn) = ∅ then none
      else some (packetToZMod (packetAt P false (site1 n hn))) := by
    rw [hv]
    simp only [lowerView, layerView, hone]
    split <;> rename_i he <;> simp_all [site1]
  have o0 : occupiedAt P false (site0 n (by omega)) ↔
      packetAt P false (site0 n (by omega)) ≠ ∅ :=
    (packetAt_nonempty _ _ _).symm.trans Finset.nonempty_iff_ne_empty
  have o1 : occupiedAt P false (site1 n hn) ↔ packetAt P false (site1 n hn) ≠ ∅ :=
    (packetAt_nonempty _ _ _).symm.trans Finset.nonempty_iff_ne_empty
  by_cases e0 : packetAt P false (site0 n (by omega)) = ∅ <;>
    by_cases e1 : packetAt P false (site1 n hn) = ∅
  all_goals simp [FusionLogAllR.completeFusionLog, hv0, hv1, e0, e1,
    emittedEvents, o0, o1, lowerLog]

private theorem lower_step_simulation {n : Nat} [NeZero n] (hn : 1 < n)
    (F : Finset (ZMod n)) {P Q : Placement n} {letter : Letter}
    (all : AllLower P) (nov : letter ≠ .v) (hs : step n hn P letter = some Q)
    (s : RegisteredAbsorptionChains.Execution n (ZMod n)) (hv : s.placed = lowerView P) :
    (RegisteredAbsorptionChains.run F s (lowerWord [letter])).placed = lowerView Q ∧
      FusionLogAllR.completeFusionLog F s (lowerWord [letter]) =
        lowerLog (emittedEvents n hn P letter) ∧ AllLower Q := by
  cases letter with
  | v => exact (nov rfl).elim
  | p layer =>
      have hQ : Q = rotate n (by omega) P layer := by simpa [step] using hs.symm
      subst Q
      cases layer with
      | false =>
          refine ⟨?_, rfl, allLower_rotate hn all false⟩
          simpa [lowerWord, RegisteredAbsorptionChains.run, RegisteredAbsorptionChains.step, hv]
            using (lowerView_rotate hn P).symm
      | true =>
          simp [lowerWord, RegisteredAbsorptionChains.run, hv, allLower_upper_rotate hn all,
            FusionLogAllR.completeFusionLog, emittedEvents, lowerLog, all]
  | d layer =>
      have hQ : Q = collapse n hn P layer := by simpa [step] using hs.symm
      subst Q
      cases layer with
      | false =>
          refine ⟨?_, lower_defect_log hn F P s hv, allLower_collapse hn all false⟩
          simpa [lowerWord, RegisteredAbsorptionChains.run,
            RegisteredAbsorptionChains.step, RegisteredAbsorptionChains.stepDefect_placed, hv]
            using (lowerView_collapse hn P).symm
      | true =>
          have ho := allLower_upper_unoccupied all (site0 n (by omega))
          simp [lowerWord, RegisteredAbsorptionChains.run, hv, allLower_upper_collapse hn all,
            FusionLogAllR.completeFusionLog, emittedEvents, lowerLog, ho, all]

/-- Erasing upper letters before any transfer preserves the actual lower
placement and the complete lower ordered fusion log, at primitive-letter cost. -/
theorem lowerWord_simulation {n : Nat} [NeZero n] (hn : 1 < n)
    (F : Finset (ZMod n)) {word : List Letter} {P Q : Placement n}
    {events : List (EffectiveEvent n)} (all : AllLower P) (nov : .v ∉ word)
    (hexec : runLogged n hn P word = some (Q, events))
    (s : RegisteredAbsorptionChains.Execution n (ZMod n)) (hv : s.placed = lowerView P) :
    (RegisteredAbsorptionChains.run F s (lowerWord word)).placed = lowerView Q ∧
      FusionLogAllR.completeFusionLog F s (lowerWord word) = lowerLog events ∧ AllLower Q := by
  induction word generalizing P s events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      obtain ⟨rfl, rfl⟩ := he
      exact ⟨hv, rfl, all⟩
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases ht : runLogged n hn R rest with
          | none => simp [runLogged, hs, ht] at hexec
          | some result =>
              obtain ⟨T, later⟩ := result
              have he : T = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, ht] using hexec
              have hnletter : letter ≠ .v := by intro h; simp [h] at nov
              have hnrest : .v ∉ rest := fun h => nov (by simp [h])
              obtain ⟨hview, hlog, hall⟩ := lower_step_simulation hn F all hnletter hs s hv
              obtain ⟨hv', hl', ha'⟩ := ih hall hnrest (by simpa [he.1] using ht)
                (RegisteredAbsorptionChains.run F s (lowerWord [letter])) hview
              have hw : lowerWord (letter :: rest) = lowerWord [letter] ++ lowerWord rest := by
                change lowerWord ([letter] ++ rest) = _
                exact List.filterMap_append
              refine ⟨?_, ?_, ha'⟩
              · simpa only [hw, RegisteredAbsorptionChains.run_append] using hv'
              · rw [hw, FusionLogAllR.completeFusionLog_append, hlog, hl', ← he.2, lowerLog_append]

end RSR2History.AllRTransfer
