import RSR2.LowerPacketLedger

/-!
# Upper receiver vacancy budget

Every successful elevator consumes the empty upper synchronization port.
Only an upper rotation can replenish that vacancy; upper defects can fill
the receiver but cannot empty an occupied receiver. The budget is proved
directly for the existing guarded `step` and `run`, from any placement and
without restricting prefusion, whole-packet transfers, or scheduling.
-/

namespace RSR2.Parametric

/-- One credit exactly when the upper receiver at site 0 is empty. -/
noncomputable def upperPortVacancy (n : Nat) (hn : 0 < n) (P : Placement n) : Nat := by
  classical
  exact if occupiedAt P true (site0 n hn) then 0 else 1

theorem upperPortVacancy_le_one (n : Nat) (hn : 0 < n) (P : Placement n) :
    upperPortVacancy n hn P ≤ 1 := by
  classical
  unfold upperPortVacancy
  split <;> omega

private theorem lowerRotation_upper_occupied (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Site n) :
    occupiedAt (rotate n hn P false) true q ↔ occupiedAt P true q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (true, q) at ha
    exact ⟨a, by simp [packet, rotate, ha]⟩

private theorem lowerDefect_upper_occupied (n : Nat) (hn : 1 < n)
    (P : Placement n) (q : Site n) :
    occupiedAt (collapse n hn P false) true q ↔ occupiedAt P true q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (true, q) at ha
    exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem upperDefect_preserves_receiver (n : Nat) (hn : 1 < n)
    (P : Placement n) (h : occupiedAt P true (site0 n (by omega))) :
    occupiedAt (collapse n hn P true) true (site0 n (by omega)) := by
  obtain ⟨a, ha⟩ := h
  change P a = (true, site0 n (by omega)) at ha
  exact ⟨a, by simp [packet, collapse, ha, site0, site1, Fin.mk.injEq]⟩

private theorem liftPacket_receiver_occupied (n : Nat) (hn : 0 < n)
    (P : Placement n) (h : occupiedAt P false (site0 n hn)) :
    occupiedAt (liftPacket n hn P) true (site0 n hn) := by
  obtain ⟨a, ha⟩ := h
  change P a = (false, site0 n hn) at ha
  exact ⟨a, by simp [packet, liftPacket, ha]⟩

/-- A legal elevator spends one vacancy credit. Only `p true` can create
a new credit; in particular `d true` cannot clear an occupied receiver. -/
theorem step_upperPortVacancy_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hstep : step n hn P letter = some Q) :
    upperPortVacancy n (by omega) Q + (if letter = .v then 1 else 0) ≤
      upperPortVacancy n (by omega) P + (if letter = .p true then 1 else 0) := by
  classical
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      cases layer with
      | false => simp [upperPortVacancy, lowerRotation_upper_occupied]
      | true =>
          have h := upperPortVacancy_le_one n (by omega) (rotate n (by omega) P true)
          simp
          omega
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      cases layer with
      | false => simp [upperPortVacancy, lowerDefect_upper_occupied]
      | true =>
          by_cases hzero : occupiedAt P true (site0 n (by omega))
          · have hafter := upperDefect_preserves_receiver n hn P hzero
            simp [upperPortVacancy, hzero, hafter]
          · have h := upperPortVacancy_le_one n (by omega) (collapse n hn P true)
            simpa [upperPortVacancy, hzero] using h
  | v =>
      obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      have hafter := liftPacket_receiver_occupied n (by omega) P hg.1
      simp [upperPortVacancy, hg.2, hafter]

/-- Telescoping receiver budget for the very same successful guarded history.
The final vacancy is retained, so this applies to arbitrary endpoint phases. -/
theorem run_upperPortVacancy_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) :
    upperPortVacancy n (by omega) Q + verticalCount word ≤
      upperPortVacancy n (by omega) P + rawUpperRotationCount word := by
  classical
  induction word generalizing P with
  | nil =>
      have h : P = Q := by simpa only [run, Option.some.injEq] using hrun
      simp [h, verticalCount, rawUpperRotationCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some P' =>
          have ht : run n hn P' rest = some Q := by simpa [run, hs] using hrun
          have htail := ih P' ht
          have hone := step_upperPortVacancy_bound n hn P P' letter hs
          have hv : verticalCount (letter :: rest) = verticalCount rest +
              (if letter = .v then 1 else 0) := by
            simp only [verticalCount, List.count_cons, beq_iff_eq]
          have hp : rawUpperRotationCount (letter :: rest) = rawUpperRotationCount rest +
              (if letter = .p true then 1 else 0) := by
            simp only [rawUpperRotationCount, List.count_cons, beq_iff_eq]
          omega

@[simp] theorem seed_upperPortVacancy (n : Nat) (hn : 0 < n) :
    upperPortVacancy n hn (seed n) = 1 := by
  have h : ¬ occupiedAt (seed n) true (site0 n hn) := by
    rintro ⟨a, ha⟩
    exact Bool.noConfusion (congrArg Prod.fst ha)
  simp [upperPortVacancy, h]

/-- The initially empty upper ring supplies one free receiver vacancy. -/
theorem singleton_run_upperPortVacancy_bound (n : Nat) (hn : 1 < n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some Q) :
    upperPortVacancy n (by omega) Q + verticalCount word ≤
      1 + rawUpperRotationCount word := by
  simpa using run_upperPortVacancy_bound n hn (seed n) Q word hrun

end RSR2.Parametric
