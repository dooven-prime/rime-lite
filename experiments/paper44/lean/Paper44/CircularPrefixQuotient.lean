import Paper44.TerminalObserverQuotient
import Paper44.ProperCarrierCounting
import FutureEvent.RegisteredPlacementEquiv

/-!
# The actual prefix-observer quotient

Normal forms count observations, not histories. In the proper-carrier sector
the current carrier is recovered uniquely from the literal placement. The
quotient below is by all-word observer equivalence on the actual generated
state space, with no bounded-history cutoff.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

abbrev CircularLabel (n : ℕ) :=
  PrefixLabel (FusionRecord (ZMod n)) (FusionRecord (ZMod n))

omit [NeZero n] in
theorem circularLabel_eq_unregistered_iff (j : ℕ) (s : Execution n (ZMod n)) :
    circularLabel j s = .unregistered ↔ s.origin = none := by
  cases h : s.origin <;> simp [circularLabel, retainedLabel, h]

theorem properCarrier_absorbed_lt (f : ProperCarrier n) : f.val.absorbed < n - 2 := by
  have h := f.val.remaining_plus_absorbed
  rw [f.val.remaining_card] at h
  have hp := f.property
  omega

/-- A proper selected carrier cannot occur in a one-packet placement. -/
theorem properCarrier_not_rankOne (s : Execution n (ZMod n))
    (f : ProperCarrier n) (hq : ∃ q, s.placed q = some f.val.carrier) :
    ¬ RankOnePlacement s := by
  rintro ⟨q0, hP⟩
  obtain ⟨q, hq⟩ := hq
  have hc := (placementOfMap_some_iff (fun _ : ZMod n => q0) q f.val.carrier).mp
    (hP ▸ hq)
  obtain ⟨a, ha⟩ := hc.2
  have hsite : q0 = q := (mem_sourceFiber _ a q).mp (hc.1.symm ▸ ha)
  have hfull : f.val.carrier = Finset.univ := by
    rw [← hc.1]
    ext a
    simp [hsite]
  have hcard := f.val.carrier_card
  rw [hfull, Finset.card_univ, ZMod.card] at hcard
  have hlt := properCarrier_absorbed_lt f
  omega

/-- Current placement determines the proper carrier, even when retained
prefixes agree but unretained historical suffixes differ. -/
theorem properCarrier_unique_of_placement (s : CircularState n)
    (f g : ProperCarrier n)
    (hf : ∃ q, s.val.placed q = some f.val.carrier)
    (hg : ∃ q, s.val.placed q = some g.val.carrier) : f = g := by
  obtain ⟨q, hq⟩ := hf
  obtain ⟨r, hr⟩ := hg
  have hin (u : CheckpointSourceFrontier n) : selectedPair n ⊆ u.carrier := by
    intro a ha
    exact Finset.mem_union_left _ (Finset.mem_union_left _ ha)
  have hn : 2 ≤ n := le_trans f.val.lo_valid (f.val.noncrossing.trans f.val.hi_valid)
  have hC := (sourceOrdered_selected_packet_unique s.val (selectedPair n) _ _ q r
    (pairGenerated_sourceOrdered s.val hn s.property)
    ⟨0, by simp [selectedPair]⟩ hq (hin _) hr (hin _)).2
  exact Subtype.ext ((frontier_eq_of_carrier_eq_of_remaining f.val g.val hC f.property))

/-- The carrier/label/placement observations in the registered nonterminal
sector. Provenance witnesses are propositions and are not counted. -/
abbrev ActualProperObservation (j : ℕ) :=
  Σ f : ProperCarrier n, Σ label : ActualProperPrefixLabel j f,
    ActualProperPlacements j f label

noncomputable def properObservationState {j : ℕ} (x : ActualProperObservation (n := n) j) :
    CircularState n := Classical.choose x.2.2.property

theorem properObservationState_spec {j : ℕ} (x : ActualProperObservation (n := n) j) :
    let s := properObservationState x
    RegisteredNonterminal s.val ∧
      (∃ q, s.val.placed q = some x.1.val.carrier) ∧
      circularLabel j s.val = x.2.1.val ∧ s.val.placed = x.2.2.val := by
  have h := Classical.choose_spec x.2.2.property
  exact ⟨⟨h.1, properCarrier_not_rankOne _ x.1 h.2.1⟩, h.2⟩

theorem properObservation_ext {j : ℕ} (x y : ActualProperObservation (n := n) j)
    (hP : x.2.2.val = y.2.2.val) (hL : x.2.1.val = y.2.1.val) : x = y := by
  have hx := properObservationState_spec x
  have hy := properObservationState_spec y
  have hf : x.1 = y.1 := properCarrier_unique_of_placement (properObservationState x) _ _
    hx.2.1 (by
      obtain ⟨q, hq⟩ := hy.2.1
      exact ⟨q, by rw [hx.2.2.2, hP, ← hy.2.2.2]; exact hq⟩)
  rcases x with ⟨f, l, P⟩
  rcases y with ⟨g, k, Q⟩
  dsimp only at hf hL hP
  subst g
  have hl : l = k := Subtype.ext hL
  subst k
  have hPQ : P = Q := Subtype.ext hP
  cases hPQ
  rfl

/-- All actual registered nonterminal states occur in the proper sector. -/
theorem properObservation_covers (hn : 3 ≤ n) (j : ℕ) (s : CircularState n)
    (hs : RegisteredNonterminal s.val) :
    ∃ x : ActualProperObservation (n := n) j,
      x.2.2.val = s.val.placed ∧ x.2.1.val = circularLabel j s.val := by
  obtain ⟨w, hw⟩ := s.property
  have hr : (run (selectedPair n) (singletonExecution n) w).origin.isSome = true := by
    simpa only [selectedPair, hw] using hs.1
  obtain ⟨c, hc⟩ := actual_chain_in_decode_range w (by omega) hr
  have hp := actual_registered_frontier_positive w hn c hr hc (by
    simpa only [selectedPair, hw] using hs.2)
  let f : ProperCarrier n := ⟨(decodeCode c (by omega)).frontier, hp⟩
  obtain ⟨q, hq⟩ := actual_code_carrier_at_site w (by omega) c hr hc
  have hq' : ∃ q, s.val.placed q = some f.val.carrier :=
    ⟨q, by simpa only [selectedPair, hw, decodedCarrier] using hq⟩
  let l : ActualProperPrefixLabel j f := ⟨circularLabel j s.val, s, hs.1, hq', rfl⟩
  exact ⟨⟨f, l, ⟨s.val.placed, s, hs.1, hq', rfl, rfl⟩⟩, rfl, rfl⟩

/-- A genuine unregistered dead state. The first fusion joins source `0`
to source `-1`, so the selected pair can never subsequently be created. -/
theorem unregistered_dead_state (hn : 3 ≤ n) :
    ∃ s : CircularState n, s.val.origin = none ∧ ¬ PairRegisterable s.val := by
  let w : List Letter := [.p, .d]
  let s := run {0, 1} (singletonExecution n) w
  let f : ZMod n → ZMod n := fun a => collapsePosition (a + 1)
  have hseed : (singletonExecution n).placed = placementOfMap (fun a : ZMod n => a) := by
    funext q
    have hf : sourceFiber (fun a : ZMod n => a) q = {q} := by ext a; simp
    simp [singletonExecution, placementOfMap, hf]
  have h2 : (2 : ZMod n) ≠ 0 := by
    intro h
    have hv := congrArg ZMod.val h
    have hv2 : (2 : ZMod n).val = 2 := ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
    rw [hv2] at hv
    simp at hv
  have h21 : (2 : ZMod n) ≠ 1 := by
    intro h
    have hv := congrArg ZMod.val h
    have hv2 : (2 : ZMod n).val = 2 := ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
    have hv1 : (1 : ZMod n).val = 1 := by
      simpa only [Nat.cast_one] using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
    rw [hv2, hv1] at hv
    omega
  have hp : s.placed = placementOfMap f := by
    simpa [s, w, forwardMapRun, forwardMapStep, f, Function.comp_def] using
      run_placementOfMap ({0, 1} : Finset (ZMod n)) (singletonExecution n)
        (fun a : ZMod n => a) w (by omega) hseed
  have ho : s.origin = none := by
    cases h : s.origin with
    | none => rfl
    | some record =>
      have hc := run_registered_colocated (singletonExecution n) (fun a : ZMod n => a)
        w (by omega) hseed (by simp [singletonExecution]) (by
          change s.origin.isSome = true; simp [h])
      have hc' : (0 : ZMod n) = 2 := by
        simpa [w, forwardMapRun, forwardMapStep, collapsePosition, h21, show
          (1 : ZMod n) + 1 = 2 by ring] using hc
      exact False.elim (h2 hc'.symm)
  refine ⟨⟨s, w, rfl⟩, ho, ?_⟩
  rintro ⟨_, v, hv⟩
  have hsingle := (future_registration_singletons s f v (by omega) hp ho hv).1
  have he : (-1 : ZMod n) = 0 := hsingle (-1) (by simp [f, collapsePosition])
  have hz : (1 : ZMod n) = 0 := neg_eq_zero.mp he
  have := ZMod.one_eq_zero_iff.mp hz
  omega

/-- Disjoint actual normal forms: an unregistered silent class, still
registerable placements, terminal labels, and proper observations. -/
abbrev PrefixNormalForms (n j : ℕ) [NeZero n] :=
  Unit ⊕ (RegisterablePlacements n ⊕
    (ActualTerminalLabel n j ⊕ ActualProperObservation (n := n) j))

noncomputable def prefixSignature (j : ℕ) (s : CircularState n) :
    FutureNormalForms n × CircularLabel n :=
  (futureNormalKey s, circularLabel j s.val)

theorem prefixSignature_eq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (s t : CircularState n) :
    prefixSignature j s = prefixSignature j t ↔
      (circularPrefixMachine hn j hj).ObserverEq s t := by
  simp only [prefixSignature, Prod.mk.injEq]
  rw [circular_prefix_classification]
  constructor
  · rintro ⟨hkey, hlabel⟩
    exact ⟨(futureNormalKey_eq_iff s t).mp hkey, hlabel⟩
  · rintro ⟨hfuture, hlabel⟩
    exact ⟨(futureNormalKey_eq_iff s t).mpr hfuture, hlabel⟩

noncomputable def properObservationPlacement {j : ℕ}
    (x : ActualProperObservation (n := n) j) : RegisteredNonterminalPlacements n :=
  ⟨x.2.2.val, (properObservationState x).val, (properObservationState x).property,
    (properObservationState_spec x).1, (properObservationState_spec x).2.2.2⟩

noncomputable def prefixNormalSignature {j : ℕ} : PrefixNormalForms n j →
    FutureNormalForms n × CircularLabel n
  | .inl _ => (.inl (), .unregistered)
  | .inr (.inl P) => (.inr (.inl P), .unregistered)
  | .inr (.inr (.inl l)) => (.inl (), l.val)
  | .inr (.inr (.inr x)) => (.inr (.inr (properObservationPlacement x)), x.2.1.val)

theorem actualTerminalLabel_ne_unregistered (j : ℕ) (l : ActualTerminalLabel n j) :
    l.val ≠ .unregistered := by
  obtain ⟨s, hr, _, hl⟩ := l.property
  intro h
  have ho := (circularLabel_eq_unregistered_iff j s.val).mp (hl.trans h)
  simp [ho] at hr

theorem prefixNormalSignature_injective (j : ℕ) :
    Function.Injective (prefixNormalSignature (n := n) (j := j)) := by
  intro x y h
  rcases x with u | (P | (l | x)) <;>
    rcases y with v | (Q | (k | y))
  all_goals simp only [prefixNormalSignature, Prod.mk.injEq, Sum.inl.injEq,
    Sum.inr.injEq, Sum.inl_ne_inr, Sum.inr_ne_inl, false_and, true_and] at h
  · cases u; cases v; rfl
  · exact False.elim (actualTerminalLabel_ne_unregistered j k h.symm)
  · cases h.1; rfl
  · exact False.elim (actualTerminalLabel_ne_unregistered j l h)
  · have he : l = k := Subtype.ext h
    cases he; rfl
  · have he : x = y := properObservation_ext x y
      (congrArg Subtype.val h.1) h.2
    cases he
    rfl

theorem prefixNormalSignature_reachable (hn : 3 ≤ n) (j : ℕ)
    (x : PrefixNormalForms n j) :
    ∃ s : CircularState n, prefixSignature j s = prefixNormalSignature x := by
  rcases x with u | (P | (l | x))
  · obtain ⟨s, ho, hr⟩ := unregistered_dead_state (n := n) hn
    refine ⟨s, ?_⟩
    simp only [prefixSignature, prefixNormalSignature,
      futureNormalKey_of_silent _ (Or.inl ⟨ho, hr⟩), circularLabel, ho]
  · obtain ⟨s, hg, hr, hp⟩ := P.property
    refine ⟨⟨s, hg⟩, ?_⟩
    apply Prod.ext
    · change futureNormalKey ⟨s, hg⟩ = _
      rw [futureNormalKey_of_registerable _ hr]
      exact congrArg (fun P => Sum.inr (Sum.inl P)) (Subtype.ext hp)
    · change circularLabel j s = .unregistered
      exact (circularLabel_eq_unregistered_iff j s).mpr hr.1
  · obtain ⟨s, hr, ht, hl⟩ := l.property
    refine ⟨s, ?_⟩
    apply Prod.ext
    · exact futureNormalKey_of_silent _ (Or.inr ⟨hr, ht⟩)
    · exact hl
  · refine ⟨properObservationState x, ?_⟩
    have h := properObservationState_spec x
    apply Prod.ext
    · change futureNormalKey _ = _
      rw [futureNormalKey_of_registered _ h.1]
      exact congrArg (fun P => Sum.inr (Sum.inr P)) (Subtype.ext h.2.2.2)
    · exact h.2.2.1

theorem prefixNormalSignature_covers (hn : 3 ≤ n) (j : ℕ) (s : CircularState n) :
    ∃ x : PrefixNormalForms n j, prefixNormalSignature x = prefixSignature j s := by
  classical
  by_cases ho : s.val.origin = none
  · by_cases hr : PairRegisterable s.val
    · let P : RegisterablePlacements n := ⟨s.val.placed, s.val, s.property, hr, rfl⟩
      refine ⟨.inr (.inl P), ?_⟩
      simp [prefixNormalSignature, prefixSignature, futureNormalKey_of_registerable _ hr,
        circularLabel, ho, P]
    · refine ⟨.inl (), ?_⟩
      simp [prefixNormalSignature, prefixSignature,
        futureNormalKey_of_silent _ (Or.inl ⟨ho, hr⟩), circularLabel, ho]
  · have hr : s.val.origin.isSome = true := by
      cases h : s.val.origin <;> simp_all
    by_cases ht : RankOnePlacement s.val
    · let l : ActualTerminalLabel n j := ⟨circularLabel j s.val, s, hr, ht, rfl⟩
      refine ⟨.inr (.inr (.inl l)), ?_⟩
      simp [prefixNormalSignature, prefixSignature,
        futureNormalKey_of_silent _ (Or.inr ⟨hr, ht⟩), l]
    · obtain ⟨x, hP, hL⟩ := properObservation_covers hn j s ⟨hr, ht⟩
      refine ⟨.inr (.inr (.inr x)), ?_⟩
      apply Prod.ext
      · change Sum.inr (Sum.inr (properObservationPlacement x)) = _
        change Sum.inr (Sum.inr (properObservationPlacement x)) = futureNormalKey s
        rw [futureNormalKey_of_registered _ ⟨hr, ht⟩]
        exact congrArg (fun P => Sum.inr (Sum.inr P)) (Subtype.ext hP)
      · exact hL

noncomputable def prefixNormalOfState (hn : 3 ≤ n) (j : ℕ) (s : CircularState n) :
    PrefixNormalForms n j := Classical.choose (prefixNormalSignature_covers hn j s)

theorem prefixNormalOfState_signature (hn : 3 ≤ n) (j : ℕ) (s : CircularState n) :
    prefixNormalSignature (prefixNormalOfState hn j s) = prefixSignature j s :=
  Classical.choose_spec (prefixNormalSignature_covers hn j s)

theorem prefixNormalOfState_eq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (s t : CircularState n) :
    prefixNormalOfState hn j s = prefixNormalOfState hn j t ↔
      (circularPrefixMachine hn j hj).ObserverEq s t := by
  rw [← prefixSignature_eq_iff hn j hj s t]
  constructor
  · intro h
    rw [← prefixNormalOfState_signature hn j s, ← prefixNormalOfState_signature hn j t, h]
  · intro h
    apply prefixNormalSignature_injective j
    rw [prefixNormalOfState_signature, prefixNormalOfState_signature, h]

def prefixObserverSetoid (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) : Setoid (CircularState n) where
  r s t := (circularPrefixMachine hn j hj).ObserverEq s t
  iseqv := ⟨fun s => LabelledMachine.observerEq_refl _ s,
    fun h => LabelledMachine.observerEq_symm _ h,
    fun hst htu => LabelledMachine.observerEq_trans _ hst htu⟩

abbrev PrefixObserverQuotient (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :=
  Quotient (prefixObserverSetoid hn j hj)

noncomputable def prefixQuotientNormal (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    PrefixObserverQuotient hn j hj → PrefixNormalForms n j :=
  Quotient.lift (prefixNormalOfState hn j)
    (fun s t h => (prefixNormalOfState_eq_iff hn j hj s t).mpr h)

theorem prefixQuotientNormal_bijective (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Function.Bijective (prefixQuotientNormal hn j hj) := by
  constructor
  · intro x y
    refine Quotient.inductionOn₂ x y ?_
    intro s t h
    exact Quotient.sound ((prefixNormalOfState_eq_iff hn j hj s t).mp h)
  · intro x
    obtain ⟨s, hs⟩ := prefixNormalSignature_reachable hn j x
    refine ⟨Quotient.mk _ s, prefixNormalSignature_injective j ?_⟩
    exact (prefixNormalOfState_signature hn j s).trans hs

/-- The full actual all-word observer quotient, including the unregistered
dead class and the two distinct registered sectors. -/
noncomputable def prefixObserverNormalEquiv (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    PrefixObserverQuotient hn j hj ≃ PrefixNormalForms n j :=
  Equiv.ofBijective (prefixQuotientNormal hn j hj) (prefixQuotientNormal_bijective hn j hj)

theorem prefixObserver_encode_decode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : PrefixObserverQuotient hn j hj) :
    (prefixObserverNormalEquiv hn j hj).symm (prefixObserverNormalEquiv hn j hj x) = x :=
  (prefixObserverNormalEquiv hn j hj).symm_apply_apply x

theorem prefixObserver_decode_encode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : PrefixNormalForms n j) :
    prefixObserverNormalEquiv hn j hj ((prefixObserverNormalEquiv hn j hj).symm x) = x :=
  (prefixObserverNormalEquiv hn j hj).apply_symm_apply x

/-- Regroup by the current carrier's absorbed size. This reindexing preserves
the carrier, retained label and literal placement, not just their counts. -/
def properObservationSizeEquiv (j : ℕ) :
    ActualProperObservation (n := n) j ≃
      Σ r : Fin (n - 2), ActualProperFibreAt (n := n) r.val j where
  toFun x := ⟨⟨x.1.val.absorbed, properCarrier_absorbed_lt x.1⟩,
    ⟨⟨⟨x.1, rfl⟩, x.2.1⟩, x.2.2⟩⟩
  invFun x := ⟨x.2.1.1.val, x.2.1.2, x.2.2⟩
  left_inv x := by rcases x with ⟨f, l, P⟩; rfl
  right_inv x := by
    rcases x with ⟨⟨r, hr⟩, ⟨⟨f, hf⟩, l⟩, P⟩
    dsimp only at hf
    subst r
    rfl

abbrev RegisteredPrefixState (n : ℕ) [NeZero n] :=
  {s : CircularState n // s.val.origin.isSome = true}

abbrev RegisteredPrefixNormalForms (n j : ℕ) [NeZero n] :=
  ActualTerminalLabel n j ⊕ ActualProperObservation (n := n) j

noncomputable def registeredNormalSignature {j : ℕ} (x : RegisteredPrefixNormalForms n j) :=
  prefixNormalSignature (Sum.inr (Sum.inr x) : PrefixNormalForms n j)

theorem registeredNormalSignature_injective (j : ℕ) :
    Function.Injective (registeredNormalSignature (n := n) (j := j)) := by
  intro x y h
  exact Sum.inr.inj (Sum.inr.inj (prefixNormalSignature_injective j h))

theorem registeredNormalSignature_label_ne (j : ℕ) (x : RegisteredPrefixNormalForms n j) :
    (registeredNormalSignature x).2 ≠ .unregistered := by
  rcases x with l | x
  · exact actualTerminalLabel_ne_unregistered j l
  · obtain ⟨s, hr, _, hl⟩ := x.2.1.property
    intro h
    have ho := (circularLabel_eq_unregistered_iff j s.val).mp (hl.trans h)
    simp [ho] at hr

theorem registeredNormalSignature_reachable (hn : 3 ≤ n) (j : ℕ)
    (x : RegisteredPrefixNormalForms n j) :
    ∃ s : RegisteredPrefixState n, prefixSignature j s.val = registeredNormalSignature x := by
  obtain ⟨s, hs⟩ := prefixNormalSignature_reachable hn j (.inr (.inr x))
  have hl : circularLabel j s.val ≠ .unregistered := by
    intro h
    exact registeredNormalSignature_label_ne j x ((congrArg Prod.snd hs).symm.trans h)
  have hr : s.val.origin.isSome = true := by
    cases ho : s.val.origin with
    | none => exact False.elim (hl ((circularLabel_eq_unregistered_iff j s.val).mpr ho))
    | some _ => simp
  exact ⟨⟨s, hr⟩, hs⟩

theorem registeredNormalSignature_covers (hn : 3 ≤ n) (j : ℕ)
    (s : RegisteredPrefixState n) :
    ∃ x : RegisteredPrefixNormalForms n j,
      registeredNormalSignature x = prefixSignature j s.val := by
  obtain ⟨x, hx⟩ := prefixNormalSignature_covers hn j s.val
  rcases x with u | (P | x)
  · have hl : circularLabel j s.val.val = .unregistered := (congrArg Prod.snd hx).symm
    have ho := (circularLabel_eq_unregistered_iff j s.val.val).mp hl
    have hr := s.property
    simp [ho] at hr
  · have hl : circularLabel j s.val.val = .unregistered := (congrArg Prod.snd hx).symm
    have ho := (circularLabel_eq_unregistered_iff j s.val.val).mp hl
    have hr := s.property
    simp [ho] at hr
  · exact ⟨x, hx⟩

noncomputable def registeredNormalOfState (hn : 3 ≤ n) (j : ℕ)
    (s : RegisteredPrefixState n) : RegisteredPrefixNormalForms n j :=
  Classical.choose (registeredNormalSignature_covers hn j s)

theorem registeredNormalOfState_signature (hn : 3 ≤ n) (j : ℕ)
    (s : RegisteredPrefixState n) :
    registeredNormalSignature (registeredNormalOfState hn j s) = prefixSignature j s.val :=
  Classical.choose_spec (registeredNormalSignature_covers hn j s)

theorem registeredNormalOfState_eq_iff (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (s t : RegisteredPrefixState n) :
    registeredNormalOfState hn j s = registeredNormalOfState hn j t ↔
      (circularPrefixMachine hn j hj).ObserverEq s.val t.val := by
  rw [← prefixSignature_eq_iff hn j hj s.val t.val]
  constructor
  · intro h
    rw [← registeredNormalOfState_signature hn j s,
      ← registeredNormalOfState_signature hn j t, h]
  · intro h
    apply registeredNormalSignature_injective j
    rw [registeredNormalOfState_signature, registeredNormalOfState_signature, h]

def registeredPrefixObserverSetoid (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Setoid (RegisteredPrefixState n) where
  r s t := (circularPrefixMachine hn j hj).ObserverEq s.val t.val
  iseqv := ⟨fun s => LabelledMachine.observerEq_refl _ s.val,
    fun h => LabelledMachine.observerEq_symm _ h,
    fun hst htu => LabelledMachine.observerEq_trans _ hst htu⟩

abbrev RegisteredPrefixObserverQuotient (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :=
  Quotient (registeredPrefixObserverSetoid hn j hj)

noncomputable def registeredPrefixQuotientNormal (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    RegisteredPrefixObserverQuotient hn j hj → RegisteredPrefixNormalForms n j :=
  Quotient.lift (registeredNormalOfState hn j)
    (fun s t h => (registeredNormalOfState_eq_iff hn j hj s t).mpr h)

theorem registeredPrefixQuotientNormal_bijective (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    Function.Bijective (registeredPrefixQuotientNormal hn j hj) := by
  constructor
  · intro x y
    refine Quotient.inductionOn₂ x y ?_
    intro s t h
    exact Quotient.sound ((registeredNormalOfState_eq_iff hn j hj s t).mp h)
  · intro x
    obtain ⟨s, hs⟩ := registeredNormalSignature_reachable hn j x
    refine ⟨Quotient.mk _ s, registeredNormalSignature_injective j ?_⟩
    exact (registeredNormalOfState_signature hn j s).trans hs

/-- The registered domain is a genuine restriction of the same observer,
not a second observer with different terminal or trace semantics. -/
noncomputable def registeredPrefixObserverNormalEquiv (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j) :
    RegisteredPrefixObserverQuotient hn j hj ≃ RegisteredPrefixNormalForms n j :=
  Equiv.ofBijective (registeredPrefixQuotientNormal hn j hj)
    (registeredPrefixQuotientNormal_bijective hn j hj)

theorem registeredPrefixObserver_encode_decode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : RegisteredPrefixObserverQuotient hn j hj) :
    (registeredPrefixObserverNormalEquiv hn j hj).symm
      (registeredPrefixObserverNormalEquiv hn j hj x) = x :=
  (registeredPrefixObserverNormalEquiv hn j hj).symm_apply_apply x

theorem registeredPrefixObserver_decode_encode (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (x : RegisteredPrefixNormalForms n j) :
    registeredPrefixObserverNormalEquiv hn j hj
      ((registeredPrefixObserverNormalEquiv hn j hj).symm x) = x :=
  (registeredPrefixObserverNormalEquiv hn j hj).apply_symm_apply x

end Paper44
