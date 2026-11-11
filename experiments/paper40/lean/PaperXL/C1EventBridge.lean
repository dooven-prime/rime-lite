import PaperXL.C1StandardSemantics
import FusionLogInterpretation.ArbitraryInitialReplay

/-!
# Ordered-event representation bridge

This bridge is compiled against both development packages. It connects the
Paper XL ternary event code to C1's ordered effective-fusion record. The
per-letter and whole-word endpoint/log correspondence is stated in the
separate `C1RunCorrespondence` module; registration metadata remains outside
that interface.
-/

namespace PaperXL

open RegisteredAbsorptionChains

variable {n m : Nat}

def codeLeftParent (e : EventCode m) : Finset (Fin m) :=
  Finset.univ.filter (fun i => e i = 0)

def codeRightParent (e : EventCode m) : Finset (Fin m) :=
  Finset.univ.filter (fun i => e i = 1)

/-- Reconstruct C1's ordered parent tuple (and its forced union) from one
Paper XL event code. -/
def codeFusionRecord (e : EventCode m) : FusionRecord (Fin m) :=
  ⟨codeLeftParent e, codeRightParent e,
    codeLeftParent e ∪ codeRightParent e⟩

/-- The ordered parent sets retain the entire ternary event code: an atom
outside both parents has code `2`. Thus the record conversion loses no
information about an effective event. -/
theorem codeFusionRecord_injective :
    Function.Injective (codeFusionRecord (m := m)) := by
  intro e f h
  have hleft : codeLeftParent e = codeLeftParent f := congrArg FusionRecord.left h
  have hright : codeRightParent e = codeRightParent f := congrArg FusionRecord.right h
  funext i
  have he0 : e i = 0 ↔ f i = 0 := by
    have := congrArg (fun S : Finset (Fin m) => i ∈ S) hleft
    simpa [codeLeftParent] using this
  have he1 : e i = 1 ↔ f i = 1 := by
    have := congrArg (fun S : Finset (Fin m) => i ∈ S) hright
    simpa [codeRightParent] using this
  simp only [Fin.ext_iff, Fin.val_zero, Fin.val_one] at he0 he1
  apply Fin.ext
  have heBound := (e i).isLt
  have hfBound := (f i).isLt
  omega

/-- Pointwise conversion of the chronological complete event list is
injective; equality of C1 ordered records cannot hide a Paper XL event-code
difference. This is a representation fact, not a run-correspondence theorem. -/
theorem codeFusionRecord_list_injective :
    Function.Injective (List.map (codeFusionRecord (m := m))) := by
  intro xs ys h
  induction xs generalizing ys with
  | nil =>
      cases ys with
      | nil => rfl
      | cons y ys => simp at h
  | cons x xs ih =>
      cases ys with
      | nil => simp at h
      | cons y ys =>
          simp only [List.map_cons, List.cons.injEq] at h
          rcases h with ⟨hxy, htail⟩
          exact congrArg₂ List.cons (codeFusionRecord_injective hxy) (ih htail)

theorem codeLeftParent_eventCode (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    codeLeftParent (CircularLogState.eventCode E s) = c1LeftParent E s := by
  ext i
  simp only [codeLeftParent, c1LeftParent, Finset.mem_filter,
    Finset.mem_univ, true_and]
  exact eventCode_left_iff E s i

theorem codeRightParent_eventCode (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    codeRightParent (CircularLogState.eventCode E s) = c1RightParent E s := by
  ext i
  simp only [codeRightParent, c1RightParent, Finset.mem_filter,
    Finset.mem_univ, true_and]
  exact eventCode_right_iff E s i

theorem codeFusionRecord_eventCode (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    codeFusionRecord (CircularLogState.eventCode E s) =
      ⟨c1LeftParent E s, c1RightParent E s,
        c1LeftParent E s ∪ c1RightParent E s⟩ := by
  simp [codeFusionRecord, codeLeftParent_eventCode,
    codeRightParent_eventCode]

/-- The set of atoms at a C1/ZMod physical site, read from Paper XL's
per-atom endpoint representation. -/
def c1PacketAtZMod [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) (q : ZMod n) : Finset (Fin m) :=
  c1PacketAt E s ((ZMod.finEquiv n).symm q)

/-- Equality of all actual packet-at-site sets recovers every atom's literal
terminal site. This is the endpoint half of the desired C1/Paper XL bridge. -/
theorem c1PacketAtZMod_recovers_sites [NeZero n]
    (E : CircularEnvironment n m) (s t : CircularLogState n m)
    (h : c1PacketAtZMod E s = c1PacketAtZMod E t) : s.site = t.site := by
  funext i
  have hi : i ∈ c1PacketAtZMod E s ((ZMod.finEquiv n) (s.site i)) := by
    simp [c1PacketAtZMod]
  rw [h] at hi
  have ht : t.site i = s.site i := by
    simpa [c1PacketAtZMod] using hi
  exact ht.symm

/-- Encode a Paper XL per-atom site map as the C1 option-valued placement.
An empty packet set is a hole, not an occupied empty packet. -/
def c1PlacementOf [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) : Placement n (Finset (Fin m)) :=
  fun q =>
    let packet := c1PacketAtZMod E s q
    if packet.Nonempty then some packet else none

/-- Equality of encoded placements implies equality of literal per-atom
endpoints; the historical event list is intentionally not encoded here. -/
theorem c1PlacementOf_recovers_sites [NeZero n]
    (E : CircularEnvironment n m) (s t : CircularLogState n m)
    (h : c1PlacementOf E s = c1PlacementOf E t) : s.site = t.site := by
  funext i
  let q := (ZMod.finEquiv n) (s.site i)
  have hs : (c1PacketAtZMod E s q).Nonempty := by
    exact ⟨i, by simp [c1PacketAtZMod, q]⟩
  have hq := congrFun h q
  have hsome : c1PlacementOf E s q = some (c1PacketAtZMod E s q) := by
    simp [c1PlacementOf, hs]
  rw [hsome] at hq
  have ht : (c1PacketAtZMod E t q).Nonempty := by
    by_contra hne
    simp [c1PlacementOf, hne] at hq
  have heq : c1PacketAtZMod E t q = c1PacketAtZMod E s q := by
    simpa [c1PlacementOf, ht] using hq.symm
  have hi : i ∈ c1PacketAtZMod E t q := by
    rw [heq]
    simp [c1PacketAtZMod, q]
  have hsite : t.site i = s.site i := by
    simpa [c1PacketAtZMod, q] using hi
  exact hsite.symm

/-- The pair of complete ordered C1 records and literal C1 placement is a
lossless view of Paper XL's declared complete state. This does not yet prove
that the two raw execution machines commute with the conversion. -/
def c1Observation [NeZero n] (E : CircularEnvironment n m)
    (s : CircularLogState n m) :
    List (FusionRecord (Fin m)) × Placement n (Finset (Fin m)) :=
  (s.events.map codeFusionRecord, c1PlacementOf E s)

theorem c1Observation_injective [NeZero n]
    (E : CircularEnvironment n m) :
    Function.Injective (c1Observation E) := by
  intro s t h
  have hlog : s.events.map codeFusionRecord =
      t.events.map codeFusionRecord := congrArg Prod.fst h
  have hplace : c1PlacementOf E s = c1PlacementOf E t :=
    congrArg Prod.snd h
  exact CircularLogState.ext
    (c1PlacementOf_recovers_sites E s t hplace)
    (codeFusionRecord_list_injective hlog)

theorem finEquiv_rotate [NeZero n] (E : CircularEnvironment n m)
    (q : Fin n) :
    (ZMod.finEquiv n) (CircularLogState.rotate E q) =
      (ZMod.finEquiv n) q + 1 := by
  cases n with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ n =>
      change
        ((⟨(q.val + 1) % (n + 1), Nat.mod_lt _ (Nat.succ_pos n)⟩ :
            Fin (n + 1)) :
          ZMod (n + 1)) =
          (q : ZMod (n + 1)) + 1
      apply Fin.ext
      simp only [Fin.val_add]
      norm_num

theorem c1PacketAtZMod_step_p [NeZero n]
    (E : CircularEnvironment n m) (s : CircularLogState n m)
    (q : ZMod n) :
    c1PacketAtZMod E (CircularLogState.step E s .p) q =
      c1PacketAtZMod E s (q - 1) := by
  ext i
  simp only [c1PacketAtZMod, mem_c1PacketAt, CircularLogState.step,
    CircularLogState.move]
  let x := s.site i
  have hiff :
      CircularLogState.rotate E x = (ZMod.finEquiv n).symm q ↔
        x = (ZMod.finEquiv n).symm (q - 1) := by
    constructor
    · intro hx
      apply (ZMod.finEquiv n).injective
      have hq := congrArg (ZMod.finEquiv n) hx
      rw [finEquiv_rotate E x] at hq
      simp only [RingEquiv.apply_symm_apply] at hq ⊢
      rw [eq_sub_iff_add_eq]
      exact hq
    · intro hx
      apply (ZMod.finEquiv n).injective
      have hq := congrArg (ZMod.finEquiv n) hx
      simp only [RingEquiv.apply_symm_apply] at hq ⊢
      rw [finEquiv_rotate E x]
      exact eq_sub_iff_add_eq.mp hq
  simpa only [Finset.mem_filter, Finset.mem_univ, true_and] using hiff

theorem c1_port0_zmod [NeZero n] (E : CircularEnvironment n m)
    (h : C1Compatible E) :
    (ZMod.finEquiv n) E.port0 = 0 := by
  cases n with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ n =>
      change (E.port0 : Fin (n + 1)) = 0
      apply Fin.ext
      simpa using h.port0_val

theorem c1_port1_zmod [NeZero n] (E : CircularEnvironment n m)
    (h : C1Compatible E) :
    (ZMod.finEquiv n) E.port1 = 1 := by
  cases n with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ n =>
      change (E.port1 : Fin (n + 1)) = 1
      apply Fin.ext
      have hn := E.hm_lower
      have hmn := E.hm_le
      have hone : 1 < n + 1 := by omega
      simpa [Nat.mod_eq_of_lt hone] using h.port1_val

theorem c1PlacementOf_step_p [NeZero n]
    (E : CircularEnvironment n m) (s : CircularLogState n m) :
    c1PlacementOf E (CircularLogState.step E s .p) =
      rotate 1 (c1PlacementOf E s) := by
  funext q
  simp [c1PlacementOf, c1PacketAtZMod_step_p, RegisteredAbsorptionChains.rotate]

theorem c1PacketAtZMod_step_d [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (s : CircularLogState n m) (q : ZMod n) :
    c1PacketAtZMod E (CircularLogState.step E s .d) q =
      if q = (ZMod.finEquiv n) E.port0 then
        c1PacketAtZMod E s ((ZMod.finEquiv n) E.port0) ∪
          c1PacketAtZMod E s ((ZMod.finEquiv n) E.port1)
      else if q = (ZMod.finEquiv n) E.port1 then ∅
      else c1PacketAtZMod E s q := by
  unfold c1PacketAtZMod
  rw [c1PacketAt_step_d E h s ((ZMod.finEquiv n).symm q)]
  by_cases h0 : q = (ZMod.finEquiv n) E.port0
  · simp [h0]
  · by_cases h1 : q = (ZMod.finEquiv n) E.port1
    · simp [h0, h1]
    · have hf0 : (ZMod.finEquiv n).symm q ≠ E.port0 := by
        intro heq
        apply h0
        have heq' := congrArg (ZMod.finEquiv n) heq
        simpa using heq'
      have hf1 : (ZMod.finEquiv n).symm q ≠ E.port1 := by
        intro heq
        apply h1
        have heq' := congrArg (ZMod.finEquiv n) heq
        simpa using heq'
      simp only [if_neg hf0, if_neg hf1, if_neg h0, if_neg h1]


end PaperXL
