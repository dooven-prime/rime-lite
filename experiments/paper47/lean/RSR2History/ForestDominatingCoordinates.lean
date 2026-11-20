import RSR2History.ForestDominatingCut
import RSR2History.GapTerminalRouting

/-! A common cyclic cut converts actual named source and target coordinates
into a dominating coordinate certificate. The cut is proof data; its initial
and final physical phases are retained for the guarded routing theorem. -/
namespace RSR2History
open RSR2.Parametric
variable {n r : Nat} [NeZero n] [NeZero r]

private theorem fin_cast_val (j : Fin r) : (Fin.ofNat r j.val) = j := by
  apply Fin.ext
  simp [Fin.ofNat_eq_cast, Nat.mod_eq_of_lt j.isLt]

private theorem cut_initial_alignment
    (x : Fin r → Fin n) (hx : StrictMono x) (xz : x 0=0) (q : Fin r) :
    ((zsite (-((x q).val : ZMod n))).val = 0) ∨
      forestCutOffset x q (1 : Fin r) ≤ (zsite (-((x q).val : ZMod n))).val := by
  by_cases hz : (x q).val = 0
  · left; simp [hz, zsite]
  · right
    have hq : q≠0 := by intro hq; simp [hq,xz] at hz
    have hne : -q ≠ (0 : Fin r) := by simpa using hq
    have hidx : (1 : Fin r) ≤ -q := by
      by_cases hr : r=1
      · subst r; exact (hne (Subsingleton.elim _ _)).elim
      · have hr1 : 1 < r := by have := NeZero.pos r; omega
        have h1 : (1 : Fin r).val=1 := by simp [Nat.mod_eq_of_lt hr1]
        have hv : (-q).val ≠0 := by intro hh; apply hne; exact Fin.ext hh
        change (1 : Fin r).val ≤ (-q).val
        omega
    have hle := (forestCutOffset_strict x hx q).monotone hidx
    have he : forestCutOffset x q (-q) = n-(x q).val := by
      simp only [forestCutOffset, add_neg_cancel, xz, Fin.val_zero]
      have hq0 : (q : Fin r).val ≠0 := by intro hh; apply hq; exact Fin.ext hh
      rw [if_pos (by omega : 0<q.val)]
      omega
    rw [he] at hle
    have hval : (zsite (-((x q).val : ZMod n))).val=n-(x q).val := by
      have hc : -((x q).val : ZMod n) = ((n-(x q).val : Nat) : ZMod n) := by
        rw [Nat.cast_sub (x q).isLt.le, ZMod.natCast_self]
        simp
      rw [hc]
      simp only [zsite, ZMod.val_natCast]
      exact Nat.mod_eq_of_lt (by have := (x q).isLt; omega)
    simpa only [hval] using hle

namespace ForestTerminalSource
variable {P Q : Placement n}

/-- Target and source are cut at one common named root. Root identities and
literal endpoints remain fixed; the chosen source cut's actual phase is
stored explicitly in `initialCursor`. -/
theorem dominating_coordinates_with_cut (h : ForestTerminalSource n r P)
    (hr : 2 ≤ r) (coordinates : ForestTerminalCoordinates h Q) :
    ∃ q : Fin r, ∃ cert : GapTerminalCoordinates n (n-r) (r-1) P Q,
      (∀ j, cert.source j = forestCutOffset h.site q (Fin.ofNat r j)) ∧
      (∀ j, cert.target j = forestCutOffset coordinates.target q (Fin.ofNat r j)) := by
  classical
  obtain ⟨q, hq⟩ := forest_dominating_cut h.site coordinates.target
    h.site_strict coordinates.target_strict
  let source : Nat → Nat := fun j => forestCutOffset h.site q (Fin.ofNat r j)
  let target : Nat → Nat := fun j => forestCutOffset coordinates.target q (Fin.ofNat r j)
  let root : Fin n → Nat := fun a => (h.root a-q).val
  let initial : Fin n := zsite (-((h.site q).val : ZMod n))
  have hval (j : Nat) (hj : j ≤ r-1) : (Fin.ofNat r j).val = j := by
    simp [Fin.ofNat_eq_cast, Fin.val_natCast, Nat.mod_eq_of_lt (by omega : j<r)]
  refine ⟨q, {
    size := by have := h.rank_le; omega
    roots_positive := by omega
    root := root
    root_bound := fun a => by dsimp [root]; have := (h.root a-q).isLt; omega
    root_nonempty := ?_
    source := source
    source_zero := by
      change forestCutOffset h.site q (Fin.ofNat r 0) = 0
      simpa using forestCutOffset_zero h.site h.site_strict q
    source_strict := ?_
    source_lt := fun j _ => forestCutOffset_lt h.site h.site_strict q _
    source_fits := ?_
    target := target
    target_zero := by
      change forestCutOffset coordinates.target q (Fin.ofNat r 0) = 0
      simpa using forestCutOffset_zero coordinates.target coordinates.target_strict q
    target_strict := ?_
    target_lt := fun j _ => forestCutOffset_lt coordinates.target coordinates.target_strict q _
    target_fits := fun j _ => hq (Fin.ofNat r j)
    phase := coordinates.phase+((coordinates.target q).val : ZMod n)
    initialCursor := initial
    initial_alignment := by
      change initial.val = 0 ∨ source 1 ≤ initial.val
      have he : Fin.ofNat r 1 = (1 : Fin r) := by
        apply Fin.ext
        simp [Fin.ofNat_eq_cast]
      simpa only [source, initial, he] using
        (cut_initial_alignment h.site h.site_strict h.site_zero q)
    start := ?_
    finish := ?_ }, (by intro j; rfl), (by intro j; rfl)⟩
  · intro j hj
    obtain ⟨a, ha⟩ := h.root_nonempty (q+(Fin.ofNat r j))
    refine ⟨a, ?_⟩
    dsimp [root]
    rw [ha, add_sub_cancel_left]
    exact hval j hj
  · intro i j hij hj
    apply forestCutOffset_strict h.site h.site_strict q
    change (Fin.ofNat r i).val < (Fin.ofNat r j).val
    rw [hval i (by omega), hval j hj]
    exact hij
  · intro j hj
    have hh := forestCutOffset_upper h.site h.site_strict q (Fin.ofNat r j)
    rw [hval j hj] at hh
    dsimp [source]
    omega
  · intro i j hij hj
    apply forestCutOffset_strict coordinates.target coordinates.target_strict q
    change (Fin.ofNat r i).val < (Fin.ofNat r j).val
    rw [hval i (by omega), hval j hj]
    exact hij
  · funext a
    have he : q+(Fin.ofNat r (root a)) = h.root a := by
      change q+Fin.ofNat r (h.root a-q).val = h.root a
      rw [fin_cast_val]
      exact add_sub_cancel _ _
    have hc := forestCutOffset_cast h.site h.site_strict q (Fin.ofNat r (root a))
    rw [he] at hc
    change phaseShift P true (initial.val : ZMod n) a =
      (true, zsite (source (root a) : ZMod n))
    simp only [phaseShift, h.start a, if_pos rfl]
    change (true, zsite (((h.site (h.root a)).val : ZMod n) +
      (initial.val : ZMod n))) = (true, zsite (source (root a) : ZMod n))
    dsimp only [source, initial]
    rw [zsite_val_cast, hc]
    congr 1
    abel
  · funext a
    have he : q+(Fin.ofNat r (root a)) = h.root a := by
      change q+Fin.ofNat r (h.root a-q).val = h.root a
      rw [fin_cast_val]
      exact add_sub_cancel _ _
    have hc := forestCutOffset_cast coordinates.target coordinates.target_strict q
      (Fin.ofNat r (root a))
    rw [he] at hc
    change Q a = phaseShift (combCoordinatePlacement root target) true
      (coordinates.phase+((coordinates.target q).val : ZMod n)) a
    simp only [phaseShift, combCoordinatePlacement, if_pos rfl, zsite_val_cast]
    rw [coordinates.finish a]
    dsimp only [target]
    rw [hc]
    congr 1
    abel

/-- Forget only the auxiliary choice of a common cut. -/
theorem dominating_coordinates (h : ForestTerminalSource n r P)
    (hr : 2 ≤ r) (coordinates : ForestTerminalCoordinates h Q) :
    Nonempty (GapTerminalCoordinates n (n-r) (r-1) P Q) := by
  obtain ⟨_, cert, _, _⟩ := h.dominating_coordinates_with_cut hr coordinates
  exact ⟨cert⟩

/-- Cyclicly matching actual named placements always admit a common cut
with source coordinates dominating target coordinates. -/
theorem dominating_coordinates_of_same_cycle (h : ForestTerminalSource n r P)
    (hr : 2 ≤ r)
    (hsig : (cyclicSignature P true).IsRotated (cyclicSignature Q true)) :
    Nonempty (GapTerminalCoordinates n (n-r) (r-1) P Q) := by
  obtain ⟨coordinates⟩ := h.target_coordinates hsig
  exact h.dominating_coordinates hr coordinates

end ForestTerminalSource
end RSR2History
