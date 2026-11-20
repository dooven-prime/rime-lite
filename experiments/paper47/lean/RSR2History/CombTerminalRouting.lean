import RSR2History.CombPhaseFreeSlide

/-! A fixed named terminal route out of the cluster of holes released by a
comb.  The roots retain their cyclic order.  A real final rotation, charged
in the word length, restores the prescribed physical phase. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

def combCoordinatePlacement (root : Fin n → Nat) (pos : Nat → Nat) : Placement n :=
  fun a => (true, zsite (pos (root a) : ZMod n))

def combIntermediatePosition (g : Nat) (target : Nat → Nat) (i j : Nat) : Nat :=
  if j < i then target j else g+j

/-- Named root coordinates in the frame anchored at the comb.  `phase` is
the physical phase of the literal target; it is restored by actual letters.
This is a coordinate certificate, not a free reindexing of the root list. -/
structure CombTerminalCoordinates (n g l : Nat) [NeZero n]
    (P Q : Placement n) where
  size : n = g+l+1
  gap_positive : 1 ≤ g
  roots_positive : 1 ≤ l
  root : Fin n → Nat
  root_bound : ∀ a, root a ≤ l
  root_nonempty : ∀ j, j ≤ l → ∃ a, root a = j
  target : Nat → Nat
  target_zero : target 0 = 0
  target_strict : ∀ i j, i < j → j ≤ l → target i < target j
  target_lt : ∀ j, j ≤ l → target j < n
  target_fits : ∀ j, j ≤ l → target j ≤ g+j
  phase : ZMod n
  start : P = combCoordinatePlacement root (fun j => if j = 0 then 0 else g+j)
  finish : Q = phaseShift (combCoordinatePlacement root target) true phase

namespace CombTerminalCoordinates
variable {g l : Nat} {P Q : Placement n}

private theorem target_ge (h : CombTerminalCoordinates n g l P Q)
    (j : Nat) (hj : j ≤ l) : j ≤ h.target j := by
  induction j with
  | zero => omega
  | succ j ih =>
      have hp := h.target_strict j (j+1) (by omega) hj
      have hi := ih (by omega)
      omega

private theorem intermediate_lt (h : CombTerminalCoordinates n g l P Q)
    (i : Nat) (a : Fin n) :
    combIntermediatePosition g h.target i (h.root a) < n := by
  unfold combIntermediatePosition
  split
  · exact h.target_lt _ (h.root_bound a)
  · have := h.root_bound a
    have := h.size
    omega

private theorem intermediate_source
    (h : CombTerminalCoordinates n g l P Q) {i : Nat}
    (hi : 1 ≤ i) (hil : i ≤ l) :
    (packetAt (combCoordinatePlacement h.root (combIntermediatePosition g h.target i))
      true (zsite ((g+i : Nat) : ZMod n))).Nonempty := by
  obtain ⟨a, ha⟩ := h.root_nonempty i hil
  refine ⟨a, (mem_packetAt _ _ _ _).mpr ?_⟩
  simp [combCoordinatePlacement, combIntermediatePosition, ha]

private theorem intermediate_holes
    (h : CombTerminalCoordinates n g l P Q) {i : Nat}
    (hi : 1 ≤ i) (hil : i ≤ l) :
    ∀ q : Nat, h.target i ≤ q → q < g+i →
      packetAt (combCoordinatePlacement h.root (combIntermediatePosition g h.target i))
        true (zsite (q : ZMod n)) = ∅ := by
  intro q hq hqx
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro a ha
  have he := congrArg Prod.snd ((mem_packetAt _ _ _ _).mp ha)
  change zsite (combIntermediatePosition g h.target i (h.root a) : ZMod n) =
    zsite (q : ZMod n) at he
  have hez := congrArg Fin.val he
  have hqn : q < n := by have := h.size; omega
  simp only [zsite, ZMod.val_natCast,
    Nat.mod_eq_of_lt (h.intermediate_lt i a), Nat.mod_eq_of_lt hqn] at hez
  unfold combIntermediatePosition at hez
  split at hez
  · have hp := h.target_strict (h.root a) i (by assumption) hil
    omega
  · omega

private theorem intermediate_move
    (h : CombTerminalCoordinates n g l P Q) {i : Nat}
    (hi : 1 ≤ i) (hil : i ≤ l) (hmove : h.target i < g+i) :
    relocateAt (combCoordinatePlacement h.root (combIntermediatePosition g h.target i))
      true ((g+i : Nat) : ZMod n) (h.target i : ZMod n) =
    combCoordinatePlacement h.root (combIntermediatePosition g h.target (i+1)) := by
  funext a
  have hxn : g+i < n := by have := h.size; omega
  by_cases he : h.root a = i
  · simp [relocateAt, combCoordinatePlacement, combIntermediatePosition, he]
  · have hne : combCoordinatePlacement h.root
        (combIntermediatePosition g h.target i) a ≠ (true, zsite ((g+i : Nat) : ZMod n)) := by
      intro hp
      have hval := congrArg (fun loc : Layer × Fin n => loc.2.val) hp
      change (zsite (combIntermediatePosition g h.target i (h.root a) : ZMod n)).val =
        (zsite ((g+i : Nat) : ZMod n)).val at hval
      simp only [combCoordinatePlacement, zsite, ZMod.val_natCast,
        Nat.mod_eq_of_lt (h.intermediate_lt i a), Nat.mod_eq_of_lt hxn] at hval
      unfold combIntermediatePosition at hval
      split at hval
      · have hl := h.target_strict (h.root a) i (by assumption) hil
        omega
      · omega
    change (if combCoordinatePlacement h.root (combIntermediatePosition g h.target i) a =
        (true, zsite ((g+i : Nat) : ZMod n)) then _ else _) = _
    rw [if_neg hne]
    have hpos : combIntermediatePosition g h.target i (h.root a) =
        combIntermediatePosition g h.target (i+1) (h.root a) := by
      unfold combIntermediatePosition
      split <;> split <;> omega
    exact congrArg (fun x : Nat => (true, zsite (x : ZMod n))) hpos

private theorem intermediate_skip
    (h : CombTerminalCoordinates n g l P Q) {i : Nat}
    (heq : h.target i = g+i) :
    combCoordinatePlacement h.root (combIntermediatePosition g h.target i) =
    combCoordinatePlacement h.root (combIntermediatePosition g h.target (i+1)) := by
  funext a
  simp only [combCoordinatePlacement]
  have hpos : combIntermediatePosition g h.target i (h.root a) =
      combIntermediatePosition g h.target (i+1) (h.root a) := by
    unfold combIntermediatePosition
    by_cases hlt : h.root a < i
    · simp [hlt, show h.root a < i+1 by omega]
    · by_cases he : h.root a = i
      · simp [he, heq]
      · simp [hlt, show ¬ h.root a < i+1 by omega]
  rw [hpos]

private theorem route_from
    (h : CombTerminalCoordinates n g l P Q) (hn : 1 < n)
    (count i a₀ : Nat) (hi : 1 ≤ i) (hend : i+count = l+1)
    (ha₀ : a₀ < i) (R : Placement n) (cursor : Fin n)
    (hc : a₀ ≤ cursor.val)
    (hnorm : phaseShift R true (cursor.val : ZMod n) =
      combCoordinatePlacement h.root (combIntermediatePosition g h.target i)) :
    ∃ (S : Placement n) (cf : Fin n) (word : List Letter) (a : Nat),
      runLogged n hn R word = some (S,[]) ∧
      phaseShift S true (cf.val : ZMod n) = combCoordinatePlacement h.root h.target ∧
      a ≤ count ∧ a₀+a ≤ cf.val ∧
      word.length + cf.val ≤ cursor.val + a*(n+g) := by
  induction count generalizing i a₀ R cursor with
  | zero =>
      have he : combCoordinatePlacement h.root (combIntermediatePosition g h.target i) =
          combCoordinatePlacement h.root h.target := by
        funext atom
        have hb := h.root_bound atom
        simp [combCoordinatePlacement, combIntermediatePosition, show h.root atom < i by omega]
      exact ⟨R,cursor,[],0,rfl,hnorm.trans he,by omega,by omega,by simp⟩
  | succ count ih =>
      have hil : i ≤ l := by omega
      have hfit := h.target_fits i hil
      by_cases hmove : h.target i < g+i
      · have hy : 0 < h.target i := (by have := h.target_ge i hil; omega)
        have hxn : g+i < n := by have := h.size; omega
        obtain ⟨S,u,hu,hS,hlen⟩ := comb_phaseFreeSlide hn R cursor hy hmove hxn
          (by rw [hnorm]; exact h.intermediate_source hi hil)
          (by rw [hnorm]; exact h.intermediate_holes hi hil)
        rw [hnorm, h.intermediate_move hi hil hmove] at hS
        let next : Fin n := ⟨h.target i, h.target_lt i hil⟩
        obtain ⟨T,cf,v,a,hv,hT,hac,hacursor,hvlen⟩ := ih (i+1) (a₀+1)
          (by omega) (by omega) (by omega) S next
          (by have := h.target_ge i hil; dsimp [next]; omega) hS
        refine ⟨T,cf,u++v,a+1,?_,hT,by omega,by omega,?_⟩
        · simp [runLogged_append, hu, hv]
        · have hw : cursorWinding cursor.val (g+i-1) ≤ 1 := by
            unfold cursorWinding
            split <;> omega
          have hd : g+i-h.target i ≤ g := by have := h.target_ge i hil; omega
          have hp := Nat.mul_le_mul_left n hw
          change v.length+cf.val ≤ h.target i+a*(n+g) at hvlen
          simp only [List.length_append]
          nlinarith
      · have heq : h.target i = g+i := by omega
        obtain ⟨S,cf,u,a,hu,hs,ha,hca,hl⟩ :=
          ih (i+1) a₀ (by omega) (by omega) (by omega) R cursor hc
            (hnorm.trans (h.intermediate_skip heq))
        exact ⟨S,cf,u,a,hu,hs,by omega,hca,hl⟩

/-- A silent route preserves every named root and restores the literal
target.  Its cost uses the comb's released holes and one shared final phase,
rather than paying an independent phase for each root. -/
theorem terminal_route (h : CombTerminalCoordinates n g l P Q) (hn : 1 < n) :
    ∃ word, runLogged n hn P word = some (Q,[]) ∧
      word.length ≤ l*(n+g-1)+(n-1) := by
  let zero : Fin n := ⟨0, by omega⟩
  have hstart : phaseShift P true (zero.val : ZMod n) =
      combCoordinatePlacement h.root (combIntermediatePosition g h.target 1) := by
    simp only [zero, Fin.val_zero, Nat.cast_zero, phaseShift_zero, h.start]
    funext a
    by_cases ha : h.root a = 0 <;>
      simp [combCoordinatePlacement, combIntermediatePosition, ha,
        show h.root a < 1 ↔ h.root a = 0 by omega, h.target_zero]
  obtain ⟨R,cf,u,a,hu,hR,ha,hca,hlen⟩ :=
    h.route_from hn l 1 0 (by omega) (by omega) (by omega) P zero (by simp [zero]) hstart
  let amount : ZMod n := (cf.val : ZMod n)+h.phase
  have hv := runLogged_phase hn R true amount
  have hRQ : phaseShift R true amount = Q := by
    change phaseShift R true ((cf.val : ZMod n)+h.phase) = Q
    calc
      _ = phaseShift (phaseShift R true (cf.val : ZMod n)) true h.phase :=
        (phaseShift_add _ _ _ _).symm
      _ = phaseShift (combCoordinatePlacement h.root h.target) true h.phase :=
        congrArg (fun S => phaseShift S true h.phase) hR
      _ = Q := h.finish.symm
  refine ⟨u++pWord true amount.val, ?_, ?_⟩
  · simp [runLogged_append, hu, hv, hRQ]
  · have hphase := ZMod.val_lt amount
    have hh : u.length ≤ a*(n+g-1) := by
      change u.length+cf.val ≤ 0+a*(n+g) at hlen
      have hng : n+g-1+1 = n+g := by omega
      nlinarith
    have ham := Nat.mul_le_mul_right (n+g-1) ha
    simp only [List.length_append, pWord, List.length_replicate]
    omega

end CombTerminalCoordinates
end RSR2History
