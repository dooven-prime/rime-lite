import RSR2History.LowerExtractionProjection
import RSR2History.ReservedEventPrimitives

/-!
Lifting an independent extraction path to actual guarded loading. Each
zero-cost deletion is implemented by `v` and `n-1` upper rotations. This
keeps the receiver empty before the next deletion and, after all atoms
arrive, puts the `i`th atom at upper site `i`.
-/

namespace RSR2History
open RSR2.Parametric

/-- The arrived prefix is packed immediately before the cyclic site zero.
Its first site is `n-arrived.length`; no upper site is occupied otherwise. -/
structure ExtractionLoadingState (n : Nat) (P : Placement n)
    (c : LowerConfiguration n) (arrived : List (Fin n)) : Prop where
  length_le : arrived.length ≤ n
  lower : lowerConfiguration P = c
  support : ∀ a, c a = none ↔ a ∈ arrived
  upper : ∀ (i : Nat) (hi : i < arrived.length),
    P arrived[i] = (true, ⟨n - arrived.length + i, by omega⟩)

theorem extractionLoadingState_seed (n : Nat) :
    ExtractionLoadingState n (seed n) (lowerExtractionSeed n) [] := by
  refine ⟨by simp, lowerConfiguration_seed n, ?_, ?_⟩
  · intro a
    simp [lowerExtractionSeed]
  · intro i hi
    simp at hi

theorem ExtractionLoadingState.upper_covered
    {P : Placement n} {c : LowerConfiguration n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived) {a : Fin n}
    (ha : (P a).1 = true) : a ∈ arrived := by
  apply (state.support a).mp
  rw [← state.lower]
  simp [lowerConfiguration, ha]

theorem ExtractionLoadingState.receiver_empty {hn : 1 < n}
    {P : Placement n} {c : LowerConfiguration n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived) (hspace : arrived.length < n) :
    ¬ occupiedAt P true (site0 n (by omega)) := by
  rintro ⟨a, ha⟩
  have haUpper : (P a).1 = true := by rw [ha]
  obtain ⟨i, hi, he⟩ := List.mem_iff_getElem.mp (state.upper_covered haUpper)
  have hp := state.upper i hi
  rw [he] at hp
  have hsite := congrArg (fun loc => loc.2.val) (ha.symm.trans hp)
  simp only [site0] at hsite
  omega

theorem ExtractionLoadingState.rotate_lower {hn : 1 < n}
    {P : Placement n} {c : LowerConfiguration n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived) :
    ExtractionLoadingState n (rotate n (by omega) P false)
      (lowerRotate n hn c) arrived := by
  refine ⟨state.length_le, ?_, ?_, ?_⟩
  · rw [lowerConfiguration_rotate_lower n hn, state.lower]
  · intro a
    cases hc : c a <;> simp [lowerRotate, hc, ← state.support a]
  · intro i hi
    simp [rotate, state.upper i hi]

theorem ExtractionLoadingState.slide_lower {hn : 1 < n}
    {P : Placement n} {c : LowerConfiguration n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived) :
    ExtractionLoadingState n (collapse n hn P false)
      (lowerSlide n hn c) arrived := by
  refine ⟨state.length_le, ?_, ?_, ?_⟩
  · rw [lowerConfiguration_collapse_lower n hn, state.lower]
  · intro a
    by_cases hc : c a = some (site1 n hn)
    · have hne : a ∉ arrived := by rw [← state.support a]; simp [hc]
      simp [lowerSlide, hc, hne]
    · simpa [lowerSlide, hc] using state.support a
  · intro i hi
    simp [collapse, state.upper i hi]

private theorem backward_site {n : Nat} [NeZero n] (hn : 1 < n)
    (q : Fin n) :
    (zsite ((q.val : ZMod n) + ((n - 1 : Nat) : ZMod n))).val =
      if q.val = 0 then n - 1 else q.val - 1 := by
  simp only [zsite, ZMod.val_add, ZMod.val_natCast,
    Nat.mod_eq_of_lt q.isLt, Nat.mod_eq_of_lt (show n - 1 < n by omega)]
  by_cases hq : q.val = 0
  · simp [hq, Nat.mod_eq_of_lt (show n - 1 < n by omega)]
  · have hs : q.val + (n - 1) = n + (q.val - 1) := by omega
    rw [hs]
    simp [hq, Nat.mod_eq_of_lt (show q.val - 1 < n by omega)]

/-- One deletion becomes a guarded singleton transfer followed by a silent
upper backward turn. Its raw length is exactly `n`. -/
theorem ExtractionLoadingState.delete {n : Nat} [NeZero n] {hn : 1 < n}
    {P : Placement n} {c : LowerConfiguration n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived) (a : Fin n)
    (atPort : c a = some (site0 n (by omega)))
    (singleton : ∀ b, c b = some (site0 n (by omega)) → b = a)
    (hspace : arrived.length < n) :
    ∃ Q, runLogged n hn P ([.v] ++ pWord true (n - 1)) =
        some (Q, singletonTransferLog [a]) ∧
      ExtractionLoadingState n Q (lowerDelete c a) (arrived ++ [a]) := by
  have hpa : P a = (false, site0 n (by omega)) := by
    apply (lowerConfiguration_eq_some _ _ _).mp
    rwa [state.lower]
  have hpacket : packetAt P false (site0 n (by omega)) = {a} := by
    ext b
    constructor
    · intro hb
      have hc := (lowerConfiguration_eq_some _ _ _).mpr ((mem_packetAt _ _ _ _).mp hb)
      rw [state.lower] at hc
      simp [singleton b hc]
    · intro hb
      have he : b = a := by simpa using hb
      subst b
      exact (mem_packetAt _ _ _ _).mpr hpa
  have hguard : liftGuard n (by omega) P :=
    ⟨⟨a, hpa⟩, state.receiver_empty (hn := hn) hspace⟩
  let R := liftPacket n (by omega) P
  have hstep : step n hn P .v = some R := by simp [step, hguard, R]
  have hevent : EventStep n hn P R .v (.transfer {a}) := by
    exact ⟨hstep, by simp [emittedEvents, hpacket]⟩
  let Q := phaseShift R true ((n - 1 : Nat) : ZMod n)
  refine ⟨Q, ?_, ?_⟩
  · rw [runLogged_append]
    simp [runLogged, hstep, emittedEvents, hpacket, runLogged_pWord, Q,
      singletonTransferLog]
  · have hlowR := lowerConfiguration_transfer_singleton n hn hevent
    rw [state.lower] at hlowR
    have hlow : lowerConfiguration Q = lowerDelete c a := by
      have he : lowerConfiguration Q = lowerConfiguration R := by
        funext b
        cases hR : R b with
        | mk layer q => cases layer <;> simp [lowerConfiguration, Q, phaseShift, hR]
      exact he.trans hlowR
    refine ⟨by simp; omega, hlow, ?_, ?_⟩
    · intro b
      by_cases hba : b = a
      · simp [lowerDelete, hba]
      · simp [lowerDelete, hba, state.support b]
    · intro i hi
      have hlen : (arrived ++ [a]).length = arrived.length + 1 := by simp
      by_cases hiOld : i < arrived.length
      · have hget : (arrived ++ [a])[i] = arrived[i] := List.getElem_append_left hiOld
        have hP := state.upper i hiOld
        have hR : R arrived[i] =
            (true, ⟨n - arrived.length + i, by omega⟩) := by
          simp [R, liftPacket, hP]
        rw [hget]
        apply Prod.ext
        · simp [Q, phaseShift, hR]
        · apply Fin.ext
          simp only [Q, phaseShift, hR, ite_true]
          rw [backward_site hn (⟨n - arrived.length + i, by omega⟩ : Fin n)]
          simp only [show n - arrived.length + i ≠ 0 by omega, if_false]
          simp only [List.length_append, List.length_singleton]
          omega
      · have hieq : i = arrived.length := by omega
        subst i
        have hRa : R a = (true, site0 n (by omega)) := by simp [R, liftPacket, hpa]
        have hget : (arrived ++ [a])[arrived.length]'(by simp) = a := by simp
        rw [hget]
        apply Prod.ext
        · simp [Q, phaseShift, hRa]
        · apply Fin.ext
          simp only [Q, phaseShift, hRa, ite_true]
          rw [backward_site hn (site0 n (by omega))]
          simp only [site0, if_true, List.length_append, List.length_singleton]
          omega

theorem LowerExtractionPath.guarded_loading {n : Nat} [NeZero n] {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {k : Nat}
    (path : LowerExtractionPath n hn c z d k)
    {P : Placement n} {arrived : List (Fin n)}
    (state : ExtractionLoadingState n P c arrived)
    (bound : arrived.length + z.length ≤ n) :
    ∃ word Q, runLogged n hn P word =
        some (Q, singletonTransferLog z) ∧
      ExtractionLoadingState n Q d (arrived ++ z) ∧
      word.length = k + n * z.length := by
  induction path generalizing P arrived with
  | refl c =>
      exact ⟨[], P, by simp [singletonTransferLog, runLogged], by simpa using state,
        by simp⟩
  | rotate c =>
      let Q := RSR2.Parametric.rotate n (by omega) P false
      refine ⟨[.p false], Q, ?_, by simpa using state.rotate_lower (hn := hn), by simp⟩
      simp [singletonTransferLog, runLogged, step, emittedEvents, Q]
  | slide c empty occupied =>
      have hzero : ¬ occupiedAt P false (site0 n (by omega)) := by
        intro h
        obtain ⟨a, ha⟩ := h
        have hc := (lowerConfiguration_eq_some _ _ _).mpr ha
        rw [state.lower] at hc
        exact empty a hc
      have hone : occupiedAt P false (site1 n hn) := by
        obtain ⟨a, ha⟩ := occupied
        exact ⟨a, (lowerConfiguration_eq_some _ _ _).mp
          (by rw [state.lower]; exact ha)⟩
      let Q := collapse n hn P false
      refine ⟨[.d false], Q, ?_, by simpa using state.slide_lower (hn := hn), by simp⟩
      simp [singletonTransferLog, runLogged, step, emittedEvents, Q, hzero, hone]
  | delete c a atPort singleton =>
      simp only [List.length_singleton] at bound
      obtain ⟨Q, hrun, hstate⟩ := state.delete a atPort singleton
        (by omega : arrived.length < n)
      refine ⟨[.v] ++ pWord true (n - 1), Q, hrun, hstate, ?_⟩
      simp only [List.length_append, List.length_singleton, pWord,
        List.length_replicate, Nat.zero_add, Nat.mul_one]
      omega
  | trans first second ih₁ ih₂ =>
      simp only [List.length_append] at bound
      obtain ⟨u, R, hfirst, sfirst, hlen₁⟩ := ih₁ state (by omega)
      obtain ⟨v, Q, hsecond, ssecond, hlen₂⟩ := ih₂ sfirst (by
        simp only [List.length_append]; omega)
      refine ⟨u ++ v, Q, ?_, by simpa only [List.append_assoc] using ssecond, ?_⟩
      · rw [runLogged_append, hfirst]
        simp only [Option.bind_some]
        rw [hsecond]
        simp [singletonTransferLog, List.map_append]
      · simp only [List.length_append, hlen₁, hlen₂, Nat.mul_add]
        omega

/-- The optimal auxiliary cost has an actual guarded loading witness for
every full duplicate-free order. No pre-existing delayed-chain run is used. -/
theorem lowerExtraction_optimal_guarded_loading
    {n : Nat} [NeZero n] {hn : 1 < n} {z : List (Fin n)}
    (hlen : z.length = n) (hnodup : z.Nodup) :
    ∃ word P, runLogged n hn (seed n) word = some (P, singletonTransferLog z) ∧
      (∀ i : Fin n, P (z[i.val]'(by omega)) = (true, i)) ∧
      word.length = lowerExtractionCost n hn z + n * n := by
  have path := @lowerExtractionCost_attained_of_permutation n hn z hlen hnodup
  obtain ⟨word, P, hrun, state, hcost⟩ := path.guarded_loading
    (extractionLoadingState_seed n) (by simpa using hlen.le)
  refine ⟨word, P, hrun, ?_, ?_⟩
  · intro i
    have hi : i.val < z.length := by rw [hlen]; exact i.isLt
    have hp := state.upper i.val hi
    simpa [hlen] using hp
  · simpa [hlen] using hcost

end RSR2History
