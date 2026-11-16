import RSR2.Construction

/-!
# Executable loading invariants

This module connects the interleaved plan to the guarded `run` semantics.
The first lemmas isolate the two geometric facts needed by each instruction:
an upper rotation opens the synchronization site without wraparound, and a
lower rotation can align a still-singleton source atom.
-/

namespace RSR2.Parametric

def upperSupportBelow (P : Placement n) (k : Nat) : Prop :=
  ∀ a, (P a).1 = true → (P a).2.val < k

def lowerAt (P : Placement n) (q : Site n) : Prop :=
  ∃ a, P a = (false, q)

def phaseSite (n : Nat) (a : Fin n) (phase : Nat) : Site n :=
  nextMany n (by have := a.isLt; omega) a phase

def lowerFamily (P : Placement n) (atoms : List (Fin n)) (phase : Nat) : Prop :=
  ∀ a, a ∈ atoms → P a = (false, phaseSite n a phase)

def loadingInvariant (P : Placement n) (atoms : List (Fin n))
    (phase k : Nat) : Prop :=
  upperSupportBelow P k ∧ lowerFamily P atoms phase ∧ atoms.Nodup

/-!
`lowerSupportSubset` records the part of the prefix invariant that the
original loading predicate intentionally left implicit: no atom outside the
remaining source list may still be on the lower layer.  Keeping this as a
separate predicate lets the older guard lemmas remain reusable while the
executable Bell-realization proof strengthens the induction only where it
needs the exact source support.
-/
def lowerSupportSubset (P : Placement n) (atoms : List (Fin n)) : Prop :=
  ∀ a, (P a).1 = false → a ∈ atoms

def exactLoadingInvariant (P : Placement n) (atoms : List (Fin n))
    (phase k : Nat) : Prop :=
  loadingInvariant P atoms phase k ∧ lowerSupportSubset P atoms

theorem lowerSupportSubset_after_rotateMany
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (layer : Layer) (turns : Nat)
    (hsub : lowerSupportSubset P atoms) :
    lowerSupportSubset
      (rotateMany n (by omega) P layer turns) atoms := by
  intro a ha
  rcases hPa : P a with ⟨oldLayer, oldSite⟩
  cases oldLayer with
  | false =>
      apply hsub a
      simpa [rotateMany_apply, hPa] using ha
  | true =>
      cases layer <;> simp [rotateMany_apply, hPa] at ha

theorem seed_lowerSupportSubset_finRange (n : Nat) :
    lowerSupportSubset (seed n) (List.finRange n) := by
  intro a _
  exact List.mem_finRange a

theorem nextMany_injective (n : Nat) (hn : 0 < n) (k : Nat) :
    Function.Injective (nextMany n hn · k) := by
  induction k with
  | zero => intro a b h; exact h
  | succ k ih =>
      intro a b h
      apply next_injective n hn
      exact ih h

theorem phaseSite_val (n : Nat) (hn : 0 < n) (a : Fin n) (phase : Nat) :
    (phaseSite n a phase).val = (a.val + phase) % n := by
  exact nextMany_val n hn a phase

theorem phaseSite_injective (n : Nat) (hn : 0 < n) (phase : Nat) :
    Function.Injective (phaseSite n · phase) := by
  exact nextMany_injective n hn phase

theorem phaseSite_add (n : Nat) (hn : 0 < n) (a : Fin n)
    (phase turns : Nat) :
    phaseSite n a (phase + turns) =
      phaseSite n (phaseSite n a phase) turns := by
  apply Fin.ext
  rw [phaseSite_val n hn a (phase + turns)]
  rw [phaseSite_val n hn (phaseSite n a phase) turns]
  rw [phaseSite_val n hn a phase]
  rw [← Nat.add_assoc]
  exact (Nat.mod_add_mod (a.val + phase) n turns).symm

theorem rotateMany_lower_upperSupportBelow_iff (n : Nat) (hn : 1 < n)
    (P : Placement n) (turns k : Nat) :
    upperSupportBelow (rotateMany n (by omega) P false turns) k ↔
      upperSupportBelow P k := by
  constructor
  · intro h a ha
    have hsame : rotateMany n (by omega) P false turns a = P a := by
      rcases hPa : P a with ⟨layer, site⟩
      cases layer
      · simp [hPa] at ha
      · simp [rotateMany_apply, hPa]
    have hrot : (rotateMany n (by omega) P false turns a).1 = true := by
      simpa [hsame] using ha
    have hbound := h a hrot
    simpa [hsame] using hbound
  · intro h a ha
    have hsame : rotateMany n (by omega) P false turns a = P a := by
      rcases hPa : P a with ⟨layer, site⟩
      cases layer
      · simp [rotateMany_apply, hPa] at ha
      · simp [rotateMany_apply, hPa]
    have hsource : (P a).1 = true := by
      simpa [hsame] using ha
    have hbound := h a hsource
    simpa [hsame] using hbound

theorem rotateMany_upper_lower_iff (n : Nat) (hn : 1 < n)
    (P : Placement n) (turns : Nat) (a : Fin n) (q : Site n) :
    (rotateMany n (by omega) P true turns) a = (false, q) ↔
      P a = (false, q) := by
  rcases hPa : P a with ⟨layer, site⟩
  cases layer <;> simp [rotateMany_apply, hPa]

theorem rotateMany_lower_upper_iff (n : Nat) (hn : 1 < n)
    (P : Placement n) (turns : Nat) (q : Site n) :
    occupiedAt (rotateMany n (by omega) P false turns) true q ↔
      occupiedAt P true q := by
  simp only [occupiedAt, packet, rotateMany_apply]
  constructor
  · rintro ⟨a, ha⟩
    refine ⟨a, ?_⟩
    rcases hPa : P a with ⟨layer, site⟩
    cases layer
    · simp [hPa] at ha ⊢
    · simpa [hPa] using ha
  · rintro ⟨a, ha⟩
    refine ⟨a, ?_⟩
    rcases hPa : P a with ⟨layer, site⟩
    cases layer
    · simp [hPa] at ha ⊢
    · simpa [hPa] using ha

theorem upperRotate_site_bounds (n : Nat) (hn : 1 < n)
    (P : Placement n) (k : Nat) (hk : k < n)
    (hsupport : upperSupportBelow P k) (a : Fin n)
    (hlayer : (P a).1 = true) :
    0 < (rotate n (by omega) P true a).2.val ∧
      (rotate n (by omega) P true a).2.val ≤ k := by
  have hsite := hsupport a hlayer
  have hbound : (P a).2.val + 1 < n := by omega
  have hnext : (next n (by omega) (P a).2).val = (P a).2.val + 1 := by
    rw [next_val, Nat.mod_eq_of_lt hbound]
  simp only [rotate, if_pos hlayer]
  change 0 < (next n (by omega) (P a).2).val ∧
    (next n (by omega) (P a).2).val ≤ k
  rw [hnext]
  constructor <;> omega

theorem upperRotate_supportBelow_succ (n : Nat) (hn : 1 < n)
    (P : Placement n) (k : Nat) (hk : k < n)
    (hsupport : upperSupportBelow P k) :
    upperSupportBelow (rotate n (by omega) P true) (k + 1) := by
  intro a ha
  have hlayer : (P a).1 = true := by
    by_cases h : (P a).1 = true
    · exact h
    · simp [rotate, h] at ha
  have hsource := hsupport a hlayer
  have h := upperRotate_site_bounds n hn P k hk hsupport a hlayer
  have hnext : (next n (by omega) (P a).2).val = (P a).2.val + 1 := by
    have hbound : (P a).2.val + 1 < n := by omega
    rw [next_val, Nat.mod_eq_of_lt hbound]
  simp only [rotate, if_pos hlayer]
  change (next n (by omega) (P a).2).val < k + 1
  rw [hnext]
  omega

theorem seed_upperSupportBelow_zero (n : Nat) :
    upperSupportBelow (seed n) 0 := by
  intro a ha
  simp [seed] at ha

theorem seed_lowerFamily_finRange (n : Nat) (hn : 0 < n) :
    lowerFamily (seed n) (List.finRange n) 0 := by
  intro a _
  apply Prod.ext
  · rfl
  · apply Fin.ext
    rw [phaseSite_val n hn a 0]
    simp [seed, Nat.mod_eq_of_lt a.isLt]

theorem seed_lowerFamily (n : Nat) (hn : 0 < n) (atoms : List (Fin n)) :
    lowerFamily (seed n) atoms 0 := by
  intro a _
  apply Prod.ext
  · rfl
  · apply Fin.ext
    rw [phaseSite_val n hn a 0]
    simp [seed, Nat.mod_eq_of_lt a.isLt]

theorem seed_loadingInvariant (n : Nat) (hn : 1 < n) :
    loadingInvariant (seed n) (List.finRange n) 0 0 := by
  refine ⟨seed_upperSupportBelow_zero n,
    seed_lowerFamily_finRange n (by omega), ?_⟩
  exact List.nodup_finRange n

/-!
The plan annotator computes each source rotation from the atom's current
phase.  This equality is the arithmetic bridge between that definition and
the executable invariant's alignment premise.
-/
theorem lowerBackCount_phaseSite_aligns
    (n : Nat) (hn : 0 < n) (a : Fin n) (phase : Nat) :
    ((phaseSite n a phase).val +
      lowerBackCount n
        ⟨(a.val + phase) % n,
          Nat.mod_lt _ (by have := a.isLt; omega)⟩) % n = 0 := by
  let q : Fin n :=
    ⟨(a.val + phase) % n,
      Nat.mod_lt _ (by have := a.isLt; omega)⟩
  have hq : phaseSite n a phase = q := by
    apply Fin.ext
    rw [phaseSite_val n hn a phase]
  rw [hq]
  exact lowerBackCount_aligns n hn q

theorem annotateMarked_cons_eq
    (n phase : Nat) (a : Fin n) (continues : Bool)
    (rest : List (Fin n × Bool)) :
    annotateMarked n phase ((a, continues) :: rest) =
      { atom := a
        sourceTurns :=
          lowerBackCount n
            ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩
        continueBlock := continues } ::
        annotateMarked n
          (phase + lowerBackCount n
            ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩) rest := by
  rfl

theorem seed_upperRotate_supportBelow_one (n : Nat) (hn : 1 < n) :
    upperSupportBelow (rotate n (by omega) (seed n) true) 1 := by
  apply upperRotate_supportBelow_succ n hn (seed n) 0 (by omega)
    (seed_upperSupportBelow_zero n)

theorem liftPacket_supportBelow (n : Nat) (hn : 1 < n)
    (P : Placement n) (k : Nat) (hk : 0 < k)
    (hsupport : upperSupportBelow P k) :
    upperSupportBelow (liftPacket n (by omega) P) k := by
  intro a ha
  by_cases hsource : P a = (false, site0 n (by omega))
  · simp [liftPacket, hsource] at ha
    simpa [liftPacket, hsource, site0] using hk
  · have hlayer : (P a).1 = true := by
      simpa [liftPacket, hsource] using ha
    have hbound := hsupport a hlayer
    simpa [liftPacket, hsource] using hbound

theorem collapse_upper_supportBelow (n : Nat) (hn : 1 < n)
    (P : Placement n) (k : Nat) (hsupport : upperSupportBelow P k) :
    upperSupportBelow (collapse n hn P true) k := by
  intro a ha
  by_cases hcollapsed : P a = (true, site1 n hn)
  · have hlayer : (P a).1 = true := by
      rw [hcollapsed]
    have hbound := hsupport a hlayer
    simp [collapse, hcollapsed, site0, site1] at hbound ⊢
    omega
  · have hsame : P a = (collapse n hn P true a) := by
      simpa [collapse, hcollapsed]
    have hlayer : (P a).1 = true := by
      simpa [hsame] using ha
    have hbound := hsupport a hlayer
    simpa [collapse, hcollapsed] using hbound

theorem lowerSupportSubset_after_liftPacket
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n))
    (hsub : lowerSupportSubset P atoms) :
    lowerSupportSubset (liftPacket n (by omega) P) atoms := by
  intro a ha
  by_cases hsource : P a = (false, site0 n (by omega))
  · simp [liftPacket, hsource] at ha
  · apply hsub a
    simpa [liftPacket, hsource] using ha

theorem lowerSupportSubset_after_collapse
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (layer : Layer)
    (hsub : lowerSupportSubset P atoms) :
    lowerSupportSubset (collapse n hn P layer) atoms := by
  intro a ha
  by_cases hcollapsed : P a = (layer, site1 n hn)
  · cases layer with
    | false =>
        apply hsub a
        simpa [hcollapsed] using hcollapsed
    | true =>
        simp [collapse, hcollapsed] at ha
  · apply hsub a
    simpa [collapse, hcollapsed] using ha

theorem upperRotate_opens_sync_site (n : Nat) (hn : 1 < n)
    (P : Placement n) (k : Nat) (hk : k < n)
    (hsupport : upperSupportBelow P k) :
    ¬ occupiedAt (rotate n (by omega) P true) true (site0 n (by omega)) := by
  intro hocc
  rcases hocc with ⟨a, ha⟩
  change rotate n (by omega) P true a = (true, site0 n (by omega)) at ha
  have hlayer : (P a).1 = true := by
    by_cases h : (P a).1 = true
    · exact h
    · simp [rotate, h] at ha
      exact False.elim (h (congrArg Prod.fst ha))
  simp [rotate, hlayer] at ha
  have hbounds := upperRotate_site_bounds n hn P k hk hsupport a hlayer
  have hsite : (next n (by omega) (P a).2).val = 0 := by
    simpa [site0] using congrArg Fin.val ha
  simp only [rotate, if_pos hlayer] at hbounds
  exact (Nat.ne_of_gt hbounds.1) hsite

theorem rotateMany_lower_aligned (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) (q : Site n) (turns : Nat)
    (hsource : P a = (false, q))
    (halign : (q.val + turns) % n = 0) :
    (rotateMany n (by omega) P false turns) a = (false, site0 n (by omega)) := by
  rw [rotateMany_apply, hsource]
  simp only [if_true]
  apply Prod.ext
  · rfl
  · apply Fin.ext
    rw [nextMany_val]
    simpa [halign, site0]

theorem liftGuard_of_aligned_source_and_empty_target (n : Nat)
    (hn : 1 < n) (P : Placement n) (a : Fin n)
    (hsource : P a = (false, site0 n (by omega)))
    (hempty : ¬ occupiedAt P true (site0 n (by omega))) :
    liftGuard n (by omega) P := by
  constructor
  · exact ⟨a, hsource⟩
  · exact hempty

theorem run_instructionWord_of_guard (n : Nat) (hn : 1 < n)
    (P : Placement n) (first : Bool) (i : LoadInstruction n)
    (hguard : liftGuard n (by omega)
      (rotateMany n (by omega)
        (rotateMany n (by omega) P true (bitCost (!first)))
        false i.sourceTurns)) :
    run n hn P (instructionWord first i) =
      some (if i.continueBlock then
        collapse n hn
          (liftPacket n (by omega)
            (rotateMany n (by omega)
              (rotateMany n (by omega) P true (bitCost (!first)))
              false i.sourceTurns)) true
        else
          liftPacket n (by omega)
            (rotateMany n (by omega)
              (rotateMany n (by omega) P true (bitCost (!first)))
              false i.sourceTurns)) := by
  let P₁ := rotateMany n (by omega) P true (bitCost (!first))
  let P₂ := rotateMany n (by omega) P₁ false i.sourceTurns
  unfold instructionWord
  have hrot₁ : run n hn P
      (List.replicate (bitCost (!first)) (.p true)) = some P₁ := by
    simpa [P₁] using
      (run_powers n hn P true (bitCost (!first)))
  have hrot₂ : run n hn P₁
      (List.replicate i.sourceTurns (.p false)) = some P₂ := by
    simpa [P₂] using
      (run_powers n hn P₁ false i.sourceTurns)
  have hrot : run n hn P
      (List.replicate (bitCost (!first)) (.p true) ++
        List.replicate i.sourceTurns (.p false)) = some P₂ := by
    rw [run_append, hrot₁]
    simp only [Option.bind_some]
    exact hrot₂
  have hprefix : run n hn P
      (List.replicate (bitCost (!first)) (.p true) ++
        List.replicate i.sourceTurns (.p false) ++ [.v]) =
      some (liftPacket n (by omega) P₂) := by
    rw [run_append, hrot]
    simp only [Option.bind_some]
    have hv : step n hn P₂ .v = some (liftPacket n (by omega) P₂) := by
      rw [step_v_eq_some_iff]
      exact ⟨hguard, rfl⟩
    simpa [run, hv]
  rw [run_append, hprefix]
  simp only [Option.bind_some]
  cases hcontinue : i.continueBlock <;>
    simp [P₁, P₂, bitCost, hcontinue, run, step_d]

/-!
The singleton seed gives a reusable base case for the executable plan
induction.  A lower-layer rotation cannot create an upper packet, so once the
chosen source atom is aligned to site zero the partial elevator action is
guaranteed to succeed.
-/
theorem seed_lower_aligned_liftGuard (n : Nat) (hn : 1 < n)
    (a : Fin n) (turns : Nat)
    (halign : (a.val + turns) % n = 0) :
    liftGuard n (by omega)
      (rotateMany n (by omega) (seed n) false turns) := by
  apply liftGuard_of_aligned_source_and_empty_target n hn
    (rotateMany n (by omega) (seed n) false turns) a
  · exact rotateMany_lower_aligned n hn (seed n) a a turns rfl halign
  · intro hocc
    rcases hocc with ⟨b, hb⟩
    change rotateMany n (by omega) (seed n) false turns b =
      (true, site0 n (by omega)) at hb
    rw [rotateMany_apply] at hb
    simp [seed] at hb

theorem run_seed_instructionWord_of_aligned
    (n : Nat) (hn : 1 < n) (turns : Nat)
    (i : LoadInstruction n)
    (halign : (i.atom.val + turns) % n = 0)
    (hiturns : i.sourceTurns = turns) :
    run n hn (seed n) (instructionWord true i) =
      some (if i.continueBlock then
        collapse n hn
          (liftPacket n (by omega)
            (rotateMany n (by omega)
              (rotateMany n (by omega) (seed n) true (bitCost (!true)))
              false i.sourceTurns)) true
        else
          liftPacket n (by omega)
            (rotateMany n (by omega)
              (rotateMany n (by omega) (seed n) true (bitCost (!true)))
              false i.sourceTurns)) := by
  have hguard : liftGuard n (by omega)
      (rotateMany n (by omega)
        (rotateMany n (by omega) (seed n) true (bitCost (!true)))
        false i.sourceTurns) := by
    simpa [bitCost, rotateMany, hiturns] using
      (seed_lower_aligned_liftGuard n hn i.atom turns halign)
  exact run_instructionWord_of_guard n hn (seed n) true i hguard

/-!
`instructionPrepared` and `instructionResult` expose the two states used by
one loading instruction.  Keeping these expressions named makes the eventual
interleaved-prefix induction state its guard at the exact point where `v` is
executed, rather than hiding it inside a whole-word equality.
-/
def instructionPrepared (n : Nat) (hn : 1 < n)
    (first : Bool) (P : Placement n) (i : LoadInstruction n) : Placement n :=
  rotateMany n (by omega)
    (rotateMany n (by omega) P true (bitCost (!first)))
    false i.sourceTurns

def instructionResult (n : Nat) (hn : 1 < n)
    (first : Bool) (P : Placement n) (i : LoadInstruction n) : Placement n :=
  if i.continueBlock then
    collapse n hn (liftPacket n (by omega) (instructionPrepared n hn first P i)) true
  else
    liftPacket n (by omega) (instructionPrepared n hn first P i)

/-!
The loading invariant supplies the guard for one instruction.  This is the
local bridge needed by the eventual interleaved-prefix induction: lower
rotations preserve upper occupancy, while a non-initial upper rotation opens
site zero.  The source alignment and the first-instruction case remain
explicit, so this theorem does not silently assume that an arbitrary plan is
guarded.
-/
theorem liftGuard_of_loadingInvariant
    (n : Nat) (hn : 1 < n)
    (P : Placement n) (atoms : List (Fin n))
    (phase k : Nat) (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k)
    (hk : k < n)
    (hatom : i.atom ∈ atoms)
    (hlower : lowerFamily P atoms phase)
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0)
    (hfirst : first = true → k = 0) :
    liftGuard n (by omega)
      (instructionPrepared n hn first P i) := by
  let P₁ := rotateMany n (by omega) P true (bitCost (!first))
  let P₂ := rotateMany n (by omega) P₁ false i.sourceTurns
  have hsource : P i.atom =
      (false, phaseSite n i.atom phase) := hlower i.atom hatom
  have hsource₁ : P₁ i.atom =
      (false, phaseSite n i.atom phase) := by
    exact (rotateMany_upper_lower_iff n hn P (bitCost (!first)) i.atom
      (phaseSite n i.atom phase)).2 hsource
  have hsource₂ : P₂ i.atom = (false, site0 n (by omega)) := by
    exact rotateMany_lower_aligned n hn P₁ i.atom
      (phaseSite n i.atom phase) i.sourceTurns hsource₁ halign
  have hempty₁ : ¬ occupiedAt P₁ true (site0 n (by omega)) := by
    cases hfirst' : first with
    | false =>
        have hopen := upperRotate_opens_sync_site n hn P k hk hupper
        simpa [P₁, hfirst', bitCost, rotateMany] using hopen
    | true =>
        have hk0 : k = 0 := hfirst hfirst'
        intro hocc
        rcases hocc with ⟨a, ha⟩
        have ha' := ha
        simp [P₁, hfirst', bitCost, rotateMany] at ha'
        change P a = (true, site0 n (by omega)) at ha'
        have haP : P a = (true, site0 n (by omega)) := by
          exact ha'
        have hbound := hupper a (by rw [haP])
        simp [hk0] at hbound
  have hempty₂ : ¬ occupiedAt P₂ true (site0 n (by omega)) := by
    intro hocc
    have hocc₁ := (rotateMany_lower_upper_iff n hn P₁ i.sourceTurns
      (site0 n (by omega))).1 hocc
    exact hempty₁ hocc₁
  exact liftGuard_of_aligned_source_and_empty_target n hn P₂ i.atom
    hsource₂ hempty₂

/-!
Phase transport is separated from the guarded elevator proof.  These lemmas
are the small equalities used by the eventual prefix induction: rotating the
upper layer leaves lower coordinates unchanged, while a lower rotation merely
advances the common phase of all still-unloaded atoms.
-/
theorem lowerFamily_after_upperRotate
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (phase turns : Nat)
    (hfamily : lowerFamily P atoms phase) :
    lowerFamily
      (rotateMany n (by omega) P true turns) atoms phase := by
  intro a ha
  exact (rotateMany_upper_lower_iff n hn P turns a
    (phaseSite n a phase)).2 (hfamily a ha)

theorem lowerFamily_after_lowerRotate
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (phase turns : Nat)
    (hfamily : lowerFamily P atoms phase) :
    lowerFamily
      (rotateMany n (by omega) P false turns) atoms (phase + turns) := by
  intro a ha
  have hsource := hfamily a ha
  rw [rotateMany_apply, hsource]
  simp only [if_true]
  apply Prod.ext
  · rfl
  · apply Fin.ext
    have hadd := phaseSite_add n (by omega) a phase turns
    simpa [phaseSite] using congrArg Fin.val hadd.symm

theorem lowerFamily_after_instructionPrepared
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (phase : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hfamily : lowerFamily P atoms phase) :
    lowerFamily
      (instructionPrepared n hn first P i) atoms
        (phase + i.sourceTurns) := by
  unfold instructionPrepared
  apply lowerFamily_after_lowerRotate n hn
  exact lowerFamily_after_upperRotate n hn P atoms phase
    (bitCost (!first)) hfamily

theorem lowerFamily_after_liftPacket
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (phase : Nat)
    (hfamily : lowerFamily P atoms phase)
    (hnozero : ∀ a, a ∈ atoms →
      P a ≠ (false, site0 n (by omega))) :
    lowerFamily (liftPacket n (by omega) P) atoms phase := by
  intro a ha
  have hvalue := hfamily a ha
  have hneq := hnozero a ha
  have hneq' : phaseSite n a phase ≠ site0 n (by omega) := by
    intro hphase
    apply hneq
    rw [hvalue, hphase]
  simp [liftPacket, hvalue, hneq']

theorem lowerFamily_after_collapse
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (atoms : List (Fin n)) (phase : Nat)
    (hfamily : lowerFamily P atoms phase) :
    lowerFamily (collapse n hn P true) atoms phase := by
  intro a ha
  have hvalue := hfamily a ha
  simp [collapse, hvalue]

theorem lowerFamily_tail_ne
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (i : Fin n) (rest : List (Fin n)) (phase : Nat)
    (hnodup : (i :: rest).Nodup)
    (hfamily : lowerFamily P (i :: rest) phase) :
    ∀ b, b ∈ rest → P b ≠ P i := by
  intro b hb hsame
  have hbi : phaseSite n b phase = phaseSite n i phase := by
    have hb' := hfamily b (by simp [hb])
    have hi' := hfamily i (by simp)
    rw [hb', hi'] at hsame
    exact congrArg Prod.snd hsame
  have hbeq : b = i := phaseSite_injective n (by omega) phase hbi
  exact (List.nodup_cons.mp hnodup).1 (hbeq ▸ hb)

theorem lowerFamily_after_instructionResult_tail
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (rest : List (Fin n)) (phase : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hnodup : (i.atom :: rest).Nodup)
    (hfamily : lowerFamily P (i.atom :: rest) phase)
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0) :
    lowerFamily
      (instructionResult n hn first P i) rest
        (phase + i.sourceTurns) := by
  let Pprep := instructionPrepared n hn first P i
  have hprepared : lowerFamily Pprep (i.atom :: rest)
      (phase + i.sourceTurns) := by
    simpa [Pprep] using
      (lowerFamily_after_instructionPrepared n hn P (i.atom :: rest)
        phase first i hfamily)
  have hsource := hfamily i.atom (by simp)
  have hsource₁ :
      rotateMany n (by omega)
        (rotateMany n (by omega) P true (bitCost (!first))) false
          i.sourceTurns i.atom = (false, site0 n (by omega)) := by
    exact rotateMany_lower_aligned n hn
      (rotateMany n (by omega) P true (bitCost (!first))) i.atom
      (phaseSite n i.atom phase) i.sourceTurns
      ((rotateMany_upper_lower_iff n hn P (bitCost (!first)) i.atom
        (phaseSite n i.atom phase)).2 hsource) halign
  have hsource₂ : Pprep i.atom = (false, site0 n (by omega)) := by
    simpa [Pprep, instructionPrepared] using hsource₁
  have hnozero : ∀ a, a ∈ rest →
      Pprep a ≠ (false, site0 n (by omega)) := by
    intro a ha hzero
    have hne := lowerFamily_tail_ne n hn Pprep i.atom rest
      (phase + i.sourceTurns) hnodup hprepared a ha
    exact hne (hzero.trans hsource₂.symm)
  have hpreparedTail : lowerFamily Pprep rest
      (phase + i.sourceTurns) := by
    intro a ha
    exact hprepared a (by simp [ha])
  have hlift : lowerFamily
      (liftPacket n (by omega) Pprep) rest
        (phase + i.sourceTurns) := by
    exact lowerFamily_after_liftPacket n hn Pprep rest
      (phase + i.sourceTurns) hpreparedTail hnozero
  cases hcontinue : i.continueBlock with
  | false =>
      simpa [instructionResult, Pprep, hcontinue] using hlift
  | true =>
      simpa [instructionResult, Pprep, hcontinue] using
        (lowerFamily_after_collapse n hn
          (liftPacket n (by omega) Pprep) rest
          (phase + i.sourceTurns) hlift)

theorem lowerSupportSubset_after_instructionResult_tail
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (rest : List (Fin n)) (phase : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hsub : lowerSupportSubset P (i.atom :: rest))
    (hfamily : lowerFamily P (i.atom :: rest) phase)
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0) :
    lowerSupportSubset
      (instructionResult n hn first P i) rest := by
  let Pprep := instructionPrepared n hn first P i
  have hsubPrep : lowerSupportSubset Pprep (i.atom :: rest) := by
    unfold Pprep instructionPrepared
    apply lowerSupportSubset_after_rotateMany n hn
      (rotateMany n (by omega) P true (bitCost (!first)))
      (i.atom :: rest) false i.sourceTurns
    exact lowerSupportSubset_after_rotateMany n hn P
      (i.atom :: rest) true (bitCost (!first)) hsub
  have hsource := hfamily i.atom (by simp)
  have hsource₁ :
      rotateMany n (by omega)
        (rotateMany n (by omega) P true (bitCost (!first))) false
          i.sourceTurns i.atom = (false, site0 n (by omega)) := by
    exact rotateMany_lower_aligned n hn
      (rotateMany n (by omega) P true (bitCost (!first))) i.atom
      (phaseSite n i.atom phase) i.sourceTurns
      ((rotateMany_upper_lower_iff n hn P (bitCost (!first)) i.atom
        (phaseSite n i.atom phase)).2 hsource) halign
  have hsource₂ : Pprep i.atom = (false, site0 n (by omega)) := by
    simpa [Pprep, instructionPrepared] using hsource₁
  have hsubLift : lowerSupportSubset
      (liftPacket n (by omega) Pprep) rest := by
    intro a ha
    have hmem := lowerSupportSubset_after_liftPacket n hn Pprep
      (i.atom :: rest) hsubPrep a ha
    rcases List.mem_cons.mp hmem with hhead | htail
    · have hupper :
          (liftPacket n (by omega) Pprep a).1 = true := by
        simp [liftPacket, hhead, hsource₂]
      simp [hupper] at ha
    · exact htail
  cases hcontinue : i.continueBlock with
  | false =>
      simpa [instructionResult, Pprep, hcontinue] using hsubLift
  | true =>
      simpa [instructionResult, Pprep, hcontinue] using
        (lowerSupportSubset_after_collapse n hn
          (liftPacket n (by omega) Pprep) rest true hsubLift)

/-!
The companion upper-layer invariant has a similarly local step rule.  The
initial upper rotation either advances an already loaded prefix by one site,
or is absent for the first instruction; the lower rotation does not affect
upper packets.  The elevator then adds only the new packet at site zero, and
an optional continuation collapse can only move site one back to site zero.
-/
theorem upperSupportBelow_after_instructionResult
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (k : Nat) (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k)
    (hk : k < n)
    (hfirst : first = true → k = 0) :
    upperSupportBelow
      (instructionResult n hn first P i) (k + 1) := by
  let P₁ := rotateMany n (by omega) P true (bitCost (!first))
  let P₂ := rotateMany n (by omega) P₁ false i.sourceTurns
  have hupper₁ : upperSupportBelow P₁ (k + 1) := by
    cases hfirst' : first with
    | false =>
        simpa [P₁, hfirst', bitCost, rotateMany] using
          (upperRotate_supportBelow_succ n hn P k hk hupper)
    | true =>
        have hk0 : k = 0 := hfirst hfirst'
        have hzero : upperSupportBelow P 1 := by
          intro a ha
          have hbound := hupper a ha
          omega
        simpa [P₁, hfirst', bitCost, rotateMany, hk0] using hzero
  have hupper₂ : upperSupportBelow P₂ (k + 1) := by
    exact (rotateMany_lower_upperSupportBelow_iff n hn P₁
      i.sourceTurns (k + 1)).2 hupper₁
  have hlift : upperSupportBelow
      (liftPacket n (by omega) P₂) (k + 1) := by
    exact liftPacket_supportBelow n hn P₂ (k + 1) (by omega) hupper₂
  cases hcontinue : i.continueBlock with
  | false =>
      simpa [instructionResult, instructionPrepared, P₁, P₂, hcontinue] using hlift
  | true =>
      simpa [instructionResult, instructionPrepared, P₁, P₂, hcontinue] using
        (collapse_upper_supportBelow n hn
          (liftPacket n (by omega) P₂) (k + 1) hlift)

/-!
The three components of `loadingInvariant` now compose at one instruction
boundary.  Keeping the selected atom as the head of the source list makes the
statement match the recursive shape needed by the interleaved-plan proof:
the head is transferred, while the tail remains lower-layer singleton data.
-/
theorem loadingInvariant_after_instructionResult_cons
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (rest : List (Fin n)) (phase k : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k)
    (hk : k < n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (i.atom :: rest) phase)
    (hnodup : (i.atom :: rest).Nodup)
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0) :
    loadingInvariant
      (instructionResult n hn first P i) rest
      (phase + i.sourceTurns) (k + 1) := by
  have hupper' := upperSupportBelow_after_instructionResult n hn P k first i
    hupper hk hfirst
  have hfamily' := lowerFamily_after_instructionResult_tail n hn P rest phase
    first i hnodup hfamily halign
  have hnodup' : rest.Nodup := (List.nodup_cons.mp hnodup).2
  exact ⟨hupper', hfamily', hnodup'⟩

theorem run_instructionWord_of_guard_eq_result
    (n : Nat) (hn : 1 < n)
    (P : Placement n) (first : Bool) (i : LoadInstruction n)
    (hguard : liftGuard n (by omega) (instructionPrepared n hn first P i)) :
    run n hn P (instructionWord first i) =
      some (instructionResult n hn first P i) := by
  simpa [instructionPrepared, instructionResult] using
    (run_instructionWord_of_guard n hn P first i hguard)

/-!
This is the executable one-step bridge: under the prefix invariant and the
source alignment equation, the guarded instruction runs successfully and the
same invariant is available for the remaining source list.  The theorem is
deliberately local; it does not yet claim that every generated plan satisfies
the alignment equation.
-/
theorem run_instructionWord_of_loadingInvariant_cons
    (n : Nat) (hn : 1 < n) (P : Placement n)
    (rest : List (Fin n)) (phase k : Nat)
    (first : Bool) (i : LoadInstruction n)
    (hupper : upperSupportBelow P k)
    (hk : k < n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (i.atom :: rest) phase)
    (hnodup : (i.atom :: rest).Nodup)
    (halign : ((phaseSite n i.atom phase).val + i.sourceTurns) % n = 0) :
    run n hn P (instructionWord first i) =
        some (instructionResult n hn first P i) ∧
      loadingInvariant
        (instructionResult n hn first P i) rest
        (phase + i.sourceTurns) (k + 1) := by
  have hguard := liftGuard_of_loadingInvariant n hn P (i.atom :: rest)
    phase k first i hupper hk (by simp) hfamily halign hfirst
  have hrun := run_instructionWord_of_guard_eq_result n hn P first i hguard
  have hinv := loadingInvariant_after_instructionResult_cons n hn P rest phase k
    first i hupper hk hfirst hfamily hnodup halign
  exact ⟨hrun, hinv⟩

/-!
The plan-level bridge deliberately keeps the state after each instruction
explicit.  This is the interface needed by the eventual prefix invariant:
the dynamic proof supplies the two `run = some ...` hypotheses, while this
lemma only concatenates their already checked executions.
-/
theorem run_emitPlanAux_cons_of_step
    (n : Nat) (hn : 1 < n)
    (first : Bool) (P Q R : Placement n)
    (i : LoadInstruction n) (rest : List (LoadInstruction n))
    (hstep : run n hn P (instructionWord first i) = some Q)
    (hrest : run n hn Q (emitPlanAux false rest) = some R) :
    run n hn P (emitPlanAux first (i :: rest)) = some R := by
  rw [emitPlanAux, run_append, hstep]
  simp only [Option.bind_some]
  exact hrest

theorem run_emitPlan_cons_of_step
    (n : Nat) (hn : 1 < n)
    (P Q R : Placement n)
    (i : LoadInstruction n) (rest : List (LoadInstruction n))
    (hstep : run n hn P (instructionWord true i) = some Q)
    (hrest : run n hn Q (emitPlanAux false rest) = some R) :
    run n hn P (emitPlan (i :: rest)) = some R := by
  simpa [emitPlan] using
    (run_emitPlanAux_cons_of_step n hn true P Q R i rest hstep hrest)

/-!
`CheckedPlan` is the small proof-carrying interface used by the eventual
prefix invariant.  It records the placement after every instruction, while
leaving the invariant that establishes each step to the caller.  The
constructor deliberately follows `emitPlanAux`: after the first instruction
the upper-rotation flag is `false` for every remaining instruction.
-/
inductive CheckedPlan (n : Nat) (hn : 1 < n) :
    Bool → Placement n → List (LoadInstruction n) → Placement n → Prop where
  | nil (first : Bool) (P : Placement n) :
      CheckedPlan n hn first P [] P
  | cons {first : Bool} {P Q R : Placement n}
      {i : LoadInstruction n} {rest : List (LoadInstruction n)}
      (hstep : run n hn P (instructionWord first i) = some Q)
      (hrest : CheckedPlan n hn false Q rest R) :
      CheckedPlan n hn first P (i :: rest) R

theorem checkedPlan_run_emitPlanAux
    (n : Nat) (hn : 1 < n)
    (first : Bool) (P R : Placement n)
    (plan : List (LoadInstruction n))
    (hchecked : CheckedPlan n hn first P plan R) :
    run n hn P (emitPlanAux first plan) = some R := by
  induction hchecked with
  | nil => rfl
  | @cons first P Q R i rest hstep hrest ih =>
      exact run_emitPlanAux_cons_of_step n hn first P Q R i rest hstep ih

theorem checkedPlan_run_emitPlan
    (n : Nat) (hn : 1 < n)
    (P R : Placement n)
    (plan : List (LoadInstruction n))
    (hchecked : CheckedPlan n hn true P plan R) :
    run n hn P (emitPlan plan) = some R := by
  simpa [emitPlan] using
    (checkedPlan_run_emitPlanAux n hn true P R plan hchecked)

/-!
`GuardedPlan` is the dynamic proof interface for RSR-2-B.  Unlike
`CheckedPlan`, it does not accept an opaque whole-instruction `run` equality:
each constructor records the actual elevator guard at the prepared state.
The remaining all-`n` work is therefore precisely to construct a
`GuardedPlan` for `interleavedPlan`; the execution theorem below is already
generic in the plan and needs no further semantic assumptions.
-/
inductive GuardedPlan (n : Nat) (hn : 1 < n) :
    Bool → Placement n → List (LoadInstruction n) → Placement n → Prop where
  | nil (first : Bool) (P : Placement n) :
      GuardedPlan n hn first P [] P
  | cons {first : Bool} {P R : Placement n}
      {i : LoadInstruction n} {rest : List (LoadInstruction n)}
      (hguard : liftGuard n (by omega)
        (instructionPrepared n hn first P i))
      (hrest : GuardedPlan n hn false
        (instructionResult n hn first P i) rest R) :
      GuardedPlan n hn first P (i :: rest) R

/-!
Plan-level executable bridge for the generated marked list.  The theorem is
parametric in the source list: the caller supplies the initial lower-family,
upper-support, and distinctness facts, while the recursive proof discharges
each guarded elevator step and exposes the next loading invariant.
-/
theorem guardedPlan_annotateMarked
    (n : Nat) (hn : 1 < n)
    (phase k : Nat) (first : Bool) (P : Placement n)
    (xs : List (Fin n × Bool))
    (hupper : upperSupportBelow P k)
    (hk : k + xs.length ≤ n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (xs.map Prod.fst) phase)
    (hnodup : (xs.map Prod.fst).Nodup) :
    ∃ R, GuardedPlan n hn first P (annotateMarked n phase xs) R := by
  induction xs generalizing P phase k first with
  | nil =>
      exact ⟨P, GuardedPlan.nil first P⟩
  | cons x rest ih =>
      cases x with
      | mk a continues =>
          let q : Fin n :=
            ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩
          let i : LoadInstruction n :=
            { atom := a
              sourceTurns := lowerBackCount n q
              continueBlock := continues }
          have hk' : k < n := by
            have hk'' : k + 1 + rest.length ≤ n := by
              simpa [List.length_cons, Nat.add_assoc, Nat.add_comm,
                Nat.add_left_comm] using hk
            omega
          have hfamily' : lowerFamily P (a :: rest.map Prod.fst) phase := by
            simpa using hfamily
          have hnodup' : (a :: rest.map Prod.fst).Nodup := by
            simpa using hnodup
          have halign :
              ((phaseSite n a phase).val + i.sourceTurns) % n = 0 := by
            simpa [i, q] using
              (lowerBackCount_phaseSite_aligns n (by omega) a phase)
          have hguard := liftGuard_of_loadingInvariant n hn P
            (a :: rest.map Prod.fst) phase k first i hupper hk'
            (by simp [i]) hfamily' halign hfirst
          have hstep := loadingInvariant_after_instructionResult_cons n hn P
            (rest.map Prod.fst) phase k first i hupper hk' hfirst
            hfamily' hnodup' halign
          have hkrest : (k + 1) + rest.length ≤ n := by
            simpa [List.length_cons, Nat.add_assoc, Nat.add_comm,
              Nat.add_left_comm] using hk
          have htail := ih
            (P := instructionResult n hn first P i)
            (phase := phase + i.sourceTurns)
            (k := k + 1)
            (first := false)
            hstep.1 hkrest (by simp) hstep.2.1 hstep.2.2
          have hcons :
              GuardedPlan n hn first P
                (i :: annotateMarked n (phase + i.sourceTurns) rest)
                htail.choose :=
            GuardedPlan.cons hguard htail.choose_spec
          refine ⟨htail.choose, ?_⟩
          simpa [annotateMarked, i, q] using hcons

/-!
The strengthened plan induction carries the complementary support fact that
the lower layer contains no atom outside the still-unloaded tail.  The
ordinary `GuardedPlan` theorem above remains useful as a lightweight bridge;
this variant is the endpoint-specific certificate needed to show that a
successful generated plan has emptied the lower layer.
-/
theorem guardedPlan_annotateMarked_lowerSupport
    (n : Nat) (hn : 1 < n)
    (phase k : Nat) (first : Bool) (P : Placement n)
    (xs : List (Fin n × Bool))
    (hupper : upperSupportBelow P k)
    (hk : k + xs.length ≤ n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (xs.map Prod.fst) phase)
    (hnodup : (xs.map Prod.fst).Nodup)
    (hsub : lowerSupportSubset P (xs.map Prod.fst)) :
    ∃ R, GuardedPlan n hn first P (annotateMarked n phase xs) R ∧
      lowerSupportSubset R [] := by
  induction xs generalizing P phase k first with
  | nil =>
      exact ⟨P, GuardedPlan.nil first P, hsub⟩
  | cons x rest ih =>
      cases x with
      | mk a continues =>
          let q : Fin n :=
            ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩
          let i : LoadInstruction n :=
            { atom := a
              sourceTurns := lowerBackCount n q
              continueBlock := continues }
          have hk' : k < n := by
            have hk'' : k + 1 + rest.length ≤ n := by
              simpa [List.length_cons, Nat.add_assoc, Nat.add_comm,
                Nat.add_left_comm] using hk
            omega
          have hfamily' : lowerFamily P (a :: rest.map Prod.fst) phase := by
            simpa using hfamily
          have hnodup' : (a :: rest.map Prod.fst).Nodup := by
            simpa using hnodup
          have hsub' : lowerSupportSubset P (a :: rest.map Prod.fst) := by
            simpa using hsub
          have halign :
              ((phaseSite n a phase).val + i.sourceTurns) % n = 0 := by
            simpa [i, q] using
              (lowerBackCount_phaseSite_aligns n (by omega) a phase)
          have hguard := liftGuard_of_loadingInvariant n hn P
            (a :: rest.map Prod.fst) phase k first i hupper hk'
            (by simp [i]) hfamily' halign hfirst
          have hstep := loadingInvariant_after_instructionResult_cons n hn P
            (rest.map Prod.fst) phase k first i hupper hk' hfirst
            hfamily' hnodup' halign
          have hsubstep := lowerSupportSubset_after_instructionResult_tail n hn P
            (rest.map Prod.fst) phase first i hsub' hfamily' halign
          have hkrest : (k + 1) + rest.length ≤ n := by
            simpa [List.length_cons, Nat.add_assoc, Nat.add_comm,
              Nat.add_left_comm] using hk
          have htail := ih
            (P := instructionResult n hn first P i)
            (phase := phase + i.sourceTurns)
            (k := k + 1)
            (first := false)
            hstep.1 hkrest (by simp) hstep.2.1 hstep.2.2 hsubstep
          have hcons :
              GuardedPlan n hn first P
                (i :: annotateMarked n (phase + i.sourceTurns) rest)
                htail.choose :=
            GuardedPlan.cons hguard htail.choose_spec.1
          refine ⟨htail.choose, ?_, htail.choose_spec.2⟩
          simpa [annotateMarked, i, q] using hcons

theorem guardedPlan_checkedPlan
    (n : Nat) (hn : 1 < n)
    (first : Bool) (P R : Placement n)
    (plan : List (LoadInstruction n))
    (hguarded : GuardedPlan n hn first P plan R) :
    CheckedPlan n hn first P plan R := by
  induction hguarded with
  | nil => exact .nil _ _
  | @cons first P R i rest hguard hrest ih =>
      exact .cons
        (run_instructionWord_of_guard_eq_result n hn P first i hguard)
        ih

theorem guardedPlan_run_emitPlanAux
    (n : Nat) (hn : 1 < n)
    (first : Bool) (P R : Placement n)
    (plan : List (LoadInstruction n))
    (hguarded : GuardedPlan n hn first P plan R) :
    run n hn P (emitPlanAux first plan) = some R := by
  exact checkedPlan_run_emitPlanAux n hn first P R plan
    (guardedPlan_checkedPlan n hn first P R plan hguarded)

theorem run_emitPlanAux_annotateMarked_of_loadingInvariant
    (n : Nat) (hn : 1 < n)
    (phase k : Nat) (first : Bool) (P : Placement n)
    (xs : List (Fin n × Bool))
    (hupper : upperSupportBelow P k)
    (hk : k + xs.length ≤ n)
    (hfirst : first = true → k = 0)
    (hfamily : lowerFamily P (xs.map Prod.fst) phase)
    (hnodup : (xs.map Prod.fst).Nodup) :
    ∃ R, run n hn P
      (emitPlanAux first (annotateMarked n phase xs)) = some R := by
  rcases guardedPlan_annotateMarked n hn phase k first P xs
      hupper hk hfirst hfamily hnodup with ⟨R, hguarded⟩
  exact ⟨R, guardedPlan_run_emitPlanAux n hn first P R
    (annotateMarked n phase xs) hguarded⟩

theorem run_orderedPartition_interleavedPlan
    (n : Nat) (hn : 1 < n) (p : OrderedPartition n) :
    ∃ R, run n hn (seed n)
      (emitPlan (interleavedPlan n p.blocks)) = some R := by
  let xs := markedReverseBlocks p.blocks
  have hlen : xs.length = n := by
    dsimp [xs]
    rw [markedReverseBlocks_length n p.blocks]
    exact orderedPartition_blockAtomCount p
  have hupper : upperSupportBelow (seed n) 0 :=
    seed_upperSupportBelow_zero n
  have hfamily : lowerFamily (seed n) (xs.map Prod.fst) 0 :=
    seed_lowerFamily n (by omega) (xs.map Prod.fst)
  have hnodup : (xs.map Prod.fst).Nodup := by
    dsimp [xs]
    exact markedReverseBlocks_atom_nodup p
  have hk : 0 + xs.length ≤ n := by omega
  rcases run_emitPlanAux_annotateMarked_of_loadingInvariant n hn 0 0 true
      (seed n) xs hupper hk (by simp) hfamily hnodup with ⟨R, hR⟩
  refine ⟨R, ?_⟩
  simpa [emitPlan, interleavedPlan, xs] using hR

theorem run_orderedPartition_interleavedPlan_with_bound
    (n : Nat) (hn : 1 < n) (p : OrderedPartition n) :
    ∃ R, run n hn (seed n)
        (emitPlan (interleavedPlan n p.blocks)) = some R ∧
      (emitPlan (interleavedPlan n p.blocks)).length ≤
        n * n + 2 * n - p.blockCount - 1 := by
  rcases run_orderedPartition_interleavedPlan n hn p with ⟨R, hrun⟩
  refine ⟨R, hrun, ?_⟩
  exact orderedPartition_interleavedPlan_length_bound p (by omega)

/-!
The strengthened executable certificate shows that the generated word really
empties the lower layer.  This is the dynamic part of the Bell construction;
the exact upper-layer coordinates are intentionally left to the subsequent
canonical-placement theorem.
-/
theorem run_orderedPartition_interleavedPlan_allUpper
    (n : Nat) (hn : 1 < n) (p : OrderedPartition n) :
    ∃ R, run n hn (seed n)
      (emitPlan (interleavedPlan n p.blocks)) = some R ∧
      ∀ a, (R a).1 = true := by
  let xs := markedReverseBlocks p.blocks
  have hlen : xs.length = n := by
    dsimp [xs]
    rw [markedReverseBlocks_length n p.blocks]
    exact orderedPartition_blockAtomCount p
  have hupper : upperSupportBelow (seed n) 0 :=
    seed_upperSupportBelow_zero n
  have hfamily : lowerFamily (seed n) (xs.map Prod.fst) 0 :=
    seed_lowerFamily n (by omega) (xs.map Prod.fst)
  have hnodup : (xs.map Prod.fst).Nodup := by
    dsimp [xs]
    exact markedReverseBlocks_atom_nodup p
  have hsub : lowerSupportSubset (seed n) (xs.map Prod.fst) := by
    intro a _
    dsimp [xs]
    rw [markedReverseBlocks_atoms, flatten_reverse_blocks]
    apply List.mem_reverse.mpr
    exact (p.flatten_perm.mem_iff).2 (List.mem_finRange a)
  have hk : 0 + xs.length ≤ n := by omega
  rcases guardedPlan_annotateMarked_lowerSupport n hn 0 0 true
      (seed n) xs hupper hk (by simp) hfamily hnodup hsub with
    ⟨R, hguarded, hsubFinal⟩
  have hrun := guardedPlan_run_emitPlanAux n hn true (seed n) R
    (annotateMarked n 0 xs) hguarded
  have hupperR : ∀ a, (R a).1 = true := by
    intro a
    cases hlayer : (R a).1 with
    | false =>
        exact (by simpa using hsubFinal a hlayer : False).elim
    | true =>
        simpa using hlayer
  refine ⟨R, ?_⟩
  constructor
  · simpa [emitPlan, interleavedPlan, xs] using hrun
  · exact hupperR

/-!
This packages the executable guarded-run certificate together with the raw
letter budget.  The remaining endpoint theorem must still identify `R` with
the canonical stacked placement, rather than merely proving that its lower
layer is empty.
-/
theorem run_orderedPartition_interleavedPlan_executable
    (n : Nat) (hn : 1 < n) (p : OrderedPartition n) :
    ∃ R, run n hn (seed n)
      (emitPlan (interleavedPlan n p.blocks)) = some R ∧
      (∀ a, (R a).1 = true) ∧
      (emitPlan (interleavedPlan n p.blocks)).length ≤
        n * n + 2 * n - p.blockCount - 1 := by
  rcases run_orderedPartition_interleavedPlan_allUpper n hn p with
    ⟨R, hrun, hupper⟩
  refine ⟨R, hrun, hupper, ?_⟩
  exact orderedPartition_interleavedPlan_length_bound p (by omega)

theorem guardedPlan_run_emitPlan
    (n : Nat) (hn : 1 < n)
    (P R : Placement n)
    (plan : List (LoadInstruction n))
    (hguarded : GuardedPlan n hn true P plan R) :
    run n hn P (emitPlan plan) = some R := by
  exact checkedPlan_run_emitPlan n hn P R plan
    (guardedPlan_checkedPlan n hn true P R plan hguarded)

end RSR2.Parametric
