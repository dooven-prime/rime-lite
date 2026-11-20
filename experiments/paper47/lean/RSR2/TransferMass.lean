import RSR2.Parameterized

/-!
# Transferred atom mass along arbitrary guarded executions

This observer reuses `step`: it does not add an action or change a failed
elevator into a no-op. A successful `v` is charged the number of atoms in its
source packet immediately before the step. Thus a prefused packet is charged
its whole atom mass, rather than one unit for one elevator letter.

The balance law holds from any placement. From the singleton seed its charge
is exactly the endpoint's upper atom count, or `n` minus its lower atom count.
No source-order, loading-plan, or retention-sufficiency hypothesis is used.
-/

namespace RSR2.Parametric

def upperAtomMass (P : Placement n) : Nat :=
  (List.finRange n).countP (fun a => (P a).1)

def lowerAtomMass (P : Placement n) : Nat :=
  (List.finRange n).countP (fun a => !(P a).1)

def packetAtomMass (P : Placement n) (layer : Layer) (q : Site n) : Nat :=
  (List.finRange n).countP (fun a => decide (P a = (layer, q)))

def transferLetterMass (n : Nat) (hn : 1 < n) (P : Placement n) : Letter → Nat
  | .v => packetAtomMass P false (site0 n (by omega))
  | .p _ | .d _ => 0

/-- Guarded replay with the sum of pre-step elevator packet masses. -/
noncomputable def runWithTransferMass (n : Nat) (hn : 1 < n) :
    Placement n → List Letter → Option (Placement n × Nat)
  | P, [] => some (P, 0)
  | P, letter :: rest =>
      (step n hn P letter).bind (fun P' =>
        (runWithTransferMass n hn P' rest).map (fun result =>
          (result.1, transferLetterMass n hn P letter + result.2)))

theorem upperAtomMass_add_lowerAtomMass (P : Placement n) :
    upperAtomMass P + lowerAtomMass P = n := by
  simpa [upperAtomMass, lowerAtomMass] using
    (List.length_eq_countP_add_countP (fun a : Fin n => (P a).1)
      (l := List.finRange n)).symm

theorem seed_upperAtomMass (n : Nat) : upperAtomMass (seed n) = 0 := by
  simp [upperAtomMass, seed]

private theorem rotate_layer (n : Nat) (hn : 0 < n) (P : Placement n)
    (layer : Layer) (a : Fin n) :
    (rotate n hn P layer a).1 = (P a).1 := by
  unfold rotate
  split
  · rename_i h
    exact h.symm
  · rfl

private theorem collapse_layer (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (a : Fin n) :
    (collapse n hn P layer a).1 = (P a).1 := by
  unfold collapse
  split
  · rename_i h
    exact (congrArg Prod.fst h).symm
  · rfl

private theorem countP_add_of_indicators {α : Type} (xs : List α)
    (p q r : α → Bool)
    (h : ∀ a, (if r a then 1 else 0) =
      (if p a then 1 else 0) + (if q a then 1 else 0)) :
    xs.countP r = xs.countP p + xs.countP q := by
  induction xs with
  | nil => simp
  | cons a xs ih =>
      simp only [List.countP_cons]
      have ha := h a
      omega

theorem liftPacket_upperAtomMass (n : Nat) (hn : 0 < n) (P : Placement n) :
    upperAtomMass (liftPacket n hn P) =
      upperAtomMass P + packetAtomMass P false (site0 n hn) := by
  apply countP_add_of_indicators
  intro a
  by_cases h : P a = (false, site0 n hn)
  · simp [liftPacket, h]
  · simp [liftPacket, h]

/-- Every successful raw letter satisfies the same atom-mass balance. -/
theorem step_transferMass_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (hstep : step n hn P letter = some Q) :
    upperAtomMass P + transferLetterMass n hn P letter = upperAtomMass Q := by
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      simp only [transferLetterMass, Nat.add_zero, upperAtomMass]
      apply List.countP_congr
      intro a _
      rw [rotate_layer]
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      simp only [transferLetterMass, Nat.add_zero, upperAtomMass]
      apply List.countP_congr
      intro a _
      rw [collapse_layer]
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      exact (liftPacket_upperAtomMass n (by omega) P).symm

/-- Forgetting the mass observation gives exactly the existing guarded run. -/
theorem runWithTransferMass_project (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runWithTransferMass n hn P word).map Prod.fst = run n hn P word := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithTransferMass, run, hs]
      | some P' =>
          simpa [runWithTransferMass, run, hs, Option.map_map,
            Function.comp_def] using ih P'

theorem runWithTransferMass_balance (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (mass : Nat)
    (hrun : runWithTransferMass n hn P word = some (Q, mass)) :
    upperAtomMass P + mass = upperAtomMass Q := by
  induction word generalizing P mass with
  | nil =>
      have h : P = Q ∧ 0 = mass := by
        simpa only [runWithTransferMass, Option.some.injEq, Prod.mk.injEq] using hrun
      simp [h.1, ← h.2]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runWithTransferMass, hs] at hrun
      | some P' =>
          cases ht : runWithTransferMass n hn P' rest with
          | none => simp [runWithTransferMass, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, m⟩
              have h : R = Q ∧ transferLetterMass n hn P letter + m = mass := by
                simpa only [runWithTransferMass, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have htail := ih P' m (by simpa [h.1] using ht)
              have hletter := step_transferMass_balance n hn P P' letter hs
              omega

/-- A successful old-style run has a mass-observed run, with no new guard. -/
theorem run_exists_transferMass (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (hrun : run n hn P word = some Q) :
    ∃ mass, runWithTransferMass n hn P word = some (Q, mass) ∧
      upperAtomMass P + mass = upperAtomMass Q := by
  have hproj := runWithTransferMass_project n hn P word
  cases ht : runWithTransferMass n hn P word with
  | none => simp [ht, hrun] at hproj
  | some result =>
      rcases result with ⟨R, m⟩
      have hR : R = Q := by simpa [ht, hrun] using hproj
      subst R
      exact ⟨m, rfl, runWithTransferMass_balance n hn P Q word m ht⟩

/-- Exact singleton-seed history identity, including prefused whole packets. -/
theorem singleton_run_transferMass (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) (mass : Nat)
    (hrun : runWithTransferMass n hn (seed n) word = some (P, mass)) :
    mass = upperAtomMass P ∧ mass = n - lowerAtomMass P := by
  have hbalance := runWithTransferMass_balance n hn (seed n) P word mass hrun
  have htotal := upperAtomMass_add_lowerAtomMass P
  rw [seed_upperAtomMass] at hbalance
  omega

theorem singleton_run_exists_transferMass (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter)
    (hrun : run n hn (seed n) word = some P) :
    ∃ mass, runWithTransferMass n hn (seed n) word = some (P, mass) ∧
      mass = upperAtomMass P ∧ mass = n - lowerAtomMass P := by
  obtain ⟨mass, hm, _⟩ := run_exists_transferMass n hn (seed n) P word hrun
  exact ⟨mass, hm, singleton_run_transferMass n hn P word mass hm⟩

end RSR2.Parametric
