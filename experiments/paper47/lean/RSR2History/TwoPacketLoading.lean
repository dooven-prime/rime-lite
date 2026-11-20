import RSR2History.TwoTransferStructure

/-! Guarded two-packet loading, retaining either requested upper port binding. -/

namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

theorem CyclicEventEdge.transfer_to_empty_short (hn : 1 < n)
    {P Q : Placement n} {B : Finset (Fin n)}
    (edge : CyclicEventEdge P (.transfer B) Q) (hu : cyclicSignature P true = []) :
    ∃ R word, runLogged n hn P word = some (R, [.transfer B]) ∧
      SameCyclicSignatures R Q ∧ word.length ≤ n := by
  obtain ⟨hb, hmem⟩ := edge.transfer_packet_mem
  obtain ⟨q, hq⟩ := packet_site_of_mem_signature P false hmem
  let S := phaseShift P false (-q)
  have hp := runLogged_phase hn P false (-q)
  have hSsame := runLogged_empty_signatures n hn _ hp
  have hSU : cyclicSignature S true = [] :=
    List.isRotated_nil_iff.mp ((hSsame true).symm.trans (hu ▸ .refl _))
  have hSB : packetAt S false (site0 n (by omega)) = B := by
    change packetAt (phaseShift P false (-q)) false _ = B
    rw [← zsite_zero, packetAt_phaseShift]
    simpa using hq
  have hg : liftGuard n (by omega) S := by
    refine ⟨(packetAt_nonempty _ _ _).mp (hSB ▸ hb), ?_⟩
    intro h
    have hm := packetAt_mem_cyclicSignature S true _ ((packetAt_nonempty _ _ _).mpr h)
    rw [hSU] at hm
    exact List.not_mem_nil hm
  let R := liftPacket n (by omega) S
  have hs : step n hn S .v = some R :=
    (step_v_eq_some_iff n hn S R).mpr ⟨hg, rfl⟩
  have ev : EventStep n hn S R .v (.transfer B) := ⟨hs, by simp [emittedEvents, hSB]⟩
  have e := ev.cyclicEventEdge
  have hupperR := e.transfer_upper_from_empty hSU
  have hupperQ := edge.transfer_upper_from_empty hu
  refine ⟨R, pWord false (-q).val ++ [.v], ?_, ?_, ?_⟩
  · simp [runLogged_append, hp, ev.runLogged, S]
  · intro layer
    cases layer with
    | false => exact e.lower_target_compatible edge (hSsame false).symm
    | true => rw [hupperR, hupperQ]
  · have hlt := ZMod.val_lt (-q)
    simp only [List.length_append, List.length_singleton, pWord, List.length_replicate]
    omega

noncomputable def layerSplit (B : Finset (Fin n)) (lower upper : ZMod n) : Placement n :=
  fun a => if a ∈ B then (true, zsite upper) else (false, zsite lower)

noncomputable def upperSplit (B : Finset (Fin n)) (first second : ZMod n) : Placement n :=
  fun a => if a ∈ B then (true, zsite first) else (true, zsite second)

theorem layerSplit_phase_lower (B : Finset (Fin n)) (lo up amount : ZMod n) :
    phaseShift (layerSplit B lo up) false amount = layerSplit B (lo+amount) up := by
  classical
  funext a
  by_cases ha : a ∈ B <;> simp [layerSplit, phaseShift, ha]

theorem layerSplit_phase_upper (B : Finset (Fin n)) (lo up amount : ZMod n) :
    phaseShift (layerSplit B lo up) true amount = layerSplit B lo (up+amount) := by
  classical
  funext a
  by_cases ha : a ∈ B <;> simp [layerSplit, phaseShift, ha]

theorem upperSplit_phase (B : Finset (Fin n)) (q r amount : ZMod n) :
    phaseShift (upperSplit B q r) true amount = upperSplit B (q+amount) (r+amount) := by
  classical
  funext a
  by_cases ha : a ∈ B <;> simp [upperSplit, phaseShift, ha]

private theorem complement_iff {A B : Finset (Fin n)}
    (hd : Disjoint A B) (hc : A ∪ B = Finset.univ) (a : Fin n) : a ∈ B ↔ a ∉ A := by
  constructor
  · intro hb ha
    exact Finset.disjoint_left.mp hd ha hb
  · intro ha
    have hm : a ∈ A ∪ B := by rw [hc]; simp
    exact (Finset.mem_union.mp hm).resolve_left ha

theorem layerSplit_of_packet_sites {P : Placement n} {A B : Finset (Fin n)}
    (hd : Disjoint A B) (hc : A ∪ B = Finset.univ) (lo up : ZMod n)
    (hl : packetAt P false (zsite lo) = B) (hu : packetAt P true (zsite up) = A) :
    P = layerSplit A lo up := by
  classical
  funext a
  by_cases ha : a ∈ A
  · simpa [layerSplit, ha] using (mem_packetAt P true (zsite up) a).mp (hu ▸ ha)
  · have hb := (complement_iff hd hc a).mpr ha
    simpa [layerSplit, ha] using (mem_packetAt P false (zsite lo) a).mp (hl ▸ hb)

theorem upperSplit_swap (A B : Finset (Fin n)) (hd : Disjoint A B)
    (hc : A ∪ B = Finset.univ) (q r : ZMod n) :
    upperSplit A q r = upperSplit B r q := by
  classical
  funext a
  by_cases ha : a ∈ A <;> simp [upperSplit, complement_iff hd hc a, ha]

theorem upperSplit_fuse_ports (hn : 1 < n) (A B : Finset (Fin n))
    (ha : A.Nonempty) (hb : B.Nonempty) (hd : Disjoint A B)
    (hc : A ∪ B = Finset.univ) :
    runLogged n hn (upperSplit A 0 1) [.d true] =
      some ((fun _ => (true, site0 n (by omega))), [.fusion true A B Finset.univ]) := by
  classical
  have hne : (0 : ZMod n) ≠ 1 := by simpa using (gap_sites_distinct hn 0 0 (by omega)).2
  have hA : packetAt (upperSplit A 0 1) true (site0 n (by omega)) = A := by
    ext a
    by_cases hm : a ∈ A <;> simp [packetAt, upperSplit, hm, hne.symm, ← zsite_zero]
  have hB : packetAt (upperSplit A 0 1) true (site1 n hn) = B := by
    rw [← zsite_one hn]
    ext a
    by_cases hm : a ∈ A <;>
      simp [packetAt, upperSplit, complement_iff hd hc a, hm, hne, ← zsite_zero]
  have hbusy : occupiedAt (upperSplit A 0 1) true (site0 n (by omega)) ∧
      occupiedAt (upperSplit A 0 1) true (site1 n hn) :=
    ⟨(packetAt_nonempty _ _ _).mp (by rwa [hA]),
      (packetAt_nonempty _ _ _).mp (by rwa [hB])⟩
  have hcollapsed : collapse n hn (upperSplit A 0 1) true =
      fun _ => (true, site0 n (by omega)) := by
    funext a
    by_cases hm : a ∈ A <;>
      simp [collapse, upperSplit, hm, hne, zsite_one hn]
  simp [runLogged, step_d, hcollapsed, emittedEvents, hbusy, hA, hB, hc]

def pairArrivalSite (firstLeft : Bool) : ZMod n := if firstLeft then -1 else 1
def pairFusionWord (firstLeft : Bool) : List Letter :=
  if firstLeft then [.p true, .d true] else [.d true]
def pairFinalEvent (firstLeft : Bool) (A B : Finset (Fin n)) : EffectiveEvent n :=
  if firstLeft then .fusion true A B Finset.univ else .fusion true B A Finset.univ

theorem pairArrivalSite_ne_zero (hn : 1 < n) (side : Bool) : pairArrivalSite (n := n) side ≠ 0 := by
  have h : (1 : ZMod n) ≠ 0 := by intro he; have := ZMod.one_eq_zero_iff.mp he; omega
  cases side <;> simpa [pairArrivalSite] using h

theorem pair_load_finish (hn : 1 < n) (A B : Finset (Fin n))
    (ha : A.Nonempty) (hb : B.Nonempty) (hd : Disjoint A B)
    (hc : A ∪ B = Finset.univ) (side : Bool) :
    runLogged n hn (layerSplit A 0 (pairArrivalSite side)) ([.v] ++ pairFusionWord side) =
      some ((fun _ => (true, site0 n (by omega))), [.transfer B, pairFinalEvent side A B]) := by
  classical
  let pos : ZMod n := pairArrivalSite side
  have hpos : pos ≠ 0 := pairArrivalSite_ne_zero hn side
  have hB : packetAt (layerSplit A 0 pos) false (site0 n (by omega)) = B := by
    ext a
    simp [packetAt, layerSplit, complement_iff hd hc a]
  have hnot : ¬ occupiedAt (layerSplit A 0 pos) true (site0 n (by omega)) := by
    rintro ⟨a, he⟩
    change layerSplit A 0 pos a = (true, site0 n (by omega)) at he
    by_cases hm : a ∈ A
    · have hp : zsite pos = site0 n (by omega) := by
        simpa [layerSplit, hm] using congrArg Prod.snd he
      exact hpos (by simpa only [← zsite_zero, zsite_inj] using hp)
    · simp [layerSplit, hm] at he
  have hg : liftGuard n (by omega) (layerSplit A 0 pos) :=
    ⟨(packetAt_nonempty _ _ _).mp (by rwa [hB]), hnot⟩
  have hv : runLogged n hn (layerSplit A 0 pos) [.v] =
      some (upperSplit A pos 0, [.transfer B]) := by
    have hstep : step n hn (layerSplit A 0 pos) .v = some (upperSplit A pos 0) := by
      apply (step_v_eq_some_iff n hn _ _).mpr
      refine ⟨hg, ?_⟩
      funext a
      by_cases hm : a ∈ A <;> simp [liftPacket, layerSplit, upperSplit, hm]
    simp [runLogged, hstep, emittedEvents, hB]
  have hf : runLogged n hn (upperSplit A pos 0) (pairFusionWord side) =
      some ((fun _ => (true, site0 n (by omega))), [pairFinalEvent side A B]) := by
    cases side with
    | false =>
        have hs := upperSplit_swap A B hd hc 1 0
        simpa [pairFusionWord, pairFinalEvent, pos, pairArrivalSite, hs] using
          upperSplit_fuse_ports hn B A hb ha hd.symm (by simpa [Finset.union_comm] using hc)
    | true =>
        have hp := runLogged_pWord hn (upperSplit A (-1) 0) true 1
        have hp' : runLogged n hn (upperSplit A (-1) 0) [.p true] =
            some (upperSplit A 0 1, []) := by
          simpa [pWord, upperSplit_phase] using hp
        change runLogged n hn (upperSplit A (-1) 0) ([.p true] ++ [.d true]) = _
        rw [runLogged_append, hp']
        simp only [Option.bind_some, upperSplit_fuse_ports hn A B ha hb hd hc,
          Option.map_some, List.nil_append, pairFinalEvent, if_true]
  rw [runLogged_append, hv]
  simp only [Option.bind_some, hf, Option.map_some, List.singleton_append]

/-- The lower alignment is charged explicitly. An empty middle log has no
last-fusion port premise, whereas a packet already at port zero saves it. -/
theorem layerSplit_finish_word (hn : 1 < n) (A B : Finset (Fin n))
    (ha : A.Nonempty) (hb : B.Nonempty) (hd : Disjoint A B)
    (hc : A ∪ B = Finset.univ) (lo up : ZMod n) (side : Bool) (q : Fin n) :
    ∃ word, runLogged n hn (layerSplit A lo up) word =
      some ((fun _ => (true, q)), [.transfer B, pairFinalEvent side A B]) ∧
      word.length ≤ (-lo).val + 2*n+1 := by
  let pos : ZMod n := pairArrivalSite side
  let w0 := pWord false (-lo).val
  let w1 := pWord true (pos-up).val
  let w2 := [.v] ++ pairFusionWord side
  let w3 := pWord true (q.val : ZMod n).val
  have h0 : runLogged n hn (layerSplit A lo up) w0 = some (layerSplit A 0 up, []) := by
    simpa only [layerSplit_phase_lower, add_neg_cancel] using
      runLogged_phase hn (layerSplit A lo up) false (-lo)
  have h1 : runLogged n hn (layerSplit A 0 up) w1 = some (layerSplit A 0 pos, []) := by
    simpa only [layerSplit_phase_upper, add_sub_cancel] using
      runLogged_phase hn (layerSplit A 0 up) true (pos-up)
  have h2 : runLogged n hn (layerSplit A 0 pos) w2 =
      some ((fun _ => (true, site0 n (by omega))), [.transfer B, pairFinalEvent side A B]) :=
    pair_load_finish hn A B ha hb hd hc side
  have h3 : runLogged n hn (fun _ => (true, site0 n (by omega))) w3 =
      some ((fun _ => (true, q)), []) := by
    have hp := runLogged_phase hn (fun _ => (true, site0 n (by omega))) true (q.val : ZMod n)
    have he : phaseShift (fun _ : Fin n => (true, site0 n (by omega))) true
        (q.val : ZMod n) = (fun _ => (true, q)) := by
      funext a
      simp [phaseShift, site0]
    rwa [he] at hp
  have h01 : runLogged n hn (layerSplit A lo up) (w0 ++ w1) =
      some (layerSplit A 0 pos, []) := by
    rw [runLogged_append, h0]
    simp only [Option.bind_some, h1, Option.map_some, List.nil_append]
  have h012 : runLogged n hn (layerSplit A lo up) ((w0 ++ w1) ++ w2) =
      some ((fun _ => (true, site0 n (by omega))), [.transfer B, pairFinalEvent side A B]) := by
    rw [runLogged_append, h01]
    simp only [Option.bind_some, h2, Option.map_some, List.nil_append]
  refine ⟨((w0 ++ w1) ++ w2) ++ w3, ?_, ?_⟩
  · rw [runLogged_append, h012]
    simp only [Option.bind_some, h3, Option.map_some, List.append_nil]
  · have hl0 : w0.length = (-lo).val := by simp [w0, pWord]
    have hl1 : w1.length ≤ n-1 := by
      simp only [w1, pWord, List.length_replicate]
      have := ZMod.val_lt (pos-up)
      omega
    have hl2 : w2.length ≤ 3 := by cases side <;> simp [w2, pairFusionWord]
    have hl3 : w3.length ≤ n-1 := by
      simp only [w3, pWord, List.length_replicate]
      have := ZMod.val_lt (q.val : ZMod n)
      omega
    simp only [List.length_append]
    omega

theorem twoPacket_guarded_finish (hn : 1 < n) {P : Placement n}
    (A B : Finset (Fin n)) (ha : A.Nonempty) (hb : B.Nonempty)
    (hd : Disjoint A B) (hc : A ∪ B = Finset.univ)
    (hu : cyclicSignature P true = [A]) (hl : cyclicSignature P false = [B])
    (side : Bool) (q : Fin n) :
    ∃ word, runLogged n hn P word =
      some ((fun _ => (true, q)), [.transfer B, pairFinalEvent side A B]) ∧
      word.length ≤ 3*n := by
  obtain ⟨lo, hlo⟩ := packet_site_of_mem_signature P false (packet := B) (by rw [hl]; simp)
  obtain ⟨up, hup⟩ := packet_site_of_mem_signature P true (packet := A) (by rw [hu]; simp)
  have hP := layerSplit_of_packet_sites hd hc lo up hlo hup
  obtain ⟨word, hr, hlen⟩ := layerSplit_finish_word hn A B ha hb hd hc lo up side q
  have hlt := ZMod.val_lt (-lo)
  exact ⟨word, by rwa [hP], by omega⟩

theorem twoPacket_at_port_guarded_finish (hn : 1 < n) {P : Placement n}
    (A B : Finset (Fin n)) (ha : A.Nonempty) (hb : B.Nonempty)
    (hd : Disjoint A B) (hc : A ∪ B = Finset.univ)
    (hu : cyclicSignature P true = [A]) (hl : packetAt P false (site0 n (by omega)) = B)
    (side : Bool) (q : Fin n) :
    ∃ word, runLogged n hn P word =
      some ((fun _ => (true, q)), [.transfer B, pairFinalEvent side A B]) ∧
      word.length ≤ 2*n+1 := by
  obtain ⟨up, hup⟩ := packet_site_of_mem_signature P true (packet := A) (by rw [hu]; simp)
  have hP := layerSplit_of_packet_sites hd hc 0 up (by simpa using hl) hup
  obtain ⟨word, hr, hlen⟩ := layerSplit_finish_word hn A B ha hb hd hc 0 up side q
  exact ⟨word, by rwa [hP], by simpa using hlen⟩

end RSR2History
