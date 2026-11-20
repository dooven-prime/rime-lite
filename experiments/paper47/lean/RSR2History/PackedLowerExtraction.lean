import RSR2History.SingletonTransferCursorLift

/-! Independent lower fusion/extraction paths. Transfer markers have zero lower
cost; their actual `v` letter is paid once by the upper cursor construction.
Configurations may contain multiple atoms at one site; no singleton validity
condition or comparison with `maxLowerExtractionCost` is imposed here.
The actual checkpoint below lifts the next whole-packet transfer and retains
the residual lower path. A complete asynchronous replay and its amortized
lower budget remain separate obligations.
-/
namespace RSR2History
open RSR2.Parametric

def lowerPacket (c : LowerConfiguration n) (q : Fin n) : Finset (Fin n) :=
  Finset.univ.filter (fun a => c a = some q)

def lowerErasePacket (c : LowerConfiguration n) (B : Finset (Fin n)) : LowerConfiguration n :=
  fun a => if a ∈ B then none else c a

theorem lowerPacket_configuration (P : Placement n) (q : Fin n) :
    lowerPacket (lowerConfiguration P) q = packetAt P false q := by
  ext a
  simp [lowerPacket, lowerConfiguration_eq_some]

inductive PackedLowerEvent (n : Nat) (hn : 1 < n) :
    LowerConfiguration n → EffectiveEvent n → LowerConfiguration n → Nat → Prop where
  | fusion (c)
      (left : (lowerPacket c (site0 n (by omega))).Nonempty)
      (right : (lowerPacket c (site1 n hn)).Nonempty) :
      PackedLowerEvent n hn c
        (.fusion false (lowerPacket c (site0 n (by omega))) (lowerPacket c (site1 n hn))
          (lowerPacket c (site0 n (by omega)) ∪ lowerPacket c (site1 n hn)))
        (lowerSlide n hn c) 1
  | extract (c) (nonempty : (lowerPacket c (site0 n (by omega))).Nonempty) :
      PackedLowerEvent n hn c (.transfer (lowerPacket c (site0 n (by omega))))
        (lowerErasePacket c (lowerPacket c (site0 n (by omega)))) 0

inductive PackedLowerPath (n : Nat) (hn : 1 < n) :
    LowerConfiguration n → List (EffectiveEvent n) → LowerConfiguration n → Nat → Prop where
  | prepare {c d cost} (path : LowerExtractionPath n hn c [] d cost) :
      PackedLowerPath n hn c [] d cost
  | event {c d e cost} (step : PackedLowerEvent n hn c e d cost) :
      PackedLowerPath n hn c [e] d cost
  | trans {c d f H K cost rest}
      (first : PackedLowerPath n hn c H d cost) (last : PackedLowerPath n hn d K f rest) :
      PackedLowerPath n hn c (H++K) f (cost+rest)

theorem PackedLowerPath.empty_preparation {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost) :
    H = [] → LowerExtractionPath n hn c [] d cost := by
  induction path with
  | prepare path => exact fun _ => path
  | event step => intro h; cases h
  | trans first last ihFirst ihLast =>
      intro he
      have hh := List.append_eq_nil_iff.mp he
      simpa using (ihFirst hh.1).trans (ihLast hh.2)

theorem PackedLowerPath.split_first_event {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost) :
    ∀ e tail, H = e::tail → ∃ mid next prep eventCost rest,
      LowerExtractionPath n hn c [] mid prep ∧ PackedLowerEvent n hn mid e next eventCost ∧
      PackedLowerPath n hn next tail d rest ∧ cost = prep+eventCost+rest := by
  induction path with
  | prepare path => intro e tail h; cases h
  | @event c d e cost step =>
      intro f tail he
      obtain ⟨rfl, rfl⟩ := List.cons.inj he
      exact ⟨c, d, 0, cost, 0, .refl c, step, .prepare (.refl d), by omega⟩
  | @trans c d f H K cost rest first last ihFirst ihLast =>
      intro e tail he
      cases H with
      | nil =>
          obtain ⟨mid, next, prep, eventCost, rem, hp, hs, hr, hc⟩ := ihLast e tail (by simpa using he)
          exact ⟨mid, next, cost+prep, eventCost, rem,
            by simpa using (first.empty_preparation rfl).trans hp, hs, hr, by omega⟩
      | cons head events =>
          simp only [List.cons_append, List.cons.injEq] at he
          obtain ⟨rfl, rfl⟩ := he
          obtain ⟨mid, next, prep, eventCost, rem, hp, hs, hr, hc⟩ := ihFirst head events rfl
          exact ⟨mid, next, prep, eventCost, rem+rest, hp, hs, hr.trans last, by omega⟩

section ActualCheckpoint
variable {n : Nat} [NeZero n]

omit [NeZero n] in
theorem lowerConfiguration_liftPacket (P : Placement n) (hn : 1 < n) :
    lowerConfiguration (liftPacket n (by omega) P) =
      lowerErasePacket (lowerConfiguration P) (packetAt P false (site0 n (by omega))) := by
  funext a
  by_cases ha : P a = (false, site0 n (by omega))
  · simp [lowerConfiguration, liftPacket, lowerErasePacket, mem_packetAt, ha]
  · simp [lowerConfiguration, liftPacket, lowerErasePacket, mem_packetAt, ha]

theorem lowerConfiguration_cursorTransfer_packet {hn : 1 < n}
    {P Q : Placement n} {cursor target : Fin n} {B : Finset (Fin n)}
    (hrun : runLogged n hn P (cursorTransferWord cursor target) = some (Q,[.transfer B])) :
    lowerConfiguration Q = lowerErasePacket (lowerConfiguration P) B := by
  let R := phaseShift P true ((cursor.val : ZMod n) - target.val)
  have hv : runLogged n hn R [.v] = some (Q,[.transfer B]) := by
    rw [cursorTransferWord, runLogged_append, runLogged_phase] at hrun
    simpa using hrun
  cases hs : step n hn R .v with
  | none => simp [runLogged, hs] at hv
  | some S =>
      have he : S = Q ∧ packetAt R false (site0 n (by omega)) = B := by
        simpa [runLogged, hs, emittedEvents] using hv
      rcases he with ⟨hSQ, hpacket⟩
      obtain ⟨_, hS⟩ := (step_v_eq_some_iff n hn R S).mp hs
      have hS' : S = liftPacket n (by omega) R := by simpa using hS
      rw [← hSQ, hS', lowerConfiguration_liftPacket R hn, hpacket]
      simp only [R, lowerConfiguration_upper_phase]

theorem packed_cursor_extract_checkpoint {hn : 1 < n}
    {P : Placement n} {cursor : Fin n} {k : Nat} {B : Finset (Fin n)} {H : List (EffectiveEvent n)}
    {c d : LowerConfiguration n} {cost : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor k forest terminal omega site)
    (lower : lowerConfiguration P = c) (path : PackedLowerPath n hn c (.transfer B :: H) d cost)
    (frame : ReservationFrame (k+1) (.leaf k B :: forest) terminal omega site) :
    ∃ mid prep rest Q word,
      LowerExtractionPath n hn c [] mid prep ∧
      PackedLowerPath n hn (lowerErasePacket mid B) H d rest ∧ cost = prep+rest ∧
      runLogged n hn P word = some (Q,[.transfer B]) ∧
      UpperReservedReplay Q (site k) (k+1) (.leaf k B :: forest) terminal omega site ∧
      lowerConfiguration Q = lowerErasePacket mid B ∧
      word.length = prep+cursorTurn n cursor.val (site k).val+1 ∧ word.count .v = 1 := by
  obtain ⟨mid, next, prep, eventCost, rest, before, step, after, hcost⟩ :=
    path.split_first_event (.transfer B) H rfl
  cases step with
  | extract nonempty =>
      obtain ⟨R, u, hu, hR, hsUpper, hlenU, letters⟩ := before.silent_lower_word rfl P lower
      have hpacket : packetAt R false (site0 n (by omega)) = lowerPacket mid (site0 n (by omega)) := by
        rw [← lowerPacket_configuration, hR]
      have stateR := state.congr_upper hsUpper
      obtain ⟨Q, hv, stateQ, hlenV⟩ := stateR.transfer_word hn
        (hpacket.symm ▸ nonempty) (by simpa only [hpacket] using frame)
      rw [hpacket] at hv stateQ
      have hQ := lowerConfiguration_cursorTransfer_packet hv
      rw [hR] at hQ
      have hno : Letter.v ∉ u := by
        intro hv
        rcases letters .v hv with he | he <;> cases he
      refine ⟨mid, prep, rest, Q, u++cursorTransferWord cursor (site k), before,
        after, by omega, ?_, stateQ, hQ, ?_, ?_⟩
      · simp [runLogged_append, hu, hv]
      · simp only [List.length_append, hlenU, hlenV]; omega
      · simp [List.count_append, List.count_eq_zero.mpr hno, cursorTransferWord, pWord, List.count_replicate]

end ActualCheckpoint
end RSR2History
