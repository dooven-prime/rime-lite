import RSR2History.ActualEventTrace
import RSR2History.UpperLoadingPhysical
import RSR2History.CyclicEventDeterminism

/-!
Upper-arrival lifts extracted from the same guarded execution. The canonical
lift of an arrival is the unique representative of site 0 strictly ahead of
the preceding arrival's current lift and less than one period away. Receiver
vacancy, rather than the site-0 equality alone, gives both strict bounds.

This local arrival extraction does not assert that all the lifts lie in one
cycle relative to the first arrival. That global property must still be
derived from the prescribed ordered fusion suffix.
-/
namespace RSR2History
open RSR2.Parametric

theorem runWithUpperAnchor_of_runLogged (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {word : List Letter} {events : List (EffectiveEvent n)}
    (hrun : runLogged n hn P word = some (Q, events))
    (anchor : UpperAnchorState n) :
    ∃ anchor', runWithUpperAnchor n hn P anchor word = some (Q, anchor') := by
  have hp := runLogged_project n hn P word
  rw [hrun] at hp
  have ha := runWithUpperAnchor_project n hn P anchor word
  rw [← hp] at ha
  cases he : runWithUpperAnchor n hn P anchor word with
  | none => simp [he] at ha
  | some result =>
      obtain ⟨R, anchor'⟩ := result
      have hRQ : R = Q := by simpa only [he, Option.map_some, Option.some.injEq] using ha
      refine ⟨anchor', ?_⟩
      cases hRQ
      rfl

theorem EventStep.transfer_target {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {packet : Finset (Fin n)}
    (event : EventStep n hn P Q .v (.transfer packet))
    {birth : Int} (periodic : birth % (n : Int) = 0) :
    UpperAnchorMatches n Q ⟨packet, birth, 0⟩ := by
  obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp event.1
  intro a ha
  have hsource : P a = (false, site0 n (by omega)) := by
    apply (mem_packetAt _ _ _ _).mp
    rwa [event.transfer_source]
  simp [liftPacket, hsource, periodic, site0]

/-- The next periodic representative at a genuinely vacant receiver. -/
def upperReceiverBirth (n : Nat) (x : Int) : Int := x - x % (n : Int) + n

private theorem rotated_cons_eq {α : Type*} {a : α} {xs ys : List α}
    (hnd : (a :: xs).Nodup)
    (hrot : (a :: xs).IsRotated (a :: ys)) : xs = ys := by
  obtain ⟨k, hk, hrotate⟩ := List.isRotated_iff_mod.mp hrot
  have hlen : (a :: xs).length = xs.length + 1 := by simp
  by_cases hend : k = xs.length + 1
  · subst k
    have hrotate' : (a :: xs).rotate (xs.length + 1) = a :: xs := by
      simp
    rw [hrotate'] at hrotate
    simpa using (List.cons.inj hrotate).2
  · have hlt : k < xs.length + 1 := by omega
    by_cases hzero : k = 0
    · subst k
      have heq : a :: xs = a :: ys := by simpa using hrotate
      exact (List.cons.inj heq).2
    · obtain ⟨j, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hzero
      have hj : j < xs.length := by omega
      have hrotate' : (xs ++ [a]).rotate j = a :: ys := by
        simpa only [List.rotate_cons_succ] using hrotate
      have hhead : ((xs ++ [a]).rotate j).head? = some a := by rw [hrotate']; rfl
      rw [List.head?_rotate (by simp; omega)] at hhead
      have hget : (xs ++ [a])[j]? = some a := by simpa using hhead
      rw [List.getElem?_append_left hj] at hget
      have hmem : a ∈ xs := List.mem_iff_getElem?.mpr ⟨j, hget⟩
      exact False.elim ((List.nodup_cons.mp hnd).1 hmem)

/-- The complete ordered fusion suffix determines the packed upper cycle.
Repeatedly undoing its prescribed prefix fusions fixes the cycle at every
earlier loading boundary. -/
theorem delayedUpperFusionPath_source_cycle {n : Nat}
    {carrier : Finset (Fin n)} {z : List (Fin n)} {P Q : Placement n}
    (path : CyclicEventPath P (orderedUpperFusionLog carrier z) Q)
    (terminal : cyclicSignature Q true = [carrier ∪ z.toFinset]) :
    (cyclicSignature P true).IsRotated
      (carrier :: z.map fun a => ({a} : Finset (Fin n))) := by
  induction z generalizing P carrier with
  | nil =>
      cases path with
      | nil same =>
          have hQ : cyclicSignature Q true = [carrier] := by
            simpa using terminal
          change (cyclicSignature P true).IsRotated [carrier]
          rw [← hQ]
          exact same true
  | cons b rest ih =>
      cases path with
      | cons edge tail =>
          have hfinal : cyclicSignature Q true =
              [ (carrier ∪ {b}) ∪ rest.toFinset ] := by
            simpa [Finset.union_assoc] using terminal
          have hmid := ih tail hfinal
          cases edge with
          | fusion _ _ _ edgeTail _ hleft hright hdis hsource htarget other =>
              have hcycle := htarget.symm.trans hmid
              have hnd : ((carrier ∪ {b}) :: edgeTail).Nodup :=
                htarget.nodup_iff.mp (cyclicSignature_nodup _ true)
              have htail : edgeTail = rest.map fun a => ({a} : Finset (Fin n)) :=
                rotated_cons_eq hnd hcycle
              rw [htail] at hsource
              simpa [orderedUpperFusionLog] using hsource

theorem EventStep.upperReceiverBirth_spec {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {packet : Finset (Fin n)}
    (event : EventStep n hn P Q .v (.transfer packet))
    {anchor : UpperAnchorState n} (nonempty : anchor.packet.Nonempty)
    (hmatch : UpperAnchorMatches n P anchor) :
    (upperReceiverBirth n anchor.coord) % (n : Int) = 0 ∧
      anchor.coord < upperReceiverBirth n anchor.coord ∧
      upperReceiverBirth n anchor.coord < anchor.coord + n := by
  have hnpos : 0 < (n : Int) := by omega
  have hrem0 := Int.emod_nonneg anchor.coord (ne_of_gt hnpos)
  have hremn := Int.emod_lt_of_pos anchor.coord hnpos
  have hremne : anchor.coord % (n : Int) ≠ 0 := by
    intro hzero
    obtain ⟨a, ha⟩ := nonempty
    obtain ⟨hl, hsite⟩ := hmatch a ha
    have hs : (P a).2 = site0 n (by omega) := by
      apply Fin.ext
      simp only [site0]
      omega
    exact ((step_v_eq_some_iff n hn P Q).mp event.1).1.2
      ⟨a, Prod.ext hl hs⟩
  refine ⟨?_, ?_, ?_⟩
  · simp [upperReceiverBirth, Int.sub_emod]
  · dsimp [upperReceiverBirth]
    omega
  · dsimp [upperReceiverBirth]
    omega

/-- A birth-chain extension whose intervening operations and both endpoint
placements are read from the actual transfer-only trace. The final silent
tail is retained and the last lift is its genuine one-packet simulation. -/
inductive ActualUpperBirthTrace (n : Nat) (hn : 1 < n) :
    Placement n → UpperAnchorState n → List (Fin n) → Placement n →
      Int → UpperAnchorState n → Type where
  | done {P Q : Placement n} {anchor last : UpperAnchorState n}
      (word : List Letter)
      (silent : runLogged n hn P word = some (Q, []))
      (tracked : runWithUpperAnchor n hn P anchor word = some (Q, last)) :
      ActualUpperBirthTrace n hn P anchor [] Q anchor.coord last
  | cons {P R S Q : Placement n} {anchor atPort last : UpperAnchorState n}
      {a : Fin n} {rest : List (Fin n)} {lastBirth : Int}
      (before : List Letter)
      (silent : runLogged n hn P before = some (R, []))
      (tracked : runWithUpperAnchor n hn P anchor before = some (R, atPort))
      (event : EventStep n hn R S .v (.transfer {a}))
      (nonempty : anchor.packet.Nonempty)
      (hmatch : UpperAnchorMatches n P anchor)
      (tail : ActualUpperBirthTrace n hn S
        ⟨{a}, upperReceiverBirth n atPort.coord, 0⟩ rest Q lastBirth last) :
      ActualUpperBirthTrace n hn P anchor (a :: rest) Q lastBirth last

def ActualUpperBirthTrace.word {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int} :
    ActualUpperBirthTrace n hn P anchor z Q birth last → List Letter
  | .done word _ _ => word
  | .cons before _ _ _ _ _ tail => before ++ .v :: tail.word

theorem actualUpperBirthTrace_of_eventTrace {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {z : List (Fin n)}
    (trace : ActualEventTrace n hn P (singletonTransferLog z) Q)
    (anchor : UpperAnchorState n) (nonempty : anchor.packet.Nonempty)
    (hmatch : UpperAnchorMatches n P anchor) :
    ∃ birth last, ∃ births : ActualUpperBirthTrace n hn P anchor z Q birth last,
      births.word = trace.word := by
  induction z generalizing P anchor with
  | nil =>
      cases trace with
      | done word hword =>
          obtain ⟨last, hlast⟩ := runWithUpperAnchor_of_runLogged n hn hword anchor
          exact ⟨anchor.coord, last, .done word hword hlast, rfl⟩
  | cons a rest ih =>
      cases trace with
      | cons before hbefore letter hevent tail =>
          have hletter := hevent.transfer_letter
          subst letter
          obtain ⟨atPort, htracked⟩ := runWithUpperAnchor_of_runLogged n hn hbefore anchor
          have hm := runWithUpperAnchor_matches n hn _ _ _ _ _ hmatch htracked
          have hp := runWithUpperAnchor_lift n hn _ _ _ _ _ htracked
          have hne : atPort.packet.Nonempty := by
            rw [hp]
            simpa [upperAnchorAdvance] using nonempty
          have hperiod := (hevent.upperReceiverBirth_spec hne hm).1
          have hbirth := hevent.transfer_target hperiod
          obtain ⟨birth, last, births, hword⟩ := ih tail _ (by simp) hbirth
          refine ⟨birth, last, .cons before hbefore htracked hevent nonempty hmatch births, ?_⟩
          simp [ActualUpperBirthTrace.word, ActualEventTrace.word, hword]
          rfl

theorem ActualUpperBirthTrace.birthChain {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last)
    {i : Nat} (prior : UpperBirthChain n i anchor.coord) :
    Nonempty (UpperBirthChain n (i + z.length) birth) := by
  induction trace generalizing i with
  | done word silent tracked => exact ⟨by simpa using prior⟩
  | @cons P R S Q anchor atPort last a rest lastBirth before silent tracked
      event nonempty hmatch tail ih =>
      have hm := runWithUpperAnchor_matches n hn P R anchor atPort before hmatch tracked
      have hl := runWithUpperAnchor_lift n hn P R anchor atPort before tracked
      have hne : atPort.packet.Nonempty := by
        rw [hl]
        simpa [upperAnchorAdvance] using nonempty
      obtain ⟨hperiod, hafter, _⟩ := event.upperReceiverBirth_spec hne hm
      have hnext : UpperBirthChain n (i + 1) (upperReceiverBirth n atPort.coord) :=
        .next prior (upperLiftProjection before) hperiod (by
          simpa [hl, upperAnchorAdvance] using hafter)
      obtain ⟨chain⟩ := ih hnext
      have hindex : i + 1 + rest.length = i + (rest.length + 1) := by omega
      exact ⟨hindex ▸ chain⟩

theorem ActualUpperBirthTrace.final_matches {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last)
    (hstart : UpperAnchorMatches n P anchor) : UpperAnchorMatches n Q last := by
  induction trace with
  | done word silent tracked =>
      exact runWithUpperAnchor_matches n hn _ _ _ _ word hstart tracked
  | @cons P R S Q anchor atPort last a rest lastBirth before silent tracked
      event nonempty hmatch tail ih =>
      have hportMatch := runWithUpperAnchor_matches n hn _ _ _ _ _ hmatch tracked
      have hlift := runWithUpperAnchor_lift n hn P R anchor atPort before tracked
      have hne : atPort.packet.Nonempty := by
        rw [hlift]
        simpa [upperAnchorAdvance] using nonempty
      have hperiod := (event.upperReceiverBirth_spec hne hportMatch).1
      exact ih (event.transfer_target hperiod)

theorem ActualUpperBirthTrace.final_packet_nonempty {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last)
    (hstart : anchor.packet.Nonempty) : last.packet.Nonempty := by
  induction trace with
  | done word silent tracked =>
      have hlift := runWithUpperAnchor_lift n hn _ _ _ _ word tracked
      rw [hlift]
      simpa [upperAnchorAdvance] using hstart
  | cons before silent tracked event nonempty hmatch tail ih =>
      exact ih (by simp)

theorem ActualUpperBirthTrace.last_packet {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last)
    (hne : z ≠ []) : ∃ a, z.getLast? = some a ∧ last.packet = {a} := by
  induction trace with
  | done word silent tracked => contradiction
  | @cons P R S Q anchor atPort last a rest lastBirth before silent tracked
      event nonempty hmatch tail ih =>
      cases rest with
      | nil =>
          cases tail with
          | done word silent' tracked' =>
              have hlast := runWithUpperAnchor_lift n hn _ _ _ _ _ tracked'
              have hpacket := congrArg UpperAnchorState.packet hlast
              exact ⟨a, by simp, by simpa [upperAnchorAdvance] using hpacket⟩
      | cons b rest' =>
          obtain ⟨lastAtom, hlastAtom, hpacket⟩ := ih (by simp)
          exact ⟨lastAtom, by simpa using hlastAtom, hpacket⟩

theorem ActualUpperBirthTrace.birth_le_final {n : Nat} {hn : 1 < n}
    {P Q : Placement n} {anchor last : UpperAnchorState n}
    {z : List (Fin n)} {birth : Int}
    (trace : ActualUpperBirthTrace n hn P anchor z Q birth last)
    (periodic : anchor.coord % (n : Int) = 0) : birth ≤ last.coord := by
  induction trace with
  | done word silent tracked =>
      have hlift := runWithUpperAnchor_lift n hn _ _ _ _ word tracked
      rw [hlift]
      exact upperLiftRun_ge_birth periodic _ _ le_rfl
  | @cons P R S Q anchor atPort last a rest lastBirth before silent tracked
      event nonempty hmatch tail ih =>
      have hm := runWithUpperAnchor_matches n hn _ _ _ _ _ hmatch tracked
      have hlift := runWithUpperAnchor_lift n hn _ _ _ _ _ tracked
      have hne : atPort.packet.Nonempty := by
        rw [hlift]
        simpa [upperAnchorAdvance] using nonempty
      exact ih (event.upperReceiverBirth_spec hne hm).1

theorem DelayedChainActualCut.upperBirthChain {n : Nat} {hn : 1 < n}
    {a : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedChainActualCut n hn (a :: rest) word Q)
    (zlength : (a :: rest).length = n) :
    ∃ birth last, Nonempty (UpperBirthChain n n birth) ∧
      last.packet.Nonempty ∧ UpperAnchorMatches n cut.packed last := by
  have hload : ActualEventTrace n hn (seed n)
      (.transfer ({a} : Finset (Fin n)) :: singletonTransferLog rest) cut.packed := by
    simpa [singletonTransferLog] using cut.loading
  cases hload with
  | cons before hbefore letter hevent tail =>
      have hletter := hevent.transfer_letter
      subst letter
      have hstart : UpperAnchorMatches n _ ⟨{a}, 0, 0⟩ :=
        hevent.transfer_target (by simp)
      obtain ⟨birth, last, births, _⟩ :=
        actualUpperBirthTrace_of_eventTrace tail ⟨{a}, 0, 0⟩ (by simp) hstart
      obtain ⟨chain⟩ := births.birthChain UpperBirthChain.first
      have hindex : 1 + rest.length = n := by simp only [List.length_cons] at zlength; omega
      have hchain : UpperBirthChain n n birth := by simpa only [hindex] using chain
      exact ⟨birth, last, ⟨hchain⟩, births.final_packet_nonempty (by simp),
        births.final_matches hstart⟩

/-- The exact physical interval after the first singleton transfer and before
the first effective upper fusion. Its log is the prescribed remaining
singleton transfers; its raw letters are a segment of the original word. -/
structure DelayedUpperLoadingPrefix (n : Nat) (hn : 1 < n)
    (a b : Fin n) (rest : List (Fin n)) (original : List Letter) (target : Placement n) where
  beforeTransfer : Placement n
  start : Placement n
  stop : Placement n
  afterFusion : Placement n
  beforeWord : List Letter
  word : List Letter
  tail : List Letter
  word_eq : original = beforeWord ++ .v :: (word ++ .d true :: tail)
  prefix_run : runLogged n hn (seed n) beforeWord = some (beforeTransfer, [])
  transfer : EventStep n hn beforeTransfer start .v (.transfer {a})
  loading_run : runLogged n hn start word =
    some (stop, singletonTransferLog (b :: rest))
  fusion : EventStep n hn stop afterFusion (.d true)
    (.fusion true {a} {b} ({a, b} : Finset (Fin n)))
  tail_run : runLogged n hn afterFusion tail =
    some (target, orderedUpperFusionLog ({a, b} : Finset (Fin n)) rest)
  lastBirth : Int
  lastAnchor : UpperAnchorState n
  births : ActualUpperBirthTrace n hn start ⟨{a}, 0, 0⟩ (b :: rest)
    stop lastBirth lastAnchor
  births_word : births.word = word
  anchorStop : UpperAnchorState n
  anchorRun : runWithUpperAnchor n hn start ⟨{a}, 0, 0⟩ word =
    some (stop, anchorStop)

theorem delayedUpperLoadingPrefix_of_runLogged (n : Nat) (hn : 1 < n)
    (a b : Fin n) (rest : List (Fin n)) {word : List Letter} {Q : Placement n}
    (hrun : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    Nonempty (DelayedUpperLoadingPrefix n hn a b rest word Q) := by
  obtain ⟨cut⟩ := delayedChainActualCut_of_runLogged n hn (a :: b :: rest) hrun
  cases hl : cut.loading with
  | cons before hbefore letter hevent remaining =>
      have hletter := hevent.transfer_letter
      subst letter
      cases hf : cut.fusion with
      | cons silent hsilent fletter fusion tail =>
          have hletter := fusion.upperFusion_letter
          subst fletter
          let loading := remaining.appendSilent silent hsilent
          have hstart : UpperAnchorMatches n _ ⟨{a}, 0, 0⟩ :=
            hevent.transfer_target (by simp)
          obtain ⟨lastBirth, lastAnchor, births, hword⟩ :=
            actualUpperBirthTrace_of_eventTrace loading ⟨{a}, 0, 0⟩ (by simp) hstart
          obtain ⟨anchorStop, hanchor⟩ :=
            runWithUpperAnchor_of_runLogged n hn loading.runLogged ⟨{a}, 0, 0⟩
          refine ⟨⟨_, _, _, _, before, loading.word, tail.word, ?_, hbefore,
            hevent, loading.runLogged, fusion, tail.runLogged, lastBirth, lastAnchor, births,
            hword, anchorStop, hanchor⟩⟩
          have hsegments := cut.segments_word
          rw [hl, hf] at hsegments
          simpa [loading, ActualEventTrace.word, List.append_assoc] using hsegments.symm

theorem DelayedUpperLoadingPrefix.arrivals {n : Nat} {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter}
    {Q : Placement n} (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n) :
    Nonempty (UpperBirthChain n n cut.lastBirth) := by
  obtain ⟨chain⟩ := cut.births.birthChain UpperBirthChain.first
  have hindex : 1 + (b :: rest).length = n := by simp only [List.length_cons] at *; omega
  exact ⟨by simpa only [hindex] using chain⟩

/-- The actual first-fusion boundary has the packet cycle prescribed by the
complete delayed-chain suffix. This is extracted from its actual fusion step
and actual remaining logged run. -/
theorem DelayedUpperLoadingPrefix.stop_cycle {n : Nat} {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (terminal : cyclicSignature Q true =
      [({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset]) :
    (cyclicSignature cut.stop true).IsRotated
      (({a} : Finset (Fin n)) :: {b} :: rest.map fun x => ({x} : Finset (Fin n))) := by
  have htail : CyclicEventPath cut.afterFusion
      (orderedUpperFusionLog ({a, b} : Finset (Fin n)) rest) Q :=
    runLogged_cyclicEventPath n hn cut.tail cut.tail_run
  have hpath : CyclicEventPath cut.stop
      (orderedUpperFusionLog ({a} : Finset (Fin n)) (b :: rest)) Q := by
    simpa [orderedUpperFusionLog] using
      (CyclicEventPath.cons cut.fusion.cyclicEventEdge htail)
  have hcover : ({a} : Finset (Fin n)) ∪ (b :: rest).toFinset =
      ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset := by
    ext x
    simp [or_left_comm]
  have hterm : cyclicSignature Q true =
      [({a} : Finset (Fin n)) ∪ (b :: rest).toFinset] := by
    rw [hcover]
    exact terminal
  simpa [orderedUpperFusionLog] using
    delayedUpperFusionPath_source_cycle hpath hterm

/-- A specified full-packet endpoint and a full, duplicate-free delayed
transfer log force both the actual loading interval's arrival chain and its
complete upper packet cycle. -/
theorem delayedUpperLoadingPrefix_extract_full_cycle {n : Nat} {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (hrun : runLogged n hn (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    Nonempty (DelayedUpperLoadingPrefix n hn a b rest word Q) ∧
      ∃ cut : DelayedUpperLoadingPrefix n hn a b rest word Q,
        Nonempty (UpperBirthChain n n cut.lastBirth) ∧
          (cyclicSignature cut.stop true).IsRotated
            (({a} : Finset (Fin n)) :: {b} ::
              rest.map fun x => ({x} : Finset (Fin n))) := by
  obtain ⟨cut⟩ := delayedUpperLoadingPrefix_of_runLogged n hn a b rest hrun
  have hset : (a :: b :: rest).toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  have hdecomp : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
      (a :: b :: rest).toFinset := by
    simp
  have hcover : ({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset =
      Finset.univ := hdecomp.trans hset
  have hterminal : cyclicSignature Q true =
      [({a} : Finset (Fin n)) ∪ ({b} : Finset (Fin n)) ∪ rest.toFinset] := by
    rw [hcover]
    exact terminal
  exact ⟨⟨cut⟩, cut, cut.arrivals hlen, cut.stop_cycle hterminal⟩

theorem DelayedUpperLoadingPrefix.anchor_periodic {n : Nat} {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter}
    {Q : Placement n} (cut : DelayedUpperLoadingPrefix n hn a b rest word Q) :
    ∃ q : Int, cut.anchorStop.coord = (n : Int) * q := by
  have hstart : UpperAnchorMatches n cut.start ⟨{a}, 0, 0⟩ :=
    cut.transfer.transfer_target (by simp)
  have hstop := runWithUpperAnchor_matches n hn _ _ _ _ _ hstart cut.anchorRun
  have hlift := runWithUpperAnchor_lift n hn _ _ _ _ _ cut.anchorRun
  have hpacket : cut.anchorStop.packet = {a} := by simp [hlift, upperAnchorAdvance]
  have hposition : cut.stop a = (true, site0 n (by omega)) := by
    apply (mem_packetAt _ _ _ _).mp
    rw [cut.fusion.upperFusion_ports.1]
    simp
  have hperiodic : cut.anchorStop.coord % (n : Int) = 0 := by
    have h := (hstop a (by simp [hpacket])).2
    simpa [hposition, site0] using h
  exact ⟨cut.anchorStop.coord / (n : Int),
    (Int.mul_ediv_cancel_of_emod_eq_zero hperiodic).symm⟩

/-- The requested exact raw-rotation identity, now for the actual loading
interval and the actual first transferred singleton. -/
theorem DelayedUpperLoadingPrefix.rotation_identity {n : Nat} {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q) :
    (cut.word.count (.p true) : Int) =
      cut.anchorStop.coord + (cut.anchorStop.slides : Int) := by
  have hcost := upperAnchorAdvance_cost_identity n (upperLiftProjection cut.word)
    (⟨{a}, 0, 0⟩ : UpperAnchorState n)
  have hlift := runWithUpperAnchor_lift n hn _ _ _ _ _ cut.anchorRun
  rw [← hlift, upperLiftRotations_projection] at hcost
  simpa using hcost.symm

end RSR2History
