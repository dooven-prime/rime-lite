import RSR2History.CyclicEventDeterminism

/-!
The continuous replay invariant couples physical upper reservations to the
lower named cycle of the same original event prefix. Forest rotations below
are proofs about representations; they emit no raw letters.
-/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

theorem ReservationFrame.rotate
    {k : Nat} {forest next terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservationFrame k forest terminal omega site)
    (same : forest.IsRotated next) : ReservationFrame k next terminal omega site := by
  refine ⟨(cyclic_flatMap same _).perm.symm.trans h.complete,
    h.terminal_order, h.omega_nodup, ?_,
    (cyclic_flatMap same _).symm.trans h.prefix_order, h.site_injective, h.site_index⟩
  intro tree ht
  exact h.subtrees tree (same.perm.mem_iff.mpr ht)

theorem ReservedState.rotate
    {P : Placement n} {k : Nat} {forest next terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site) (same : forest.IsRotated next) :
    ReservedState P k next terminal omega site :=
  h.reframe same.perm (h.frame.rotate same)

theorem ReservedState.congr_upper
    {P Q : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site)
    (same : ∀ a q, Q a = (true, q) ↔ P a = (true, q)) :
    ReservedState Q k forest terminal omega site :=
  ⟨h.frame, h.packet_nonempty, fun a q => (same a q).trans (h.upper_position a q)⟩

/-- Lower cycle synchronization is an independent part of the invariant;
upper reservations alone would not justify the next lower event. -/
structure ReplayCompatible (P reference : Placement n) (k : Nat)
    (forest terminal : List (UpperFusionTree n))
    (omega : List Nat) (site : Nat → Fin n) : Prop where
  reserved : ReservedState P k forest terminal omega site
  lower : (cyclicSignature P false).IsRotated (cyclicSignature reference false)

theorem ReplayCompatible.same_signatures
    {P reference : Placement n} {k : Nat} {forest terminal : List (UpperFusionTree n)}
    {omega : List Nat} {site : Nat → Fin n}
    (h : ReplayCompatible P reference k forest terminal omega site)
    (hmatch : (forestPackets forest).IsRotated (cyclicSignature reference true)) :
    SameCyclicSignatures P reference := by
  intro layer
  cases layer with
  | false => exact h.lower
  | true => exact h.reserved.current_packet_cycle.symm.trans hmatch

def eventReplayCost (n : Nat) : EffectiveEvent n → Nat
  | .fusion _ _ _ _ => 4*n
  | .transfer _ => 2*n+1

section PhysicalReplay
variable [NeZero n]

theorem ReservedState.lower_fusion_word
    (hn : 1 < n) {P : Placement n} {k : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (h : ReservedState P k forest terminal omega site)
    (A B : Finset (Fin n)) (tail : List (Finset (Fin n)))
    (ha : A.Nonempty) (hb : B.Nonempty)
    (hs : (cyclicSignature P false).IsRotated (A :: B :: tail)) :
    ∃ Q word, runLogged n hn P word = some (Q, [.fusion false A B (A ∪ B)]) ∧
      ReservedState Q k forest terminal omega site ∧ word.length ≤ 4*n := by
  obtain ⟨left, hleft⟩ := packet_site_of_mem_signature P false
    (hs.perm.mem_iff.mpr (by simp : A ∈ A :: B :: tail))
  obtain ⟨right, hright⟩ := packet_site_of_mem_signature P false
    (hs.perm.mem_iff.mpr (by simp : B ∈ A :: B :: tail))
  obtain ⟨f, hfn, hgap, hholes⟩ := cyclic_parents_gap hn P false left right A B tail
    hleft hright ha hb hs
  obtain ⟨hrun, hlen⟩ := reservedFusionWord_spec hn P false left right f hfn hgap
    (hleft.symm ▸ ha) (hright.symm ▸ hb) hholes
  refine ⟨_, _, by simpa only [hleft, hright] using hrun, ?_, hlen⟩
  apply h.congr_upper
  intro a q
  have he := packetAt_relocateAt_other P false true (by decide) right left q
  simpa only [mem_packetAt] using
    Iff.of_eq (congrArg (fun packet => a ∈ packet) he)

/-- One actual event is replayed on the current reserved placement. The
future path supplies order frames, not physical or cost assumptions. -/
theorem ReplayCompatible.advance
    (hn : 1 < n) {P reference nextReference : Placement n} {k k' kfinal : Nat}
    {forest next terminal : List (UpperFusionTree n)} {omega : List Nat}
    {site : Nat → Fin n} {event : EffectiveEvent n} {events : List (EffectiveEvent n)}
    (h : ReplayCompatible P reference k forest terminal omega site)
    (edge : CyclicEventEdge reference event nextReference)
    (update : UpperForestStep k forest event k' next)
    (future : UpperForestPath k' next events kfinal terminal) :
    ∃ Q word, runLogged n hn P word = some (Q, [event]) ∧
      ReplayCompatible Q nextReference k' next terminal omega site ∧
      word.length ≤ eventReplayCost n event := by
  have frame := ReservationFrame.of_path future
    (update.complete_leaves h.reserved.frame.complete)
    h.reserved.frame.terminal_order h.reserved.frame.site_injective h.reserved.frame.site_index
  have lift_lower : ∀ Q word, runLogged n hn P word = some (Q, [event]) →
      (cyclicSignature Q false).IsRotated (cyclicSignature nextReference false) := by
    intro Q word hw
    have replayEdge := (cyclicEventEdge_iff_one_event_word n hn P Q event).mpr ⟨word, hw⟩
    exact replayEdge.lower_target_compatible edge h.lower
  cases update with
  | lower A B same =>
      obtain ⟨ha, hb, tail, hs⟩ := edge.fusion_source
      obtain ⟨Q, word, hw, hr, hl⟩ := h.reserved.lower_fusion_word hn A B tail ha hb
        (h.lower.trans hs)
      exact ⟨Q, word, hw, ⟨hr.rotate same, lift_lower Q word hw⟩, hl⟩
  | fusion A B tail before after =>
      have hr := h.reserved.rotate before
      obtain ⟨Q, word, hw, hr', hl⟩ := hr.fusion_word hn (frame.rotate after)
      exact ⟨Q, word, hw, ⟨hr'.rotate after.symm, lift_lower Q word hw⟩, hl⟩
  | transfer packet tail before after =>
      have hp := edge.transfer_packet_mem
      obtain ⟨source, hsource⟩ := packet_site_of_mem_signature P false
        (h.lower.perm.mem_iff.mpr hp.2)
      have hr := h.reserved.rotate before
      have frame' := frame.rotate after
      rw [← hsource] at frame'
      obtain ⟨Q, word, hw, hr', hl⟩ := hr.transfer_word hn source (hsource.symm ▸ hp.1) frame'
      rw [hsource] at hw hr'
      exact ⟨Q, word, hw, ⟨hr'.rotate after.symm, lift_lower Q word hw⟩, hl⟩

end PhysicalReplay
end RSR2History
