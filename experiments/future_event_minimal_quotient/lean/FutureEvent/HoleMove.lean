import FutureEvent.GapAdmission

namespace FutureEvent

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

omit [NeZero n] in
theorem execution_ext (s t : Execution n (ZMod n))
    (hp : s.placed = t.placed) (ho : s.origin = t.origin)
    (hc : s.chain = t.chain) : s = t := by
  cases s
  cases t
  cases hp
  cases ho
  cases hc
  rfl

omit [NeZero n] in
theorem natCast_injective_below_modulus {u v : ℕ} (hu : u < n) (hv : v < n)
    (h : (u : ZMod n) = (v : ZMod n)) : u = v := by
  have hval := congrArg ZMod.val h
  simpa [ZMod.val_natCast_of_lt hu, ZMod.val_natCast_of_lt hv] using hval

theorem localLetters_site (j q : ZMod n) :
    siteWord (localLetters j) q = if q = j + 1 then j else q := by
  simp only [localLetters, siteWord_append, siteWord_pWord, siteWord,
    siteLetter, ZMod.natCast_zmod_val]
  by_cases h : q = j + 1
  · subst q
    simp [collapsePosition, add_assoc]
  · have hne : q + -j ≠ 1 := by
      intro heq
      apply h
      calc
        q = (q + -j) + j := by abel
        _ = 1 + j := congrArg (· + j) heq
        _ = j + 1 := add_comm _ _
    simp [collapsePosition, hne, h]

def shiftBackSites (f : ZMod n → ZMod n) (k : ℕ) : ZMod n → ZMod n :=
  fun atom => if atom = 1 then f 1 - (k : ZMod n) else f atom

def shiftBackExecution (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (k : ℕ) : Execution n (ZMod n) :=
  { s with placed := placementOfMap (shiftBackSites f k) }

def backShiftWord (b : ZMod n) : ℕ → List Letter
  | 0 => []
  | k + 1 => backShiftWord b k ++ localLetters (b - ((k + 1 : ℕ) : ZMod n))

def holeMoveSites (f : ZMod n → ZMod n) (h : ℕ) : ZMod n → ZMod n :=
  fun atom => if atom = 1 then f 0 + (h : ZMod n) else f atom

def holeMoveExecution (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (h : ℕ) : Execution n (ZMod n) :=
  { s with placed := placementOfMap (holeMoveSites f h) }

omit [NeZero n] in
@[simp] theorem shiftBackSites_zero (f : ZMod n → ZMod n) :
    shiftBackSites f 0 = f := by
  funext atom
  by_cases h : atom = 1 <;> simp [shiftBackSites, h]

theorem original_gap_hole (f : ZMod n → ZMod n) (g k : ℕ)
    (hg : g < n) (hkpos : 0 < k) (hkg : k < g)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    sourceFiber f (f 1 - (k : ZMod n)) = ∅ := by
  ext atom
  simp only [mem_sourceFiber, Finset.notMem_empty, iff_false]
  intro hsite
  have hdist : (f 1 - f atom).val = k := by
    rw [hsite, sub_sub_cancel, ZMod.val_natCast_of_lt (by omega : k < n)]
  have heq := hsupport atom (by rw [hdist]; exact hkg)
  rw [heq] at hdist
  simp only [sub_self, ZMod.val_zero] at hdist
  omega

theorem shiftBackSites_singleton_one (f : ZMod n → ZMod n) (g k : ℕ)
    (hg : g < n) (hk : k < g) (hone : SingletonSource f 1)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    SingletonSource (shiftBackSites f k) 1 := by
  intro atom hsite
  by_cases ha : atom = 1
  · exact ha
  · have hsite' : f atom = f 1 - (k : ZMod n) := by
      simpa [shiftBackSites, ha] using hsite
    by_cases hkzero : k = 0
    · exact hone atom (by simpa [hkzero] using hsite')
    · have hmem : atom ∈ sourceFiber f (f 1 - (k : ZMod n)) :=
        (mem_sourceFiber _ _ _).mpr hsite'
      rw [original_gap_hole f g k hg (by omega) hk hsupport] at hmem
      exact False.elim (Finset.notMem_empty atom hmem)

theorem shiftBack_destination_hole (f : ZMod n → ZMod n) (g k : ℕ)
    (hg : g < n) (hk : k + 1 < g)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    placementOfMap (shiftBackSites f k) (f 1 - ((k + 1 : ℕ) : ZMod n)) = none := by
  rw [placementOfMap_none_iff]
  ext atom
  simp only [mem_sourceFiber, Finset.notMem_empty, iff_false]
  intro hsite
  by_cases ha : atom = 1
  · have hsites : f 1 - (k : ZMod n) = f 1 - ((k + 1 : ℕ) : ZMod n) := by
      simpa [shiftBackSites, ha] using hsite
    have hcasts : (k : ZMod n) = ((k + 1 : ℕ) : ZMod n) := by
      calc
        (k : ZMod n) = f 1 - (f 1 - (k : ZMod n)) := by ring
        _ = f 1 - (f 1 - ((k + 1 : ℕ) : ZMod n)) := congrArg (fun z => f 1 - z) hsites
        _ = ((k + 1 : ℕ) : ZMod n) := by ring
    have := natCast_injective_below_modulus (by omega : k < n) (by omega : k + 1 < n) hcasts
    omega
  · have hmem : atom ∈ sourceFiber f (f 1 - ((k + 1 : ℕ) : ZMod n)) := by
      apply (mem_sourceFiber _ _ _).mpr
      simpa [shiftBackSites, ha] using hsite
    rw [original_gap_hole f g (k + 1) hg (by omega) hk hsupport] at hmem
    exact Finset.notMem_empty atom hmem

theorem shiftBack_step_map (f : ZMod n → ZMod n) (g k : ℕ)
    (hg : g < n) (hk : k + 1 < g) (hone : SingletonSource f 1)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    siteWord (localLetters (f 1 - ((k + 1 : ℕ) : ZMod n))) ∘ shiftBackSites f k =
      shiftBackSites f (k + 1) := by
  let j := f 1 - ((k + 1 : ℕ) : ZMod n)
  have hport : shiftBackSites f k 1 = j + 1 := by
    simp only [shiftBackSites, ite_true, j, Nat.cast_add, Nat.cast_one]
    ring
  funext atom
  change siteWord (localLetters j) (shiftBackSites f k atom) = _
  rw [localLetters_site]
  by_cases ha : atom = 1
  · subst atom
    rw [hport, if_pos rfl]
    simp [shiftBackSites, j]
  · have hne : shiftBackSites f k atom ≠ j + 1 := by
      intro h
      exact ha (shiftBackSites_singleton_one f g k hg (by omega) hone hsupport atom
        (h.trans hport.symm))
    rw [if_neg hne]
    simp [shiftBackSites, ha]

theorem shiftBack_one_actual (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (g k : ℕ) (hn : 2 ≤ n)
    (hg : g < n) (hk : k + 1 < g) (hone : SingletonSource f 1)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    let word := localLetters (f 1 - ((k + 1 : ℕ) : ZMod n))
    run {0, 1} (shiftBackExecution s f k) word = shiftBackExecution s f (k + 1) ∧
      FusionFree {0, 1} (shiftBackExecution s f k) word := by
  have hhole := shiftBack_destination_hole f g k hg hk hsupport
  have hlocal := run_localLetters_safe {0, 1} (shiftBackExecution s f k)
    (f 1 - ((k + 1 : ℕ) : ZMod n)) hn hhole
  have hplaced := atomSite_run {0, 1} (shiftBackExecution s f k)
    (shiftBackSites f k) (localLetters (f 1 - ((k + 1 : ℕ) : ZMod n))) hn rfl
  rw [shiftBack_step_map f g k hg hk hone hsupport] at hplaced
  refine ⟨execution_ext _ _ hplaced ?_ ?_, fusionFree_localLetters _ _ _ hhole⟩
  · have ho := congrArg (fun t : Execution n (ZMod n) => t.origin) hlocal
    simpa only [shiftBackExecution] using ho
  · have hc := congrArg (fun t : Execution n (ZMod n) => t.chain) hlocal
    simpa only [shiftBackExecution] using hc

/-- Every stage is the actual successor of its predecessor, with empty target
site checked before its literal local word. -/
theorem backShiftWord_actual (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (g k : ℕ) (hn : 2 ≤ n)
    (hg : g < n) (hk : k < g) (hplaced : s.placed = placementOfMap f)
    (hone : SingletonSource f 1)
    (hsupport : ∀ atom, (f 1 - f atom).val < g → f atom = f 1) :
    run {0, 1} s (backShiftWord (f 1) k) = shiftBackExecution s f k ∧
      FusionFree {0, 1} s (backShiftWord (f 1) k) := by
  induction k with
  | zero =>
      refine ⟨execution_ext _ _ ?_ rfl rfl, trivial⟩
      simpa [run, backShiftWord, shiftBackExecution] using hplaced
  | succ k ih =>
      obtain ⟨hp, hf⟩ := ih (by omega)
      obtain ⟨hstep, hfree⟩ := shiftBack_one_actual s f g k hn hg hk hone hsupport
      constructor
      · rw [backShiftWord, run_append, hp]
        exact hstep
      · rw [backShiftWord, fusionFree_append, hp]
        exact ⟨hf, hfree⟩

theorem shiftBackSites_eq_holeMove (f : ZMod n → ZMod n) (h : ℕ)
    (hle : h ≤ (f 1 - f 0).val) :
    shiftBackSites f ((f 1 - f 0).val - h) = holeMoveSites f h := by
  funext atom
  by_cases ha : atom = 1
  · simp only [shiftBackSites, holeMoveSites, ha, ite_true]
    rw [Nat.cast_sub hle, ZMod.natCast_zmod_val]
    ring
  · simp [shiftBackSites, holeMoveSites, ha]

theorem pairGenerated_run (s : Execution n (ZMod n)) (word : List Letter)
    (hgen : PairGenerated s) : PairGenerated (run {0, 1} s word) := by
  obtain ⟨history, hhistory⟩ := hgen
  exact ⟨history ++ word, by rw [run_append, hhistory]⟩

/-- The paper's descending E-word realizes x^(h), including the empty word h=g. -/
theorem holeMove_actual_word (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hreg : PairRegisterable s)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    let word := backShiftWord (f 1) ((f 1 - f 0).val - h)
    run {0, 1} s word = holeMoveExecution s f h ∧ FusionFree {0, 1} s word := by
  obtain ⟨hs, hgpos, hgmax, _, _, hsupport⟩ :=
    registerable_gap_admission s f hn hgen hplaced hreg
  obtain ⟨hr, hf⟩ := backShiftWord_actual s f (f 1 - f 0).val ((f 1 - f 0).val - h)
    (by omega) (by omega)
    (by omega) hplaced hs.2 hsupport
  refine ⟨?_, hf⟩
  rw [hr]
  exact execution_ext _ _
    (congrArg placementOfMap (shiftBackSites_eq_holeMove f h hle)) rfl rfl

theorem holeMove_generated (s : Execution n (ZMod n))
    (f : ZMod n → ZMod n) (hn : 3 ≤ n) (hgen : PairGenerated s)
    (hplaced : s.placed = placementOfMap f) (hreg : PairRegisterable s)
    (h : ℕ) (hpos : 1 ≤ h) (hle : h ≤ (f 1 - f 0).val) :
    PairGenerated (holeMoveExecution s f h) := by
  have hr := (holeMove_actual_word s f hn hgen hplaced hreg h hpos hle).1
  rw [← hr]
  exact pairGenerated_run s _ hgen

end FutureEvent
