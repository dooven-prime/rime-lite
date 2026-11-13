import FusionLogAllR.MinimalTraceRigidity

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! # Carrier-anchored gaps of an actual physical placement

The integer coordinates below are witnesses for the occupied sites in one
turn, not extra machine state. Packet contents and the marked atom remain
those of the frozen execution semantics.
-/

def consecutiveGaps : List ℤ → List ℤ
  | x :: y :: rest => (y - x - 1) :: consecutiveGaps (y :: rest)
  | _ => []

theorem consecutiveGaps_translate (xs : List ℤ) (k : ℤ) :
    consecutiveGaps (xs.map (· + k)) = consecutiveGaps xs := by
  induction xs using List.twoStepInduction with
  | nil => rfl
  | singleton x => rfl
  | cons_cons x y rest _ ih =>
      simp only [List.map_cons, consecutiveGaps]
      rw [show y + k - (x + k) - 1 = y - x - 1 by ring]
      exact congrArg (fun l => (y - x - 1) :: l) (ih y)

structure PhysicalPacketRing (n : ℕ) where
  head : ℤ
  tail : List ℤ
  increasing : (head :: tail).Pairwise (· < ·)
  below_end : ∀ x ∈ tail, x < head + n

def PhysicalPacketRing.sites (ring : PhysicalPacketRing n) : List ℤ :=
  ring.head :: ring.tail

def PhysicalPacketRing.gaps (ring : PhysicalPacketRing n) : List ℤ :=
  consecutiveGaps (ring.head :: (ring.tail ++ [ring.head + n]))

theorem PhysicalPacketRing.bounds (ring : PhysicalPacketRing n) {x : ℤ}
    (hx : x ∈ ring.sites) (hn : 0 < n) :
    ring.head ≤ x ∧ x < ring.head + n := by
  rcases List.mem_cons.mp hx with rfl | hx
  · constructor <;> omega
  · have hlt := (List.pairwise_cons.mp ring.increasing).1 x hx
    exact ⟨le_of_lt hlt, ring.below_end x hx⟩

theorem PhysicalPacketRing.cast_injective {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n) {x y : ℤ}
    (hx : x ∈ ring.sites) (hy : y ∈ ring.sites)
    (heq : (x : ZMod n) = (y : ZMod n)) : x = y := by
  have hn : 0 < n := NeZero.pos n
  obtain ⟨hxl, hxu⟩ := ring.bounds hx hn
  obtain ⟨hyl, hyu⟩ := ring.bounds hy hn
  have hdiv := (ZMod.intCast_eq_intCast_iff_dvd_sub x y n).mp heq
  obtain ⟨k, hk⟩ := hdiv
  have hn' : (0 : ℤ) < n := by exact_mod_cast hn
  have hkzero : k = 0 := by
    by_contra h
    have hcases : k ≤ -1 ∨ 1 ≤ k := by omega
    rcases hcases with hneg | hpos
    · have hle : (n : ℤ) * k ≤ -n := by nlinarith
      omega
    · have hle : (n : ℤ) ≤ n * k := by nlinarith
      omega
  rw [hkzero] at hk
  omega

theorem intCast_injective_on_turn {n : ℕ} [NeZero n]
    {base x y : ℤ} (hxl : base ≤ x) (hxu : x < base + n)
    (hyl : base ≤ y) (hyu : y < base + n)
    (heq : (x : ZMod n) = (y : ZMod n)) : x = y := by
  obtain ⟨k, hk⟩ := (ZMod.intCast_eq_intCast_iff_dvd_sub x y n).mp heq
  have hn : (0 : ℤ) < n := by exact_mod_cast (NeZero.pos n)
  have hkzero : k = 0 := by
    by_contra h
    rcases (by omega : k ≤ -1 ∨ 1 ≤ k) with hneg | hpos
    · have : (n : ℤ) * k ≤ -n := by nlinarith
      omega
    · have : (n : ℤ) ≤ n * k := by nlinarith
      omega
  rw [hkzero] at hk
  omega

def PhysicalPacketRing.translate (ring : PhysicalPacketRing n) (k : ℤ) :
    PhysicalPacketRing n where
  head := ring.head + k
  tail := ring.tail.map (· + k)
  increasing := by
    exact List.Pairwise.map (fun x => x + k) (fun _ _ h => by omega) ring.increasing
  below_end := by
    intro x hx
    obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hx
    have := ring.below_end y hy
    omega

@[simp] theorem PhysicalPacketRing.translate_gaps (ring : PhysicalPacketRing n)
    (k : ℤ) : (ring.translate k).gaps = ring.gaps := by
  have h := consecutiveGaps_translate
    (ring.head :: (ring.tail ++ [ring.head + n])) k
  simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.translate,
    List.map_append, add_assoc, add_comm, add_left_comm] using h

def PhysicalPacketRing.backslide (ring : PhysicalPacketRing n)
    (hend : ∀ x ∈ ring.sites, x ≠ ring.head + n - 1) :
    PhysicalPacketRing n where
  head := ring.head - 1
  tail := ring.tail
  increasing := by
    apply List.pairwise_cons.mpr
    constructor
    · intro x hx
      have hlt := (List.pairwise_cons.mp ring.increasing).1 x hx
      omega
    · exact (List.pairwise_cons.mp ring.increasing).2
  below_end := by
    intro x hx
    have hlt := ring.below_end x hx
    have hne := hend x (List.mem_cons_of_mem _ hx)
    omega

theorem PhysicalPacketRing.backslide_sites (ring : PhysicalPacketRing n)
    (hend : ∀ x ∈ ring.sites, x ≠ ring.head + n - 1) :
    (ring.backslide hend).sites = (ring.head - 1) :: ring.tail := rfl

def PhysicalPacketRing.fuseNext (ring : PhysicalPacketRing n)
    (rest : List ℤ) (htail : ring.tail = (ring.head + 1) :: rest) :
    PhysicalPacketRing n where
  head := ring.head
  tail := rest
  increasing := by
    have hinc := ring.increasing
    rw [htail] at hinc
    apply List.pairwise_cons.mpr
    constructor
    · intro x hx
      exact (List.pairwise_cons.mp hinc).1 x (by simp [hx])
    · exact (List.pairwise_cons.mp (List.pairwise_cons.mp hinc).2).2
  below_end := by
    intro x hx
    have hend := ring.below_end
    rw [htail] at hend
    exact hend x (by simp [hx])

theorem PhysicalPacketRing.fuseNext_sites (ring : PhysicalPacketRing n)
    (rest : List ℤ) (htail : ring.tail = (ring.head + 1) :: rest) :
    (ring.fuseNext rest htail).sites = ring.head :: rest := rfl

/-- The ring reads every occupied physical site exactly once and is anchored
at the actual packet containing the marked source atom. -/
def GapRep {n : ℕ} [NeZero n] (s : Execution n (ZMod n))
    (a : ZMod n) (g : List ℤ) : Prop :=
  SourceOrdered s.placed ∧ ∃ ring : PhysicalPacketRing n,
    (∀ q, s.placed q ≠ none ↔ ∃ x ∈ ring.sites, (x : ZMod n) = q) ∧
    a ∈ (s.placed (ring.head : ZMod n)).getD ∅ ∧ g = ring.gaps

theorem gapRep_rotation {n : ℕ} [NeZero n] (F : Finset (ZMod n))
    {s : Execution n (ZMod n)} {a : ZMod n} {g : List ℤ}
    (hn : 2 ≤ n) (hrep : GapRep s a g) : GapRep (step F s .p) a g := by
  rcases hrep with ⟨horder, ring, hoccupied, hmarked, rfl⟩
  refine ⟨step_ordered F s .p hn horder, ring.translate 1, ?_, ?_, ?_⟩
  · intro q
    change s.placed (q - 1) ≠ none ↔ _
    rw [hoccupied]
    constructor
    · rintro ⟨x, hx, hq⟩
      refine ⟨x + 1, ?_, ?_⟩
      · simpa [PhysicalPacketRing.sites, PhysicalPacketRing.translate] using hx
      · push_cast
        rw [hq]
        abel
    · rintro ⟨x, hx, hq⟩
      have hmem : x ∈ ring.sites.map (· + 1) := by
        simpa [PhysicalPacketRing.sites, PhysicalPacketRing.translate] using hx
      obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hmem
      refine ⟨y, hy, ?_⟩
      push_cast at hq
      exact eq_sub_iff_add_eq.mpr hq
  · simpa [step, rotate, PhysicalPacketRing.translate] using hmarked
  · exact (ring.translate_gaps 1).symm

theorem gapRep_stationary_defect {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g)
    (h1 : s.placed 1 = none) : GapRep (step F s .d) a g := by
  have hplaced : (step F s .d).placed = s.placed := by
    rw [show (step F s .d).placed = fusionPlacement s.placed from stepDefect_placed F s]
    funext q
    by_cases hq0 : q = 0
    · subst q
      cases h0 : s.placed 0 <;> simp [fusionPlacement, h0, h1]
    by_cases hq1 : q = 1
    · subst q
      simp [fusionPlacement, hq0, h1]
    · simp [fusionPlacement, hq0, hq1]
  rcases hrep with ⟨horder, ring, hoccupied, hmarked, hg⟩
  exact ⟨step_ordered F s .d hn horder, ring,
    by simpa [hplaced] using hoccupied,
    by simpa [hplaced] using hmarked, hg⟩

/-- Moving one internal occupied coordinate by minus one changes just the
two adjacent gaps, with exactly the external-slide rewrite. -/
theorem consecutiveGaps_slide (pre post : List ℤ) (z : ℤ)
    (hpre : pre ≠ []) (hpost : post ≠ []) :
    ∃ before x y after,
      consecutiveGaps (pre ++ z :: post) = slideSource before x y after ∧
      consecutiveGaps (pre ++ (z - 1) :: post) = slideTarget before x y after := by
  induction pre using List.twoStepInduction with
  | nil => contradiction
  | singleton w =>
      cases post with
      | nil => contradiction
      | cons u rest =>
          refine ⟨[], z - w - 1, u - z - 1, consecutiveGaps (u :: rest), rfl, ?_⟩
          simp only [List.singleton_append, consecutiveGaps, slideTarget,
            List.nil_append]
          congr 1
          · ring
          · congr 1
            ring
  | cons_cons u v rest _ ih =>
      obtain ⟨before, x, y, after, hsource, htarget⟩ := ih v (by simp)
      refine ⟨(v - u - 1) :: before, x, y, after, ?_, ?_⟩
      · simpa [consecutiveGaps, slideSource] using
          congrArg (fun l => (v - u - 1) :: l) hsource
      · simpa [consecutiveGaps, slideTarget] using
          congrArg (fun l => (v - u - 1) :: l) htarget

theorem consecutiveGaps_endpoints (xs : List ℤ) (a e : ℤ)
    (hxs : xs ≠ []) :
    consecutiveGaps (a :: (xs ++ [e])) =
      (xs.head hxs - a - 1) ::
        (consecutiveGaps xs ++ [e - xs.getLast hxs - 1]) := by
  induction xs using List.twoStepInduction with
  | nil => contradiction
  | singleton x => rfl
  | cons_cons x y rest _ ih =>
      have h := ih y (by simp)
      simpa [consecutiveGaps] using
        congrArg (fun l => (x - a - 1) :: l) h

theorem consecutiveGaps_backslide (a : ℤ) (xs : List ℤ) (n : ℕ)
    (hxs : xs ≠ []) :
    ∃ x middle y,
      consecutiveGaps (a :: (xs ++ [a + n])) =
        carrierBackslideSource x middle y ∧
      consecutiveGaps ((a - 1) :: (xs ++ [a - 1 + n])) =
        carrierBackslideTarget x middle y := by
  refine ⟨xs.head hxs - a - 1, consecutiveGaps xs,
    a + n - xs.getLast hxs - 1, ?_, ?_⟩
  · exact consecutiveGaps_endpoints xs a (a + n) hxs
  · rw [consecutiveGaps_endpoints xs (a - 1) (a - 1 + n) hxs]
    unfold carrierBackslideTarget
    congr 1
    · ring
    · congr 1
      congr 1
      ring

theorem consecutiveGaps_fusion (a : ℤ) (xs : List ℤ) (n : ℕ) :
    ∃ x tail,
      consecutiveGaps (a :: (a + 1) :: (xs ++ [a + n])) = fusionSource x tail ∧
      consecutiveGaps (a :: (xs ++ [a + n])) = fusionTarget x tail := by
  cases xs with
  | nil =>
      refine ⟨a + n - (a + 1) - 1, [], ?_, ?_⟩
      · simp [consecutiveGaps, fusionSource]
      · simp only [List.nil_append, consecutiveGaps, fusionTarget]
        congr 1
        ring
  | cons x rest =>
      refine ⟨x - (a + 1) - 1, consecutiveGaps (x :: (rest ++ [a + n])), ?_, ?_⟩
      · simp [consecutiveGaps, fusionSource]
      · simp only [List.cons_append, consecutiveGaps, fusionTarget]
        congr 1
        ring

theorem occupied_placementOfMap_iff {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (q : ZMod n) :
    placementOfMap f q ≠ none ↔ ∃ a, f a = q := by
  rw [ne_eq, placementOfMap_none_iff]
  change sourceFiber f q ≠ ∅ ↔ _
  rw [← Finset.nonempty_iff_ne_empty]
  simp only [Finset.Nonempty, mem_sourceFiber]

theorem marked_placementOfMap_iff {n : ℕ} [NeZero n]
    (f : ZMod n → ZMod n) (a q : ZMod n) :
    a ∈ (placementOfMap f q).getD ∅ ↔ f a = q := by
  by_cases h : (sourceFiber f q).Nonempty
  · simp [placementOfMap, h]
  · have hne : f a ≠ q := by
      intro heq
      exact h ⟨a, (mem_sourceFiber f a q).mpr heq⟩
    simp [placementOfMap, h, hne]

theorem marked_site_unique {n : ℕ} [NeZero n]
    {s : Execution n (ZMod n)} (horder : SourceOrdered s.placed)
    {a q r : ZMod n} (hq : a ∈ (s.placed q).getD ∅)
    (hr : a ∈ (s.placed r).getD ∅) : q = r := by
  obtain ⟨lift, hplaced⟩ := horder
  rw [hplaced, marked_placementOfMap_iff] at hq hr
  exact hq.symm.trans hr

theorem PhysicalPacketRing.sites_eq_of_same_head_support {n : ℕ} [NeZero n]
    (left right : PhysicalPacketRing n) (hhead : left.head = right.head)
    (hsupport : ∀ q : ZMod n,
      (∃ x ∈ left.sites, (x : ZMod n) = q) ↔
        ∃ x ∈ right.sites, (x : ZMod n) = q) :
    left.sites = right.sites := by
  apply List.Pairwise.eq_of_mem_iff left.increasing right.increasing
  intro x
  constructor
  · intro hx
    obtain ⟨y, hy, hcast⟩ := (hsupport (x : ZMod n)).mp ⟨x, hx, rfl⟩
    obtain ⟨hxl, hxu⟩ := left.bounds hx (NeZero.pos n)
    obtain ⟨hyl, hyu⟩ := right.bounds hy (NeZero.pos n)
    rw [← hhead] at hyl hyu
    have hxy := intCast_injective_on_turn hxl hxu hyl hyu hcast.symm
    exact hxy ▸ hy
  · intro hx
    obtain ⟨y, hy, hcast⟩ := (hsupport (x : ZMod n)).mpr ⟨x, hx, rfl⟩
    obtain ⟨hxl, hxu⟩ := right.bounds hx (NeZero.pos n)
    obtain ⟨hyl, hyu⟩ := left.bounds hy (NeZero.pos n)
    rw [hhead] at hyl hyu
    have hxy := intCast_injective_on_turn hxl hxu hyl hyu hcast.symm
    exact hxy ▸ hy

theorem PhysicalPacketRing.gaps_eq_of_same_support {n : ℕ} [NeZero n]
    (left right : PhysicalPacketRing n)
    (hhead : (left.head : ZMod n) = (right.head : ZMod n))
    (hsupport : ∀ q : ZMod n,
      (∃ x ∈ left.sites, (x : ZMod n) = q) ↔
        ∃ x ∈ right.sites, (x : ZMod n) = q) :
    left.gaps = right.gaps := by
  let k := left.head - right.head
  let shifted := right.translate k
  have hk : (k : ZMod n) = 0 := by simp [k, hhead]
  have hshiftHead : left.head = shifted.head := by
    change left.head = right.head + (left.head - right.head)
    omega
  have hshiftSupport : ∀ q : ZMod n,
      (∃ x ∈ right.sites, (x : ZMod n) = q) ↔
        ∃ x ∈ shifted.sites, (x : ZMod n) = q := by
    intro q
    have hs : shifted.sites = right.sites.map (· + k) := by
      rfl
    rw [hs]
    constructor
    · rintro ⟨x, hx, hxq⟩
      refine ⟨x + k, List.mem_map.mpr ⟨x, hx, rfl⟩, ?_⟩
      simpa [hk] using hxq
    · rintro ⟨x, hx, hxq⟩
      obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hx
      exact ⟨y, hy, by simpa [hk] using hxq⟩
  have hsites := left.sites_eq_of_same_head_support shifted hshiftHead
    (fun q => (hsupport q).trans (hshiftSupport q))
  have htail : left.tail = shifted.tail := by
    change left.head :: left.tail = shifted.head :: shifted.tail at hsites
    exact (List.cons.inj hsites).2
  have hgap : left.gaps = shifted.gaps := by
    simp only [PhysicalPacketRing.gaps, hshiftHead, htail]
  exact hgap.trans (right.translate_gaps k)

/-- The integer ring is only a witness: a fixed actual state and marked
carrier determine the same gap vector for every such witness. -/
theorem gapRep_unique {n : ℕ} [NeZero n]
    {s : Execution n (ZMod n)} {a : ZMod n} {g h : List ℤ}
    (hg : GapRep s a g) (hh : GapRep s a h) : g = h := by
  rcases hg with ⟨horder, left, hleft, hmarkedLeft, rfl⟩
  rcases hh with ⟨_, right, hright, hmarkedRight, rfl⟩
  apply left.gaps_eq_of_same_support right
    (marked_site_unique horder hmarkedLeft hmarkedRight)
  intro q
  exact (hleft q).symm.trans (hright q)

theorem occupied_defect_iff {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)}
    (hn : 2 ≤ n) (horder : SourceOrdered s.placed) (q : ZMod n) :
    (step F s .d).placed q ≠ none ↔
      ∃ r, s.placed r ≠ none ∧ collapsePosition r = q := by
  obtain ⟨lift, hplaced⟩ := horder
  rw [step_placementOfMap F s lift.position .d hn hplaced,
    occupied_placementOfMap_iff]
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨lift.position a, ?_, ha⟩
    rw [hplaced, occupied_placementOfMap_iff]
    exact ⟨a, rfl⟩
  · rintro ⟨r, hr, hq⟩
    rw [hplaced, occupied_placementOfMap_iff] at hr
    obtain ⟨a, rfl⟩ := hr
    exact ⟨a, hq⟩

theorem marked_defect {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)}
    (hn : 2 ≤ n) (horder : SourceOrdered s.placed) {a q : ZMod n}
    (hmarked : a ∈ (s.placed q).getD ∅) :
    a ∈ ((step F s .d).placed (collapsePosition q)).getD ∅ := by
  obtain ⟨lift, hplaced⟩ := horder
  rw [hplaced, marked_placementOfMap_iff] at hmarked
  rw [step_placementOfMap F s lift.position .d hn hplaced,
    marked_placementOfMap_iff]
  change collapsePosition (lift.position a) = collapsePosition q
  rw [hmarked]

/-- The support proof is transported through the actual defect map. No
assumption about the next gap rewrite is used here. -/
theorem gapRep_defect_of_site_image {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    (hn : 2 ≤ n) (horder : SourceOrdered s.placed)
    (ring next : PhysicalPacketRing n)
    (hoccupied : ∀ q, s.placed q ≠ none ↔ ∃ x ∈ ring.sites, (x : ZMod n) = q)
    (hmarked : a ∈ (s.placed (ring.head : ZMod n)).getD ∅)
    (himage : ∀ q, (∃ x ∈ next.sites, (x : ZMod n) = q) ↔
      ∃ x ∈ ring.sites, collapsePosition (x : ZMod n) = q)
    (hhead : (next.head : ZMod n) = collapsePosition (ring.head : ZMod n)) :
    GapRep (step F s .d) a next.gaps := by
  refine ⟨step_ordered F s .d hn horder, next, ?_, ?_, rfl⟩
  · intro q
    rw [occupied_defect_iff F hn horder, himage q]
    constructor
    · rintro ⟨r, hr, hq⟩
      obtain ⟨x, hx, rfl⟩ := (hoccupied r).mp hr
      exact ⟨x, hx, hq⟩
    · rintro ⟨x, hx, hq⟩
      exact ⟨(x : ZMod n), (hoccupied _).mpr ⟨x, hx, rfl⟩, hq⟩
  · rw [hhead]
    exact marked_defect F hn horder hmarked

def lowerOneSite (z x : ℤ) : ℤ := if x = z then x - 1 else x

def PhysicalPacketRing.lowerOutside (ring : PhysicalPacketRing n) (z : ℤ)
    (hz : z ∈ ring.tail) (hprevious : ∀ x ∈ ring.sites, x ≠ z - 1) :
    PhysicalPacketRing n where
  head := ring.head
  tail := ring.tail.map (lowerOneSite z)
  increasing := by
    have hhead : ring.head ≠ z := by
      have := (List.pairwise_cons.mp ring.increasing).1 z hz
      omega
    have hmap : (ring.sites.map (lowerOneSite z)).Pairwise (· < ·) := by
      apply List.pairwise_map.mpr
      apply List.Pairwise.imp_of_mem (p := ring.increasing)
      intro x y hx hy hxy
      have hprev := hprevious x hx
      unfold lowerOneSite
      split_ifs <;> omega
    simpa [PhysicalPacketRing.sites, lowerOneSite, hhead] using hmap
  below_end := by
    intro x hx
    obtain ⟨y, hy, rfl⟩ := List.mem_map.mp hx
    have hlt := ring.below_end y hy
    unfold lowerOneSite
    split_ifs <;> omega

theorem PhysicalPacketRing.lowerOutside_sites (ring : PhysicalPacketRing n)
    (z : ℤ) (hz : z ∈ ring.tail) (hprevious : ∀ x ∈ ring.sites, x ≠ z - 1) :
    (ring.lowerOutside z hz hprevious).sites = ring.sites.map (lowerOneSite z) := by
  have hhead : ring.head ≠ z := by
    have := (List.pairwise_cons.mp ring.increasing).1 z hz
    omega
  simp [PhysicalPacketRing.sites, PhysicalPacketRing.lowerOutside, lowerOneSite, hhead]

theorem lowerOneSite_cast {n : ℕ} [NeZero n] (ring : PhysicalPacketRing n)
    (z : ℤ) (hz : z ∈ ring.sites) (hz1 : (z : ZMod n) = 1)
    (x : ℤ) (hx : x ∈ ring.sites) :
    (lowerOneSite z x : ZMod n) = collapsePosition (x : ZMod n) := by
  by_cases hxz : x = z
  · subst x
    simp [lowerOneSite, collapsePosition, hz1]
  · have hx1 : (x : ZMod n) ≠ 1 := by
      intro h
      exact hxz (ring.cast_injective hx hz (h.trans hz1.symm))
    simp [lowerOneSite, hxz, collapsePosition, hx1]

theorem PhysicalPacketRing.lowerOutside_gapTransition (ring : PhysicalPacketRing n)
    (z : ℤ) (hz : z ∈ ring.tail) (hprevious : ∀ x ∈ ring.sites, x ≠ z - 1) :
    ∃ t : HoleTransition ring.gaps (ring.lowerOutside z hz hprevious).gaps,
      t.ledger.slides = 1 ∧ t.ledger.backslides = 0 ∧ t.fusionStep = 0 := by
  obtain ⟨pre, post, htail⟩ := List.mem_iff_append.mp hz
  have horder : (pre ++ z :: post).Pairwise (· < ·) := by
    rw [← htail]
    exact (List.pairwise_cons.mp ring.increasing).2
  have hpre : ∀ x ∈ pre, lowerOneSite z x = x := by
    intro x hx
    have hlt := (List.pairwise_append.mp horder).2.2 x hx z (by simp)
    simp [lowerOneSite, ne_of_lt hlt]
  have hpost : ∀ x ∈ post, lowerOneSite z x = x := by
    intro x hx
    have hlt := (List.pairwise_cons.mp (List.pairwise_append.mp horder).2.1).1 x hx
    simp [lowerOneSite, ne_of_gt hlt]
  have hmapPre : pre.map (lowerOneSite z) = pre := by
    simpa using List.map_congr_left hpre
  have hmapPost : post.map (lowerOneSite z) = post := by
    simpa using List.map_congr_left hpost
  obtain ⟨before, x, y, after, hsource, htarget⟩ :=
    consecutiveGaps_slide (ring.head :: pre) (post ++ [ring.head + n]) z
      (by simp) (by simp)
  have hs : ring.gaps = slideSource before x y after := by
    simpa [PhysicalPacketRing.gaps, htail, List.append_assoc] using hsource
  have ht : (ring.lowerOutside z hz hprevious).gaps =
      slideTarget before x y after := by
    simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.lowerOutside, htail,
      List.map_append, hmapPre, hmapPost, lowerOneSite, List.append_assoc] using htarget
  rw [hs, ht]
  exact ⟨.slide before x y after, rfl, rfl, rfl⟩

/-- A real external packet at port 1 slides into the empty port 0. -/
theorem gapRep_externalSlide {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    (hn : 2 ≤ n) (horder : SourceOrdered s.placed) (ring : PhysicalPacketRing n)
    (hoccupied : ∀ q, s.placed q ≠ none ↔ ∃ x ∈ ring.sites, (x : ZMod n) = q)
    (hmarked : a ∈ (s.placed (ring.head : ZMod n)).getD ∅)
    (z : ℤ) (hz : z ∈ ring.tail) (hz1 : (z : ZMod n) = 1)
    (h0 : s.placed 0 = none) :
    ∃ g, ∃ t : HoleTransition ring.gaps g,
      GapRep (step F s .d) a g ∧ t.ledger.slides = 1 ∧
        t.ledger.backslides = 0 ∧ t.fusionStep = 0 := by
  have hprevious : ∀ x ∈ ring.sites, x ≠ z - 1 := by
    intro x hx heq
    have hx0 : (x : ZMod n) = 0 := by rw [heq]; simp [hz1]
    have := (hoccupied 0).mpr ⟨x, hx, hx0⟩
    exact this h0
  let next := ring.lowerOutside z hz hprevious
  have hzsite : z ∈ ring.sites := List.mem_cons_of_mem _ hz
  have hhead1 : (ring.head : ZMod n) ≠ 1 := by
    intro heq
    have hxz := ring.cast_injective (by simp [PhysicalPacketRing.sites]) hzsite
      (heq.trans hz1.symm)
    have hlt := (List.pairwise_cons.mp ring.increasing).1 z hz
    omega
  have hrep : GapRep (step F s .d) a next.gaps := by
    apply gapRep_defect_of_site_image F hn horder ring next hoccupied hmarked
    · intro q
      rw [show next.sites = ring.sites.map (lowerOneSite z) from
        ring.lowerOutside_sites z hz hprevious]
      simp only [List.mem_map, exists_exists_and_eq_and]
      constructor
      · rintro ⟨x, hx, hq⟩
        exact ⟨x, hx, (lowerOneSite_cast ring z hzsite hz1 x hx).symm.trans hq⟩
      · rintro ⟨x, hx, hq⟩
        exact ⟨x, hx, (lowerOneSite_cast ring z hzsite hz1 x hx).trans hq⟩
    · simp [next, PhysicalPacketRing.lowerOutside, collapsePosition, hhead1]
  obtain ⟨t, hslide, hback, hfusion⟩ := ring.lowerOutside_gapTransition z hz hprevious
  exact ⟨next.gaps, t, hrep, hslide, hback, hfusion⟩

/-! The two remaining local support transports.  They are stated separately
from the case split below so that the integer representative bookkeeping is
not hidden in the `d` classification theorem. -/

theorem PhysicalPacketRing.backslide_site_image {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n)
    (hend : ∀ x ∈ ring.sites, x ≠ ring.head + n - 1)
    (hhead1 : (ring.head : ZMod n) = 1) :
    ∀ q, (∃ x ∈ (ring.backslide hend).sites, (x : ZMod n) = q) ↔
      ∃ x ∈ ring.sites, collapsePosition (x : ZMod n) = q := by
  intro q
  constructor
  · rintro ⟨x, hx, hxq⟩
    by_cases hhead : x = ring.head - 1
    · subst x
      refine ⟨ring.head, by simp [PhysicalPacketRing.sites], ?_⟩
      have hprev0 : ((ring.head - 1 : ℤ) : ZMod n) = 0 := by
        push_cast
        rw [hhead1]
        ring
      calc
        collapsePosition (ring.head : ZMod n) = 0 := by
          simp [collapsePosition, hhead1]
        _ = ((ring.head - 1 : ℤ) : ZMod n) := hprev0.symm
        _ = q := hxq
    · have hxtail : x ∈ ring.tail := by
        have hx' : x = ring.head - 1 ∨ x ∈ ring.tail := by
          simpa [PhysicalPacketRing.backslide_sites ring hend] using hx
        exact hx'.resolve_left hhead
      have hxone : (x : ZMod n) ≠ 1 := by
        intro hxone
        have hcast := ring.cast_injective
          (List.mem_cons_of_mem _ hxtail)
          (by simp [PhysicalPacketRing.sites])
          (hxone.trans hhead1.symm)
        have hlt := (List.pairwise_cons.mp ring.increasing).1 x hxtail
        omega
      refine ⟨x, List.mem_cons_of_mem _ hxtail, ?_⟩
      simpa [collapsePosition, hxone] using hxq
  · rintro ⟨x, hx, hxq⟩
    by_cases hxeq : x = ring.head
    · subst x
      refine ⟨ring.head - 1, by simp [PhysicalPacketRing.backslide_sites], ?_⟩
      have hprev0 : ((ring.head - 1 : ℤ) : ZMod n) = 0 := by
        push_cast
        rw [hhead1]
        ring
      calc
        ((ring.head - 1 : ℤ) : ZMod n) = 0 := hprev0
        _ = q := by simpa [collapsePosition, hhead1] using hxq
    · have hxtail : x ∈ ring.tail := by
        have hx' : x = ring.head ∨ x ∈ ring.tail := by
          simpa [PhysicalPacketRing.sites] using hx
        exact hx'.resolve_left hxeq
      have hxone : (x : ZMod n) ≠ 1 := by
        intro hxone
        have hcast := ring.cast_injective
          (List.mem_cons_of_mem _ hxtail)
          (by simp [PhysicalPacketRing.sites])
          (hxone.trans hhead1.symm)
        have hlt := (List.pairwise_cons.mp ring.increasing).1 x hxtail
        omega
      refine ⟨x, by simpa [PhysicalPacketRing.backslide_sites ring hend] using
        (List.mem_cons_of_mem (ring.head - 1) hxtail), ?_⟩
      simpa [collapsePosition, hxone] using hxq

theorem PhysicalPacketRing.fusion_site_image {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n) (rest : List ℤ)
    (htail : ring.tail = (ring.head + 1) :: rest)
    (hhead0 : (ring.head : ZMod n) = 0) :
    ∀ q, (∃ x ∈ (ring.fuseNext rest htail).sites, (x : ZMod n) = q) ↔
      ∃ x ∈ ring.sites, collapsePosition (x : ZMod n) = q := by
  intro q
  have hinc : (ring.head :: (ring.head + 1) :: rest).Pairwise (· < ·) := by
    simpa [htail] using ring.increasing
  have hone : ((ring.head + 1 : ℤ) : ZMod n) = 1 := by
    push_cast
    rw [hhead0]
    ring
  have hrest1 : ∀ x ∈ rest, (x : ZMod n) ≠ 1 := by
    intro x hx hOne
    have hcast := ring.cast_injective
      (by simp [PhysicalPacketRing.sites, htail, hx])
      (by simp [PhysicalPacketRing.sites, htail])
      (hOne.trans hone.symm)
    have hlt := (List.pairwise_cons.mp (List.pairwise_cons.mp hinc).2).1 x hx
    omega
  constructor
  · rintro ⟨x, hx, hxq⟩
    by_cases hxeq : x = ring.head
    · subst x
      refine ⟨ring.head, by simp [PhysicalPacketRing.sites], ?_⟩
      simpa [collapsePosition, hhead0] using hxq
    · have hxrest : x ∈ rest := by
        have hx' : x = ring.head ∨ x ∈ rest := by
          change x ∈ ring.head :: rest at hx
          exact List.mem_cons.mp hx
        exact hx'.resolve_left hxeq
      refine ⟨x, by simp [PhysicalPacketRing.sites, htail, hxrest], ?_⟩
      simpa [collapsePosition, hrest1 x hxrest] using hxq
  · rintro ⟨x, hx, hxq⟩
    by_cases hxeq : x = ring.head
    · subst x
      refine ⟨ring.head, by simp [PhysicalPacketRing.fuseNext_sites ring rest htail], ?_⟩
      simpa [collapsePosition, hhead0] using hxq
    · have hxparts : x = ring.head ∨ x = ring.head + 1 ∨ x ∈ rest := by
        simpa [PhysicalPacketRing.sites, htail] using hx
      rcases hxparts with hxhead | hxparts
      · exact (hxeq hxhead).elim
      rcases hxparts with hxnext | hxrest
      · subst x
        refine ⟨ring.head, by simp [PhysicalPacketRing.fuseNext_sites ring rest htail], ?_⟩
        simpa [collapsePosition, hhead0] using hxq
      · refine ⟨x, by
          change x ∈ ring.head :: rest
          exact List.mem_cons_of_mem _ hxrest, ?_⟩
        simpa [collapsePosition, hrest1 x hxrest] using hxq

theorem PhysicalPacketRing.backslide_gapTransition {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n)
    (hend : ∀ x ∈ ring.sites, x ≠ ring.head + n - 1) :
    ∃ t : HoleTransition ring.gaps (ring.backslide hend).gaps,
      t.ledger.slides = 0 ∧ t.ledger.backslides = 1 ∧
        t.fusionStep = 0 := by
  cases htail : ring.tail with
  | nil =>
      have hsource : ring.gaps = [((n : ℤ) - 1)] := by
        simp [PhysicalPacketRing.gaps, PhysicalPacketRing.sites, htail,
          consecutiveGaps]
      have htarget : (ring.backslide hend).gaps = [((n : ℤ) - 1)] := by
        simp [PhysicalPacketRing.gaps, PhysicalPacketRing.backslide,
          PhysicalPacketRing.sites, htail, consecutiveGaps]
      rw [hsource, htarget]
      exact ⟨.rankOneBackslide _, rfl, rfl, rfl⟩
  | cons z rest =>
      have htailne : ring.tail ≠ [] := by simp [htail]
      obtain ⟨x, middle, y, hsource, htarget⟩ :=
        consecutiveGaps_backslide ring.head ring.tail n htailne
      have hsource' : ring.gaps = carrierBackslideSource x middle y := by
        simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.sites] using hsource
      have htarget' : (ring.backslide hend).gaps =
          carrierBackslideTarget x middle y := by
        simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.backslide,
          PhysicalPacketRing.sites] using htarget
      rw [hsource', htarget']
      exact ⟨.backslide x middle y, rfl, rfl, rfl⟩

theorem PhysicalPacketRing.fusion_gapTransition {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n) (rest : List ℤ)
    (htail : ring.tail = (ring.head + 1) :: rest) :
    ∃ t : HoleTransition ring.gaps (ring.fuseNext rest htail).gaps,
      t.ledger.slides = 0 ∧ t.ledger.backslides = 0 ∧
        t.fusionStep = 1 := by
  obtain ⟨x, tail, hsource, htarget⟩ :=
    consecutiveGaps_fusion ring.head rest n
  have hsource' : ring.gaps = fusionSource x tail := by
    simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.sites, htail] using hsource
  have htarget' : (ring.fuseNext rest htail).gaps = fusionTarget x tail := by
    simpa [PhysicalPacketRing.gaps, PhysicalPacketRing.fuseNext,
      PhysicalPacketRing.sites] using htarget
  rw [hsource', htarget']
  exact ⟨.fusion x tail, rfl, rfl, rfl⟩

/-! `GapRep` deliberately describes arbitrary source-ordered states.  A raw
all-R interval supplies one additional local hypothesis: if both defect ports
are occupied, the marked carrier is the left parent and the next integer site
is the right parent.  With that hypothesis the five physical cases are
complete, including the rank-one carrier return. -/

theorem PhysicalPacketRing.next_of_port_one {n : ℕ} [NeZero n]
    (ring : PhysicalPacketRing n) (hn : 2 ≤ n)
    (hhead0 : (ring.head : ZMod n) = 0)
    (hoccupied1 : ∃ x ∈ ring.sites, (x : ZMod n) = 1) :
    ∃ rest, ring.tail = (ring.head + 1) :: rest := by
  obtain ⟨x, hx, hx1⟩ := hoccupied1
  obtain ⟨hxl, hxu⟩ := ring.bounds hx (by omega)
  have hxnext : x = ring.head + 1 := by
    apply intCast_injective_on_turn hxl hxu (by omega) (by omega)
    simpa [hhead0] using hx1
  have hxTail : ring.head + 1 ∈ ring.tail := by
    have hx' : x = ring.head ∨ x ∈ ring.tail := by
      simpa [PhysicalPacketRing.sites] using hx
    rcases hx' with h | h
    · omega
    · simpa [hxnext] using h
  cases htail : ring.tail with
  | nil => simp [htail] at hxTail
  | cons z rest =>
      have hz : ring.head < z := (List.pairwise_cons.mp ring.increasing).1 z
        (by simp [htail])
      have hle : z ≤ ring.head + 1 := by
        rw [htail] at hxTail
        rcases List.mem_cons.mp hxTail with h | h
        · omega
        · have hinc : (z :: rest).Pairwise (· < ·) := by
            simpa [htail] using (List.pairwise_cons.mp ring.increasing).2
          exact le_of_lt ((List.pairwise_cons.mp hinc).1 _ h)
      have heq : z = ring.head + 1 := by omega
      exact ⟨rest, by simpa [heq] using htail⟩

/-- The physical restriction to right-carrier fusions.  It imposes no
condition on `d` when either port is empty. -/
def RightCarrierDefect {n : ℕ} [NeZero n]
    (s : Execution n (ZMod n)) (a : ZMod n) : Prop :=
  s.placed 0 ≠ none → s.placed 1 ≠ none → a ∈ (s.placed 0).getD ∅

theorem HoleTransition.unit_accounting {g h : List ℤ}
    (transition : HoleTransition g h) :
    transition.ledger.slides + transition.ledger.backslides +
      transition.fusionStep + transition.idleStep = 1 := by
  cases transition <;> simp [HoleTransition.ledger, HoleTransition.fusionStep,
    HoleTransition.idleStep]

/-- These charges are read from the actual predecessor, including the
zero-weight rank-one return.  Thus a stationary rewrite cannot be silently
substituted for a physical carrier return. -/
structure DefectMatches {n : ℕ} [NeZero n]
    (s : Execution n (ZMod n)) (a : ZMod n) {g h : List ℤ}
    (transition : HoleTransition g h) : Prop where
  backslides : transition.ledger.backslides =
    if a ∈ (s.placed 1).getD ∅ then 1 else 0
  fusion : transition.fusionStep =
    if s.placed 0 ≠ none ∧ s.placed 1 ≠ none then 1 else 0
  idle : transition.idleStep = if s.placed 1 = none then 1 else 0
  slides : transition.ledger.slides =
    if s.placed 0 = none ∧ s.placed 1 ≠ none ∧
      a ∉ (s.placed 1).getD ∅ then 1 else 0

theorem gapRep_defect_complete_accounted {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g)
    (hready : RightCarrierDefect s a) :
    ∃ h, ∃ transition : HoleTransition g h,
      GapRep (step F s .d) a h ∧ DefectMatches s a transition := by
  rcases hrep with ⟨horder, ring, hoccupied, hmarked, rfl⟩
  by_cases h1 : s.placed 1 = none
  · refine ⟨ring.gaps, .stationary ring.gaps,
      gapRep_stationary_defect F hn
        ⟨horder, ring, hoccupied, hmarked, rfl⟩ h1, ?_⟩
    constructor <;> simp [HoleTransition.ledger, HoleTransition.fusionStep,
      HoleTransition.idleStep, h1]
  by_cases h0 : s.placed 0 = none
  · by_cases hhead1 : (ring.head : ZMod n) = 1
    · have hend : ∀ x ∈ ring.sites, x ≠ ring.head + n - 1 := by
        intro x hx hxeq
        have hx0 : (x : ZMod n) = 0 := by
          rw [hxeq]
          simp [hhead1]
        exact (hoccupied 0).mpr ⟨x, hx, hx0⟩ |>.elim h0
      let next := ring.backslide hend
      have hrep' : GapRep (step F s .d) a next.gaps := by
        apply gapRep_defect_of_site_image F hn horder ring next
          hoccupied hmarked
        · exact ring.backslide_site_image hend hhead1
        · simp [next, PhysicalPacketRing.backslide, collapsePosition, hhead1]
      obtain ⟨t, hslide, hback, hfusion⟩ :=
        ring.backslide_gapTransition hend
      have hmarker1 : a ∈ (s.placed 1).getD ∅ := by
        simpa [hhead1] using hmarked
      have hidle : t.idleStep = 0 := by
        have := t.unit_accounting
        omega
      refine ⟨next.gaps, t, hrep', ?_⟩
      constructor
      · simpa [hmarker1] using hback
      · simpa [h0] using hfusion
      · simpa [h1] using hidle
      · simpa [hmarker1] using hslide
    · obtain ⟨z, hz, hz1⟩ := (hoccupied 1).mp h1
      have hzTail : z ∈ ring.tail := by
        have hz' : z = ring.head ∨ z ∈ ring.tail := by
          simpa [PhysicalPacketRing.sites] using hz
        exact hz'.resolve_left (by
          intro h
          exact hhead1 (by simpa [h] using hz1))
      obtain ⟨h, t, hrep', hslide, hback, hfusion⟩ :=
        gapRep_externalSlide F hn horder ring hoccupied hmarked z hzTail hz1 h0
      have hmarker1 : a ∉ (s.placed 1).getD ∅ := by
        intro ha1
        exact hhead1 (marked_site_unique horder hmarked ha1)
      have hidle : t.idleStep = 0 := by
        have := t.unit_accounting
        omega
      refine ⟨h, t, hrep', ?_⟩
      constructor
      · simpa [hmarker1] using hback
      · simpa [h0] using hfusion
      · simpa [h1] using hidle
      · simpa [h0, h1, hmarker1] using hslide
  · have hhead0 : (ring.head : ZMod n) = 0 :=
      marked_site_unique horder hmarked (hready h0 h1)
    obtain ⟨rest, htail⟩ := ring.next_of_port_one hn hhead0 ((hoccupied 1).mp h1)
    let next := ring.fuseNext rest htail
    have hrep' : GapRep (step F s .d) a next.gaps := by
      apply gapRep_defect_of_site_image F hn horder ring next
        hoccupied hmarked
      · exact ring.fusion_site_image rest htail hhead0
      · simp [next, PhysicalPacketRing.fuseNext, collapsePosition, hhead0]
    obtain ⟨t, hslide, hback, hfusion⟩ :=
      ring.fusion_gapTransition rest htail
    have hmarker1 : a ∉ (s.placed 1).getD ∅ := by
      intro ha1
      have h01 : (0 : ZMod n) = 1 :=
        marked_site_unique horder (hready h0 h1) ha1
      have := ZMod.one_eq_zero_iff.mp h01.symm
      omega
    have hidle : t.idleStep = 0 := by
      have := t.unit_accounting
      omega
    refine ⟨next.gaps, t, hrep', ?_⟩
    constructor
    · simpa [hmarker1] using hback
    · simpa [h0, h1] using hfusion
    · simpa [h1] using hidle
    · simpa [h0] using hslide

theorem gapRep_defect_complete {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g)
    (hready : RightCarrierDefect s a) :
    ∃ h, GapRep (step F s .d) a h ∧ Nonempty (HoleTransition g h) := by
  obtain ⟨h, transition, hnext, _⟩ :=
    gapRep_defect_complete_accounted F hn hrep hready
  exact ⟨h, hnext, ⟨transition⟩⟩

/-! A state-indexed physical trace.  Its `p` and `d` constructors expose the
actual predecessor and successor states in their indices; projection to the
older word-only `ExecutionTrace` is therefore a theorem, not an assumption.
-/
inductive PhysicalTrace {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n) :
    Execution n (ZMod n) → List Letter → Execution n (ZMod n) →
      List ℤ → List ℤ → Type
  | nil {s : Execution n (ZMod n)} {g : List ℤ}
      (hrep : GapRep s a g) :
      PhysicalTrace F a s [] s g g
  | p {s : Execution n (ZMod n)} {word : List Letter}
      {t : Execution n (ZMod n)} {g h : List ℤ}
      (hrep : GapRep s a g)
      (rest : PhysicalTrace F a (step F s .p) word t g h) :
      PhysicalTrace F a s (.p :: word) t g h
  | d {s : Execution n (ZMod n)} {word : List Letter}
      {t : Execution n (ZMod n)} {g h k : List ℤ}
      (hrep : GapRep s a g)
      (transition : HoleTransition g h)
      (hnext : GapRep (step F s .d) a h)
      (hmatch : DefectMatches s a transition)
      (rest : PhysicalTrace F a (step F s .d) word t h k) :
      PhysicalTrace F a s (.d :: word) t g k

def PhysicalTrace.toExecutionTrace {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} :
    PhysicalTrace F a s word t g h → ExecutionTrace word g h
  | .nil _ => .nil g
  | .p _ rest => .p rest.toExecutionTrace
  | .d _ transition _ _ rest => .d transition rest.toExecutionTrace

theorem PhysicalTrace.terminal_eq_run {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a s word t g h) :
    t = run F s word := by
  induction trace with
  | nil hrep => simp [run]
  | p hrep rest ih => simpa [run] using ih
  | d hrep transition hnext hmatch rest ih => simpa [run] using ih

theorem PhysicalTrace.toExecutionTrace_word {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a s word t g h) :
    (trace.toExecutionTrace).dLetters = word.count .d := by
  exact trace.toExecutionTrace.dLetters_eq_count

def PhysicalTrace.single_p {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g) :
    PhysicalTrace F a s [.p] (step F s .p) g g := by
  exact .p hrep (.nil (gapRep_rotation F hn hrep))

theorem PhysicalTrace.single_d_of_complete {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {s : Execution n (ZMod n)} {a : ZMod n}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g)
    (hready : RightCarrierDefect s a) :
    ∃ h, Nonempty (PhysicalTrace F a s [.d] (step F s .d) g h) := by
  obtain ⟨h, transition, hnext, hmatch⟩ :=
    gapRep_defect_complete_accounted F hn hrep hready
  exact ⟨h, ⟨.d hrep transition hnext hmatch (.nil hnext)⟩⟩

/-- All effective fusions in this word have the carrier in their left
parent.  The predicate is evaluated along the real execution, not along
independently chosen states. -/
def RightCarrierRun {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n) (s : Execution n (ZMod n)) :
    List Letter → Prop
  | [] => True
  | .p :: rest => RightCarrierRun F a (step F s .p) rest
  | .d :: rest => RightCarrierDefect s a ∧
      RightCarrierRun F a (step F s .d) rest

theorem physicalTrace_exists {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) {a : ZMod n} {s : Execution n (ZMod n)}
    {g : List ℤ} (hn : 2 ≤ n) (hrep : GapRep s a g)
    (word : List Letter) (hright : RightCarrierRun F a s word) :
    ∃ h, Nonempty (PhysicalTrace F a s word (run F s word) g h) := by
  induction word generalizing s g with
  | nil => exact ⟨g, ⟨.nil hrep⟩⟩
  | cons letter rest ih =>
      cases letter with
      | p =>
          obtain ⟨h, ⟨trace⟩⟩ :=
            ih (gapRep_rotation F hn hrep) hright
          exact ⟨h, ⟨.p hrep trace⟩⟩
      | d =>
          obtain ⟨hnext, transition, hnextRep, hmatch⟩ :=
            gapRep_defect_complete_accounted F hn hrep hright.1
          obtain ⟨h, ⟨trace⟩⟩ := ih hnextRep hright.2
          exact ⟨h, ⟨.d hrep transition hnextRep hmatch trace⟩⟩

theorem PhysicalTrace.start_rep {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a s word t g h) : GapRep s a g := by
  cases trace with
  | nil hrep => exact hrep
  | p hrep rest => exact hrep
  | d hrep transition hnext hmatch rest => exact hrep

theorem PhysicalTrace.end_rep {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a s word t g h) : GapRep t a h := by
  induction trace with
  | nil hrep => exact hrep
  | p hrep rest ih => exact ih
  | d hrep transition hnext hmatch rest ih => exact ih

/-- The unweighted return ledger is exactly the physical carrier counter;
in particular a rank-one backslide is charged despite zero potential weight. -/
theorem PhysicalTrace.backslides_eq_returns {n : ℕ} [NeZero n]
    {F : Finset (ZMod n)} {a : ZMod n}
    {s t : Execution n (ZMod n)} {word : List Letter}
    {g h : List ℤ} (trace : PhysicalTrace F a s word t g h) :
    trace.toExecutionTrace.holeTrace.ledger.backslides =
      executionCarrierReturns F s a word := by
  induction trace with
  | nil hrep => rfl
  | p hrep rest ih => exact ih
  | d hrep transition hnext hmatch rest ih =>
      change transition.ledger.backslides +
        rest.toExecutionTrace.holeTrace.ledger.backslides = _
      rw [hmatch.backslides, ih]
      rfl

end FusionLogAllR
