import Mathlib.Tactic

namespace FusionLogCompression

/-- Linear coordinates start immediately after the zero-flow edge. The final
index is that edge; only indices strictly before it are executed. -/
def scheduledGap (g target flow : ℕ → ℕ) (stage i : ℕ) : ℕ :=
  if i < stage then target i
  else if i = stage then g i + if stage = 0 then 0 else flow (stage - 1)
  else g i

/-- State after moving `amount` holes from one gap to its successor. -/
def transferGap (g : ℕ → ℕ) (i amount : ℕ) : ℕ → ℕ :=
  Function.update (Function.update g i (g i - amount)) (i + 1) (g (i + 1) + amount)

theorem scheduledGap_initial (g target flow : ℕ → ℕ) :
    scheduledGap g target flow 0 = g := by
  funext i
  simp [scheduledGap]

/-- Conservation makes the next scheduled donor capable of paying its flow. -/
theorem scheduledGap_donor (g target flow : ℕ → ℕ) (i : ℕ)
    (balance : flow i + target i =
      g i + if i = 0 then 0 else flow (i - 1)) :
    scheduledGap g target flow i i = target i + flow i := by
  simp only [scheduledGap, lt_self_iff_false, ↓reduceIte]
  omega

theorem scheduledGap_capacity (g target flow : ℕ → ℕ) (i : ℕ)
    (balance : flow i + target i =
      g i + if i = 0 then 0 else flow (i - 1)) :
    flow i ≤ scheduledGap g target flow i i := by
  rw [scheduledGap_donor g target flow i balance]
  omega

/-- One legal transfer advances the linear schedule exactly one stage. -/
theorem scheduledGap_transfer (g target flow : ℕ → ℕ) (i : ℕ)
    (balance : flow i + target i =
      g i + if i = 0 then 0 else flow (i - 1)) :
    transferGap (scheduledGap g target flow i) i (flow i) =
      scheduledGap g target flow (i + 1) := by
  funext j
  by_cases hji : j = i
  · subst j
    simp [transferGap, scheduledGap]
    omega
  · by_cases hnext : j = i + 1
    · subst j
      simp [transferGap, scheduledGap]
    · have hlt : j < i ↔ j < i + 1 := by omega
      have hnot : ¬j = i := hji
      simp [transferGap, scheduledGap, hji, hnext, hlt]

/-- At the zero edge, conservation also finishes the one unprocessed gap. -/
theorem scheduledGap_final (g target flow : ℕ → ℕ) (r : ℕ)
    (hr : 1 ≤ r) (zero : flow (r - 1) = 0)
    (balance : flow (r - 1) + target (r - 1) =
      g (r - 1) + if r - 1 = 0 then 0 else flow (r - 1 - 1)) :
    ∀ i < r, scheduledGap g target flow (r - 1) i = target i := by
  intro i hi
  by_cases hlast : i = r - 1
  · subst i
    simp only [scheduledGap, lt_self_iff_false, ↓reduceIte]
    omega
  · have hlt : i < r - 1 := by omega
    simp [scheduledGap, hlt]

/-- The total transfer amount of the executed edges is bounded independently
of the number of holes' repeated crossings. -/
theorem scheduledGap_transfer_budget (flow : ℕ → ℕ) (r h : ℕ)
    (bounded : ∀ i < r - 1, flow i ≤ h) :
    ∑ i ∈ Finset.range (r - 1), flow i ≤ h * (r - 1) := by
  calc
    ∑ i ∈ Finset.range (r - 1), flow i ≤
        ∑ _i ∈ Finset.range (r - 1), h := by
          apply Finset.sum_le_sum
          intro i hi
          exact bounded i (Finset.mem_range.mp hi)
    _ = h * (r - 1) := by simp [Nat.mul_comm]

/-- The concrete arithmetic state after executing the first `stage` edges of
the linear schedule. -/
def scheduledState (g : ℕ → ℕ) (flow : ℕ → ℕ) : ℕ → (ℕ → ℕ)
  | 0 => g
  | stage + 1 =>
      transferGap (scheduledState g flow stage) stage (flow stage)

theorem scheduledState_eq_scheduledGap (g target flow : ℕ → ℕ)
    (balance : ∀ i, flow i + target i =
      g i + if i = 0 then 0 else flow (i - 1)) :
    ∀ stage, scheduledState g flow stage =
      scheduledGap g target flow stage := by
  intro stage
  induction stage with
  | zero =>
      exact (scheduledGap_initial g target flow).symm
  | succ stage ih =>
      rw [scheduledState]
      rw [ih]
      exact scheduledGap_transfer g target flow stage (balance stage)

/-- Executing the `r-1` linear transfers reaches the target gap vector. -/
theorem scheduledState_final (g target flow : ℕ → ℕ) (r : ℕ)
    (hr : 1 ≤ r) (zero : flow (r - 1) = 0)
    (balance : ∀ i, flow i + target i =
      g i + if i = 0 then 0 else flow (i - 1)) :
    ∀ i < r, scheduledState g flow (r - 1) i = target i := by
  intro i hi
  rw [scheduledState_eq_scheduledGap g target flow balance]
  exact scheduledGap_final g target flow r hr zero (balance (r - 1)) i hi

end FusionLogCompression
