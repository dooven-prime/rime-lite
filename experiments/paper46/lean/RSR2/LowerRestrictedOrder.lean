import RSR2.Parameterized

/-!
# Lower restricted source order

A monotone degree-one integer lift is an execution-independent geometric
certificate. Its residues agree with the physical sites of atoms still below;
transferred atoms impose no constraint. Thus deletion does not require an
invariant for either the upper source order or the original full partition.

The lift is updated by the actual five-letter semantics. In particular the
lower defect acts on the lift even at deleted source atoms (ghost coordinates).
Those coordinates are proof witnesses, not additional machine state.
-/

namespace RSR2.Parametric

/-- The atom represented by an integer source coordinate. -/
def sourceAtom (n : Nat) (hn : 0 < n) (x : Int) : Fin n :=
  ⟨(x % (n : Int)).toNat, by
    have hnonneg := Int.emod_nonneg x (show (n : Int) ≠ 0 by omega)
    have hlt := Int.emod_lt_of_pos x (show (0 : Int) < n by omega)
    omega⟩

theorem sourceAtom_val (n : Nat) (hn : 0 < n) (x : Int) :
    ((sourceAtom n hn x).val : Int) = x % (n : Int) := by
  have h := Int.emod_nonneg x (show (n : Int) ≠ 0 by omega)
  simp [sourceAtom, Int.toNat_of_nonneg h]

theorem sourceAtom_fin (n : Nat) (hn : 0 < n) (a : Fin n) :
    sourceAtom n hn a.val = a := by
  apply Fin.ext
  have h := sourceAtom_val n hn a.val
  rw [Int.emod_eq_of_lt (by omega) (by omega)] at h
  omega

theorem sourceAtom_periodic (n : Nat) (hn : 0 < n) (x : Int) :
    sourceAtom n hn (x + n) = sourceAtom n hn x := by
  apply Fin.ext
  simp [sourceAtom]

/-- A genuine geometric order certificate, with no stored execution word. -/
structure LowerOrderLift (n : Nat) where
  coord : Int → Int
  nondecreasing : ∀ {x y}, x ≤ y → coord x ≤ coord y
  periodic : ∀ x, coord (x + n) = coord x + n

/-- Only atoms still on the lower layer must match their lifted coordinates. -/
def LowerOrderLift.Matches (f : LowerOrderLift n) (hn : 0 < n)
    (P : Placement n) : Prop :=
  ∀ x : Int, (P (sourceAtom n hn x)).1 = false →
    f.coord x % (n : Int) = ((P (sourceAtom n hn x)).2.val : Int)

def LowerRestrictedOrdered (P : Placement n) : Prop :=
  ∃ f : LowerOrderLift n, ∀ hn : 0 < n, f.Matches hn P

def LowerOrderLift.seed (n : Nat) : LowerOrderLift n where
  coord := id
  nondecreasing := fun h => h
  periodic := by intro x; rfl

def LowerOrderLift.rotateLift (f : LowerOrderLift n) : LowerOrderLift n where
  coord := fun x => f.coord x + 1
  nondecreasing := by intro x y h; have := f.nondecreasing h; omega
  periodic := by intro x; rw [f.periodic]; omega

/-- Degree-one lift of the physical map `1 -> 0`. -/
def lowerDefectLift (n : Nat) (x : Int) : Int :=
  if x % (n : Int) = 1 then x - 1 else x

theorem lowerDefectLift_nondecreasing (n : Nat) {x y : Int} (h : x ≤ y) :
    lowerDefectLift n x ≤ lowerDefectLift n y := by
  by_cases heq : x = y
  · simp [heq]
  unfold lowerDefectLift
  split <;> split <;> omega

theorem lowerDefectLift_periodic (n : Nat) (x : Int) :
    lowerDefectLift n (x + n) = lowerDefectLift n x + n := by
  simp only [lowerDefectLift, Int.add_emod_right]
  split <;> omega

def LowerOrderLift.collapseLift (f : LowerOrderLift n) : LowerOrderLift n where
  coord := fun x => lowerDefectLift n (f.coord x)
  nondecreasing := fun h => lowerDefectLift_nondecreasing n (f.nondecreasing h)
  periodic := by intro x; rw [f.periodic, lowerDefectLift_periodic]

theorem lowerDefectLift_residue (n : Nat) (hn : 1 < n) (x : Int) :
    lowerDefectLift n x % (n : Int) =
      if x % (n : Int) = 1 then 0 else x % (n : Int) := by
  by_cases h : x % (n : Int) = 1
  · simp only [lowerDefectLift, h, if_pos]
    rw [Int.sub_emod, h]
    simp [Int.emod_eq_of_lt (show (0 : Int) ≤ 1 by omega)
      (show (1 : Int) < n by omega)]
  · simp [lowerDefectLift, h]

theorem lowerRestrictedOrdered_seed (n : Nat) :
    LowerRestrictedOrdered (seed n) := by
  refine ⟨LowerOrderLift.seed n, ?_⟩
  intro hn x _
  exact (sourceAtom_val n hn x).symm

theorem LowerOrderLift.matches_rotate_lower (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (h : f.Matches hn P) :
    f.rotateLift.Matches hn (rotate n hn P false) := by
  intro x hx
  have hlower : (P (sourceAtom n hn x)).1 = false := by
    by_cases hl : (P (sourceAtom n hn x)).1 = false
    · exact hl
    · simp [rotate, hl] at hx
  have hm := h x hlower
  change (f.coord x + 1) % (n : Int) = _
  rw [← Int.emod_add_emod, hm]
  simp only [rotate, hlower, if_pos, next_val]
  exact (Int.natCast_emod _ _).symm

theorem LowerOrderLift.matches_rotate_upper (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (h : f.Matches hn P) :
    f.Matches hn (rotate n hn P true) := by
  intro x hx
  by_cases hl : (P (sourceAtom n hn x)).1 = true
  · simp [rotate, hl] at hx
  · have heq : rotate n hn P true (sourceAtom n hn x) =
        P (sourceAtom n hn x) := by simp [rotate, hl]
    rw [heq] at hx ⊢
    exact h x hx

theorem LowerOrderLift.matches_collapse_lower (n : Nat) (hn : 1 < n)
    (P : Placement n) (f : LowerOrderLift n) (h : f.Matches (by omega) P) :
    f.collapseLift.Matches (by omega) (collapse n hn P false) := by
  intro x hx
  by_cases hp : P (sourceAtom n (by omega) x) = (false, site1 n hn)
  · have hm := h x (show (P (sourceAtom n (by omega) x)).1 = false by rw [hp])
    change lowerDefectLift n (f.coord x) % (n : Int) = _
    rw [lowerDefectLift_residue n hn]
    simp [hp, site1] at hm
    simp [hm, collapse, hp, site0]
  · have heq : collapse n hn P false (sourceAtom n (by omega) x) =
        P (sourceAtom n (by omega) x) := by simp [collapse, hp]
    rw [heq] at hx ⊢
    have hm := h x hx
    have hnot : f.coord x % (n : Int) ≠ 1 := by
      intro he
      have hsite : (P (sourceAtom n (by omega) x)).2 = site1 n hn := by
        apply Fin.ext
        simp only [site1]
        omega
      apply hp
      exact Prod.ext hx hsite
    change lowerDefectLift n (f.coord x) % (n : Int) = _
    rw [lowerDefectLift_residue n hn, if_neg hnot]
    exact hm

theorem LowerOrderLift.matches_collapse_upper (n : Nat) (hn : 1 < n)
    (P : Placement n) (f : LowerOrderLift n) (h : f.Matches (by omega) P) :
    f.Matches (by omega) (collapse n hn P true) := by
  intro x hx
  by_cases hp : P (sourceAtom n (by omega) x) = (true, site1 n hn)
  · simp [collapse, hp] at hx
  · have heq : collapse n hn P true (sourceAtom n (by omega) x) =
        P (sourceAtom n (by omega) x) := by simp [collapse, hp]
    rw [heq] at hx ⊢
    exact h x hx

/-- Removing lower atoms drops constraints; it never imposes an upper order. -/
theorem LowerOrderLift.matches_lift (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (h : f.Matches hn P) :
    f.Matches hn (liftPacket n hn P) := by
  intro x hx
  by_cases hp : P (sourceAtom n hn x) = (false, site0 n hn)
  · simp [liftPacket, hp] at hx
  · have heq : liftPacket n hn P (sourceAtom n hn x) =
        P (sourceAtom n hn x) := by simp [liftPacket, hp]
    rw [heq] at hx ⊢
    exact h x hx

/-- Preservation for every successful raw letter, including the guarded lift. -/
theorem lowerRestrictedOrdered_step (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (hP : LowerRestrictedOrdered P) (hstep : step n hn P letter = some Q) :
    LowerRestrictedOrdered Q := by
  obtain ⟨f, hf⟩ := hP
  cases letter with
  | p layer =>
      have hQ : Q = rotate n (by omega) P layer := by
        simpa only [step_p, Option.some.injEq] using hstep.symm
      subst Q
      cases layer
      · exact ⟨f.rotateLift, fun hp => f.matches_rotate_lower n hp P (hf hp)⟩
      · exact ⟨f, fun hp => f.matches_rotate_upper n hp P (hf hp)⟩
  | d layer =>
      have hQ : Q = collapse n hn P layer := by
        simpa only [step_d, Option.some.injEq] using hstep.symm
      subst Q
      cases layer
      · exact ⟨f.collapseLift, fun _ => f.matches_collapse_lower n hn P (hf (by omega))⟩
      · exact ⟨f, fun _ => f.matches_collapse_upper n hn P (hf (by omega))⟩
  | v =>
      obtain ⟨_, hQ⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      subst Q
      exact ⟨f, fun hp => f.matches_lift n hp P (hf hp)⟩

theorem lowerRestrictedOrdered_run (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hP : LowerRestrictedOrdered P) (hrun : run n hn P word = some Q) :
    LowerRestrictedOrdered Q := by
  induction word generalizing P with
  | nil =>
      have hQ : P = Q := by simpa only [run, Option.some.injEq] using hrun
      exact hQ ▸ hP
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have hr : run n hn R rest = some Q := by simpa [run, hs] using hrun
          exact ih R (lowerRestrictedOrdered_step n hn P R letter hP hs) hr

/-- RSR-2-C1: every legally reached prefix admits a lower restricted-order lift. -/
theorem singleton_run_lowerRestrictedOrdered (n : Nat) (hn : 1 < n)
    (word : List Letter) (Q : Placement n)
    (hrun : run n hn (seed n) word = some Q) :
    LowerRestrictedOrdered Q :=
  lowerRestrictedOrdered_run n hn (seed n) Q word
    (lowerRestrictedOrdered_seed n) hrun

/-- Within one source turn the lift traverses at most one physical turn. -/
theorem LowerOrderLift.span (f : LowerOrderLift n) {x y : Int}
    (hxy : x ≤ y) (hy : y ≤ x + n) :
    f.coord x ≤ f.coord y ∧ f.coord y ≤ f.coord x + n := by
  refine ⟨f.nondecreasing hxy, ?_⟩
  have h := f.nondecreasing hy
  rw [f.periodic] at h
  exact h

theorem LowerOrderLift.samePacket_iff_residue (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (hf : f.Matches hn P)
    (x y : Int) (hx : (P (sourceAtom n hn x)).1 = false)
    (hy : (P (sourceAtom n hn y)).1 = false) :
    P (sourceAtom n hn x) = P (sourceAtom n hn y) ↔
      f.coord x % (n : Int) = f.coord y % (n : Int) := by
  rw [hf x hx, hf y hy]
  constructor
  · intro h
    exact congrArg (fun loc : Location n => (loc.2.val : Int)) h
  · intro h
    apply Prod.ext
    · rw [hx, hy]
    · apply Fin.ext
      omega

/-- Equal endpoint packets have equal lifts, or differ by one complete turn. -/
theorem LowerOrderLift.equal_packet_lift_cases (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (hf : f.Matches hn P)
    (x z : Int) (hxz : x ≤ z) (hz : z ≤ x + n)
    (hx : (P (sourceAtom n hn x)).1 = false)
    (hzlower : (P (sourceAtom n hn z)).1 = false)
    (heq : P (sourceAtom n hn x) = P (sourceAtom n hn z)) :
    f.coord z = f.coord x ∨ f.coord z = f.coord x + n := by
  have hmod := (f.samePacket_iff_residue n hn P hf x z hx hzlower).mp heq
  have hspan := f.span hxz hz
  have hzero : (f.coord z - f.coord x) % (n : Int) = 0 := by
    rw [Int.sub_emod, ← hmod]
    simp
  by_cases hlt : f.coord z - f.coord x < n
  · rw [Int.emod_eq_of_lt (by omega) hlt] at hzero
    left
    omega
  · right
    omega

/-- A lower packet occupies one cyclic source interval after deleted atoms
are ignored. One of the two arcs between any equal-labelled endpoints contains
only that packet's remaining atoms. This includes intervals crossing `n-1 -> 0`.
-/
theorem lowerRestrictedOrdered_packet_cyclic_interval
    (n : Nat) (hn : 0 < n) (P : Placement n)
    (hP : LowerRestrictedOrdered P) (x z : Int)
    (hxz : x ≤ z) (hz : z ≤ x + n)
    (hx : (P (sourceAtom n hn x)).1 = false)
    (hzlower : (P (sourceAtom n hn z)).1 = false)
    (heq : P (sourceAtom n hn x) = P (sourceAtom n hn z)) :
    (∀ y : Int, x ≤ y → y ≤ z → (P (sourceAtom n hn y)).1 = false →
      P (sourceAtom n hn y) = P (sourceAtom n hn x)) ∨
    (∀ y : Int, z ≤ y → y ≤ x + n → (P (sourceAtom n hn y)).1 = false →
      P (sourceAtom n hn y) = P (sourceAtom n hn x)) := by
  obtain ⟨f, hmatch⟩ := hP
  have hf := hmatch hn
  rcases f.equal_packet_lift_cases n hn P hf x z hxz hz hx hzlower heq with h | h
  · left
    intro y hxy hyz hylower
    have h1 := f.nondecreasing hxy
    have h2 := f.nondecreasing hyz
    have he : f.coord y = f.coord x := by omega
    exact (f.samePacket_iff_residue n hn P hf y x hylower hx).mpr (by rw [he])
  · right
    intro y hzy hyend hylower
    have h1 := f.nondecreasing hzy
    have h2 := f.nondecreasing hyend
    rw [f.periodic] at h2
    have he : f.coord y = f.coord x + n := by omega
    exact (f.samePacket_iff_residue n hn P hf y x hylower hx).mpr
      (by rw [he, Int.add_emod_right])

/-- Directed physical distance is exactly the lift increment when two distinct
lower packets are encountered within one source turn. -/
theorem LowerOrderLift.forward_offset (n : Nat) (hn : 0 < n)
    (P : Placement n) (f : LowerOrderLift n) (hf : f.Matches hn P)
    (x y : Int) (hxy : x ≤ y) (hy : y ≤ x + n)
    (hx : (P (sourceAtom n hn x)).1 = false)
    (hylower : (P (sourceAtom n hn y)).1 = false)
    (hne : P (sourceAtom n hn x) ≠ P (sourceAtom n hn y)) :
    0 < f.coord y - f.coord x ∧ f.coord y - f.coord x < n ∧
    (((P (sourceAtom n hn y)).2.val : Int) -
      ((P (sourceAtom n hn x)).2.val : Int)) % (n : Int) =
        f.coord y - f.coord x := by
  have hs := f.span hxy hy
  have hzero : f.coord y ≠ f.coord x := by
    intro he
    apply hne
    exact (f.samePacket_iff_residue n hn P hf x y hx hylower).mpr (by rw [he])
  have hfull : f.coord y ≠ f.coord x + n := by
    intro he
    apply hne
    exact (f.samePacket_iff_residue n hn P hf x y hx hylower).mpr
      (by rw [he, Int.add_emod_right])
  have hpos : 0 < f.coord y - f.coord x := by omega
  have hlt : f.coord y - f.coord x < n := by omega
  refine ⟨hpos, hlt, ?_⟩
  rw [Int.sub_emod, ← hf y hylower, ← hf x hx]
  simp only [Int.emod_emod]
  exact (Int.sub_emod (f.coord y) (f.coord x) (n : Int)).symm.trans
    (Int.emod_eq_of_lt (by omega) hlt)

/-- Any three different lower packets have the same positive circular order
in the restricted source cycle and in physical space. Two-packet and empty
cases do not impose an artificial choice of orientation. -/
theorem lowerRestrictedOrdered_three_packet_order
    (n : Nat) (hn : 0 < n) (P : Placement n)
    (hP : LowerRestrictedOrdered P) (x y z : Int)
    (hxy : x < y) (hyz : y < z) (hz : z < x + n)
    (hx : (P (sourceAtom n hn x)).1 = false)
    (hy : (P (sourceAtom n hn y)).1 = false)
    (hzlower : (P (sourceAtom n hn z)).1 = false)
    (hxyne : P (sourceAtom n hn x) ≠ P (sourceAtom n hn y))
    (hxzne : P (sourceAtom n hn x) ≠ P (sourceAtom n hn z))
    (hyzne : P (sourceAtom n hn y) ≠ P (sourceAtom n hn z)) :
    (((P (sourceAtom n hn y)).2.val : Int) -
      ((P (sourceAtom n hn x)).2.val : Int)) % (n : Int) <
    (((P (sourceAtom n hn z)).2.val : Int) -
      ((P (sourceAtom n hn x)).2.val : Int)) % (n : Int) := by
  obtain ⟨f, hmatch⟩ := hP
  have hf := hmatch hn
  have h1 := f.forward_offset n hn P hf x y (by omega) (by omega) hx hy hxyne
  have h2 := f.forward_offset n hn P hf x z (by omega) (by omega) hx hzlower hxzne
  have h3 := f.forward_offset n hn P hf y z (by omega) (by omega) hy hzlower hyzne
  rw [h1.2.2, h2.2.2]
  omega

end RSR2.Parametric
