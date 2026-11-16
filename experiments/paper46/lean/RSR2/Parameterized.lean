import RSR2.Model

/-!
# Parameterized RSR-2 semantics

Atoms and sites are indexed by `Fin n`. A state assigns each atom to one of
the two layers and one of the `n` sites. Packets are fibers of this assignment,
so coverage and disjointness are intrinsic to the representation. The elevator
letter has partial (`Option`) semantics.
-/

namespace RSR2.Parametric

abbrev Site (n : Nat) := Fin n
abbrev Layer := Bool
abbrev Location (n : Nat) := Layer × Site n
abbrev Placement (n : Nat) := Fin n → Location n

inductive Letter where
  | p (layer : Layer)
  | d (layer : Layer)
  | v
  deriving DecidableEq, Repr

def site0 (n : Nat) (hn : 0 < n) : Site n := ⟨0, hn⟩

def site1 (n : Nat) (hn : 1 < n) : Site n := ⟨1, hn⟩

def next (n : Nat) (hn : 0 < n) (q : Site n) : Site n :=
  if h : q.val + 1 < n then ⟨q.val + 1, h⟩ else ⟨0, hn⟩

def nextMany (n : Nat) (hn : 0 < n) (q : Site n) : Nat → Site n
  | 0 => q
  | k + 1 => nextMany n hn (next n hn q) k

theorem next_val (n : Nat) (hn : 0 < n) (q : Site n) :
    (next n hn q).val = (q.val + 1) % n := by
  unfold next
  split
  · rename_i h
    simp [h, Nat.mod_eq_of_lt h]
  · rename_i h
    have heq : q.val + 1 = n := by omega
    simp [h, heq]

theorem nextMany_val (n : Nat) (hn : 0 < n) (q : Site n) (k : Nat) :
    (nextMany n hn q k).val = (q.val + k) % n := by
  induction k generalizing q with
  | zero => simp [nextMany, Nat.mod_eq_of_lt q.isLt]
  | succ k ih =>
      simp only [nextMany, ih, next_val]
      rw [Nat.mod_add_mod]
      congr 1
      omega

def packet (P : Placement n) (layer : Layer) (site : Site n) : Fin n → Prop :=
  fun a => P a = (layer, site)

def occupiedAt (P : Placement n) (layer : Layer) (site : Site n) : Prop :=
  ∃ a, packet P layer site a

def rotate (n : Nat) (hn : 0 < n) (P : Placement n) (layer : Layer) : Placement n :=
  fun a => if (P a).1 = layer then (layer, next n hn (P a).2) else P a

def rotateMany (n : Nat) (hn : 0 < n) (P : Placement n) (layer : Layer) :
    Nat → Placement n
  | 0 => P
  | k + 1 => rotateMany n hn (rotate n hn P layer) layer k

theorem rotateMany_apply (n : Nat) (hn : 0 < n) (P : Placement n)
    (layer : Layer) (k : Nat) (a : Fin n) :
    rotateMany n hn P layer k a =
      if (P a).1 = layer then (layer, nextMany n hn (P a).2 k) else P a := by
  induction k generalizing P with
  | zero =>
      cases hloc : P a with
      | mk l q =>
          by_cases h : l = layer <;> simp [rotateMany, nextMany, h, hloc]
  | succ k ih =>
      simp only [rotateMany, ih, rotate]
      by_cases h : (P a).1 = layer
      · simp [h, nextMany]
      · simp [h]

theorem next_injective (n : Nat) (hn : 0 < n) :
    Function.Injective (next n hn) := by
  intro a b h
  apply Fin.ext
  have hv := congrArg Fin.val h
  unfold next at hv
  by_cases ha : a.val + 1 < n <;> by_cases hb : b.val + 1 < n
  all_goals simp [ha, hb] at hv <;> omega

def collapse (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) : Placement n :=
  fun a => if P a = (layer, site1 n hn) then (layer, site0 n (by omega)) else P a

def liftGuard (n : Nat) (hn : 0 < n) (P : Placement n) : Prop :=
  occupiedAt P false (site0 n hn) ∧ ¬ occupiedAt P true (site0 n hn)

def liftPacket (n : Nat) (hn : 0 < n) (P : Placement n) : Placement n :=
  fun a =>
    if P a = (false, site0 n hn) then (true, site0 n hn) else P a

noncomputable def step (n : Nat) (hn : 1 < n) (P : Placement n) :
    Letter → Option (Placement n) := by
  classical
  intro letter
  cases letter with
  | p layer => exact some (rotate n (by omega) P layer)
  | d layer => exact some (collapse n hn P layer)
  | v => exact if liftGuard n (by omega) P then some (liftPacket n (by omega) P) else none

noncomputable def run (n : Nat) (hn : 1 < n) : Placement n → List Letter →
    Option (Placement n)
  | P, [] => some P
  | P, letter :: rest =>
      (step n hn P letter).bind (fun P' => run n hn P' rest)

def seed (n : Nat) : Placement n := fun a => (false, a)

def samePacket (P : Placement n) (a b : Fin n) : Prop := P a = P b

def pWord (layer : Layer) (count : Nat) : List Letter :=
  List.replicate count (.p layer)

def dWord (layer : Layer) : List Letter := [.d layer]

def liftWord : List Letter := [.v]

theorem run_nil (n : Nat) (hn : 1 < n) (P : Placement n) :
    run n hn P [] = some P := rfl

theorem run_append (n : Nat) (hn : 1 < n) (P : Placement n)
    (xs ys : List Letter) :
    run n hn P (xs ++ ys) = (run n hn P xs).bind (fun P' => run n hn P' ys) := by
  induction xs generalizing P with
  | nil => rfl
  | cons x xs ih => simp [run, ih, Option.bind_assoc]

theorem step_p (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) :
    step n hn P (.p layer) = some (rotate n (by omega) P layer) := by
  simp [step]

theorem step_d (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) :
    step n hn P (.d layer) = some (collapse n hn P layer) := by
  simp [step]

theorem step_v_eq_some_iff (n : Nat) (hn : 1 < n) (P Q : Placement n) :
    step n hn P .v = some Q ↔
      liftGuard n (by omega) P ∧ Q = liftPacket n (by omega) P := by
  classical
  by_cases hg : liftGuard n (by omega) P
  · simp [step, hg, eq_comm]
  · simp [step, hg]

theorem packet_ext (P : Placement n) (l : Location n) (a : Fin n) :
    packet P l.1 l.2 a ↔ P a = l := Iff.rfl

theorem packets_at_distinct_locations_disjoint (P : Placement n)
    (l₁ l₂ : Location n) (hne : l₁ ≠ l₂) :
    ∀ a, packet P l₁.1 l₁.2 a → packet P l₂.1 l₂.2 a → False := by
  intro a h₁ h₂
  exact hne (h₁.symm.trans h₂)

theorem atom_assignment_total (P : Placement n) :
    ∀ a : Fin n, (∃ loc : Location n, P a = loc) ∧
      (∀ loc₁ loc₂ : Location n, P a = loc₁ → P a = loc₂ → loc₁ = loc₂) := by
  intro a
  exact ⟨⟨P a, rfl⟩, fun _ _ h₁ h₂ => h₁.symm.trans h₂⟩

theorem next_zero (n : Nat) (hn : 1 < n) :
    next n (by omega) (site0 n (by omega)) = site1 n hn := by
  simp [next, site0, site1, hn]

theorem liftGuard_iff (n : Nat) (hn : 1 < n) (P : Placement n) :
    liftGuard n (by omega) P ↔
      occupiedAt P false (site0 n (by omega)) ∧
      ¬ occupiedAt P true (site0 n (by omega)) := Iff.rfl

theorem liftPacket_preserves_partition (n : Nat) (hn : 1 < n)
    (P : Placement n) (hguard : liftGuard n (by omega) P) (a b : Fin n) :
    samePacket (liftPacket n (by omega) P) a b ↔ samePacket P a b := by
  let z : Site n := site0 n (by omega)
  change (if P a = (false, z) then (true, z) else P a) =
      (if P b = (false, z) then (true, z) else P b) ↔ P a = P b
  by_cases ha : P a = (false, z)
  · by_cases hb : P b = (false, z)
    · simp [ha, hb]
    · rw [if_pos ha, if_neg hb]
      constructor
      · intro h
        have hUpper : P b = (true, z) := h.symm
        exact False.elim (hguard.2 ⟨b, hUpper⟩)
      · intro h
        exact False.elim (hb (h.symm.trans ha))
  · by_cases hb : P b = (false, z)
    · rw [if_neg ha, if_pos hb]
      constructor
      · intro h
        have hUpper : P a = (true, z) := h
        exact False.elim (hguard.2 ⟨a, hUpper⟩)
      · intro h
        exact False.elim (ha (h.trans hb))
    · simp [ha, hb]

theorem successful_lift_has_source_and_empty_target (n : Nat) (hn : 1 < n)
    (P P' : Placement n) (h : step n hn P .v = some P') :
    liftGuard n (by omega) P ∧ P' = liftPacket n (by omega) P := by
  exact (step_v_eq_some_iff n hn P P').mp h

theorem successful_lift_preserves_partition (n : Nat) (hn : 1 < n)
    (P P' : Placement n) (h : step n hn P .v = some P') (a b : Fin n) :
    samePacket P' a b ↔ samePacket P a b := by
  obtain ⟨hg, rfl⟩ := successful_lift_has_source_and_empty_target n hn P P' h
  exact liftPacket_preserves_partition n hn P hg a b

theorem rotate_samePacket_iff (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) (a b : Fin n) :
    samePacket (rotate n (by omega) P layer) a b ↔ samePacket P a b := by
  unfold samePacket rotate
  constructor
  · intro h
    by_cases ha : (P a).1 = layer
    · by_cases hb : (P b).1 = layer
      · simp [ha, hb] at h
        have hsites := next_injective n (by omega) h
        apply Prod.ext
        · exact ha.trans hb.symm
        · exact hsites
      · simp [ha, hb] at h
        exact False.elim (hb (congrArg Prod.fst h).symm)
    · by_cases hb : (P b).1 = layer
      · simp [ha, hb] at h
        exact False.elim (ha (congrArg Prod.fst h))
      · simpa [ha, hb] using h
  · intro h
    rw [h]

theorem collapse_preserves_existing_packet_eq (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) (a b : Fin n) :
    samePacket P a b → samePacket (collapse n hn P layer) a b := by
  intro h
  unfold samePacket collapse
  rw [h]

theorem collapse_samePacket_iff (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) (a b : Fin n) :
    samePacket (collapse n hn P layer) a b ↔
      samePacket P a b ∨
      (P a = (layer, site0 n (by omega)) ∧ P b = (layer, site1 n hn)) ∨
      (P a = (layer, site1 n hn) ∧ P b = (layer, site0 n (by omega))) := by
  unfold samePacket collapse
  by_cases ha : P a = (layer, site1 n hn)
  · by_cases hb : P b = (layer, site1 n hn)
    · simp [ha, hb]
    · by_cases hd : P b = (layer, site0 n (by omega))
      · simp [ha, hb, hd]
      · simp [ha, hb, hd, eq_comm]
  · by_cases hb : P b = (layer, site1 n hn)
    · by_cases hd : P a = (layer, site0 n (by omega))
      · simp [ha, hb, hd]
      · simp [ha, hb, hd]
    · simp [ha, hb]

end RSR2.Parametric
