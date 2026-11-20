import RSR2History.ForestGapMomentGeometry

/-! A gap profile is intrinsic to named physical positions. A common
physical translation and common cyclic reindexing do not change its moment. -/
namespace RSR2History
open RegisteredAbsorptionChains (GapFrame)
variable {n r : Nat} [NeZero n] [NeZero r]

/-- Every frame gap is a strict natural representative modulo the physical
ring size, including the one-root frame's gap `n-1`. -/
theorem forestGapFrame_gap_lt {α : Type*} (frame : GapFrame n r α) (j : ZMod r) :
    frame.gap j < n := by
  have hs : frame.gap j ≤ n-r := by
    have he := Finset.single_le_sum (f := frame.gap)
      (fun i _ => Nat.zero_le (frame.gap i)) (Finset.mem_univ j)
    simpa only [frame.gap_total] using he
  have hn := NeZero.pos n
  have hr := NeZero.pos r
  omega

/-- Named successor positions determine the natural gap. A common physical
phase is retained in the hypothesis and cancels, rather than being free. -/
theorem forestGapFrame_gap_eq_of_positions
    {α β : Type*} (A : GapFrame n r α) (B : GapFrame n r β)
    (c : ZMod r) (phase : ZMod n)
    (positions : ∀ j, A.position (j+c) = B.position j + phase) (j : ZMod r) :
    A.gap (j+c) = B.gap j := by
  have he := positions (j+1)
  rw [show j+1+c=(j+c)+1 by abel, A.next_eq, B.next_eq, positions j] at he
  have hcast : (A.gap (j+c) : ZMod n) = (B.gap j : ZMod n) := by
    linear_combination he
  have hv := congrArg ZMod.val hcast
  simpa only [ZMod.val_natCast, Nat.mod_eq_of_lt (forestGapFrame_gap_lt A (j+c)),
    Nat.mod_eq_of_lt (forestGapFrame_gap_lt B j)] using hv

/-- A profile comparison preserves the same cyclic root correspondence. -/
theorem forestGapFrame_profile_eq_of_positions
    (A B : GapFrame n r (Fin n)) (c : ZMod r) (phase : ZMod n)
    (positions : ∀ j, A.position (j+c) = B.position j + phase) :
    (fun i : Fin r => forestFrameGapProfile A ((ZMod.finEquiv r).symm c+i)) =
      forestFrameGapProfile B := by
  funext i
  unfold forestFrameGapProfile
  have hcast : ((((ZMod.finEquiv r).symm c+i).val : Nat) : ZMod r) =
      (i.val : ZMod r)+c := by
    have hv : ((ZMod.finEquiv r).symm c).val = c.val := by
      cases r with
      | zero => exact (NeZero.ne 0 rfl).elim
      | succ r => rfl
    simp [Fin.val_add, Nat.cast_add, hv, add_comm]
  rw [hcast]
  exact forestGapFrame_gap_eq_of_positions A B c phase positions _

/-- Physical phase changes and cyclic choices of the same named root cut
leave the source hole moment unchanged. -/
theorem forestGapFrame_moment_eq_of_positions
    (A B : GapFrame n r (Fin n)) (c : ZMod r) (phase : ZMod n)
    (positions : ∀ j, A.position (j+c) = B.position j + phase) :
    forestGapMoment (forestFrameGapProfile A) =
      forestGapMoment (forestFrameGapProfile B) := by
  have he := forestGapFrame_profile_eq_of_positions A B c phase positions
  have hm := congrArg forestGapMoment he
  simpa only [forestGapMoment_rotate] using hm

end RSR2History
