import PaperXL.Core
import Mathlib.Data.Fintype.Fin
import Mathlib.Data.Finset.Card

namespace PaperXL

inductive RawLetter
  | p
  | d
  deriving DecidableEq

structure CircularEnvironment (n m : Nat) where
  hn : 0 < n
  hm_lower : 2 ≤ m
  hm_le : m ≤ n
  defect : Fin n → Fin n
  port0 : Fin n
  port1 : Fin n
  seed : Fin m → Fin n
  ports_ne : port0 ≠ port1
  ports_collide : defect port0 = defect port1
  seed_injective : Function.Injective seed
  defect_fiber : ∀ x y : Fin n, defect x = defect y →
    x = y ∨ (x = port0 ∧ y = port1) ∨ (x = port1 ∧ y = port0)

abbrev EventCode (m : Nat) := Fin m → Fin 3

namespace EventCode

def inLeftParent (e : EventCode m) (i : Fin m) : Prop := e i = 0
def inRightParent (e : EventCode m) (i : Fin m) : Prop := e i = 1
def inNeitherParent (e : EventCode m) (i : Fin m) : Prop := e i = 2

end EventCode

structure CircularLogState (n m : Nat) where
  site : Fin m → Fin n
  events : List (EventCode m)

namespace CircularLogState

theorem ext {n m : Nat} {s t : CircularLogState n m}
    (hsite : s.site = t.site) (hevents : s.events = t.events) : s = t := by
  cases s
  cases t
  simp_all

end CircularLogState

namespace CircularLogState

variable {n m : Nat} (E : CircularEnvironment n m)

def support (s : CircularLogState n m) : Finset (Fin n) :=
  Finset.univ.image s.site

def occupied (s : CircularLogState n m) (q : Fin n) : Bool :=
  decide (q ∈ support s)

def eventCode (s : CircularLogState n m) : EventCode m := fun i =>
  if s.site i = E.port0 then 0 else if s.site i = E.port1 then 1 else 2

def rotate (q : Fin n) : Fin n :=
  ⟨(q.val + 1) % n, Nat.mod_lt _ E.hn⟩

def move (letter : RawLetter) (q : Fin n) : Fin n :=
  match letter with
  | .p => rotate E q
  | .d => E.defect q

def step (s : CircularLogState n m) (letter : RawLetter) :
    CircularLogState n m := by
  let s' : Fin m → Fin n := fun i => move E letter (s.site i)
  match letter with
  | .p => exact ⟨s', s.events⟩
  | .d =>
      if occupied s E.port0 then
        if occupied s E.port1 then
          exact ⟨s', s.events ++ [eventCode E s]⟩
        else exact ⟨s', s.events⟩
      else exact ⟨s', s.events⟩

def seedState : CircularLogState n m := ⟨E.seed, []⟩

def rawSystem : RawSystem (CircularLogState n m) RawLetter :=
  ⟨step E, seedState E⟩

theorem support_map (s : CircularLogState n m) (f : Fin n → Fin n) :
    support ⟨fun i => f (s.site i), s.events⟩ = (support s).image f := by
  classical
  unfold support
  rw [Finset.image_image]
  rfl

theorem rotate_injective : Function.Injective (rotate E) := by
  intro a b hab
  apply Fin.ext
  have hval := congrArg Fin.val hab
  change (a.val + 1) % n = (b.val + 1) % n at hval
  have hn2 : 2 ≤ n := le_trans E.hm_lower E.hm_le
  by_cases ha : a.val + 1 < n
  · have hb : b.val + 1 < n := by
      by_contra hnot
      have hb' : b.val + 1 = n := by omega
      simp [Nat.mod_eq_of_lt ha, hb'] at hval
    simp [Nat.mod_eq_of_lt ha, Nat.mod_eq_of_lt hb] at hval
    omega
  · have ha' : a.val + 1 = n := by omega
    by_cases hb : b.val + 1 < n
    · simp [ha', Nat.mod_eq_of_lt hb] at hval
    · have hb' : b.val + 1 = n := by omega
      omega

theorem defect_image_card_of_both_occupied (s : CircularLogState n m)
    (h0 : E.port0 ∈ support s) (h1 : E.port1 ∈ support s) :
    (Finset.image E.defect (support s)).card = (support s).card - 1 := by
  classical
  let S := support s
  have h01 : E.port0 ∈ S := h0
  have h11 : E.port1 ∈ S := h1
  have hImage : Finset.image E.defect S = Finset.image E.defect (S.erase E.port1) := by
    ext q
    constructor
    · intro hq
      rcases Finset.mem_image.mp hq with ⟨x, hx, rfl⟩
      by_cases hx1 : x = E.port1
      · subst x
        apply Finset.mem_image.mpr
        refine ⟨E.port0, Finset.mem_erase.mpr ⟨E.ports_ne, h01⟩, ?_⟩
        exact E.ports_collide
      · exact Finset.mem_image.mpr ⟨x, Finset.mem_erase.mpr ⟨hx1, hx⟩, rfl⟩
    · intro hq
      rcases Finset.mem_image.mp hq with ⟨x, hx, rfl⟩
      exact Finset.mem_image.mpr ⟨x, (Finset.mem_erase.mp hx).2, rfl⟩
  have hinj : Set.InjOn E.defect (↑(S.erase E.port1)) := by
    intro x hx y hy hxy
    rcases E.defect_fiber x y hxy with h | h | h
    · exact h
    · rcases h with ⟨_, hy1⟩
      exact False.elim ((Finset.mem_erase.mp hy).1 hy1)
    · rcases h with ⟨hx1, _⟩
      exact False.elim ((Finset.mem_erase.mp hx).1 hx1)
  rw [hImage, Finset.card_image_of_injOn hinj, Finset.card_erase_of_mem h11]

theorem support_step_p (s : CircularLogState n m) :
    support (step E s .p) = (support s).image (rotate E) := by
  change support ⟨fun i => rotate E (s.site i), s.events⟩ = _
  exact support_map s (rotate E)

theorem support_step_d (s : CircularLogState n m) :
    support (step E s .d) = (support s).image E.defect := by
  cases h0 : occupied s E.port0 <;> cases h1 : occupied s E.port1
  · simp only [step, h0, h1, move]
    exact support_map s E.defect
  · simp only [step, h0, h1, move]
    exact support_map s E.defect
  · simp only [step, h0, h1, move]
    exact support_map s E.defect
  · simp only [step, h0, h1, move]
    exact support_map s E.defect

theorem support_step_d_card_le (s : CircularLogState n m) :
    (support (step E s .d)).card ≤ (support s).card := by
  rw [support_step_d]
  exact Finset.card_image_le

theorem support_step_d_card_of_logs (s : CircularLogState n m)
    (h0 : occupied s E.port0 = true) (h1 : occupied s E.port1 = true) :
    (support (step E s .d)).card = (support s).card - 1 := by
  have hp0 : E.port0 ∈ support s := by simpa [occupied] using h0
  have hp1 : E.port1 ∈ support s := by simpa [occupied] using h1
  rw [support_step_d]
  exact defect_image_card_of_both_occupied E s hp0 hp1

def budgetInvariant (s : CircularLogState n m) : Prop :=
  s.events.length + (support s).card ≤ m

theorem seed_budgetInvariant : budgetInvariant (seedState E) := by
  classical
  have hcard : (support (seedState E)).card = m := by
    unfold support seedState
    rw [Finset.card_image_of_injective _ E.seed_injective]
    simp
  unfold budgetInvariant
  change 0 + (support (seedState E)).card ≤ m
  rw [hcard]
  omega

theorem step_budgetInvariant (s : CircularLogState n m)
    (h : budgetInvariant s) (letter : RawLetter) :
    budgetInvariant (step E s letter) := by
  cases letter with
  | p =>
      have hcard := support_step_p E s
      unfold budgetInvariant at h ⊢
      rw [hcard]
      rw [Finset.card_image_of_injective _ (rotate_injective E)]
      exact h
  | d =>
      by_cases h0 : occupied s E.port0 = true
      · by_cases h1 : occupied s E.port1 = true
        · have hcard := support_step_d_card_of_logs E s h0 h1
          have hevents :
              (step E s .d).events = s.events ++ [eventCode E s] := by
            simp [step, h0, h1]
          have hpos : 0 < (support s).card := by
            apply Finset.card_pos.mpr
            exact ⟨E.port0, by simpa [occupied] using h0⟩
          unfold budgetInvariant at h ⊢
          rw [hevents, hcard]
          simp only [List.length_append, List.length_singleton]
          omega
        · have hcard := support_step_d_card_le E s
          have hevents : (step E s .d).events = s.events := by
            simp [step, h0, h1]
          unfold budgetInvariant at h ⊢
          rw [hevents]
          exact (Nat.add_le_add_left hcard _).trans h
      · have hcard := support_step_d_card_le E s
        have hevents : (step E s .d).events = s.events := by
          simp [step, h0]
        unfold budgetInvariant at h ⊢
        rw [hevents]
        exact (Nat.add_le_add_left hcard _).trans h

theorem foldl_budgetInvariant (s : CircularLogState n m)
    (h : budgetInvariant s) (w : List RawLetter) :
    budgetInvariant (w.foldl (step E) s) := by
  induction w generalizing s with
  | nil => simpa using h
  | cons a w ih =>
      simp only [List.foldl_cons]
      exact ih _ (step_budgetInvariant E s h a)

theorem run_budgetInvariant (w : List RawLetter) :
    budgetInvariant (RawSystem.run (rawSystem E) w) := by
  exact foldl_budgetInvariant E (seedState E) (seed_budgetInvariant E) w

theorem support_nonempty (s : CircularLogState n m) (hm : 0 < m) :
    (support s).card > 0 := by
  classical
  let i : Fin m := ⟨0, hm⟩
  apply Finset.card_pos.mpr
  exact ⟨s.site i, Finset.mem_image.mpr ⟨i, Finset.mem_univ _, rfl⟩⟩

theorem event_count_lt_atoms (w : List RawLetter) :
    (RawSystem.run (rawSystem E) w).events.length < m := by
  have hb := run_budgetInvariant E w
  have hnemp := support_nonempty (RawSystem.run (rawSystem E) w)
    (Nat.lt_of_lt_of_le (by decide : 0 < 2) E.hm_lower)
  unfold budgetInvariant at hb
  omega

theorem event_count_le_atoms_sub_one (w : List RawLetter) :
    (RawSystem.run (rawSystem E) w).events.length ≤ m - 1 := by
  have h := event_count_lt_atoms E w
  omega

theorem eventCode_at_port0 (s : CircularLogState n m) (i : Fin m)
    (h : s.site i = E.port0) : eventCode E s i = 0 := by
  simp [eventCode, h]

theorem eventCode_at_port1 (s : CircularLogState n m) (i : Fin m)
    (h : s.site i = E.port1) : eventCode E s i = 1 := by
  have hne : s.site i ≠ E.port0 := by
    intro heq
    apply E.ports_ne
    exact heq.symm.trans h
  unfold eventCode
  rw [if_neg hne, if_pos h]

theorem eventCode_elsewhere (s : CircularLogState n m) (i : Fin m)
    (h0 : s.site i ≠ E.port0) (h1 : s.site i ≠ E.port1) :
    eventCode E s i = 2 := by
  simp [eventCode, h0, h1]

theorem step_p_preserves_events (s : CircularLogState n m) :
    (step E s .p).events = s.events := by
  rfl

theorem step_d_logs_iff (s : CircularLogState n m) :
    (step E s .d).events ≠ s.events ↔
      occupied s E.port0 = true ∧ occupied s E.port1 = true := by
  cases h0 : occupied s E.port0 <;>
    cases h1 : occupied s E.port1 <;>
      simp [step, h0, h1]

end CircularLogState

end PaperXL
