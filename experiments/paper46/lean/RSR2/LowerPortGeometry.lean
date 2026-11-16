import RSR2.LowerPacketLedger

/-!
# Lower control-port approach and unavoidable rotations

The lower control-letter cost counts `p false`, `d false`, and `v`; it is
not a count of physical visits to the elevator port. This module gives a
geometric lower bound for every successful raw history, without imposing a
loading plan or prohibiting prefusion and whole-packet transfer.

A lower atom outside sites 0 and 1 can first reach these active sites only
through lower rotation. Its remaining forward distance to the active set is
`n - site.val`. Rotations pay this distance at most one unit at a time. A
second potential discharges the same debt when the atom first shares a packet
with a specified different atom: a first collision must also occur at active
ports. Neither potential adds ghost state to the executor or charges a common
rotation separately for different atoms.
-/

namespace RSR2.Parametric

/-- One raw lower rotation, not an atom-travel or elevator-visit count. -/
def lowerRotationCharge (letter : Letter) : Nat :=
  if letter = .p false then 1 else 0

/-- Forward rotation distance to the lower active set `{0,1}`. At an upper
location or a lower active site there is no remaining approach debt. -/
def lowerPortApproachDistance (n : Nat) (P : Placement n) (a : Fin n) : Nat :=
  if (P a).1 = false ∧ 1 < (P a).2.val then n - (P a).2.val else 0

/-- Approach debt of an atom whose packet has not yet met the other atom.
The debt is discharged by a collision as well as by arrival at active ports. -/
def lowerSeparationDistance (n : Nat) (P : Placement n) (a b : Fin n) : Nat :=
  if P a = P b then 0 else lowerPortApproachDistance n P a

/-- One available occupied lower sync port. A successful elevator consumes
this credit; an effective lower fusion cannot replenish it from an empty port. -/
noncomputable def lowerSyncCredit (n : Nat) (hn : 0 < n) (P : Placement n) : Nat := by
  classical
  exact if occupiedAt P false (site0 n hn) then 1 else 0

private theorem syncCredit_le_one (n : Nat) (hn : 0 < n) (P : Placement n) :
    lowerSyncCredit n hn P ≤ 1 := by
  classical
  unfold lowerSyncCredit
  split <;> omega

private theorem upperRotation_lower_occupied (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Site n) :
    occupiedAt (rotate n hn P true) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, rotate, ha]⟩

private theorem upperDefect_lower_occupied (n : Nat) (hn : 1 < n)
    (P : Placement n) (q : Site n) :
    occupiedAt (collapse n hn P true) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem lowerDefect_sync_occupied (n : Nat) (hn : 1 < n)
    (P : Placement n) :
    occupiedAt (collapse n hn P false) false (site0 n (by omega)) ↔
      occupiedAt P false (site0 n (by omega)) ∨ occupiedAt P false (site1 n hn) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · rename_i h
      exact Or.inr ⟨a, h⟩
    · exact Or.inl ⟨a, ha⟩
  · rintro (⟨a, ha⟩ | ⟨a, ha⟩)
    · change P a = (false, site0 n (by omega)) at ha
      exact ⟨a, by simp [packet, collapse, ha, site0, site1, Fin.mk.injEq]⟩
    · change P a = (false, site1 n hn) at ha
      exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem liftPacket_sync_empty (n : Nat) (hn : 0 < n) (P : Placement n) :
    ¬ occupiedAt (liftPacket n hn P) false (site0 n hn) := by
  rintro ⟨a, ha⟩
  unfold packet liftPacket at ha
  split at ha
  · exact Bool.noConfusion (congrArg Prod.fst ha)
  · rename_i h
    exact h ha

/-- One-step readiness budget. Only a lower rotation or a nonfusing lower
defect can replenish the occupied sync-port credit consumed by an elevator. -/
theorem step_lowerSyncCredit_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hstep : step n hn P letter = some Q) :
    lowerSyncCredit n (by omega) Q + (if letter = .v then 1 else 0) ≤
      lowerSyncCredit n (by omega) P + lowerRotationCharge letter +
        lowerNonfusionCharge n hn P letter := by
  classical
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      cases layer with
      | false =>
          have h := syncCredit_le_one n (by omega) (rotate n (by omega) P false)
          simp [lowerRotationCharge, lowerNonfusionCharge]
          omega
      | true =>
          simp [lowerSyncCredit, lowerRotationCharge, lowerNonfusionCharge,
            upperRotation_lower_occupied]
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      cases layer with
      | false =>
          by_cases hzero : occupiedAt P false (site0 n (by omega)) <;>
            by_cases hone : occupiedAt P false (site1 n hn)
          all_goals simp [lowerSyncCredit, lowerRotationCharge, lowerNonfusionCharge,
            lowerFusionCharge, lowerDefect_sync_occupied, hzero, hone]
      | true =>
          simp [lowerSyncCredit, lowerRotationCharge, lowerNonfusionCharge,
            upperDefect_lower_occupied]
  | v =>
      obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      simp [lowerSyncCredit, lowerRotationCharge, lowerNonfusionCharge,
        hg.1, liftPacket_sync_empty]

private theorem approach_rotate_lower (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) :
    lowerPortApproachDistance n P a ≤
      1 + lowerPortApproachDistance n (rotate n (by omega) P false) a := by
  by_cases hactive : (P a).1 = false ∧ 1 < (P a).2.val
  · have hsite := (P a).2.isLt
    unfold lowerPortApproachDistance
    rw [if_pos hactive]
    by_cases hnext : (P a).2.val + 1 < n
    · have hpos : 0 < (P a).2.val := by omega
      simp [rotate, hactive.1, next, hnext, hpos]
      omega
    · have hlast : (P a).2.val + 1 = n := by omega
      simp [rotate, hactive.1, next, hnext]
      omega
  · simp [lowerPortApproachDistance, hactive]

private theorem approach_rotate_upper (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) :
    lowerPortApproachDistance n (rotate n (by omega) P true) a =
      lowerPortApproachDistance n P a := by
  by_cases hl : (P a).1 = true
  · simp [lowerPortApproachDistance, rotate, hl]
  · simp [lowerPortApproachDistance, rotate, hl]

private theorem approach_collapse (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) (a : Fin n) :
    lowerPortApproachDistance n (collapse n hn P layer) a =
      lowerPortApproachDistance n P a := by
  by_cases hloc : P a = (layer, site1 n hn)
  · cases layer <;> simp [lowerPortApproachDistance, collapse, hloc, site0, site1]
  · simp [lowerPortApproachDistance, collapse, hloc]

private theorem approach_liftPacket (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) :
    lowerPortApproachDistance n (liftPacket n (by omega) P) a =
      lowerPortApproachDistance n P a := by
  by_cases hloc : P a = (false, site0 n (by omega))
  · simp [lowerPortApproachDistance, liftPacket, hloc, site0]
  · simp [lowerPortApproachDistance, liftPacket, hloc]

/-- All successful physical steps respect the one-unit rotation budget.
Defects, elevators, and upper rotations cannot pay approach debt. -/
theorem step_lowerPortApproachDistance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (a : Fin n)
    (hstep : step n hn P letter = some Q) :
    lowerPortApproachDistance n P a ≤
      lowerRotationCharge letter + lowerPortApproachDistance n Q a := by
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      cases layer with
      | false => simpa [lowerRotationCharge] using approach_rotate_lower n hn P a
      | true => simp [lowerRotationCharge, approach_rotate_upper n hn]
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      simp [lowerRotationCharge, approach_collapse]
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      simp [lowerRotationCharge, approach_liftPacket n hn]

/-- A first fusion of two previously separate packets can discharge the
separation debt only when the distinguished atom is already at an active
port. This also covers upper fusions and legal whole-packet elevators. -/
theorem step_lowerSeparationDistance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (a b : Fin n)
    (hstep : step n hn P letter = some Q) :
    lowerSeparationDistance n P a b ≤
      lowerRotationCharge letter + lowerSeparationDistance n Q a b := by
  by_cases hbefore : P a = P b
  · simp [lowerSeparationDistance, hbefore]
  · by_cases hafter : Q a = Q b
    · have hzero : lowerPortApproachDistance n P a = 0 := by
        cases letter with
        | p layer =>
            have hQ : rotate n (by omega) P layer = Q := by
              simpa only [step_p, Option.some.injEq] using hstep
            subst Q
            exact False.elim (hbefore ((rotate_samePacket_iff n hn P layer a b).mp hafter))
        | d layer =>
            have hQ : collapse n hn P layer = Q := by
              simpa only [step_d, Option.some.injEq] using hstep
            subst Q
            rcases (collapse_samePacket_iff n hn P layer a b).mp hafter with h | h | h
            · exact False.elim (hbefore h)
            · cases layer <;> simp [lowerPortApproachDistance, h.1, site0]
            · cases layer <;> simp [lowerPortApproachDistance, h.1, site1]
        | v =>
            exact False.elim (hbefore
              ((successful_lift_preserves_partition n hn P Q hstep a b).mp hafter))
      simp [lowerSeparationDistance, hbefore, hafter, hzero]
    · simpa [lowerSeparationDistance, hbefore, hafter] using
        step_lowerPortApproachDistance n hn P Q letter a hstep

private theorem run_rotation_potential (n : Nat) (hn : 1 < n)
    (potential : Placement n → Nat)
    (hstep : ∀ P Q letter, step n hn P letter = some Q →
      potential P ≤ lowerRotationCharge letter + potential Q)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) :
    potential P ≤ lowerRotationCount word + potential Q := by
  induction word generalizing P with
  | nil =>
      have h : P = Q := by simpa only [run, Option.some.injEq] using hrun
      simp [h, lowerRotationCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          have htail := ih R ht
          have hone := hstep P R letter hs
          have hcount : lowerRotationCount (letter :: rest) =
              lowerRotationCount rest + lowerRotationCharge letter := by
            simp only [lowerRotationCount, lowerRotationCharge, List.count_cons, beq_iff_eq]
          omega

theorem run_lowerPortApproachDistance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (a : Fin n)
    (hrun : run n hn P word = some Q) :
    lowerPortApproachDistance n P a ≤
      lowerRotationCount word + lowerPortApproachDistance n Q a :=
  run_rotation_potential n hn (fun R => lowerPortApproachDistance n R a)
    (fun _ _ _ hs => step_lowerPortApproachDistance n hn _ _ _ a hs) P Q word hrun

theorem run_lowerSeparationDistance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (a b : Fin n)
    (hrun : run n hn P word = some Q) :
    lowerSeparationDistance n P a b ≤
      lowerRotationCount word + lowerSeparationDistance n Q a b :=
  run_rotation_potential n hn (fun R => lowerSeparationDistance n R a b)
    (fun _ _ _ hs => step_lowerSeparationDistance n hn _ _ _ a b hs) P Q word hrun

/-- Any source atom initially outside the active ports must pay its full
forward approach distance before it can appear on the upper layer. -/
theorem singleton_run_upperAtom_rotation_lower_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (a : Fin n) (ha : 1 < a.val)
    (hrun : run n hn (seed n) word = some Q) (hupper : (Q a).1 = true) :
    n - a.val ≤ lowerRotationCount word := by
  have h := run_lowerPortApproachDistance n hn (seed n) Q word a hrun
  simpa [lowerPortApproachDistance, seed, ha, hupper] using h

/-- The same geometric price is necessary for merging that atom with any
other atom, irrespective of the endpoint's layer or physical phase. -/
theorem singleton_run_mergedAtom_rotation_lower_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (a b : Fin n) (ha : 1 < a.val)
    (hab : a ≠ b) (hrun : run n hn (seed n) word = some Q)
    (hmerged : samePacket Q a b) :
    n - a.val ≤ lowerRotationCount word := by
  have h := run_lowerSeparationDistance n hn (seed n) Q word a b hrun
  have hseed : seed n a ≠ seed n b := by
    intro h
    exact hab (congrArg Prod.snd h)
  have hsame : Q a = Q b := hmerged
  simpa [lowerSeparationDistance, hseed, hsame, hab,
    lowerPortApproachDistance, seed, ha] using h

/-- An explicit endpoint family: atom 2 shares a packet with atom 0. This
includes complete coalescence on either layer, with arbitrary literal phase.
The lower bound quantifies over every successful five-letter execution. -/
theorem singleton_run_atomTwo_merged_rotation_lower_bound (n : Nat) (hn : 2 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hmerged : samePacket Q ⟨2, hn⟩ (site0 n (by omega))) :
    n - 2 ≤ lowerRotationCount word := by
  exact singleton_run_mergedAtom_rotation_lower_bound n (by omega) Q word
    ⟨2, hn⟩ (site0 n (by omega)) (by simp) (by simp [site0, Fin.mk.injEq]) hrun hmerged

/-- The requested preparation bound on the actual ledger path. `N0` counts
all nonfusing lower defects, so it cannot weaken the rotation lower bound. -/
theorem singleton_ledger_atomTwo_merged_preparation_lower_bound
    (n : Nat) (hn : 2 < n) (Q : Placement n) (word : List Letter)
    (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n (by omega) (seed n) word =
      some (Q, fusions, nonfusions))
    (hmerged : samePacket Q ⟨2, hn⟩ (site0 n (by omega))) :
    n - 2 ≤ lowerRotationCount word + nonfusions := by
  have hplain : run n (by omega) (seed n) word = some Q := by
    have hp := runWithLowerPacketLedger_project n (by omega) (seed n) word
    rw [hrun] at hp
    exact hp.symm
  have h := singleton_run_atomTwo_merged_rotation_lower_bound n hn Q word hplain hmerged
  omega

/-- Raw-word interface: the preparation bound uses counters extracted from
the very same successful history, not a selected or normalized strategy. -/
theorem singleton_run_atomTwo_merged_preparation_lower_bound
    (n : Nat) (hn : 2 < n) (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hmerged : samePacket Q ⟨2, hn⟩ (site0 n (by omega))) :
    ∃ fusions nonfusions,
      runWithLowerPacketLedger n (by omega) (seed n) word =
        some (Q, fusions, nonfusions) ∧
      n - 2 ≤ lowerRotationCount word + nonfusions := by
  obtain ⟨f, z, hledger, _⟩ := run_exists_lowerPacketLedger n (by omega)
    (seed n) Q word hrun
  exact ⟨f, z, hledger, singleton_ledger_atomTwo_merged_preparation_lower_bound
    n hn Q word f z hledger hmerged⟩

/-- No sequence of upper operations or productive lower fusions refills an
empty sync port for free. The bound uses the exact nonfusion counter on the
same successful guarded history, from an arbitrary initial placement. -/
theorem runWithLowerPacketLedger_refill_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn P word = some (Q, fusions, nonfusions)) :
    lowerSyncCredit n (by omega) Q + verticalCount word ≤
      lowerSyncCredit n (by omega) P + lowerRotationCount word + nonfusions := by
  induction word generalizing P fusions nonfusions with
  | nil =>
      have h : P = Q ∧ 0 = fusions ∧ 0 = nonfusions := by
        simpa only [runWithLowerPacketLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      simp [h.1, ← h.2.2, verticalCount, lowerRotationCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithLowerPacketLedger, hs] at hrun
      | some P' =>
          cases ht : runWithLowerPacketLedger n hn P' rest with
          | none => simp [runWithLowerPacketLedger, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, f, z⟩
              have h : R = Q ∧ lowerFusionCharge n hn P letter + f = fusions ∧
                  lowerNonfusionCharge n hn P letter + z = nonfusions := by
                simpa only [runWithLowerPacketLedger, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have htail := ih P' f z (by simpa [h.1] using ht)
              have hone := step_lowerSyncCredit_bound n hn P P' letter hs
              have hv : verticalCount (letter :: rest) = verticalCount rest +
                  (if letter = .v then 1 else 0) := by
                simp only [verticalCount, List.count_cons, beq_iff_eq]
              have hp : lowerRotationCount (letter :: rest) =
                  lowerRotationCount rest + lowerRotationCharge letter := by
                simp only [lowerRotationCount, lowerRotationCharge, List.count_cons, beq_iff_eq]
              omega

theorem singleton_ledger_refill_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n hn (seed n) word = some (Q, fusions, nonfusions)) :
    lowerSyncCredit n (by omega) Q + verticalCount word ≤
      1 + lowerRotationCount word + nonfusions := by
  have h := runWithLowerPacketLedger_refill_bound n hn (seed n) Q word
    fusions nonfusions hrun
  have hseed : lowerSyncCredit n (by omega) (seed n) = 1 := by
    classical
    have hocc : occupiedAt (seed n) false (site0 n (by omega)) := ⟨site0 n (by omega), rfl⟩
    simp [lowerSyncCredit, hocc]
  simpa [hseed] using h

/-- Atom 2 need only be non-singleton or upper at the endpoint; no literal
phase or intermediate physical schedule is prescribed. -/
theorem singleton_run_atomTwo_serviced_rotation_lower_bound (n : Nat) (hn : 2 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hserviced : (Q ⟨2, hn⟩).1 = true ∨
      ∃ b : Fin n, b ≠ ⟨2, hn⟩ ∧ samePacket Q ⟨2, hn⟩ b) :
    n - 2 ≤ lowerRotationCount word := by
  rcases hserviced with hupper | ⟨b, hne, hmerged⟩
  · exact singleton_run_upperAtom_rotation_lower_bound n (by omega) Q word
      ⟨2, hn⟩ (by simp) hrun hupper
  · exact singleton_run_mergedAtom_rotation_lower_bound n (by omega) Q word
      ⟨2, hn⟩ b (by simp) hne.symm hrun hmerged

/-- Geometric excess over productive lower packet reduction, for all
histories whose endpoint services atom 2. -/
theorem singleton_run_atomTwo_serviced_control_lower_bound (n : Nat) (hn : 2 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hserviced : (Q ⟨2, hn⟩).1 = true ∨
      ∃ b : Fin n, b ≠ ⟨2, hn⟩ ∧ samePacket Q ⟨2, hn⟩ b) :
    2 * n - 2 ≤ lowerPortCost word + lowerPacketCount Q := by
  have hrot := singleton_run_atomTwo_serviced_rotation_lower_bound n hn Q word hrun hserviced
  obtain ⟨_, z, _, _, _, hport⟩ := singleton_run_exists_lowerPacketLedger n (by omega)
    Q word hrun
  omega

/-- If no atoms remain below then the lower packet count is zero, regardless
of the upper partition or coordinates. -/
theorem lowerPacketCount_eq_zero_of_allUpper (Q : Placement n)
    (hupper : ∀ a, (Q a).1 = true) : lowerPacketCount Q = 0 := by
  classical
  unfold lowerPacketCount
  apply List.countP_eq_zero.mpr
  intro q _ hq
  have ho : occupiedAt Q false q := of_decide_eq_true hq
  obtain ⟨a, ha⟩ := ho
  exact Bool.noConfusion ((hupper a).symm.trans (congrArg Prod.fst ha))

/-- Every all-upper allocation, with any endpoint partition and phase, has
this geometric lower control-letter cost. It is not an unlayered partition
diameter bound: some of these partitions also admit lower-ring endpoints. -/
theorem singleton_run_allUpper_control_lower_bound (n : Nat) (hn : 2 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hupper : ∀ a, (Q a).1 = true) :
    n - 2 ≤ lowerRotationCount word ∧
      2 * n - 2 ≤ lowerPortCost word ∧ 2 * n - 2 ≤ word.length := by
  have hserviced : (Q ⟨2, hn⟩).1 = true ∨
      ∃ b : Fin n, b ≠ ⟨2, hn⟩ ∧ samePacket Q ⟨2, hn⟩ b := Or.inl (hupper _)
  have hrot := singleton_run_atomTwo_serviced_rotation_lower_bound n hn Q word hrun hserviced
  have hcontrol := singleton_run_atomTwo_serviced_control_lower_bound n hn Q word hrun hserviced
  have hzero := lowerPacketCount_eq_zero_of_allUpper Q hupper
  have hlength := lowerPortCost_le_length word
  exact ⟨hrot, by omega, by omega⟩

/-- Approach and refill debts share rotations, so their unconditional joint
budget is a maximum, not a sum. Both use the same observed raw history. -/
theorem singleton_ledger_serviced_preparation_max_lower_bound
    (n : Nat) (hn : 2 < n) (Q : Placement n) (word : List Letter)
    (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger n (by omega) (seed n) word =
      some (Q, fusions, nonfusions))
    (hserviced : (Q ⟨2, hn⟩).1 = true ∨
      ∃ b : Fin n, b ≠ ⟨2, hn⟩ ∧ samePacket Q ⟨2, hn⟩ b) :
    max (n - 2) (verticalCount word + lowerSyncCredit n (by omega) Q - 1) ≤
      lowerRotationCount word + nonfusions := by
  have hplain : run n (by omega) (seed n) word = some Q := by
    have hp := runWithLowerPacketLedger_project n (by omega) (seed n) word
    rw [hrun] at hp
    exact hp.symm
  have hrot := singleton_run_atomTwo_serviced_rotation_lower_bound n hn Q word hplain hserviced
  have hfill := singleton_ledger_refill_bound n (by omega) Q word fusions nonfusions hrun
  exact Nat.max_le.mpr ⟨by omega, by omega⟩

theorem singleton_run_serviced_port_max_lower_bound
    (n : Nat) (hn : 2 < n) (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (hserviced : (Q ⟨2, hn⟩).1 = true ∨
      ∃ b : Fin n, b ≠ ⟨2, hn⟩ ∧ samePacket Q ⟨2, hn⟩ b) :
    n - lowerPacketCount Q +
      max (n - 2) (verticalCount word + lowerSyncCredit n (by omega) Q - 1) ≤
        lowerPortCost word := by
  obtain ⟨f, z, hl, hpackets, _, hport⟩ := singleton_run_exists_lowerPacketLedger n (by omega)
    Q word hrun
  have hmax := singleton_ledger_serviced_preparation_max_lower_bound n hn Q word f z hl hserviced
  omega

end RSR2.Parametric
