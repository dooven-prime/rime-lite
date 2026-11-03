import FutureEvent.RegistrationDomain

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def sourceOffset (lift : SourceOrderLift n) (atom : ZMod n) : ℕ :=
  (lift.map atom.val - lift.map 0).toNat

omit [NeZero n] in
theorem sourceOffset_int (lift : SourceOrderLift n) (atom : ZMod n) :
    (sourceOffset lift atom : ℤ) = lift.map atom.val - lift.map 0 := by
  exact Int.toNat_of_nonneg (sub_nonneg.mpr (lift.monotone (by omega)))

omit [NeZero n] in
@[simp] theorem sourceOffset_zero (lift : SourceOrderLift n) :
    sourceOffset lift 0 = 0 := by simp [sourceOffset]

omit [NeZero n] in
theorem sourceOffset_position (lift : SourceOrderLift n) (atom : ZMod n) :
    lift.position atom = lift.position 0 + (sourceOffset lift atom : ZMod n) := by
  have hc := congrArg (fun k : ℤ => (k : ZMod n)) (sourceOffset_int lift atom)
  push_cast at hc
  unfold SourceOrderLift.position
  simp only [ZMod.val_zero, Nat.cast_zero]
  rw [hc]
  abel

theorem sourceOffset_le (lift : SourceOrderLift n) (atom : ZMod n) :
    sourceOffset lift atom ≤ n := by
  have htop : lift.map (n : ℤ) = lift.map 0 + n := by
    simpa using lift.periodic 0 1
  have hmono := lift.monotone (show (atom.val : ℤ) ≤ n by
    exact_mod_cast (ZMod.val_lt atom).le)
  have hoff := sourceOffset_int lift atom
  omega

/-- A singleton at source zero removes the duplicated endpoint of a lift turn. -/
theorem sourceOffset_lt (lift : SourceOrderLift n)
    (hzero : SingletonSource lift.position 0) (atom : ZMod n) :
    sourceOffset lift atom < n := by
  have hle := sourceOffset_le lift atom
  by_contra hlt
  have heq : sourceOffset lift atom = n := by omega
  have hpos : lift.position atom = lift.position 0 := by
    simpa [heq] using sourceOffset_position lift atom
  have hatom := hzero atom hpos
  subst atom
  have := NeZero.ne n
  simp only [sourceOffset_zero] at heq
  omega

omit [NeZero n] in
theorem sourceOffset_monotone (lift : SourceOrderLift n) (a b : ZMod n)
    (hab : a.val ≤ b.val) : sourceOffset lift a ≤ sourceOffset lift b := by
  have hmono := lift.monotone (show (a.val : ℤ) ≤ b.val by exact_mod_cast hab)
  have ha := sourceOffset_int lift a
  have hb := sourceOffset_int lift b
  omega

theorem sourceOffset_pair_bounds (lift : SourceOrderLift n) (hn : 3 ≤ n)
    (hs : SeparateSingletons lift.position) :
    1 ≤ sourceOffset lift 1 ∧ sourceOffset lift 1 ≤ n - 2 := by
  have hv1 : (1 : ZMod n).val = 1 := by
    simpa using ZMod.val_natCast_of_lt (show 1 < n by omega)
  have hv2 : (2 : ZMod n).val = 2 := by
    simpa using ZMod.val_natCast_of_lt (show 2 < n by omega)
  have hpos : 0 < sourceOffset lift 1 := by
    by_contra h
    have hz : sourceOffset lift 1 = 0 := by omega
    exact (separateSingletons_distinct lift.position (by omega) hs)
      (by simpa [hz] using (sourceOffset_position lift 1).symm)
  have hmono : sourceOffset lift 1 ≤ sourceOffset lift 2 :=
    sourceOffset_monotone lift 1 2 (by rw [hv1, hv2]; omega)
  have hstrict : sourceOffset lift 1 < sourceOffset lift 2 := by
    by_contra h
    have heq : sourceOffset lift 1 = sourceOffset lift 2 := by omega
    have hsites : lift.position 2 = lift.position 1 := by
      rw [sourceOffset_position lift 2, sourceOffset_position lift 1, heq]
    have hatoms := hs.2 2 hsites
    have hval := congrArg ZMod.val hatoms
    rw [hv2, hv1] at hval
    omega
  have hlast := sourceOffset_lt lift hs.1 2
  omega

theorem sourceOffset_gap (lift : SourceOrderLift n)
    (hs : SeparateSingletons lift.position) :
    (lift.position 1 - lift.position 0).val = sourceOffset lift 1 := by
  rw [sourceOffset_position lift 1, add_sub_cancel_left,
    ZMod.val_natCast_of_lt (sourceOffset_lt lift hs.1 1)]

/-- No source image lies strictly between the two neighboring singleton images. -/
theorem sourceOffset_empty_gap (lift : SourceOrderLift n) (hn : 3 ≤ n)
    (hs : SeparateSingletons lift.position) :
    ∀ atom, (lift.position 1 - lift.position atom).val < sourceOffset lift 1 →
      lift.position atom = lift.position 1 := by
  intro atom hgap
  by_cases hzero : atom = 0
  · subst atom
    rw [sourceOffset_gap lift hs] at hgap
    omega
  · have hv1 : (1 : ZMod n).val = 1 := by
      simpa using ZMod.val_natCast_of_lt (show 1 < n by omega)
    have hvpos : 1 ≤ atom.val := by
      have hne := (ZMod.val_eq_zero atom).not.mpr hzero
      omega
    have hge : sourceOffset lift 1 ≤ sourceOffset lift atom :=
      sourceOffset_monotone lift 1 atom (by omega)
    let distance := (lift.position 1 - lift.position atom).val
    let offset := sourceOffset lift atom
    let gap := sourceOffset lift 1
    have hcast : (distance : ZMod n) = (gap : ZMod n) - (offset : ZMod n) := by
      dsimp [distance, offset, gap]
      rw [ZMod.natCast_zmod_val, sourceOffset_position lift 1,
        sourceOffset_position lift atom]
      ring
    have hoff : offset < n := sourceOffset_lt lift hs.1 atom
    have hbound : distance + offset - gap < n := by dsimp [distance, offset, gap] at *; omega
    have hnonneg : gap ≤ distance + offset := by dsimp [offset, gap] at *; omega
    have hresidue : ((distance + offset - gap : ℕ) : ZMod n) = 0 := by
      rw [Nat.cast_sub hnonneg, Nat.cast_add, hcast]
      ring
    have hnat := congrArg ZMod.val hresidue
    rw [ZMod.val_natCast_of_lt hbound, ZMod.val_zero] at hnat
    have heq : offset = gap := by omega
    rw [sourceOffset_position lift atom, sourceOffset_position lift 1]
    exact congrArg (fun k : ℕ => lift.position 0 + (k : ZMod n)) heq

/-- Source order supplies all the concrete admission premises of the raw probe. -/
theorem sourceOrdered_gap_admission (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n)
    (hplaced : s.placed = placementOfMap f) (horder : SourceOrdered s.placed)
    (hs : SeparateSingletons f) :
    let g := (f 1 - f 0).val
    1 ≤ g ∧ g ≤ n - 2 ∧
      sourceFiber f (f 1 - (g : ZMod n)) = {0} ∧
      sourceFiber f (f 1) = {1} ∧
      (∀ atom, (f 1 - f atom).val < g → f atom = f 1) := by
  obtain ⟨lift, hlift⟩ := horder
  have heq : f = lift.position := placementOfMap_injective (hplaced.symm.trans hlift)
  subst f
  dsimp only
  rw [sourceOffset_gap lift hs]
  obtain ⟨hgpos, hgmax⟩ := sourceOffset_pair_bounds lift hn hs
  refine ⟨hgpos, hgmax, ?_, (singletonSource_iff_fiber _ _).mp hs.2,
    sourceOffset_empty_gap lift hn hs⟩
  have hleft : lift.position 1 - (sourceOffset lift 1 : ZMod n) = lift.position 0 := by
    rw [sourceOffset_position lift 1]
    ring
  rw [hleft]
  exact (singletonSource_iff_fiber _ _).mp hs.1

/-- A generated source with separate singleton atoms actually registers under
its own gap probe; admission is a conclusion, not a caller obligation. -/
theorem generated_singletons_probe (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hunregistered : s.origin = none)
    (hs : SeparateSingletons f) :
    let b := f 1
    let g := (f 1 - f 0).val
    eventTrace {0, 1} s (gapProbe b g) =
        List.replicate (gapPreFinal b g).length none ++
          [some (.registration (pairRegistration n))] ∧
      (run {0, 1} s (gapProbe b g)).origin = some (pairRegistration n) ∧
      (run {0, 1} s (gapProbe b g)).chain = s.chain ∧
      (gapProbe b g).length ≤ 3 * n - 6 := by
  obtain ⟨hgpos, hgmax, hzero, hone, hsupport⟩ :=
    sourceOrdered_gap_admission s f hn hplaced (pairGenerated_sourceOrdered s (by omega) hgen) hs
  obtain ⟨ht, ho, hc⟩ := gapProbe_first_registration s f (f 1) _ (by omega)
    hgpos (by omega) hplaced hunregistered hzero hone hsupport
  exact ⟨ht, ho, hc, gapProbe_length_le _ _ hn hgpos hgmax⟩

theorem generated_registerable_iff_singletons (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hunregistered : s.origin = none) :
    PairRegisterable s ↔ SeparateSingletons f := by
  constructor
  · rintro ⟨ho, word, hword⟩
    exact future_registration_singletons s f word (by omega) hplaced ho hword
  · intro hs
    have hprobe := generated_singletons_probe s f hn hgen hplaced hunregistered hs
    refine ⟨hunregistered, gapProbe (f 1) (f 1 - f 0).val, ?_⟩
    rw [hprobe.2.1]
    rfl

theorem registerable_gap_admission (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hreg : PairRegisterable s) :
    let g := (f 1 - f 0).val
    SeparateSingletons f ∧ 1 ≤ g ∧ g ≤ n - 2 ∧
      sourceFiber f (f 1 - (g : ZMod n)) = {0} ∧
      sourceFiber f (f 1) = {1} ∧
      (∀ atom, (f 1 - f atom).val < g → f atom = f 1) := by
  have hs := (generated_registerable_iff_singletons s f hn hgen hplaced hreg.1).mp hreg
  exact ⟨hs, sourceOrdered_gap_admission s f hn hplaced
    (pairGenerated_sourceOrdered s (by omega) hgen) hs⟩

theorem registerable_gap_prefix_fusionFree (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hreg : PairRegisterable s) :
    FusionFree {0, 1} s (gapPreFinal (f 1) (f 1 - f 0).val) := by
  obtain ⟨_, hgpos, _, _, _, hsupport⟩ :=
    registerable_gap_admission s f hn hgen hplaced hreg
  exact gapPreFinal_fusionFree {0, 1} s f (f 1) _ (by omega) hgpos hplaced hsupport

theorem generated_registerable_probe (s : Execution n (ZMod n))
    (hn : 3 ≤ n) (hgen : PairGenerated s) (hreg : PairRegisterable s) :
    ∃ (b : ZMod n) (g : ℕ), 1 ≤ g ∧ g ≤ n - 2 ∧
      eventTrace {0, 1} s (gapProbe b g) =
        List.replicate (gapPreFinal b g).length none ++
          [some (.registration (pairRegistration n))] ∧
      (run {0, 1} s (gapProbe b g)).origin = some (pairRegistration n) ∧
      (gapProbe b g).length ≤ 3 * n - 6 := by
  obtain ⟨lift, hplaced⟩ := pairGenerated_sourceOrdered s (by omega) hgen
  have hs := (generated_registerable_iff_singletons s lift.position hn hgen hplaced hreg.1).mp hreg
  obtain ⟨hgpos, hgmax, _⟩ := sourceOrdered_gap_admission s lift.position hn hplaced
    ⟨lift, hplaced⟩ hs
  obtain ⟨ht, ho, _, hlen⟩ := generated_singletons_probe s lift.position hn hgen hplaced hreg.1 hs
  exact ⟨lift.position 1, (lift.position 1 - lift.position 0).val,
    hgpos, hgmax, ht, ho, hlen⟩

end FutureEvent
