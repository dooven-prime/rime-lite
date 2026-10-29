import RegisteredAbsorptionChains.ActualChainRange
import RegisteredAbsorptionChains.FiberReachability
import RegisteredAbsorptionChains.FixedPartnerSchedule
import Mathlib.Tactic

namespace RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- A one-block cut is the entire complement of its source frontier. -/
theorem oneCut_outside_eq_remaining
    (data : ValidFiberPlacement n 1)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi) :
    data.outside ⟨0, by decide⟩ = f.remaining := by
  ext a
  rw [ValidFiberPlacement.outside, CheckpointSourceFrontier.remaining,
    mem_sourceInterval_iff f.lo f.hi f.hi_valid]
  simp only [Finset.mem_filter, Finset.mem_univ, true_and]
  have hz := data.cut_zero
  have hl := data.cut_last
  change data.cut ⟨0, by decide⟩ ≤ a.val ∧
    a.val < data.cut ⟨1, by decide⟩ ↔
      f.lo ≤ a.val ∧ a.val < f.hi
  rw [hz, hl, hu, hv]

theorem oneCut_carrier_eq_frontier
    (data : ValidFiberPlacement n 1)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi) :
    data.carrier = f.carrier := by
  ext a
  rw [f.mem_carrier_iff]
  simp [ValidFiberPlacement.carrier, hu, hv]

/-- Full-complement assembly starts with the clean code witness and ends
with precisely the carrier and its sole outside cut block, both still
attached to one actual execution. -/
theorem oneCut_assemble_named
    (F : Finset (ZMod n))
    (data : ValidFiberPlacement n 1)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s) :
    ∃ (final : Execution n (ZMod n))
      (source : LegalNamedPlacement n 2 (ZMod n)),
      CountedOutsideSchedule F f.carrier (f.hi - f.lo - 1) s final ∧
      final.placed = source.placed ∧
      source.PositivelyOrdered ∧
      source.block = data.toLegal.block := by
  let ell := f.hi - f.lo
  have hellpos : 0 < ell := by
    have := data.huv
    dsimp [ell]
    omega
  obtain ⟨r, hr, first, aligned⟩ :=
    f.exists_named_alignment F s reachable registered selected inside clean
  letI : NeZero r := hr
  have hrn : r ≤ n := by
    have := aligned.count
    have := f.lo_valid
    have := f.noncrossing
    have := f.hi_valid
    omega
  have hB : f.remaining = f.partnerR ell := by
    dsimp [CheckpointSourceFrontier.remaining,
      CheckpointSourceFrontier.partnerR, ell]
    congr 1
    omega
  have hprefix : RPartnerPrefix first f.remaining ell := by
    rw [hB]
    exact aligned.admitR F f s first ell hellpos (by dsimp [ell]; omega)
  obtain ⟨m, hm, final, lastNamed, hmEq, hplaced, hordered,
      hcarrier, hpartner, hsched, _⟩ :=
    RPartnerPrefix.assemble_named ell F f.carrier f.remaining s first
      aligned.ordered hrn aligned.source aligned.carrier registered selected
      inside (clean_partner_assembly_invariant f.carrier f.remaining s clean)
      hprefix
  have hm2 : r - ell + 1 = 2 := by
    have := aligned.count
    dsimp [ell] at *
    omega
  have hm2' : m = 2 := hmEq.trans hm2
  cases hm2'
  have hcar : data.carrier = f.carrier :=
    oneCut_carrier_eq_frontier data f hu hv
  have hout : data.outside ⟨0, by decide⟩ = f.remaining :=
    oneCut_outside_eq_remaining data f hu hv
  have hblocks : lastNamed.block = data.toLegal.block := by
    funext i
    have hi : i = 0 ∨ i = 1 := by
      have hv := i.val_lt
      have hval : i.val = 0 ∨ i.val = 1 := by omega
      rcases hval with h0 | h1
      · left
        exact ZMod.val_injective 2 (by simpa using h0)
      · right
        have hv1 : (1 : ZMod 2).val = 1 := by decide
        exact ZMod.val_injective 2 (by simpa [hv1] using h1)
    rcases hi with rfl | rfl
    · rw [hcarrier, ← hcar]
      simpa [ValidFiberPlacement.toLegal_block] using data.blockFin_zero.symm
    · rw [hpartner, ← hout]
      simp [ValidFiberPlacement.toLegal_block, ValidFiberPlacement.blockFin]
  exact ⟨final, lastNamed, hsched, hplaced, hordered, hblocks⟩

/-- For a one-block outside cut, the counted assembly and the final
fusion-free placement adjustment concatenate on the same concrete state. -/
theorem oneCut_realize_target
    (F : Finset (ZMod n))
    (data : ValidFiberPlacement n 1)
    (f : CheckpointSourceFrontier n)
    (hu : data.u = f.lo) (hv : data.v = f.hi)
    (s : Execution n (ZMod n))
    (reachable : ReachableExecution F s)
    (registered : s.origin.isSome = true)
    (selected : F.Nonempty) (inside : F ⊆ f.carrier)
    (clean : CleanOutside f.carrier s) :
    ∃ word : List Letter,
      run F s word = {s with placed := data.target} := by
  obtain ⟨final, source, hsched, hplaced, hordered, hblocks⟩ :=
    oneCut_assemble_named F data f hu hv s reachable registered selected
      inside clean
  obtain ⟨assembly, hassembly, horigin, hchain⟩ := hsched.realize
  obtain ⟨adjust, hadjust, _⟩ :=
    data.realize_from_named_source F final source hplaced hordered hblocks
  refine ⟨assembly ++ adjust, ?_⟩
  rw [run_append, hassembly, hadjust]
  cases s with
  | mk placed origin chain =>
      cases final with
      | mk placed' origin' chain' =>
          simp_all

end RegisteredAbsorptionChains
