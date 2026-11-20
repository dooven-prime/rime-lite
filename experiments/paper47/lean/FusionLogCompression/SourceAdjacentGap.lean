import FusionLogCompression.M2AdjacentFusion

namespace FusionLogCompression

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The ordered source packets `A,B` meet at a source-atom boundary: the
source atoms represented by `x` and `x+1` lie in the respective fibers.
Keeping the order in this predicate is essential when there are exactly two
packets, since either boundary may be used for an ordered fusion record. -/
def SourceAdjacentPackets (placed : Placement n (Finset (ZMod n)))
    (A B : Finset (ZMod n)) : Prop :=
  ∃ lift : SourceOrderLift n, placed = placementOfMap lift.position ∧
    ∃ x : ℤ,
      sourceFiber lift.position (lift.map x : ZMod n) = A ∧
      sourceFiber lift.position (lift.map (x + 1) : ZMod n) = B

/-- Source-level adjacency of two ordered atom blocks, before choosing any
physical coordinates or integer-lift representatives. -/
def SourceAtomAdjacent (A B : Finset (ZMod n)) : Prop :=
  ∃ a : ZMod n, a ∈ A ∧ a + 1 ∈ B

/-- Reduction of a lifted integer input to its represented source atom does
not change its physical position modulo `n`. -/
theorem SourceOrderLift.position_intCast (lift : SourceOrderLift n) (x : ℤ) :
    lift.position (x : ZMod n) = (lift.map x : ZMod n) := by
  rw [SourceOrderLift.position]
  have hval : ((x : ZMod n).val : ℤ) = x % n := ZMod.val_intCast x
  have hdecomp : x = ((x : ZMod n).val : ℤ) + (x / n) * n := by
    calc
      x = x % n + (x / n) * n := (Int.emod_add_ediv_mul x n).symm
      _ = ((x : ZMod n).val : ℤ) + (x / n) * n := by rw [hval]
  have hperiod := lift.periodic ((x : ZMod n).val : ℤ) (x / n)
  rw [show ((x : ZMod n).val : ℤ) + (x / n) * n = x by omega] at hperiod
  have hcast := congrArg (fun z : ℤ => (z : ZMod n)) hperiod
  simpa using hcast.symm

/-- A source-atom boundary between two occupied packets determines the
corresponding consecutive fibers of any source-order lift for that placement. -/
theorem sourceAdjacentPackets_of_sourceAtoms
    (placed : Placement n (Finset (ZMod n))) (A B : Finset (ZMod n))
    (ordered : SourceOrdered placed)
    (hA : ∃ q, placed q = some A) (hB : ∃ q, placed q = some B)
    (hadj : SourceAtomAdjacent A B) :
    SourceAdjacentPackets placed A B := by
  obtain ⟨lift, hplaced⟩ := ordered
  obtain ⟨qA, hqA⟩ := hA
  obtain ⟨qB, hqB⟩ := hB
  obtain ⟨a, haA, haB⟩ := hadj
  have hfiberA : sourceFiber lift.position qA = A :=
    ((placementOfMap_some_iff lift.position qA A).mp (hplaced ▸ hqA)).1
  have hfiberB : sourceFiber lift.position qB = B :=
    ((placementOfMap_some_iff lift.position qB B).mp (hplaced ▸ hqB)).1
  have hpositionA : lift.position a = qA := by
    have : a ∈ sourceFiber lift.position qA := by rw [hfiberA]; exact haA
    exact (mem_sourceFiber lift.position a qA).mp this
  have hpositionB : lift.position (a + 1) = qB := by
    have : a + 1 ∈ sourceFiber lift.position qB := by rw [hfiberB]; exact haB
    exact (mem_sourceFiber lift.position (a + 1) qB).mp this
  let x : ℤ := a.val
  have hx : (x : ZMod n) = a := by
    dsimp [x]
    exact_mod_cast ZMod.natCast_zmod_val a
  have hxnext : ((x + 1 : ℤ) : ZMod n) = a + 1 := by
    calc
      ((x + 1 : ℤ) : ZMod n) = (x : ZMod n) + 1 := by push_cast; rfl
      _ = a + 1 := by rw [hx]
  have hmapA : (lift.map x : ZMod n) = qA := by
    have h := SourceOrderLift.position_intCast lift x
    rw [hx] at h
    exact h.symm.trans hpositionA
  have hmapB : (lift.map (x + 1) : ZMod n) = qB := by
    have h := SourceOrderLift.position_intCast lift (x + 1)
    rw [hxnext] at h
    exact h.symm.trans hpositionB
  refine ⟨lift, hplaced, x, ?_, ?_⟩
  · rw [hmapA, hfiberA]
  · rw [hmapB, hfiberB]

/-- An ordered adjacent pair of source fibers has a physical positive gap
whose interior sites are all holes. The gap is computed from the lift's
one-source-step jump; source order prevents an occupied site from being
inserted inside that jump. -/
theorem sourceAdjacentPackets_gap
    (placed : Placement n (Finset (ZMod n)))
    (A B : Finset (ZMod n)) (hAB : A ≠ B)
    (hadj : SourceAdjacentPackets placed A B) (hn : 3 ≤ n) :
    ∃ qLeft qRight : ZMod n, ∃ f : ℕ,
      placed qLeft = some A ∧ placed qRight = some B ∧
      qRight = qLeft + 1 + (f : ZMod n) ∧ f ≤ n - 2 ∧
      ∀ i : ℕ, 1 ≤ i → i ≤ f →
        placed (qRight - (i : ZMod n)) = none := by
  rcases hadj with ⟨lift, hplaced, x, hleftFiber, hrightFiber⟩
  let qLeft : ZMod n := (lift.map x : ZMod n)
  let qRight : ZMod n := (lift.map (x + 1) : ZMod n)
  let jump : ℤ := lift.map (x + 1) - lift.map x
  have hleftSource : (x : ZMod n) ∈ sourceFiber lift.position qLeft := by
    rw [mem_sourceFiber, SourceOrderLift.position_intCast]
  have hrightSource : ((x + 1 : ℤ) : ZMod n) ∈ sourceFiber lift.position qRight := by
    rw [mem_sourceFiber, SourceOrderLift.position_intCast]
  have hleftNonempty : (sourceFiber lift.position qLeft).Nonempty :=
    ⟨(x : ZMod n), hleftSource⟩
  have hrightNonempty : (sourceFiber lift.position qRight).Nonempty :=
    ⟨((x + 1 : ℤ) : ZMod n), hrightSource⟩
  have hleft : placed qLeft = some A := by
    rw [hplaced]
    exact (placementOfMap_some_iff lift.position qLeft A).2
      ⟨by simpa [qLeft] using hleftFiber, hleftFiber.symm ▸ hleftNonempty⟩
  have hright : placed qRight = some B := by
    rw [hplaced]
    exact (placementOfMap_some_iff lift.position qRight B).2
      ⟨by simpa [qRight] using hrightFiber, hrightFiber.symm ▸ hrightNonempty⟩
  have hsites : qLeft ≠ qRight := by
    intro heq
    apply hAB
    calc
      A = sourceFiber lift.position qLeft := hleftFiber.symm
      _ = sourceFiber lift.position qRight := by rw [heq]
      _ = B := hrightFiber
  have hmono : 0 ≤ jump := by
    dsimp [jump]
    have := lift.monotone (show x ≤ x + 1 by omega)
    omega
  have hstepBound : jump ≤ n := by
    dsimp [jump]
    have hle := lift.monotone (show x + 1 ≤ x + n by omega)
    have hperiod : lift.map (x + n) = lift.map x + n := by
      simpa using lift.periodic x 1
    rw [hperiod] at hle
    omega
  have hjumpNonzero : (jump : ZMod n) ≠ 0 := by
    intro hzero
    apply hsites
    have hcast : (lift.map (x + 1) : ZMod n) = (lift.map x : ZMod n) := by
      have hsub : (lift.map (x + 1) : ZMod n) - (lift.map x : ZMod n) = 0 := by
        simpa [jump] using hzero
      exact sub_eq_zero.mp hsub
    simpa [qLeft, qRight] using hcast.symm
  have hjumpPos : 0 < jump := by
    by_contra h
    have : jump = 0 := by omega
    exact hjumpNonzero (by simp [this])
  have hjumpLt : jump < n := by
    by_contra h
    have : jump = n := by omega
    apply hjumpNonzero
    simp [this]
  let d : ℕ := jump.toNat
  have hdcast : (d : ℤ) = jump := by
    simp [d, Int.toNat_of_nonneg (le_of_lt hjumpPos)]
  have hdpos : 1 ≤ d := by omega
  have hdlt : d < n := by omega
  let f : ℕ := d - 1
  have hdf : f + 1 = d := by dsimp [f]; omega
  have hdfcast : (d : ZMod n) = 1 + (f : ZMod n) := by
    have hnat : f + 1 = d := hdf
    calc
      (d : ZMod n) = ((f + 1 : ℕ) : ZMod n) :=
        congrArg (fun k : ℕ => (k : ZMod n)) hnat.symm
      _ = 1 + (f : ZMod n) := by push_cast; ring
  have hgap : qRight = qLeft + 1 + (f : ZMod n) := by
    have hjumpCast : (jump : ZMod n) = (d : ZMod n) := by
      simpa using congrArg (fun z : ℤ => (z : ZMod n)) hdcast.symm
    have hdiff : qRight - qLeft = (d : ZMod n) := by
      dsimp [qRight, qLeft, jump]
      calc
        (lift.map (x + 1) : ZMod n) - (lift.map x : ZMod n) =
            ((lift.map (x + 1) - lift.map x : ℤ) : ZMod n) := by rw [Int.cast_sub]
        _ = (d : ZMod n) := hjumpCast
    calc
      qRight = qLeft + (qRight - qLeft) := by ring
      _ = qLeft + (d : ZMod n) := by rw [hdiff]
      _ = qLeft + 1 + (f : ZMod n) := by rw [hdfcast]; ring
  have hgap' : qRight = qLeft + (d : ZMod n) := by
    calc
      qRight = qLeft + (1 + (f : ZMod n)) := by rw [hgap]; abel
      _ = qLeft + (d : ZMod n) := by rw [← hdfcast]
  have hfbound : f ≤ n - 2 := by
    dsimp [f]
    omega
  refine ⟨qLeft, qRight, f, hleft, hright, hgap, hfbound, ?_⟩
  intro i hi₁ hif
  by_contra hoccupied
  have hfiberNe : (sourceFiber lift.position (qRight - (i : ZMod n))).Nonempty := by
    apply Finset.nonempty_iff_ne_empty.mpr
    intro he
    apply hoccupied
    rw [hplaced, placementOfMap_none_iff]
    exact he
  obtain ⟨c, hc⟩ := hfiberNe
  have hcpos : lift.position c = qRight - (i : ZMod n) :=
    (mem_sourceFiber lift.position c _).mp hc
  have hiLt : i < d := by dsimp [f] at hif; omega
  let t : ℕ := d - i
  have htPos : 1 ≤ t := by dsimp [t]; omega
  have htLt : t < d := by dsimp [t]; omega
  have hsite : qRight - (i : ZMod n) = qLeft + (t : ZMod n) := by
    have hti : t + i = d := by dsimp [t]; omega
    have htiCast : (t : ZMod n) + (i : ZMod n) = (d : ZMod n) := by
      calc
        (t : ZMod n) + (i : ZMod n) = ((t + i : ℕ) : ZMod n) := by push_cast; rfl
        _ = (d : ZMod n) := congrArg Nat.cast hti
    have hdiCast : (d : ZMod n) - (i : ZMod n) = (t : ZMod n) := by
      rw [← htiCast]
      ring
    calc
      qRight - (i : ZMod n) = (qLeft + (d : ZMod n)) - (i : ZMod n) := by
        rw [hgap']
      _ = qLeft + ((d : ZMod n) - (i : ZMod n)) := by abel
      _ = qLeft + (t : ZMod n) := by rw [hdiCast]
  have hcast : ((lift.map c.val - (lift.map x + (t : ℤ)) : ℤ) : ZMod n) = 0 := by
    have hcpos' : lift.position c = qLeft + (t : ZMod n) := by rw [hsite] at hcpos; exact hcpos
    have hcpos'' : (lift.map c.val : ZMod n) = (lift.map x : ZMod n) + (t : ZMod n) := by
      simpa [SourceOrderLift.position, qLeft] using hcpos'
    have := congrArg (fun z : ZMod n => z - ((lift.map x : ZMod n) + (t : ZMod n))) hcpos''
    simpa using this
  obtain ⟨k, hk⟩ := (ZMod.intCast_zmod_eq_zero_iff_dvd _ n).mp hcast
  let z : ℤ := c.val - k * n
  have hzmap : lift.map z = lift.map x + (t : ℤ) := by
    have hperiod := lift.periodic c.val (-k)
    have harg : (c.val : ℤ) + (-k) * n = z := by dsimp [z]; ring
    rw [harg] at hperiod
    dsimp [z]
    nlinarith [hk, hperiod]
  have htargetGt : lift.map x < lift.map z := by
    rw [hzmap]
    have : (0 : ℤ) < (t : ℤ) := by omega
    omega
  have htargetLt : lift.map z < lift.map (x + 1) := by
    rw [hzmap]
    have : (t : ℤ) < jump := by dsimp [jump]; omega
    omega
  have hzGt : x < z := by
    by_contra h
    have hle : z ≤ x := by omega
    have hmono' := lift.monotone hle
    omega
  have hzLt : z < x + 1 := by
    by_contra h
    have hle : x + 1 ≤ z := by omega
    have hmono' := lift.monotone hle
    omega
  omega

/-- Source adjacency is now a direct M2 input: it yields a physical gap and
holes certificate, then the existing route performs exactly the requested
ordered fusion. Since `A,B` are ordered parameters, the rank-two case can use
either of its two source boundaries without quotienting away port order. -/
theorem sourceAdjacentFusionWord_spec
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (A B : Finset (ZMod n)) (hAB : A ≠ B)
    (hadj : SourceAdjacentPackets s.placed A B) (hn : 3 ≤ n) :
    ∃ qLeft qRight : ZMod n, ∃ f : ℕ,
      s.placed qLeft = some A ∧ s.placed qRight = some B ∧
      qRight = qLeft + 1 + (f : ZMod n) ∧ f ≤ n - 2 ∧
      (∀ i : ℕ, 1 ≤ i → i ≤ f →
        s.placed (qRight - (i : ZMod n)) = none) ∧
      let route := adjacentRoutePrefix qLeft qRight f
      let mid := run F s route
      FusionFree F s route ∧
        mid.placed 0 = some A ∧
        mid.placed 1 = some B ∧
        run F s (adjacentFusionWord qLeft qRight f) = stepDefect F mid ∧
        (stepDefect F mid).placed 0 = some (A ∪ B) ∧
        (stepDefect F mid).placed 1 = none ∧
        (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f := by
  obtain ⟨qLeft, qRight, f, hA, hB, hgap, hfn, hholes⟩ :=
    sourceAdjacentPackets_gap s.placed A B hAB hadj hn
  have hspec := adjacentFusionWord_spec F s qLeft qRight A B f
    hn hfn hgap hA hB hholes
  exact ⟨qLeft, qRight, f, hA, hB, hgap, hfn, hholes, hspec⟩

/-- Source-order plus a source-atom boundary between the named packets is
enough to obtain and execute the ordered physical fusion route. -/
theorem sourceAtomAdjacentFusionWord_spec
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (A B : Finset (ZMod n)) (hAB : A ≠ B)
    (ordered : SourceOrdered s.placed)
    (hA : ∃ q, s.placed q = some A) (hB : ∃ q, s.placed q = some B)
    (hadj : SourceAtomAdjacent A B) (hn : 3 ≤ n) :
    ∃ qLeft qRight : ZMod n, ∃ f : ℕ,
      s.placed qLeft = some A ∧ s.placed qRight = some B ∧
      qRight = qLeft + 1 + (f : ZMod n) ∧ f ≤ n - 2 ∧
      (∀ i : ℕ, 1 ≤ i → i ≤ f →
        s.placed (qRight - (i : ZMod n)) = none) ∧
      let route := adjacentRoutePrefix qLeft qRight f
      let mid := run F s route
      FusionFree F s route ∧
        mid.placed 0 = some A ∧
        mid.placed 1 = some B ∧
        run F s (adjacentFusionWord qLeft qRight f) = stepDefect F mid ∧
        (stepDefect F mid).placed 0 = some (A ∪ B) ∧
        (stepDefect F mid).placed 1 = none ∧
        (adjacentFusionWord qLeft qRight f).length ≤ 3 * n + f := by
  have hadjLift : SourceAdjacentPackets s.placed A B :=
    sourceAdjacentPackets_of_sourceAtoms s.placed A B ordered hA hB hadj
  exact sourceAdjacentFusionWord_spec F s A B hAB hadjLift hn

private theorem exists_step_across_unit_jump
    (f : ℤ → ℤ) (a base : ℤ) (d : ℕ)
    (hd : 0 < d)
    (hstart : f a = base) (hend : f (a + d) = base + 1)
    (hbetween : ∀ k : ℕ, k ≤ d →
      f (a + k) = base ∨ f (a + k) = base + 1) :
    ∃ k : ℕ, k < d ∧ f (a + k) = base ∧ f (a + (k + 1)) = base + 1 := by
  induction d using Nat.strong_induction_on generalizing a with
  | h d ih =>
      cases d with
      | zero => omega
      | succ d =>
          by_cases hnext : f (a + 1) = base + 1
          · exact ⟨0, by omega, by simpa using hstart, by simpa using hnext⟩
          · have hnext0 : f (a + 1) = base := by
              rcases hbetween 1 (by omega) with h0 | h1
              · exact h0
              · exact (hnext h1).elim
            by_cases hd0 : d = 0
            · subst d
              have : f (a + 1) = base + 1 := by simpa using hend
              exact (hnext this).elim
            · have hdpos : 0 < d := by omega
              have hend' : f ((a + 1) + (d : ℤ)) = base + 1 := by
                have harg : (a + 1) + (d : ℤ) = a + ((d + 1 : ℕ) : ℤ) := by
                  push_cast
                  ring
                rw [harg]
                exact hend
              have hbetween' : ∀ k : ℕ, k ≤ d →
                  f ((a + 1) + k) = base ∨ f ((a + 1) + k) = base + 1 := by
                intro k hk
                have hk' : k + 1 ≤ d + 1 := by omega
                have h := hbetween (k + 1) hk'
                have harg : (a + 1) + (k : ℤ) = a + ((k + 1 : ℕ) : ℤ) := by
                  push_cast
                  ring
                rw [harg]
                exact h
              obtain ⟨k, hk, hk0, hk1⟩ :=
                ih d (by omega) (a + 1) hdpos hnext0 hend' hbetween'
              refine ⟨k + 1, ?_, ?_, ?_⟩
              · omega
              · have harg : a + ((k + 1 : ℕ) : ℤ) = (a + 1) + (k : ℤ) := by
                  push_cast
                  abel
                rw [harg]
                exact hk0
              · convert hk1 using 1 <;> push_cast <;> abel

/-- A real two-port fusion in a source-ordered state exposes an actual
source-atom boundary between its ordered parents. The frozen lift theorem
provides the two endpoint fibers and rules out every intervening source
fiber; discreteness of the source line then gives consecutive atoms. -/
theorem sourceAtomAdjacent_of_actual_fusion
    (s : Execution n (ZMod n)) (A B : Finset (ZMod n))
    (ordered : SourceOrdered s.placed) (hn : 3 ≤ n)
    (hA : s.placed 0 = some A) (hB : s.placed 1 = some B) :
    A.Nonempty ∧ B.Nonempty ∧ A ≠ B ∧ SourceAtomAdjacent A B := by
  obtain ⟨lift, a, b, k, hplaced, haA, hbB, hab, hend, hbetween⟩ :=
    fusion_ports_source_adjacent s A B ordered hA hB
  have hAdata : sourceFiber lift.position 0 = A ∧ A.Nonempty :=
    (placementOfMap_some_iff lift.position 0 A).mp (hplaced ▸ hA)
  have hBdata : sourceFiber lift.position 1 = B ∧ B.Nonempty :=
    (placementOfMap_some_iff lift.position 1 B).mp (hplaced ▸ hB)
  have h01 : (0 : ZMod n) ≠ 1 := by
    intro heq
    have hv := congrArg ZMod.val heq
    have hzero : (0 : ZMod n).val = 0 := by simp
    have hone : (1 : ZMod n).val = 1 := by
      simpa using (ZMod.val_natCast_of_lt (by omega : 1 < n))
    rw [hzero, hone] at hv
    omega
  have hdisjoint : Disjoint A B := by
    rw [← hAdata.1, ← hBdata.1]
    apply Finset.disjoint_left.mpr
    intro x hxA hxB
    have hx0 := (mem_sourceFiber lift.position x 0).mp hxA
    have hx1 := (mem_sourceFiber lift.position x 1).mp hxB
    exact h01 (hx0.symm.trans hx1)
  have hne : A ≠ B := by
    intro heq
    subst B
    obtain ⟨x, hx⟩ := hAdata.2
    exact (Finset.disjoint_left.mp hdisjoint) hx hx
  let start : ℤ := a.val
  let finish : ℤ := b.val + k * n
  let d : ℕ := (finish - start).toNat
  have hdelta : 0 < finish - start := by
    dsimp [finish, start]
    omega
  have hdcast : (d : ℤ) = finish - start := by
    dsimp [d]
    exact Int.toNat_of_nonneg (le_of_lt hdelta)
  have hdpos : 0 < d := by
    have hpos : (0 : ℤ) < (d : ℤ) := by rw [hdcast]; exact hdelta
    exact_mod_cast hpos
  have hfinish : start + (d : ℤ) = finish := by
    rw [hdcast]
    ring
  let base : ℤ := lift.map start
  have hstart : lift.map start = base := rfl
  have hend' : lift.map (start + (d : ℤ)) = base + 1 := by
    rw [hfinish]
    simpa [base, start, finish] using hend
  have hbetween' : ∀ j : ℕ, j ≤ d →
      lift.map (start + j) = base ∨ lift.map (start + j) = base + 1 := by
    intro j hj
    have hj' : start ≤ start + (j : ℤ) := by omega
    have hj'' : start + (j : ℤ) ≤ finish := by
      rw [← hfinish]
      have hjcast : (j : ℤ) ≤ (d : ℤ) := by exact_mod_cast hj
      omega
    simpa [base, start] using hbetween (start + (j : ℤ)) hj' hj''
  obtain ⟨j, hjd, hj0, hj1⟩ :=
    exists_step_across_unit_jump lift.map start base d hdpos
      hstart hend' hbetween'
  let x : ℤ := start + j
  let atom : ZMod n := (x : ZMod n)
  have haFiber : a ∈ sourceFiber lift.position 0 := by
    rw [((placementOfMap_some_iff lift.position 0 A).mp (hplaced ▸ hA)).1]
    exact haA
  have haPosition : lift.position a = 0 :=
    (mem_sourceFiber lift.position a 0).mp haFiber
  have hstartAtom : (start : ZMod n) = a := by
    dsimp [start]
    exact_mod_cast ZMod.natCast_zmod_val a
  have hbaseCast : (base : ZMod n) = 0 := by
    have hpos := SourceOrderLift.position_intCast lift start
    rw [hstartAtom, haPosition] at hpos
    simpa [base] using hpos.symm
  have hmap0 : lift.position atom = 0 := by
    have hcast0 : (lift.map x : ZMod n) = 0 := by
      rw [show x = start + (j : ℤ) by rfl, hj0, hbaseCast]
    exact (SourceOrderLift.position_intCast lift x).trans hcast0
  have hmap1 : lift.position (atom + 1) = 1 := by
    have hcast1 : (lift.map (x + 1) : ZMod n) = 1 := by
      have hxnext : x + 1 = start + (j + 1 : ℕ) := by
        dsimp [x]
        push_cast
        abel
      rw [hxnext]
      have hj1' : lift.map (start + ((j + 1 : ℕ) : ℤ)) = base + 1 := by
        convert hj1 using 1 <;> push_cast <;> abel
      rw [hj1']
      simpa [hbaseCast]
    have hpos := SourceOrderLift.position_intCast lift (x + 1)
    have hcastAtom : ((x + 1 : ℤ) : ZMod n) = atom + 1 := by
      simp [atom]
    rw [hcastAtom] at hpos
    exact hpos.trans hcast1
  have ha : atom ∈ A := by
    have hfiber : atom ∈ sourceFiber lift.position 0 := by
      exact (mem_sourceFiber lift.position atom 0).2 hmap0
    rw [((placementOfMap_some_iff lift.position 0 A).mp (hplaced ▸ hA)).1] at hfiber
    exact hfiber
  have hb : atom + 1 ∈ B := by
    have hfiber : atom + 1 ∈ sourceFiber lift.position 1 := by
      exact (mem_sourceFiber lift.position (atom + 1) 1).2 hmap1
    rw [((placementOfMap_some_iff lift.position 1 B).mp (hplaced ▸ hB)).1] at hfiber
    exact hfiber
  exact ⟨hAdata.2, hBdata.2, hne, ⟨atom, ha, hb⟩⟩

end FusionLogCompression
