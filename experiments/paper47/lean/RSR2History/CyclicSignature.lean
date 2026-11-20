import RSR2History.LoggedExecution
import RSR2History.SlotRouting
import Mathlib.Data.List.OfFn

namespace RSR2History

open RSR2.Parametric

def layerSlots (P : Placement n) (layer : Layer) : List (Finset (Fin n)) :=
  List.ofFn (packetAt P layer)

@[simp] theorem layerSlots_length (P : Placement n) (layer : Layer) :
    (layerSlots P layer).length = n := by simp [layerSlots]

@[simp] theorem layerSlots_getElem (P : Placement n) (layer : Layer) (q : Nat)
    (hq : q < (layerSlots P layer).length) :
    (layerSlots P layer)[q] = packetAt P layer ⟨q, by simpa using hq⟩ := by
  simp [layerSlots]

def cyclicSignature (P : Placement n) (layer : Layer) : List (Finset (Fin n)) :=
  stripEmpty ∅ (layerSlots P layer)

def SameCyclicSignatures (P Q : Placement n) : Prop :=
  ∀ layer, (cyclicSignature P layer).IsRotated (cyclicSignature Q layer)

theorem layerSlots_ext {P Q : Placement n}
    (h : ∀ layer, layerSlots P layer = layerSlots Q layer) : P = Q := by
  funext a
  have hm : a ∈ packetAt P (P a).1 (P a).2 := by simp
  have hp := congrArg (fun xs : List (Finset (Fin n)) =>
    xs[(P a).2.val]?) (h (P a).1)
  simp [layerSlots] at hp
  rw [hp] at hm
  exact (mem_packetAt _ _ _ _).mp hm |>.symm

private theorem shift_cancel (n : Nat) (_hn : 0 < n) (c x y : Nat)
    (hc : c ≤ n) (hx : x < n) (hy : y < n) :
    (x + (n-c)) % n = y ↔ x = (y+c) % n := by
  by_cases hxc : x < c
  · rw [Nat.mod_eq_of_lt (show x + (n-c) < n by omega)]
    by_cases hyc : y+c < n
    · rw [Nat.mod_eq_of_lt hyc]; omega
    · have hsplit : y+c = n+(y+c-n) := by omega
      rw [hsplit]
      simp only [Nat.add_mod_left,
        Nat.mod_eq_of_lt (show y+c-n < n by omega)]
      omega
  · have hsplit : x+(n-c) = n+(x-c) := by omega
    rw [hsplit]
    simp only [Nat.add_mod_left,
      Nat.mod_eq_of_lt (show x-c < n by omega)]
    by_cases hyc : y+c < n
    · rw [Nat.mod_eq_of_lt hyc]; omega
    · have hsplit : y+c = n+(y+c-n) := by omega
      rw [hsplit]
      simp only [Nat.add_mod_left,
        Nat.mod_eq_of_lt (show y+c-n < n by omega)]
      omega

theorem layerSlots_rotateMany (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (cut : Nat) (hc : cut ≤ n) :
    layerSlots (rotateMany n (by omega) P layer (n-cut)) layer =
      (layerSlots P layer).rotate cut := by
  apply List.ext_getElem
  · simp
  · intro q hq hq'
    simp only [List.getElem_rotate, layerSlots_length, layerSlots_getElem]
    apply Finset.ext
    intro a
    simp only [mem_packetAt, rotateMany_apply]
    by_cases hl : (P a).1 = layer
    · simp only [hl, if_pos, Prod.mk.injEq, true_and]
      rw [Fin.ext_iff, nextMany_val]
      have hb : q < n := by simpa using hq
      rw [shift_cancel n (by omega) cut (P a).2.val q hc (P a).2.isLt hb]
      exact ⟨fun h => Prod.ext hl (Fin.ext h),
        fun h => congrArg (fun l => l.2.val) h⟩
    · simp only [hl, if_false]
      constructor <;> intro h <;> exact False.elim (hl (congrArg Prod.fst h))

theorem layerSlots_rotateMany_other (n : Nat) (hn : 0 < n) (P : Placement n)
    (layer other : Layer) (hne : other ≠ layer) (count : Nat) :
    layerSlots (rotateMany n hn P layer count) other = layerSlots P other := by
  unfold layerSlots
  congr 1
  funext q
  apply Finset.ext
  intro a
  simp only [mem_packetAt, rotateMany_apply]
  by_cases hl : (P a).1 = layer
  · simp only [hl, if_pos]
    constructor <;> intro h
    · exact False.elim (hne (congrArg Prod.fst h).symm)
    · exact False.elim (hne ((congrArg Prod.fst h).symm.trans hl))
  · simp [hl]

theorem silent_rotateMany (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (count : Nat) :
    SilentReachable n hn P (rotateMany n (by omega) P layer count) := by
  induction count generalizing P with
  | zero => exact .refl n hn P
  | succ count ih =>
      exact (silentStep_p n hn P layer).reachable.trans (ih _)

end RSR2History
