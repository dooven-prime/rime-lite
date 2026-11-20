import RSR2History.PortFacingExtraction
import RSR2History.ReservedGeometry

/-! Pure extraction prefixes preserve the restricted source cycle.  The
same-prefix interface applies to arbitrary alternative preparations and
retains directed adjacency even when only two live packets remain. -/
namespace RSR2History
open RSR2.Parametric

private def keepsPacket (z : List (Fin n)) (B : Finset (Fin n)) : Bool :=
  decide (∀ a ∈ z, B ≠ {a})

private theorem keepsPacket_nil : keepsPacket ([] : List (Fin n)) = fun _ => true := by
  funext B
  simp [keepsPacket]

private theorem portFacingPackets_nodup (c : LowerConfiguration n) :
    (portFacingPackets c).Nodup := by
  unfold portFacingPackets stripEmpty
  change List.Pairwise (fun A B => A ≠ B) _
  rw [List.pairwise_filter, List.pairwise_iff_getElem]
  intro i j hi hj hij hne _ heq
  have hn : (extractionSlots c)[i] ≠ ∅ := by simpa using hne
  obtain ⟨a, ha⟩ := Finset.nonempty_iff_ne_empty.mpr hn
  have hb : a ∈ (extractionSlots c)[j] := heq ▸ ha
  rw [extractionSlots_getElem] at ha hb
  have hp := (mem_extractionPacketAt _ _ _).mp ha
  have hq := (mem_extractionPacketAt _ _ _).mp hb
  have he : i = j := by
    have he := hp.symm.trans hq
    simpa only [Option.some.injEq, Fin.ext_iff] using he
  omega

/-- The packet cycle of a pure extraction path is exactly the initial
cycle with its specified singleton deletions removed, up to rotation. -/
theorem LowerExtractionPath.restricted_packet_cycle
    {n : Nat} {hn : 1 < n} {c d : LowerConfiguration n}
    {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) :
    (portFacingPackets d).IsRotated
      ((portFacingPackets c).filter (keepsPacket z)) := by
  induction path with
  | refl c => simpa [keepsPacket_nil] using List.IsRotated.refl (portFacingPackets c)
  | rotate c =>
      obtain ⟨k, _, hk⟩ := portFacingPackets_rotate n hn c
      simpa [keepsPacket_nil] using (show (portFacingPackets (lowerRotate n hn c)).IsRotated
        (portFacingPackets c) from ⟨k, hk⟩)
  | slide c empty occupied =>
      simpa [keepsPacket_nil, portFacingPackets_slide n hn c empty] using
        List.IsRotated.refl (portFacingPackets c)
  | delete c a atPort singleton =>
      obtain ⟨tail, hbefore, hafter⟩ := portFacingPackets_delete hn c a atPort singleton
      have hnot : ({a} : Finset (Fin n)) ∉ tail := by
        have hnd := portFacingPackets_nodup c
        rw [hbefore] at hnd
        exact (List.nodup_cons.mp hnd).1
      have hf : tail.filter (keepsPacket [a]) = tail := by
        apply List.filter_eq_self.mpr
        intro B hB
        simp only [keepsPacket, List.mem_singleton, forall_eq, decide_eq_true_eq]
        intro he
        exact hnot (he ▸ hB)
      have hhead : keepsPacket [a] ({a} : Finset (Fin n)) = false := by
        simp [keepsPacket]
      rw [hbefore, List.filter_cons, hhead]
      simp only [Bool.false_eq_true, ↓reduceIte]
      rw [hf, hafter]
  | @trans c d e u v k l first second ihFirst ihSecond =>
      have hfilter := cyclic_filter ihFirst (keepsPacket v)
      have he : ((portFacingPackets c).filter (keepsPacket u)).filter (keepsPacket v) =
          (portFacingPackets c).filter (keepsPacket (u++v)) := by
        rw [List.filter_filter]
        congr 1
        funext B
        apply Bool.eq_iff_iff.mpr
        simp only [keepsPacket, Bool.and_eq_true, decide_eq_true_eq, List.mem_append]
        constructor
        · rintro ⟨hv, hu⟩ a (ha | ha)
          · exact hu a ha
          · exact hv a ha
        · intro h
          exact ⟨fun a ha => h a (Or.inr ha), fun a ha => h a (Or.inl ha)⟩
      exact ihSecond.trans (he ▸ hfilter)

/-- Alternative implementations of precisely the same pure deletion prefix
have identical named packet cycles. -/
theorem LowerExtractionPath.same_prefix_packet_cycle
    {n : Nat} {hn : 1 < n} {c d e : LowerConfiguration n}
    {z : List (Fin n)} {k l : Nat}
    (first : LowerExtractionPath n hn c z d k)
    (second : LowerExtractionPath n hn c z e l) :
    (portFacingPackets d).IsRotated (portFacingPackets e) :=
  first.restricted_packet_cycle.trans second.restricted_packet_cycle.symm


private def prefixPlacement (hn : 1 < n) (c : LowerConfiguration n) : Placement n :=
  fun a => match c a with
    | some q => (false,q)
    | none => (true,site0 n (by omega))

private theorem prefix_packet (hn : 1 < n) (c : LowerConfiguration n) (q : Fin n) :
    packetAt (prefixPlacement hn c) false q = extractionPacketAt c q := by
  ext a
  cases h : c a <;> simp [prefixPlacement, extractionPacketAt, mem_packetAt, h]

private theorem prefix_cycle (hn : 1 < n) (c : LowerConfiguration n) :
    cyclicSignature (prefixPlacement hn c) false = portFacingPackets c := by
  unfold cyclicSignature portFacingPackets layerSlots extractionSlots
  congr 1
  apply congrArg List.ofFn
  funext q
  exact prefix_packet hn c q

private theorem singleton_packet_of_valid {c : LowerConfiguration n}
    (hc : c.Valid) (a : Fin n) (q : Fin n) (ha : c a = some q) :
    extractionPacketAt c q = {a} := by
  ext b
  simp only [mem_extractionPacketAt, Finset.mem_singleton]
  exact ⟨fun hb => hc b a q hb ha, fun hb => hb ▸ ha⟩

private theorem portFacingPackets_first_two {n : Nat} {hn : 1 < n}
    {c : LowerConfiguration n} {a b : Fin n} (hc : c.Valid)
    (ha : c a = some (site0 n (by omega))) (hb : c b = some (site1 n hn)) :
    ∃ tail, portFacingPackets c = {a} :: {b} :: tail := by
  have hslots : extractionSlots c =
      {a} :: {b} :: (extractionSlots c).drop 2 := by
    apply List.ext_getElem
    · simp; omega
    · intro i hi hi'
      cases i with
      | zero => simpa [site0] using singleton_packet_of_valid hc a _ ha
      | succ i =>
          cases i with
          | zero => simpa [site1] using singleton_packet_of_valid hc b _ hb
          | succ i => simp [Nat.add_comm, Nat.add_left_comm]
  refine ⟨stripEmpty ∅ ((extractionSlots c).drop 2), ?_⟩
  unfold portFacingPackets
  conv_lhs => rw [hslots]
  simp [stripEmpty]

/-- A directed physical adjacency in one realization of a singleton deletion
prefix forces the corresponding directed empty arc in every alternative
realization. Both ordered bindings of the two-packet case are retained. -/
theorem LowerExtractionPath.same_prefix_fusion_gap
    {n : Nat} {hn : 1 < n} {c d : LowerConfiguration n}
    {z : List (Fin n)} {k l : Nat} {a b : Fin n}
    (first : LowerExtractionPath n hn (lowerExtractionSeed n) z c k)
    (second : LowerExtractionPath n hn (lowerExtractionSeed n) z d l)
    (ha : c a = some (site0 n (by omega)))
    (hb : c b = some (site1 n hn))
    (db : d b = some (site0 n (by omega))) :
    ∃ q : Fin n, d a = some q ∧ q ≠ site0 n (by omega) ∧
      ∀ site : Fin n, q.val < site.val → ∀ x, d x ≠ some site := by
  have : NeZero n := ⟨by omega⟩
  have cvalid := first.valid (lowerExtractionSeed_valid n)
  have dvalid := second.valid (lowerExtractionSeed_valid n)
  have hab : a ≠ b := by
    intro he
    have hp := ha.symm.trans (he ▸ hb)
    simp [site0, site1, Fin.ext_iff] at hp
  have hasupport : c a ≠ none := by simp [ha]
  have hdel : a ∉ z := (first.support a).mp hasupport |>.2
  have halive : d a ≠ none := (second.support a).mpr ⟨by simp [lowerExtractionSeed],hdel⟩
  obtain ⟨q, hq⟩ := Option.ne_none_iff_exists'.mp halive
  have hqne : q ≠ site0 n (by omega) := by
    intro he
    exact hab (dvalid a b _ (he ▸ hq) db)
  have hqpos : 0 < q.val := by
    by_contra he
    have : q = site0 n (by omega) := Fin.ext (by simpa [site0] using (show q.val = 0 by omega))
    exact hqne this
  obtain ⟨tail, hcycle⟩ := portFacingPackets_first_two cvalid ha hb
  have hsame := first.same_prefix_packet_cycle second
  have hnew : (cyclicSignature (prefixPlacement hn d) false).IsRotated
      (({a} : Finset (Fin n)) :: {b} :: tail) := by
    rw [prefix_cycle]
    rw [hcycle] at hsame
    exact hsame.symm
  have hdA : packetAt (prefixPlacement hn d) false (zsite (q.val : ZMod n)) = {a} := by
    rw [zsite_cast, prefix_packet]
    exact singleton_packet_of_valid dvalid a q hq
  have hdB : packetAt (prefixPlacement hn d) false (zsite (0 : ZMod n)) = {b} := by
    have hzero : zsite (0 : ZMod n) = site0 n (by omega) := by
      apply Fin.ext
      simp [zsite, site0]
    rw [hzero, prefix_packet]
    exact singleton_packet_of_valid dvalid b _ db
  obtain ⟨f,hfn,hpos,hholes⟩ := cyclic_parents_gap hn (prefixPlacement hn d) false
    (q.val : ZMod n) 0 {a} {b} tail hdA hdB (by simp) (by simp) hnew
  have hmod : (q.val+1+f) % n = 0 := by
    have hecast : ((q.val+1+f : Nat) : ZMod n) = 0 := by
      push_cast
      exact hpos.symm
    have hv := congrArg ZMod.val hecast
    simpa only [ZMod.val_natCast, ZMod.val_zero] using hv
  have hsum : q.val+1+f = n := by
    by_cases hlt : q.val+1+f < n
    · rw [Nat.mod_eq_of_lt hlt] at hmod
      omega
    · have hbound : q.val+1+f-n < n := by omega
      have hh := Nat.mod_eq_sub_mod (by omega : n ≤ q.val+1+f)
      rw [hh, Nat.mod_eq_of_lt hbound] at hmod
      omega
  refine ⟨q,hq,hqne,?_⟩
  intro site hsite x hx
  let j := n-site.val
  have hj : 1 ≤ j := by dsimp [j]; omega
  have hjf : j ≤ f := by dsimp [j]; omega
  have he : (0 : ZMod n) - (j : ZMod n) = (site.val : ZMod n) := by
    have hjval : j+site.val = n := by dsimp [j]; omega
    have hz := congrArg (fun x : Nat => (x : ZMod n)) hjval
    push_cast at hz
    simp only [ZMod.natCast_self] at hz
    linear_combination -hz
  have hempty := hholes j hj hjf
  rw [he, zsite_cast, prefix_packet] at hempty
  have hmem : x ∈ extractionPacketAt d site := by simpa using hx
  rw [hempty] at hmem
  simp at hmem

end RSR2History
