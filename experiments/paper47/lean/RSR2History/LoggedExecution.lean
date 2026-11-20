import RSR2.Parameterized
import Mathlib.Data.Finset.Basic
import Mathlib.Tactic

/-!
Arbitrary-size effective-event observation on the original guarded executor.
An event is observed only after the underlying step succeeds. The wrapper
does not turn a failed elevator into a silent step.
-/

namespace RSR2History

open RSR2.Parametric

def packetAt (P : Placement n) (layer : Layer) (q : Fin n) : Finset (Fin n) :=
  Finset.univ.filter (fun a => P a = (layer, q))

@[simp] theorem mem_packetAt (P : Placement n) (layer : Layer)
    (q a : Fin n) : a ∈ packetAt P layer q ↔ P a = (layer, q) := by
  simp [packetAt]

theorem packetAt_nonempty (P : Placement n) (layer : Layer) (q : Fin n) :
    (packetAt P layer q).Nonempty ↔ occupiedAt P layer q := by
  simp [Finset.Nonempty, occupiedAt, packet]

inductive EffectiveEvent (n : Nat) where
  | fusion (layer : Layer) (left right result : Finset (Fin n))
  | transfer (packet : Finset (Fin n))
  deriving DecidableEq

/-- Pre-step data, used by `runLogged` only after a successful guarded step. -/
noncomputable def emittedEvents (n : Nat) (hn : 1 < n) (P : Placement n) :
    Letter → List (EffectiveEvent n) := by
  classical
  intro letter
  cases letter with
  | p _ => exact []
  | d layer =>
      exact if occupiedAt P layer (site0 n (by omega)) ∧
          occupiedAt P layer (site1 n hn) then
        [.fusion layer (packetAt P layer (site0 n (by omega)))
          (packetAt P layer (site1 n hn))
          (packetAt P layer (site0 n (by omega)) ∪ packetAt P layer (site1 n hn))]
      else []
  | v => exact [.transfer (packetAt P false (site0 n (by omega)))]

noncomputable def runLogged (n : Nat) (hn : 1 < n) :
    Placement n → List Letter → Option (Placement n × List (EffectiveEvent n))
  | P, [] => some (P, [])
  | P, letter :: rest =>
      (step n hn P letter).bind (fun Q =>
        (runLogged n hn Q rest).map (fun result =>
          (result.1, emittedEvents n hn P letter ++ result.2)))

/-- Exact erasure, including failure, to the pre-existing guarded `run`. -/
theorem runLogged_project (n : Nat) (hn : 1 < n)
    (P : Placement n) (word : List Letter) :
    (runLogged n hn P word).map Prod.fst = run n hn P word := by
  induction word generalizing P with
  | nil => rfl
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, run, hs]
      | some Q =>
          simpa [runLogged, run, hs, Option.map_map, Function.comp_def] using ih Q

theorem runLogged_exists_of_run (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {word : List Letter}
    (h : run n hn P word = some Q) :
    ∃ events, runLogged n hn P word = some (Q, events) := by
  have hp := runLogged_project n hn P word
  rw [h] at hp
  cases hl : runLogged n hn P word with
  | none => simp [hl] at hp
  | some result =>
      obtain ⟨R, events⟩ := result
      have he : R = Q := by simpa [hl] using hp
      exact ⟨events, by simp_all⟩

theorem runLogged_append (n : Nat) (hn : 1 < n)
    (P : Placement n) (u v : List Letter) :
    runLogged n hn P (u ++ v) =
      (runLogged n hn P u).bind (fun first =>
        (runLogged n hn first.1 v).map (fun last =>
          (last.1, first.2 ++ last.2))) := by
  induction u generalizing P with
  | nil =>
      cases h : runLogged n hn P v <;> simp [runLogged, h]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs]
      | some Q =>
          simp only [List.cons_append, runLogged, hs, Option.bind_some, ih]
          cases hu : runLogged n hn Q rest with
          | none => simp
          | some first =>
              simp [Function.comp_def, List.append_assoc]

def SilentStep (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) : Prop :=
  step n hn P letter = some Q ∧ emittedEvents n hn P letter = []

def SilentReachable (n : Nat) (hn : 1 < n) (P Q : Placement n) : Prop :=
  ∃ word, runLogged n hn P word = some (Q, [])

theorem SilentReachable.refl (n : Nat) (hn : 1 < n) (P : Placement n) :
    SilentReachable n hn P P := ⟨[], rfl⟩

theorem SilentReachable.trans {n : Nat} {hn : 1 < n} {P Q R : Placement n}
    (hPQ : SilentReachable n hn P Q) (hQR : SilentReachable n hn Q R) :
    SilentReachable n hn P R := by
  obtain ⟨u, hu⟩ := hPQ
  obtain ⟨v, hv⟩ := hQR
  exact ⟨u ++ v, by simp [runLogged_append, hu, hv]⟩

theorem SilentStep.reachable {n : Nat} {hn : 1 < n} {P Q : Placement n}
    {letter : Letter} (h : SilentStep n hn P Q letter) :
    SilentReachable n hn P Q := by
  exact ⟨[letter], by simp [runLogged, h.1, h.2]⟩

theorem silentStep_p (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) :
    SilentStep n hn P (rotate n (by omega) P layer) (.p layer) := by
  exact ⟨step_p n hn P layer, rfl⟩

theorem silentStep_d_iff (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) :
    SilentStep n hn P (collapse n hn P layer) (.d layer) ↔
      ¬ (occupiedAt P layer (site0 n (by omega)) ∧
        occupiedAt P layer (site1 n hn)) := by
  classical
  simp [SilentStep, step_d, emittedEvents]

theorem not_silentStep_v (n : Nat) (hn : 1 < n) (P Q : Placement n) :
    ¬ SilentStep n hn P Q .v := by
  simp [SilentStep, emittedEvents]

end RSR2History
