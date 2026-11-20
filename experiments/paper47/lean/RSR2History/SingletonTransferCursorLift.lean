import RSR2History.UpperReservedReplay
import RSR2History.LowerExtractionProjection

/-! Actual lower preparation and one deletion/transfer checkpoint. -/
namespace RSR2History
open RSR2.Parametric

theorem LowerExtractionPath.split_first_delete {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) :
    ∀ a tail, z = a :: tail → ∃ mid prep rest,
      LowerExtractionPath n hn c [] mid prep ∧
      mid a = some (site0 n (by omega)) ∧
      (∀ b, mid b = some (site0 n (by omega)) → b = a) ∧
      LowerExtractionPath n hn (lowerDelete mid a) tail d rest ∧ cost = prep + rest := by
  induction path with
  | refl c => intro a tail he; cases he
  | rotate c => intro a tail he; cases he
  | slide c empty occupied => intro a tail he; cases he
  | delete c b atPort singleton =>
      intro a tail he
      have hh := List.cons.inj he
      obtain ⟨rfl, rfl⟩ := hh
      exact ⟨c, 0, 0, .refl c, atPort, singleton, .refl _, rfl⟩
  | @trans c d e u v k l first second ihFirst ihSecond =>
      intro a tail he
      cases u with
      | nil =>
          obtain ⟨mid, prep, rest, hp, ha, hs, hr, hcost⟩ := ihSecond a tail (by simpa using he)
          exact ⟨mid, k+prep, rest, by simpa using first.trans hp,
            ha, hs, hr, by omega⟩
      | cons b us =>
          simp only [List.cons_append, List.cons.injEq] at he
          obtain ⟨rfl, rfl⟩ := he
          obtain ⟨mid, prep, rest, hp, ha, hs, hr, hcost⟩ := ihFirst b us rfl
          exact ⟨mid, prep, rest+l, hp, ha, hs, hr.trans second, by omega⟩

/-- Every pure preparation path has an actual word of exactly its charged cost. -/
theorem LowerExtractionPath.silent_lower_word {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) :
    z = [] → ∀ P : Placement n, lowerConfiguration P = c →
      ∃ Q word, runLogged n hn P word = some (Q, []) ∧
        lowerConfiguration Q = d ∧
        (∀ a q, Q a = (true, q) ↔ P a = (true, q)) ∧
        word.length = cost ∧
        (∀ letter ∈ word, letter = .p false ∨ letter = .d false) := by
  induction path with
  | refl c =>
      intro _ P hp
      exact ⟨P, [], rfl, hp, fun _ _ => Iff.rfl, rfl, by simp⟩
  | rotate c =>
      intro _ P hp
      refine ⟨RSR2.Parametric.rotate n (by omega) P false, [.p false], ?_, ?_, ?_, rfl, ?_⟩
      · simp [runLogged, step, emittedEvents]
      · rw [lowerConfiguration_rotate_lower, hp]
      · intro a q
        cases hh : P a with
        | mk layer site => cases layer <;> simp [RSR2.Parametric.rotate, hh]
      · simp
  | slide c empty occupied =>
      intro _ P hp
      have hzero : ¬ occupiedAt P false (site0 n (by omega)) := by
        rintro ⟨a, ha⟩
        apply empty a
        rw [← hp]
        exact (lowerConfiguration_eq_some _ _ _).mpr ha
      refine ⟨collapse n hn P false, [.d false], ?_, ?_, ?_, rfl, ?_⟩
      · simp [runLogged, step, emittedEvents, hzero]
      · rw [lowerConfiguration_collapse_lower, hp]
      · intro a q
        cases hh : P a with
        | mk layer site =>
            cases layer <;> by_cases hs : site = site1 n hn <;> simp [collapse, hh, hs]
      · simp
  | delete c a atPort singleton => intro he; cases he
  | trans first second ihFirst ihSecond =>
      intro he P hp
      have hv := List.append_eq_nil_iff.mp he
      obtain ⟨R, u, hu, hR, hsR, hlU, lettersU⟩ := ihFirst hv.1 P hp
      obtain ⟨Q, v, hv, hQ, hsQ, hlV, lettersV⟩ := ihSecond hv.2 R hR
      refine ⟨Q, u++v, ?_, hQ, fun a q => (hsQ a q).trans (hsR a q), ?_, ?_⟩
      · simp [runLogged_append, hu, hv]
      · simp [hlU, hlV]
      · intro letter hmem
        rcases List.mem_append.mp hmem with h | h
        · exact lettersU letter h
        · exact lettersV letter h

section CursorCheckpoint
variable {n : Nat} [NeZero n]

theorem lowerConfiguration_upper_phase (P : Placement n) (amount : ZMod n) :
    lowerConfiguration (phaseShift P true amount) = lowerConfiguration P := by
  funext a
  rcases hh : P a with ⟨layer, site⟩
  cases layer <;> simp [phaseShift, lowerConfiguration, hh]

omit [NeZero n] in
theorem run_upper_preserves_lower {hn : 1 < n} {P Q : Placement n} {word : List Letter}
    (letters : ∀ letter ∈ word, letter = .p true ∨ letter = .d true)
    (hrun : run n hn P word = some Q) : lowerConfiguration Q = lowerConfiguration P := by
  induction word generalizing P with
  | nil => simpa [run] using (congrArg (Option.map lowerConfiguration) hrun).symm
  | cons letter rest ih =>
      have hrest : ∀ x ∈ rest, x = .p true ∨ x = .d true :=
        fun x hx => letters x (by simp [hx])
      rcases letters letter (by simp) with rfl | rfl
      · have hr : run n hn (RSR2.Parametric.rotate n (by omega) P true) rest = some Q := by
          simpa [run, step] using hrun
        exact (ih hrest hr).trans (lowerConfiguration_rotate_upper n hn P)
      · have hr : run n hn (collapse n hn P true) rest = some Q := by
          simpa [run, step] using hrun
        exact (ih hrest hr).trans (lowerConfiguration_collapse_upper n hn P)

omit [NeZero n] in
theorem phaseFreeFusionWord_upper_letters (left right : ZMod n) (f : Nat) :
    ∀ letter ∈ phaseFreeFusionWord true left right f,
      letter = .p true ∨ letter = .d true := by
  have mapped (word : List RegisteredAbsorptionChains.Letter) :
      ∀ letter ∈ word.map (layerLetter true), letter = .p true ∨ letter = .d true := by
    intro letter hm
    obtain ⟨x, _, rfl⟩ := List.mem_map.mp hm
    cases x <;> simp [layerLetter]
  intro letter hm
  by_cases hf : f = 0
  · simp only [phaseFreeFusionWord, if_pos hf, List.mem_append, pWord,
      List.mem_replicate, List.mem_cons, List.not_mem_nil, or_false] at hm
    rcases hm with ⟨_, rfl⟩ | rfl <;> simp
  · simp only [phaseFreeFusionWord, if_neg hf, List.mem_append, pWord,
      List.mem_replicate, List.mem_cons, List.not_mem_nil, or_false] at hm
    rcases hm with ((⟨_, rfl⟩ | rfl) | hm) | (rfl | rfl)
    · simp
    · simp
    · exact mapped _ letter hm
    · simp
    · simp

/-- Upper cursor fusion preparation can be interleaved without changing the
entire auxiliary lower extraction configuration, not merely its support. -/
theorem cursorFusion_preserves_lower {hn : 1 < n}
    {P Q : Placement n} {left right : ZMod n} {f : Nat} {events : List (EffectiveEvent n)}
    (hrun : runLogged n hn P (phaseFreeFusionWord true left right f) = some (Q, events)) :
    lowerConfiguration Q = lowerConfiguration P := by
  have hp := runLogged_project n hn P (phaseFreeFusionWord true left right f)
  rw [hrun] at hp
  apply run_upper_preserves_lower (phaseFreeFusionWord_upper_letters left right f)
  simpa using hp.symm

theorem lowerConfiguration_cursorTransfer {hn : 1 < n}
    {P Q : Placement n} {cursor target : Fin n} {a : Fin n}
    (hrun : runLogged n hn P (cursorTransferWord cursor target) =
      some (Q, [.transfer {a}])) :
    lowerConfiguration Q = lowerDelete (lowerConfiguration P) a := by
  let R := phaseShift P true ((cursor.val : ZMod n) - target.val)
  have hv : runLogged n hn R [.v] = some (Q, [.transfer {a}]) := by
    rw [cursorTransferWord, runLogged_append, runLogged_phase] at hrun
    simpa using hrun
  cases hs : step n hn R .v with
  | none => simp [runLogged, hs] at hv
  | some S =>
      have he : S = Q ∧ packetAt R false (site0 n (by omega)) = {a} := by
        simpa [runLogged, hs, emittedEvents] using hv
      obtain ⟨rfl, hpacket⟩ := he
      have event : EventStep n hn R S .v (.transfer {a}) :=
        ⟨hs, by simp [emittedEvents, hpacket]⟩
      have hl := lowerConfiguration_transfer_singleton n hn event
      simpa only [R, lowerConfiguration_upper_phase] using hl

/-- One auxiliary deletion becomes one actual guarded transfer, with an actual
remaining extraction path. Upper fusions may occur before the next call. -/
theorem singleton_cursor_delete_checkpoint {hn : 1 < n}
    {P : Placement n} {cursor : Fin n} {k : Nat} {a : Fin n} {z : List (Fin n)}
    {c d : LowerConfiguration n} {cost : Nat}
    {forest terminal : List (UpperFusionTree n)} {omega : List Nat} {site : Nat → Fin n}
    (state : UpperReservedReplay P cursor k forest terminal omega site)
    (lower : lowerConfiguration P = c)
    (path : LowerExtractionPath n hn c (a :: z) d cost)
    (frame : ReservationFrame (k+1) (.leaf k {a} :: forest) terminal omega site) :
    ∃ mid prep rest Q word,
      LowerExtractionPath n hn c [] mid prep ∧
      LowerExtractionPath n hn (lowerDelete mid a) z d rest ∧ cost = prep+rest ∧
      runLogged n hn P word = some (Q, [.transfer {a}]) ∧
      UpperReservedReplay Q (site k) (k+1) (.leaf k {a} :: forest) terminal omega site ∧
      lowerConfiguration Q = lowerDelete mid a ∧
      word.length = prep + cursorTurn n cursor.val (site k).val + 1 ∧
      word.count .v = 1 := by
  obtain ⟨mid, prep, rest, before, atPort, singleton, after, hcost⟩ :=
    path.split_first_delete a z rfl
  obtain ⟨R, u, hu, hR, hsUpper, hlenU, lettersU⟩ := before.silent_lower_word rfl P lower
  have hpacket : packetAt R false (site0 n (by omega)) = {a} := by
    ext b
    rw [mem_packetAt, ← lowerConfiguration_eq_some, hR, Finset.mem_singleton]
    exact ⟨singleton b, fun h => h ▸ atPort⟩
  have stateR := state.congr_upper hsUpper
  obtain ⟨Q, hv, stateQ, hlenV⟩ := stateR.transfer_word hn
    (by rw [hpacket]; exact Finset.singleton_nonempty a)
    (by simpa only [hpacket] using frame)
  rw [hpacket] at hv stateQ
  have hQ := lowerConfiguration_cursorTransfer hv
  rw [hR] at hQ
  have hno : Letter.v ∉ u := by
    intro hmem
    rcases lettersU .v hmem with h | h <;> cases h
  refine ⟨mid, prep, rest, Q, u ++ cursorTransferWord cursor (site k), before,
    after, hcost, ?_, stateQ, hQ, ?_, ?_⟩
  · simp [runLogged_append, hu, hv]
  · simp only [List.length_append, hlenU, hlenV]
    omega
  · simp [List.count_append, cursorTransferWord, pWord, List.count_replicate,
      List.count_eq_zero.mpr hno]

end CursorCheckpoint
end RSR2History
