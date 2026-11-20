import RSR2History.DelayedChainCostLedger
import Mathlib.Data.List.NodupEquivFin

/-!
Erasure of the actual upper-ring suffix.  Atom names are reindexed by the
given full transfer order, and the two layers are exchanged only in this
proof adapter.  No new physical action is added to RSR-2.
-/

namespace RSR2History
open RSR2.Parametric

namespace UpperAllR

private theorem range_split_two (m : Nat) :
    List.range (m + 2) = 0 :: 1 :: (List.range m).map (fun i => i + 2) := by
  induction m with
  | zero => rfl
  | succ m ih =>
      rw [show m + 1 + 2 = (m + 2) + 1 by omega, List.range_succ]
      rw [ih, List.range_succ]
      simp [List.map_append]

def reindexPacket (e : Fin n ≃ Fin n) (A : Finset (Fin n)) : Finset (Fin n) :=
  A.map e.symm.toEmbedding

@[simp] theorem mem_reindexPacket (e : Fin n ≃ Fin n) (A : Finset (Fin n))
    (a : Fin n) : a ∈ reindexPacket e A ↔ e a ∈ A := by
  simp [reindexPacket]

@[simp] theorem reindexPacket_union (e : Fin n ≃ Fin n)
    (A B : Finset (Fin n)) :
    reindexPacket e (A ∪ B) = reindexPacket e A ∪ reindexPacket e B := by
  ext a
  simp

def asLower (e : Fin n ≃ Fin n) (P : Placement n) : Placement n :=
  fun a => (!(P (e a)).1, (P (e a)).2)

def flipLetter : Letter → Letter
  | .p layer => .p (!layer)
  | .d layer => .d (!layer)
  | .v => .v

def reindexEvent (e : Fin n ≃ Fin n) : EffectiveEvent n → EffectiveEvent n
  | .fusion layer A B C =>
      .fusion (!layer) (reindexPacket e A) (reindexPacket e B) (reindexPacket e C)
  | .transfer A => .transfer (reindexPacket e A)

theorem asLower_rotate (hn : 1 < n) (e : Fin n ≃ Fin n)
    (P : Placement n) (layer : Layer) :
    asLower e (rotate n (by omega) P layer) =
      rotate n (by omega) (asLower e P) (!layer) := by
  funext a
  cases hloc : P (e a) with
  | mk l q => cases l <;> cases layer <;> simp [asLower, rotate, hloc]

theorem asLower_collapse (hn : 1 < n) (e : Fin n ≃ Fin n)
    (P : Placement n) (layer : Layer) :
    asLower e (collapse n hn P layer) =
      collapse n hn (asLower e P) (!layer) := by
  funext a
  cases hloc : P (e a) with
  | mk l q =>
      cases l <;> cases layer <;>
        by_cases hq : q = site1 n hn <;> simp [asLower, collapse, hloc, hq]

theorem packetAt_asLower (e : Fin n ≃ Fin n) (P : Placement n)
    (layer : Layer) (q : Fin n) :
    packetAt (asLower e P) (!layer) q = reindexPacket e (packetAt P layer q) := by
  ext a
  cases hloc : P (e a) with
  | mk l r => cases l <;> cases layer <;> simp [asLower, hloc]

theorem occupiedAt_asLower (e : Fin n ≃ Fin n) (P : Placement n)
    (layer : Layer) (q : Fin n) :
    occupiedAt (asLower e P) (!layer) q ↔ occupiedAt P layer q := by
  rw [← packetAt_nonempty, packetAt_asLower, ← packetAt_nonempty]
  simp [reindexPacket]

theorem emitted_asLower (hn : 1 < n) (e : Fin n ≃ Fin n)
    (P : Placement n) (letter : Letter) (nov : letter ≠ .v) :
    emittedEvents n hn (asLower e P) (flipLetter letter) =
      (emittedEvents n hn P letter).map (reindexEvent e) := by
  cases letter with
  | p layer => rfl
  | d layer =>
      simp only [flipLetter, emittedEvents]
      by_cases h : occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn)
      · have h' : occupiedAt (asLower e P) (!layer) (site0 n (by omega)) ∧
            occupiedAt (asLower e P) (!layer) (site1 n hn) := by
          simpa only [occupiedAt_asLower] using h
        simp only [if_pos h, if_pos h']
        simp [packetAt_asLower, reindexEvent, reindexPacket_union]
      · have h' : ¬ (occupiedAt (asLower e P) (!layer) (site0 n (by omega)) ∧
            occupiedAt (asLower e P) (!layer) (site1 n hn)) := by
          intro hh
          apply h
          simpa only [occupiedAt_asLower] using hh
        simp only [if_neg h, if_neg h']
        rfl
  | v => exact (nov rfl).elim

/-- The adapter follows this very raw word. Its use is restricted to a
no-transfer interval, rather than interpreting an inverted elevator. -/
theorem runLogged_asLower (hn : 1 < n) (e : Fin n ≃ Fin n)
    {P Q : Placement n} {word : List Letter} {events : List (EffectiveEvent n)}
    (nov : .v ∉ word)
    (hexec : runLogged n hn P word = some (Q, events)) :
    runLogged n hn (asLower e P) (word.map flipLetter) =
      some (asLower e Q, events.map (reindexEvent e)) := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.1, he.2, runLogged]
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
              have hnletter : letter ≠ .v := by intro h; simp [h] at nov
              have hnrest : .v ∉ rest := fun h => nov (by simp [h])
              have ht := ih hnrest (by simpa [he.1] using hr)
              have hstep : step n hn (asLower e P) (flipLetter letter) =
                  some (asLower e R) := by
                cases letter with
                | p layer =>
                    have hR : R = rotate n (by omega) P layer := by
                      simpa [step] using hs.symm
                    simp [flipLetter, step, hR, asLower_rotate hn]
                | d layer =>
                    have hR : R = collapse n hn P layer := by
                      simpa [step] using hs.symm
                    simp [flipLetter, step, hR, asLower_collapse hn]
                | v => exact (hnletter rfl).elim
              simp only [List.map_cons, runLogged, hstep, Option.bind_some, ht,
                Option.map_some, emitted_asLower hn e P letter hnletter]
              rw [← List.map_append, he.2]

theorem asLower_involutive (e : Fin n ≃ Fin n) (P : Placement n) :
    asLower e.symm (asLower e P) = P := by
  funext a
  cases h : P a with
  | mk layer q => cases layer <;> simp [asLower, h]

private theorem reindexPacket_symm (e : Fin n ≃ Fin n) (A : Finset (Fin n)) :
    reindexPacket e.symm (reindexPacket e A) = A := by
  ext a
  simp [reindexPacket]

private theorem reindexEvent_symm (e : Fin n ≃ Fin n) (event : EffectiveEvent n) :
    reindexEvent e.symm (reindexEvent e event) = event := by
  cases event <;> simp [reindexEvent, reindexPacket_symm]

/-- Reverse the layer/name adapter. This lets an actual run on the reindexed
single layer be transported back to the original physical layer. -/
theorem runLogged_asLower_reverse (hn : 1 < n) (e : Fin n ≃ Fin n)
    {P Q : Placement n} {word : List Letter} {events : List (EffectiveEvent n)}
    (nov : .v ∉ word)
    (hexec : runLogged n hn (asLower e P) (word.map flipLetter) =
      some (asLower e Q, events.map (reindexEvent e))) :
    runLogged n hn P word = some (Q, events) := by
  have hnov : .v ∉ word.map flipLetter := by
    intro h
    obtain ⟨letter, hm, he⟩ := List.mem_map.mp h
    cases letter <;> simp_all [flipLetter]
  have h := runLogged_asLower hn e.symm hnov hexec
  have hP := asLower_involutive e P
  have hQ := asLower_involutive e Q
  have hword : (word.map flipLetter).map flipLetter = word := by
    have hflip : flipLetter ∘ flipLetter = id := by
      funext letter
      cases letter with
      | p layer => cases layer <;> rfl
      | d layer => cases layer <;> rfl
      | v => rfl
    simp only [List.map_map]
    rw [hflip]
    simp
  have hevents : (events.map (reindexEvent e)).map (reindexEvent e.symm) = events := by
    have hindex : reindexEvent e.symm ∘ reindexEvent e = id := by
      funext event
      exact reindexEvent_symm e event
    simp only [List.map_map]
    rw [hindex]
    simp
  simpa [hP, hQ, hword, hevents] using h

/-- Only actual upper raw letters survive this erasure. -/
def upperWord (word : List Letter) : List RegisteredAbsorptionChains.Letter :=
  AllRTransfer.lowerWord (word.map flipLetter)

def phaseEndpoint {n : Nat} [NeZero n] (q : ZMod n) :
    RegisteredAbsorptionChains.Placement n (Finset (ZMod n)) :=
  fun x => if x = q then some Finset.univ else none

theorem upperWord_length (word : List Letter) :
    (upperWord word).length = word.count (.p true) + word.count (.d true) := by
  induction word with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p layer => cases layer <;> simp [upperWord, AllRTransfer.lowerWord,
          flipLetter] at * <;> omega
      | d layer => cases layer <;> simp [upperWord, AllRTransfer.lowerWord,
          flipLetter] at * <;> omega
      | v => simpa [upperWord, AllRTransfer.lowerWord, flipLetter] using ih

theorem upperWord_simulation {n : Nat} [NeZero n] (hn : 1 < n)
    (e : Fin n ≃ Fin n) (F : Finset (ZMod n))
    {P Q : Placement n} {word : List Letter} {events : List (EffectiveEvent n)}
    (source : asLower e P = seed n) (nov : .v ∉ word)
    (hexec : runLogged n hn P word = some (Q, events)) :
    (RegisteredAbsorptionChains.run F (RegisteredAbsorptionChains.singletonExecution n)
      (upperWord word)).placed = AllRTransfer.lowerView (asLower e Q) ∧
    FusionLogAllR.completeFusionLog F (RegisteredAbsorptionChains.singletonExecution n)
      (upperWord word) = AllRTransfer.lowerLog (events.map (reindexEvent e)) := by
  have hr := runLogged_asLower hn e nov hexec
  rw [source] at hr
  have hnov : .v ∉ word.map flipLetter := by
    intro h
    obtain ⟨letter, hm, he⟩ := List.mem_map.mp h
    cases letter <;> simp_all [flipLetter]
  obtain ⟨hp, hl, _⟩ := AllRTransfer.lowerWord_simulation hn F
    (AllRTransfer.allLower_seed n) hnov hr
    (RegisteredAbsorptionChains.singletonExecution n) AllRTransfer.lowerView_seed.symm
  exact ⟨hp, hl⟩

theorem full_order_covers {z : List (Fin n)} (hlen : z.length = n)
    (hnodup : z.Nodup) : ∀ a, a ∈ z := by
  have hset : z.toFinset = Finset.univ := by
    apply (Finset.card_eq_iff_eq_univ _).mp
    rw [List.toFinset_card_of_nodup hnodup, hlen]
    simp
  intro a
  have : a ∈ z.toFinset := by simp [hset]
  simpa using this

/-- Index `i` denotes the actual atom transferred in position `i`. -/
def orderEquiv (z : List (Fin n)) (hlen : z.length = n) (hnodup : z.Nodup) :
    Fin n ≃ Fin n :=
  (finCongr hlen.symm).trans
    (hnodup.getEquivOfForallMemList z (full_order_covers hlen hnodup))

theorem orderEquiv_apply (z : List (Fin n)) (hlen : z.length = n)
    (hnodup : z.Nodup) (i : Fin n) :
    orderEquiv z hlen hnodup i = z[i.val]'(by omega) := rfl

theorem full_order_eq_map (z : List (Fin n)) (hlen : z.length = n)
    (hnodup : z.Nodup) :
    z = (List.finRange n).map (orderEquiv z hlen hnodup) := by
  apply List.ext_getElem
  · simp [hlen]
  · intro i hi hi'
    simp [orderEquiv_apply, List.getElem_finRange]

@[simp] theorem reindexPacket_singleton (e : Fin n ≃ Fin n) (a : Fin n) :
    reindexPacket e {a} = {e.symm a} := by simp [reindexPacket]

@[simp] theorem packetToZMod_singleton {n : Nat} [NeZero n] (a : Fin n) :
    AllRTransfer.packetToZMod {a} = {ZMod.finEquiv n a} := by
  simp [AllRTransfer.packetToZMod]

theorem ordered_log_reindex {n : Nat} [NeZero n] (e : Fin n ≃ Fin n)
    (carrier : Finset (Fin n)) (z : List (Fin n)) :
    AllRTransfer.lowerLog ((orderedUpperFusionLog carrier z).map (reindexEvent e)) =
      FusionLogAllR.rightFusionLog (AllRTransfer.packetToZMod (reindexPacket e carrier))
        (z.map (fun a => ZMod.finEquiv n (e.symm a))) := by
  induction z generalizing carrier with
  | nil => rfl
  | cons a rest ih =>
      simp only [orderedUpperFusionLog, List.map_cons, reindexEvent, Bool.not_true,
        AllRTransfer.lowerLog, List.filterMap_cons, reindexPacket_singleton,
        reindexPacket_union, AllRTransfer.packetToZMod_union,
        packetToZMod_singleton, FusionLogAllR.rightFusionLog]
      have hcarrier :
          AllRTransfer.packetToZMod (reindexPacket e (carrier ∪ {a})) =
            AllRTransfer.packetToZMod (reindexPacket e carrier) ∪
              {ZMod.finEquiv n (e.symm a)} := by
        rw [reindexPacket_union, AllRTransfer.packetToZMod_union,
          reindexPacket_singleton, packetToZMod_singleton]
      have htail := ih (carrier ∪ {a})
      rw [hcarrier] at htail
      exact congrArg (List.cons _) htail

theorem delayed_log_reindex_of_order {n : Nat} [NeZero n] (z : List (Fin n))
    (e : Fin n ≃ Fin n)
    (horder : z.map (fun a => ZMod.finEquiv n (e.symm a)) =
      (0 : ZMod n) :: 1 :: FusionLogAllR.allRPartners n) :
    AllRTransfer.lowerLog
      ((delayedUpperFusionLog z).map (reindexEvent e)) =
      FusionLogAllR.allRLog n := by
  cases z with
  | nil => simp at horder
  | cons a rest =>
      have hhead : ZMod.finEquiv n (e.symm a) = 0 := by
        simpa using congrArg List.head? horder
      have htail : rest.map (fun a => ZMod.finEquiv n (e.symm a)) =
          (1 : ZMod n) :: FusionLogAllR.allRPartners n := by
        simpa using congrArg List.tail horder
      change AllRTransfer.lowerLog
        ((orderedUpperFusionLog {a} rest).map (reindexEvent e)) = _
      rw [ordered_log_reindex, reindexPacket_singleton, packetToZMod_singleton,
        hhead, htail]
      rfl

theorem delayed_log_reindex {n : Nat} [NeZero n] (z : List (Fin n))
    (hlen : z.length = n) (hnodup : z.Nodup) (hn : 1 < n) :
    AllRTransfer.lowerLog
      ((delayedUpperFusionLog z).map (reindexEvent (orderEquiv z hlen hnodup))) =
      FusionLogAllR.allRLog n := by
  apply delayed_log_reindex_of_order
  let e := orderEquiv z hlen hnodup
  have hz := full_order_eq_map z hlen hnodup
  change z = (List.finRange n).map e at hz
  have hfin : (List.finRange n).map (fun a => ZMod.finEquiv n a) =
      (List.range n).map (fun (i : Nat) => (i : ZMod n)) := by
    apply List.ext_getElem
    · simp
    · intro i hi hi'
      have hin : i < n := by simpa using hi
      apply ZMod.val_injective
      cases n with
      | zero => omega
      | succ n =>
          have hi1 : i < n + 1 := by omega
          simp [ZMod.finEquiv, ZMod.val_natCast, Nat.mod_eq_of_lt hi1,
            List.getElem_map, List.getElem_finRange, List.getElem_range]
          rfl
  have hsplit : (List.range n).map (fun (i : Nat) => (i : ZMod n)) =
      (0 : ZMod n) :: 1 :: FusionLogAllR.allRPartners n := by
    have hn2 : n - 2 + 2 = n := by omega
    have hrange : List.range n =
        0 :: 1 :: (List.range (n - 2)).map (fun i => i + 2) := by
      simpa only [hn2] using range_split_two (n - 2)
    have hbase := congrArg (List.map (fun i : Nat => (i : ZMod n))) hrange
    simpa [FusionLogAllR.allRPartners, List.map_map, Function.comp_def,
      Nat.add_comm] using hbase
  change z.map (fun a => ZMod.finEquiv n (e.symm a)) = _
  rw [hz, List.map_map]
  simpa [Function.comp_def, hfin] using hsplit

theorem asLower_packed (z : List (Fin n)) (hlen : z.length = n)
    (hnodup : z.Nodup) {P : Placement n}
    (packed : ∀ i : Fin n, packetAt P true i = {z[i.val]'(by omega)}) :
    asLower (orderEquiv z hlen hnodup) P = seed n := by
  funext i
  have hi : P (orderEquiv z hlen hnodup i) = (true, i) := by
    apply (mem_packetAt _ _ _ _).mp
    rw [packed]
    simp [orderEquiv_apply]
  simp [asLower, hi, seed]

/-- At the actual first-fusion cut, reindexing by the specified transfer
order gives precisely the single-ring singleton seed. -/
theorem loading_stop_asLower_seed
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    asLower (orderEquiv (a :: b :: rest) hlen hnodup) cut.stop = seed n :=
  asLower_packed _ hlen hnodup (cut.stop_packed_sites hlen hnodup terminal)

theorem loading_suffix_run
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q) :
    runLogged n hn cut.stop (.d true :: cut.tail) =
      some (Q, delayedUpperFusionLog (a :: b :: rest)) := by
  simp only [runLogged, cut.fusion.1, Option.bind_some, cut.tail_run,
    Option.map_some, cut.fusion.2]
  rfl

theorem loading_suffix_no_transfer
    {n : Nat} {hn : 1 < n} {a b : Fin n} {rest : List (Fin n)}
    {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q) :
    .v ∉ .d true :: cut.tail := by
  have hc := AllRTransfer.runLogged_transfer_count n hn (loading_suffix_run cut)
  have hzero : logTransferCount (delayedUpperFusionLog (a :: b :: rest)) = 0 := by
    simp [delayedUpperFusionLog]
  rw [hzero] at hc
  exact List.count_eq_zero.mp hc.symm

/-- Exact placement and ordered-log projection of the *actual* upper suffix,
starting with its first effective fusion. -/
theorem loading_suffix_projection {n : Nat} [NeZero n] {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ]) :
    FusionLogAllR.completeFusionLog (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n)
        (upperWord (.d true :: cut.tail)) = FusionLogAllR.allRLog n ∧
      (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n)
        (upperWord (.d true :: cut.tail))).placed =
          AllRTransfer.lowerView (asLower (orderEquiv (a :: b :: rest) hlen hnodup) Q) := by
  obtain ⟨hp, hl⟩ := upperWord_simulation hn (orderEquiv (a :: b :: rest) hlen hnodup)
    (FusionLogAllR.allRSelectedPair n) (loading_stop_asLower_seed cut hlen hnodup terminal)
    (loading_suffix_no_transfer cut) (loading_suffix_run cut)
  exact ⟨hl.trans (delayed_log_reindex _ hlen hnodup hn), hp⟩

theorem lowerView_full_upper_phase {n : Nat} [NeZero n]
    (e : Fin n ≃ Fin n) {Q : Placement n} {q : Fin n}
    (hQ : ∀ a, Q a = (true, q)) :
    AllRTransfer.lowerView (asLower e Q) = phaseEndpoint (ZMod.finEquiv n q) := by
  funext x
  let site : Fin n := ⟨x.val, ZMod.val_lt x⟩
  have hval : (ZMod.finEquiv n q).val = q.val := by
    cases n with
    | zero => exact (NeZero.ne 0 rfl).elim
    | succ n => rfl
  have hsite : site = q ↔ x = ZMod.finEquiv n q := by
    constructor
    · intro h
      apply ZMod.val_injective
      simpa only [hval] using congrArg Fin.val h
    · intro h
      apply Fin.ext
      have hv := congrArg ZMod.val h
      simpa only [hval] using hv
  have hp : packetAt (asLower e Q) false site =
      if x = ZMod.finEquiv n q then Finset.univ else ∅ := by
    by_cases hx : x = ZMod.finEquiv n q
    · rw [if_pos hx]
      ext a
      simp [asLower, hQ, site, (hsite.mpr hx)]
    · rw [if_neg hx]
      ext a
      have hne : q ≠ site := Ne.symm (hsite.not.mpr hx)
      simp [asLower, hQ, hne]
  change (if packetAt (asLower e Q) false site = ∅ then none
    else some (packetAt (asLower e Q) false site)).map AllRTransfer.packetToZMod =
      (if x = ZMod.finEquiv n q then some Finset.univ else none)
  by_cases hx : x = ZMod.finEquiv n q
  · rw [if_pos hx] at hp
    have hu : (Finset.univ : Finset (Fin n)) ≠ ∅ := by
      exact Finset.univ_nonempty.ne_empty
    simp [hp, hx, hu]
  · rw [if_neg hx] at hp
    simp [hp, hx]

theorem phaseEndpoint_rotate {n : Nat} [NeZero n]
    (q j : ZMod n) :
    RegisteredAbsorptionChains.rotate j (phaseEndpoint q) = phaseEndpoint (q + j) := by
  funext x
  simp [RegisteredAbsorptionChains.rotate, phaseEndpoint, sub_eq_iff_eq_add]

/-- Normalize only the final physical phase. The prefix of this single-ring
word is exactly the upper-letter projection of the actual raw suffix. -/
theorem loading_suffix_to_allR {n : Nat} [NeZero n] {hn : 1 < n}
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n hn a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (q : Fin n) (hQ : ∀ atom, Q atom = (true, q)) :
    FusionLogAllR.RealizesAllR (n := n)
      (upperWord (.d true :: cut.tail) ++
        RegisteredAbsorptionChains.pWord (n - 1 - q.val)) := by
  obtain ⟨hlog, hview⟩ := loading_suffix_projection cut hlen hnodup terminal
  rw [lowerView_full_upper_phase _ hQ] at hview
  constructor
  · rw [FusionLogAllR.completeFusionLog_append, hlog]
    have ht := (FusionLogAllR.completeFusionLog_eq_nil_iff_fusionFree _ _ _).mpr
      (RegisteredAbsorptionChains.fusionFree_pWord
        (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
          (RegisteredAbsorptionChains.singletonExecution n)
          (upperWord (.d true :: cut.tail))) (n - 1 - q.val))
    simp [ht]
  · rw [RegisteredAbsorptionChains.run_append, RegisteredAbsorptionChains.run_pWord]
    change RegisteredAbsorptionChains.rotate ((n - 1 - q.val : Nat) : ZMod n)
      ((RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n)
        (upperWord (.d true :: cut.tail))).placed) = _
    have hview' : (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
      (RegisteredAbsorptionChains.singletonExecution n)
      (upperWord (.d true :: cut.tail))).1 =
        phaseEndpoint (ZMod.finEquiv n q) := by simpa using hview
    rw [hview', phaseEndpoint_rotate]
    have hcast : ZMod.finEquiv n q = (q.val : ZMod n) := by
      cases n with
      | zero => exact (NeZero.ne 0 rfl).elim
      | succ n =>
          apply ZMod.val_injective
          rw [ZMod.finEquiv, ZMod.val_natCast_of_lt q.isLt]
          rfl
    have hsum : q.val + (n - 1 - q.val) = n - 1 := by omega
    rw [hcast, ← Nat.cast_add, hsum]
    rfl

/-- The upper suffix is charged separately from the loading window. The
first effective upper fusion belongs to this suffix and is counted here. -/
theorem loading_suffix_cost_lower_bound {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (cut : DelayedUpperLoadingPrefix n (by omega) a b rest word Q)
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (q : Fin n) (hQ : ∀ atom, Q atom = (true, q)) :
    (3 * n * (n - 1)) / 2 - n + q.val ≤
      (upperWord (.d true :: cut.tail)).length := by
  have h := (loading_suffix_to_allR cut hlen hnodup terminal q hQ).word_length_lower_bound hn
  simp only [List.length_append, FusionLogCompression.pWord_length] at h
  have hd : n - 1 - q.val + q.val = n - 1 := by omega
  have hq : q.val ≤ n - 1 := by omega
  have hA : n ≤ (3 * n * (n - 1)) / 2 := by
    apply (Nat.le_div_iff_mul_le (by decide : 0 < 2)).mpr
    have hn1 : 2 ≤ n - 1 := by omega
    calc
      n * 2 ≤ n * (n - 1) := Nat.mul_le_mul_left n hn1
      _ ≤ 3 * (n * (n - 1)) := by
        nlinarith [Nat.zero_le (n * (n - 1))]
      _ = 3 * n * (n - 1) := by ring
  omega

end UpperAllR

/-- The loading rotations and the all-R suffix are disjoint pieces of the
same raw word. Lower preparation and transfers are charged by letter type. -/
theorem delayedChain_total_cost_lower_bound {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (q : Fin n) (hQ : ∀ atom, Q atom = (true, q))
    (hexec : runLogged n (by omega) (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    lowerExtractionCost n (by omega) (a :: b :: rest) +
      n * (n - 1) + (3 * n * (n - 1)) / 2 + q.val ≤ word.length := by
  obtain ⟨cut⟩ := delayedUpperLoadingPrefix_of_runLogged n (by omega) a b rest hexec
  have hlower := delayedChain_lowerExtractionCost_lower_bound n (by omega)
    (a :: b :: rest) hlen hnodup hexec
  have hload := cut.loading_rotations_lower_bound hlen hnodup terminal
  have hsuffix := UpperAllR.loading_suffix_cost_lower_bound hn cut hlen hnodup terminal q hQ
  have htransfer := AllRTransfer.runLogged_transfer_count n (by omega) hexec
  rw [delayedUpperChainLog_transfer_count, hlen] at htransfer
  have hupper : cut.word.count (.p true) +
      (UpperAllR.upperWord (.d true :: cut.tail)).length ≤
        word.count (.p true) + word.count (.d true) := by
    have he := congrArg (fun w : List Letter => w.count (.p true) + w.count (.d true))
      cut.word_eq
    rw [UpperAllR.upperWord_length]
    simp only [List.count_append] at he
    simp at he ⊢
    omega
  have hcount := raw_letter_count_partition word
  have hA : n ≤ (3 * n * (n - 1)) / 2 := by
    apply (Nat.le_div_iff_mul_le (by decide : 0 < 2)).mpr
    have hn1 : 2 ≤ n - 1 := by omega
    calc
      n * 2 ≤ n * (n - 1) := Nat.mul_le_mul_left n hn1
      _ ≤ 3 * (n * (n - 1)) := by omega
      _ = 3 * n * (n - 1) := by ring
  omega

/-- Closed-form lower half of the delayed-chain exact-cost conjecture. An
attaining guarded lift of an optimal extraction path is not assumed here. -/
theorem delayedChain_cost_lower_bound_closed {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {a b : Fin n} {rest : List (Fin n)} {word : List Letter} {Q : Placement n}
    (hlen : (a :: b :: rest).length = n)
    (hnodup : (a :: b :: rest).Nodup)
    (terminal : cyclicSignature Q true = [Finset.univ])
    (q : Fin n) (hQ : ∀ atom, Q atom = (true, q))
    (hexec : runLogged n (by omega) (seed n) word =
      some (Q, delayedUpperChainLog (a :: b :: rest))) :
    lowerExtractionCost n (by omega) (a :: b :: rest) +
      (5 * n * (n - 1)) / 2 + q.val ≤ word.length := by
  have h := delayedChain_total_cost_lower_bound hn hlen hnodup terminal q hQ hexec
  have he : 5 * n * (n - 1) = 2 * (n * (n - 1)) + 3 * n * (n - 1) := by ring
  omega

end RSR2History
