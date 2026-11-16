import RSR2.LowerRestrictedOrder
import RSR2.BellProjection

/-!
# Necessity of admissible lower retention

The finite source cycle is cut at an original atom, then filtered to atoms
still below. A packet is a cyclic interval when some such cut makes its
occurrences contiguous. Contiguity means that no three entries, in order,
have labels `inside, outside, inside`. The cut may depend on the packet.

The proof uses the lower lift of an arbitrary legal execution, not the Bell
loading algorithm. This module isolates necessity; constructive sufficiency is
proved separately in `RetentionSufficiency.lean`. Minimum-transfer optimization
is not imported from the mathematical note.
-/

namespace RSR2.Parametric

/-- Contiguous labels in a finite linear list (no `inside,outside,inside`). -/
def ListLabelInterval (B : α → Prop) (xs : List α) : Prop :=
  ∀ a b c, [a, b, c].Sublist xs → B a → B c → B b

/-- Original cyclic source order, starting at `cut`, with deleted atoms removed. -/
noncomputable def restrictedSourceCycle (n : Nat) (hn : 0 < n)
    (cut : Fin n) (U : Fin n → Prop) : List (Fin n) := by
  classical
  exact ((List.finRange n).filter (fun i =>
    decide (U (sourceAtom n hn ((cut.val : Int) + i.val))))).map
      (fun i => sourceAtom n hn ((cut.val : Int) + i.val))

/-- A packet is one interval in the source circle restricted to `U`.
No block order or within-block atom order occurs in this definition. -/
def RestrictedCyclicInterval (n : Nat) (hn : 0 < n)
    (U B : Fin n → Prop) : Prop :=
  ∃ cut : Fin n, ListLabelInterval B (restrictedSourceCycle n hn cut U)

/-- All atoms retained on the lower layer at the endpoint. -/
def lowerAtoms (P : Placement n) (a : Fin n) : Prop := (P a).1 = false

private theorem listLabelInterval_map (xs : List (Fin n))
    (horder : xs.Pairwise (· < ·)) (atom : Fin n → α) (B : α → Prop)
    (hconvex : ∀ i ∈ xs, ∀ j ∈ xs, ∀ k ∈ xs,
      i < j → j < k → B (atom i) → B (atom k) → B (atom j)) :
    ListLabelInterval B (xs.map atom) := by
  intro a b c hsub ha hc
  obtain ⟨ys, hys, heq⟩ := List.sublist_map_iff.mp hsub
  have hmap : ys.map atom = [a, b, c] := heq.symm
  obtain ⟨i, is, rfl, hi, his⟩ := List.map_eq_cons_iff.mp hmap
  obtain ⟨j, js, rfl, hj, hjs⟩ := List.map_eq_cons_iff.mp his
  obtain ⟨k, ks, rfl, hk, hks⟩ := List.map_eq_cons_iff.mp hjs
  have hnil : ks = [] := List.map_eq_nil_iff.mp hks
  subst ks
  have hord := List.Pairwise.sublist hys horder
  have hij : i < j := (List.pairwise_cons.mp hord).1 j (by simp)
  have hjk : j < k := (List.pairwise_cons.mp
    (List.pairwise_cons.mp hord).2).1 k (by simp)
  rw [← hj]
  exact hconvex i (hys.subset (by simp)) j (hys.subset (by simp))
    k (hys.subset (by simp)) hij hjk (hi ▸ ha) (hk ▸ hc)

/-- Cutting at a lower atom outside a packet prevents the packet's lift
from wrapping: equal packet endpoints then have equal integer lifts. -/
theorem LowerOrderLift.packet_interval_cut_outside
    (n : Nat) (hn : 0 < n) (P : Placement n) (f : LowerOrderLift n)
    (hf : f.Matches hn P) (a cut : Fin n)
    (ha : lowerAtoms P a) (hcut : lowerAtoms P cut) (hne : P cut ≠ P a)
    (i j k : Fin n) (hij : i ≤ j) (hjk : j ≤ k)
    (hi : P (sourceAtom n hn ((cut.val : Int) + i.val)) = P a)
    (hj : lowerAtoms P (sourceAtom n hn ((cut.val : Int) + j.val)))
    (hk : P (sourceAtom n hn ((cut.val : Int) + k.val)) = P a) :
    P (sourceAtom n hn ((cut.val : Int) + j.val)) = P a := by
  have hiLower : (P (sourceAtom n hn ((cut.val : Int) + i.val))).1 = false := by
    rw [hi]; exact ha
  have hkLower : (P (sourceAtom n hn ((cut.val : Int) + k.val))).1 = false := by
    rw [hk]; exact ha
  have hcLower : (P (sourceAtom n hn cut.val)).1 = false := by
    rw [sourceAtom_fin]; exact hcut
  have hcase := f.equal_packet_lift_cases n hn P hf
    ((cut.val : Int) + i.val) ((cut.val : Int) + k.val)
    (by omega) (by have := k.isLt; omega) hiLower hkLower (hi.trans hk.symm)
  have hequal : f.coord ((cut.val : Int) + k.val) =
      f.coord ((cut.val : Int) + i.val) := by
    rcases hcase with h | h
    · exact h
    · have hstart := f.nondecreasing
        (show (cut.val : Int) ≤ (cut.val : Int) + i.val by omega)
      have hend := (f.span
        (show (cut.val : Int) ≤ (cut.val : Int) + k.val by omega)
        (show (cut.val : Int) + k.val ≤ cut.val + n by have := k.isLt; omega)).2
      have he : f.coord ((cut.val : Int) + i.val) = f.coord cut.val := by omega
      have hePacket := (f.samePacket_iff_residue n hn P hf cut.val
        ((cut.val : Int) + i.val) hcLower hiLower).mpr (by rw [he])
      rw [sourceAtom_fin, hi] at hePacket
      exact False.elim (hne hePacket)
  have hleft := f.nondecreasing
    (show (cut.val : Int) + i.val ≤ (cut.val : Int) + j.val by omega)
  have hright := f.nondecreasing
    (show (cut.val : Int) + j.val ≤ (cut.val : Int) + k.val by omega)
  have hmid : f.coord ((cut.val : Int) + j.val) =
      f.coord ((cut.val : Int) + i.val) := by omega
  exact ((f.samePacket_iff_residue n hn P hf
    ((cut.val : Int) + j.val) ((cut.val : Int) + i.val) hj hiLower).mpr
      (by rw [hmid])).trans hi

/-- Every lower packet is a finite cyclic interval after deletion, including
the sole-packet case. Empty lower families impose no packet obligation. -/
theorem lowerRestrictedOrdered_retained_packet_interval
    (n : Nat) (hn : 0 < n) (P : Placement n)
    (hP : LowerRestrictedOrdered P) (a : Fin n) (ha : lowerAtoms P a) :
    RestrictedCyclicInterval n hn (lowerAtoms P) (fun b => P b = P a) := by
  classical
  obtain ⟨f, hmatch⟩ := hP
  by_cases hex : ∃ cut, lowerAtoms P cut ∧ P cut ≠ P a
  · obtain ⟨cut, hcut, hne⟩ := hex
    refine ⟨cut, ?_⟩
    unfold restrictedSourceCycle
    apply listLabelInterval_map
    · exact (List.pairwise_lt_finRange n).filter _
    · intro i hi j hj k hk hij hjk hia hka
      have hjlower : lowerAtoms P (sourceAtom n hn ((cut.val : Int) + j.val)) := by
        simpa using (List.mem_filter.mp hj).2
      exact f.packet_interval_cut_outside n hn P (hmatch hn) a cut ha hcut hne
        i j k (by omega) (by omega) hia hjlower hka
  · refine ⟨a, ?_⟩
    unfold restrictedSourceCycle
    apply listLabelInterval_map
    · exact (List.pairwise_lt_finRange n).filter _
    · intro i hi j hj k hk hij hjk hia hka
      have hjlower : lowerAtoms P (sourceAtom n hn ((a.val : Int) + j.val)) := by
        simpa using (List.mem_filter.mp hj).2
      by_cases heq : P (sourceAtom n hn ((a.val : Int) + j.val)) = P a
      · exact heq
      · exact False.elim (hex ⟨_, hjlower, heq⟩)

/-- Atoms in a chosen finite family of retained blocks. -/
def retainedAtoms (blocks : List (List (Fin n))) (a : Fin n) : Prop :=
  ∃ B ∈ blocks, a ∈ B

/-- Finite block-family admissibility; neither block order nor internal
atom order is used by the interval predicate. -/
def RetentionAdmissible (n : Nat) (hn : 0 < n)
    (blocks : List (List (Fin n))) : Prop :=
  ∀ B ∈ blocks, RestrictedCyclicInterval n hn (retainedAtoms blocks) (· ∈ B)

theorem RestrictedCyclicInterval.congr
    (h : RestrictedCyclicInterval n hn U B)
    (hU : ∀ a, U a ↔ U' a) (hB : ∀ a, B a ↔ B' a) :
    RestrictedCyclicInterval n hn U' B' := by
  have eU : U = U' := funext fun a => propext (hU a)
  have eB : B = B' := funext fun a => propext (hB a)
  simpa only [eU, eB] using h

/-- Reordering the retained blocks cannot change admissibility. -/
theorem retentionAdmissible_perm (hperm : blocks.Perm blocks') :
    RetentionAdmissible n hn blocks ↔ RetentionAdmissible n hn blocks' := by
  have hU : ∀ a, retainedAtoms blocks a ↔ retainedAtoms blocks' a := by
    intro a
    simp only [retainedAtoms, hperm.mem_iff]
  constructor
  · intro h B hB
    exact (h B (hperm.mem_iff.mpr hB)).congr hU (fun _ => Iff.rfl)
  · intro h B hB
    exact (h B (hperm.mem_iff.mp hB)).congr (fun a => (hU a).symm)
      (fun _ => Iff.rfl)

/-- Endpoint semantics for an ordered presentation and its chosen lower
blocks. A block is selected exactly when one of its atoms is below; the
partition clause will force all of that block to be below. -/
structure OrderedLayerAllocation (P : Placement n) (p : RSR2.OrderedPartition n)
    (retained : List (List (Fin n))) : Prop where
  partition : ∀ a b, samePacket P a b ↔ ∃ B ∈ p.blocks, a ∈ B ∧ b ∈ B
  subset : ∀ B ∈ retained, B ∈ p.blocks
  selected : ∀ B ∈ p.blocks, (∃ a ∈ B, lowerAtoms P a) ↔ B ∈ retained

/-- Pure endpoint bridge: the actual lower atom set is precisely the union
of the selected target blocks. No reachability hypothesis is needed. -/
theorem OrderedLayerAllocation.lowerAtoms_iff_retainedAtoms
    {n : Nat} {P : Placement n} {p : RSR2.OrderedPartition n}
    {retained : List (List (Fin n))}
    (h : OrderedLayerAllocation P p retained) (a : Fin n) :
    lowerAtoms P a ↔ retainedAtoms retained a := by
  constructor
  · intro ha
    obtain ⟨B, hB, haB, _⟩ := (h.partition a a).mp rfl
    exact ⟨B, (h.selected B hB).mp ⟨a, haB, ha⟩, haB⟩
  · rintro ⟨B, hB, haB⟩
    obtain ⟨b, hbB, hb⟩ := (h.selected B (h.subset B hB)).mpr hB
    have hba := (h.partition b a).mpr ⟨B, h.subset B hB, hbB, haB⟩
    unfold lowerAtoms at *
    rw [← hba]
    exact hb

/-- Each target block is exactly one actual endpoint packet, not merely a
subset of one. The ordered presentation's exact canonical blocks provide
the uniqueness interface. -/
theorem OrderedLayerAllocation.packet_iff_block
    {n : Nat} {P : Placement n} {p : RSR2.OrderedPartition n}
    {retained : List (List (Fin n))} {B : List (Fin n)} {a : Fin n}
    (h : OrderedLayerAllocation P p retained) (hB : B ∈ p.blocks) (ha : a ∈ B)
    (b : Fin n) : P b = P a ↔ b ∈ B := by
  obtain ⟨pre, post, hblocks⟩ := List.mem_iff_append.mp hB
  have haq := (canonicalPlacement_packet_iff p pre B post hblocks a).mpr ha
  constructor
  · intro hba
    have hc := (canonicalPlacement_samePacket_iff p b a).mpr
      ((h.partition b a).mp hba)
    apply (canonicalPlacement_packet_iff p pre B post hblocks b).mp
    exact (congrArg (fun loc => loc.2.val) hc).trans haq
  · intro hb
    exact (h.partition b a).mpr ⟨B, hB, hb, ha⟩

/-- Ordered finite-family necessity, derived from geometry rather than the
loading algorithm. This applies to arbitrary lower prefusions and transfers. -/
theorem lowerRestrictedOrdered_retentionAdmissible
    (n : Nat) (hn : 0 < n) (P : Placement n)
    (hP : LowerRestrictedOrdered P)
    (p : RSR2.OrderedPartition n) (retained : List (List (Fin n)))
    (halloc : OrderedLayerAllocation P p retained) :
    RetentionAdmissible n hn retained := by
  intro B hB
  obtain ⟨a, haB, ha⟩ := (halloc.selected B (halloc.subset B hB)).mpr hB
  exact (lowerRestrictedOrdered_retained_packet_interval n hn P hP a ha).congr
    (halloc.lowerAtoms_iff_retainedAtoms)
    (halloc.packet_iff_block (halloc.subset B hB) haB)

/-- The necessary direction of the endpoint allocation criterion for every
actual legal singleton-seed word. No sufficiency theorem is assumed. -/
theorem singleton_run_retentionAdmissible
    (n : Nat) (hn : 1 < n) (word : List Letter) (P : Placement n)
    (hrun : run n hn (seed n) word = some P)
    (p : RSR2.OrderedPartition n) (retained : List (List (Fin n)))
    (halloc : OrderedLayerAllocation P p retained) :
    RetentionAdmissible n (by omega) retained := by
  exact lowerRestrictedOrdered_retentionAdmissible n (by omega) P
    (singleton_run_lowerRestrictedOrdered n hn word P hrun) p retained halloc

/-- An order-free selection of whole classes and their restricted intervals.
`U` names the atoms assigned to the lower layer. -/
def UnorderedRetentionAdmissible (n : Nat) (hn : 0 < n)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop) : Prop :=
  (∀ a b, π.r a b → (U a ↔ U b)) ∧
    ∀ a, U a → RestrictedCyclicInterval n hn U (fun b => π.r b a)

/-- Unordered endpoint semantics; no presentation or class ordering is
supplied by the caller. -/
def EndpointLayerAllocation (P : Placement n)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop) : Prop :=
  (∀ a b, samePacket P a b ↔ π.r a b) ∧ (∀ a, lowerAtoms P a ↔ U a)

/-- Forget the ordering of the target blocks while keeping exactly the same
endpoint and retained atom set. No presentation algorithm is required. -/
theorem OrderedLayerAllocation.toEndpointLayerAllocation
    {n : Nat} {P : Placement n} {p : RSR2.OrderedPartition n}
    {retained : List (List (Fin n))} {π : RSR2.UnorderedPartition n}
    (h : OrderedLayerAllocation P p retained) (hp : p.Represents π) :
    EndpointLayerAllocation P π (retainedAtoms retained) := by
  exact ⟨fun a b => (h.partition a b).trans (hp a b),
    h.lowerAtoms_iff_retainedAtoms⟩

/-- A geometric endpoint with a target relation has an admissible unordered
lower family. This formulation is independent of all presentation choices. -/
theorem lowerRestrictedOrdered_unorderedRetentionAdmissible
    (n : Nat) (hn : 0 < n) (P : Placement n) (hP : LowerRestrictedOrdered P)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop)
    (halloc : EndpointLayerAllocation P π U) :
    UnorderedRetentionAdmissible n hn π U := by
  constructor
  · intro a b hab
    have heq := (halloc.1 a b).mpr hab
    have hlower : lowerAtoms P a ↔ lowerAtoms P b := by
      unfold lowerAtoms
      rw [heq]
    exact (halloc.2 a).symm.trans (hlower.trans (halloc.2 b))
  · intro a ha
    exact (lowerRestrictedOrdered_retained_packet_interval n hn P hP a
      ((halloc.2 a).mpr ha)).congr halloc.2 (fun b => halloc.1 b a)

/-- Reachable layer allocation implies retention admissibility for a truly
unordered target partition, over every legal history and every `n > 1`. -/
theorem singleton_run_unorderedRetentionAdmissible
    (n : Nat) (hn : 1 < n) (word : List Letter) (P : Placement n)
    (hrun : run n hn (seed n) word = some P)
    (π : RSR2.UnorderedPartition n) (U : Fin n → Prop)
    (halloc : EndpointLayerAllocation P π U) :
    UnorderedRetentionAdmissible n (by omega) π U := by
  exact lowerRestrictedOrdered_unorderedRetentionAdmissible n (by omega) P
    (singleton_run_lowerRestrictedOrdered n hn word P hrun) π U halloc

end RSR2.Parametric
