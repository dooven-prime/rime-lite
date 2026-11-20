import RSR2History.CombTerminalRouting

/-! Terminal routing from distributed source gaps. A common cyclic cut
keeps names fixed and makes source coordinates dominate the target. The
initial cursor and final physical rotation are included in the cost. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

def gapIntermediatePosition (source target : Nat → Nat) (i j : Nat) : Nat :=
  if j < i then target j else source j

/-- A fixed named common cut with source positions dominating target
positions. The initial cursor is the actual phase of the source cut. -/
structure GapTerminalCoordinates (n g l : Nat) [NeZero n]
    (P Q : Placement n) where
  size : n = g+l+1
  roots_positive : 1 ≤ l
  root : Fin n → Nat
  root_bound : ∀ a, root a ≤ l
  root_nonempty : ∀ j, j ≤ l → ∃ a, root a = j
  source : Nat → Nat
  source_zero : source 0 = 0
  source_strict : ∀ i j, i < j → j ≤ l → source i < source j
  source_lt : ∀ j, j ≤ l → source j < n
  source_fits : ∀ j, j ≤ l → source j ≤ g+j
  target : Nat → Nat
  target_zero : target 0 = 0
  target_strict : ∀ i j, i < j → j ≤ l → target i < target j
  target_lt : ∀ j, j ≤ l → target j < n
  target_fits : ∀ j, j ≤ l → target j ≤ source j
  phase : ZMod n
  initialCursor : Fin n
  initial_alignment : initialCursor.val = 0 ∨ source 1 ≤ initialCursor.val
  start : phaseShift P true (initialCursor.val : ZMod n) =
    combCoordinatePlacement root source
  finish : Q = phaseShift (combCoordinatePlacement root target) true phase

namespace GapTerminalCoordinates
variable {g l : Nat} {P Q : Placement n}

/-- Total unsigned coordinate displacement at the common dominating cut. -/
def displacement (h : GapTerminalCoordinates n g l P Q) : Nat :=
  ∑ j ∈ Finset.range (l+1), (h.source j-h.target j)

private def displacementFrom (h : GapTerminalCoordinates n g l P Q)
    (i count : Nat) : Nat :=
  ∑ j ∈ Finset.range count, (h.source (i+j)-h.target (i+j))

private theorem displacementFrom_succ (h : GapTerminalCoordinates n g l P Q)
    (i count : Nat) :
    h.displacementFrom i (count+1) = h.source i-h.target i +
      h.displacementFrom (i+1) count := by
  unfold displacementFrom
  rw [Finset.sum_range_succ']
  simp only [Nat.add_zero]
  rw [Nat.add_comm]
  congr 1
  apply Finset.sum_congr rfl
  intro j hj
  rw [show i+(j+1) = i+1+j by omega]

private theorem displacementFrom_start (h : GapTerminalCoordinates n g l P Q) :
    h.displacementFrom 1 l = h.displacement := by
  unfold displacement
  rw [Finset.sum_range_succ']
  simp only [h.source_zero, h.target_zero, Nat.sub_self, Nat.add_zero]
  unfold displacementFrom
  apply Finset.sum_congr rfl
  intro j hj
  rw [Nat.add_comm 1 j]

private theorem target_ge (h : GapTerminalCoordinates n g l P Q)
    (j : Nat) (hj : j ≤ l) : j ≤ h.target j := by
  induction j with
  | zero => omega
  | succ j ih =>
      have hp := h.target_strict j (j+1) (by omega) hj
      have hi := ih (by omega)
      omega

private theorem intermediate_lt (h : GapTerminalCoordinates n g l P Q)
    (i : Nat) (a : Fin n) :
    gapIntermediatePosition h.source h.target i (h.root a) < n := by
  unfold gapIntermediatePosition
  split
  · exact h.target_lt _ (h.root_bound a)
  · exact h.source_lt _ (h.root_bound a)

private theorem intermediate_source
    (h : GapTerminalCoordinates n g l P Q) {i : Nat}
    (hil : i ≤ l) :
    (packetAt (combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i))
      true (zsite ((h.source i : Nat) : ZMod n))).Nonempty := by
  obtain ⟨a, ha⟩ := h.root_nonempty i hil
  refine ⟨a, (mem_packetAt _ _ _ _).mpr ?_⟩
  simp [combCoordinatePlacement, gapIntermediatePosition, ha]

private theorem intermediate_holes
    (h : GapTerminalCoordinates n g l P Q) {i : Nat}
    (hil : i ≤ l) :
    ∀ q : Nat, h.target i ≤ q → q < h.source i →
      packetAt (combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i))
        true (zsite (q : ZMod n)) = ∅ := by
  intro q hq hqx
  apply Finset.eq_empty_iff_forall_notMem.mpr
  intro a ha
  have he := congrArg Prod.snd ((mem_packetAt _ _ _ _).mp ha)
  change zsite (gapIntermediatePosition h.source h.target i (h.root a) : ZMod n) =
    zsite (q : ZMod n) at he
  have hez := congrArg Fin.val he
  have hqn : q < n := by have := h.source_lt i hil; omega
  simp only [zsite, ZMod.val_natCast,
    Nat.mod_eq_of_lt (h.intermediate_lt i a), Nat.mod_eq_of_lt hqn] at hez
  unfold gapIntermediatePosition at hez
  split at hez
  · have hp := h.target_strict (h.root a) i (by assumption) hil
    omega
  · have hle : h.source i ≤ h.source (h.root a) := by
      by_cases heq : i = h.root a
      · rw [heq]
      · exact (h.source_strict i (h.root a) (by omega) (h.root_bound a)).le
    omega

private theorem intermediate_move
    (h : GapTerminalCoordinates n g l P Q) {i : Nat}
    (hil : i ≤ l) (hmove : h.target i < h.source i) :
    relocateAt (combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i))
      true ((h.source i : Nat) : ZMod n) (h.target i : ZMod n) =
    combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target (i+1)) := by
  funext a
  have hxn : h.source i < n := h.source_lt i hil
  by_cases he : h.root a = i
  · simp [relocateAt, combCoordinatePlacement, gapIntermediatePosition, he]
  · have hne : combCoordinatePlacement h.root
        (gapIntermediatePosition h.source h.target i) a ≠ (true, zsite ((h.source i : Nat) : ZMod n)) := by
      intro hp
      have hval := congrArg (fun loc : Layer × Fin n => loc.2.val) hp
      change (zsite (gapIntermediatePosition h.source h.target i (h.root a) : ZMod n)).val =
        (zsite ((h.source i : Nat) : ZMod n)).val at hval
      simp only [zsite, ZMod.val_natCast,
        Nat.mod_eq_of_lt (h.intermediate_lt i a), Nat.mod_eq_of_lt hxn] at hval
      unfold gapIntermediatePosition at hval
      split at hval
      · have hl := h.target_strict (h.root a) i (by assumption) hil
        omega
      · have hl := h.source_strict i (h.root a) (by omega) (h.root_bound a)
        omega
    change (if combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i) a =
        (true, zsite ((h.source i : Nat) : ZMod n)) then _ else _) = _
    rw [if_neg hne]
    have hpos : gapIntermediatePosition h.source h.target i (h.root a) =
        gapIntermediatePosition h.source h.target (i+1) (h.root a) := by
      unfold gapIntermediatePosition
      split <;> split <;> omega
    exact congrArg (fun x : Nat => (true, zsite (x : ZMod n))) hpos

private theorem intermediate_skip
    (h : GapTerminalCoordinates n g l P Q) {i : Nat}
    (heq : h.target i = h.source i) :
    combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i) =
    combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target (i+1)) := by
  funext a
  simp only [combCoordinatePlacement]
  have hpos : gapIntermediatePosition h.source h.target i (h.root a) =
      gapIntermediatePosition h.source h.target (i+1) (h.root a) := by
    unfold gapIntermediatePosition
    by_cases hlt : h.root a < i
    · simp [hlt, show h.root a < i+1 by omega]
    · by_cases he : h.root a = i
      · simp [he, heq]
      · simp [hlt, show ¬ h.root a < i+1 by omega]
  rw [hpos]

private theorem route_from_displacement
    (h : GapTerminalCoordinates n g l P Q) (hn : 1 < n)
    (count i a₀ : Nat) (hi : 1 ≤ i) (hend : i+count = l+1)
    (ha₀ : a₀ < i) (R : Placement n) (cursor : Fin n)
    (hc : a₀ ≤ cursor.val)
    (hnorm : phaseShift R true (cursor.val : ZMod n) =
      combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i)) :
    ∃ (S : Placement n) (cf : Fin n) (word : List Letter) (a : Nat),
      runLogged n hn R word = some (S,[]) ∧
      phaseShift S true (cf.val : ZMod n) = combCoordinatePlacement h.root h.target ∧
      a ≤ count ∧ a₀+a ≤ cf.val ∧
      word.length + cf.val ≤ cursor.val + a*n + h.displacementFrom i count := by
  induction count generalizing i a₀ R cursor with
  | zero =>
      have he : combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target i) =
          combCoordinatePlacement h.root h.target := by
        funext atom
        have hb := h.root_bound atom
        simp [combCoordinatePlacement, gapIntermediatePosition, show h.root atom < i by omega]
      exact ⟨R,cursor,[],0,rfl,hnorm.trans he,by omega,by omega,by simp [displacementFrom]⟩
  | succ count ih =>
      have hil : i ≤ l := by omega
      have hfit := h.target_fits i hil
      by_cases hmove : h.target i < h.source i
      · have hy : 0 < h.target i := (by have := h.target_ge i hil; omega)
        have hxn : h.source i < n := h.source_lt i hil
        obtain ⟨S,u,hu,hS,hlen⟩ := comb_phaseFreeSlide hn R cursor hy hmove hxn
          (by rw [hnorm]; exact h.intermediate_source hil)
          (by rw [hnorm]; exact h.intermediate_holes hil)
        rw [hnorm, h.intermediate_move hil hmove] at hS
        let next : Fin n := ⟨h.target i, h.target_lt i hil⟩
        obtain ⟨T,cf,v,a,hv,hT,hac,hacursor,hvlen⟩ := ih (i+1) (a₀+1)
          (by omega) (by omega) (by omega) S next
          (by have := h.target_ge i hil; dsimp [next]; omega) hS
        refine ⟨T,cf,u++v,a+1,?_,hT,by omega,by omega,?_⟩
        · simp [runLogged_append, hu, hv]
        · have hw : cursorWinding cursor.val (h.source i-1) ≤ 1 := by
            unfold cursorWinding
            split <;> omega
          have hp := Nat.mul_le_mul_left n hw
          change v.length+cf.val ≤ h.target i+a*n+h.displacementFrom (i+1) count at hvlen
          simp only [List.length_append]
          rw [h.displacementFrom_succ]
          nlinarith
      · have heq : h.target i = h.source i := by omega
        obtain ⟨S,cf,u,a,hu,hs,ha,hca,hl⟩ :=
          ih (i+1) a₀ (by omega) (by omega) (by omega) R cursor hc
            (hnorm.trans (h.intermediate_skip heq))
        refine ⟨S,cf,u,a,hu,hs,by omega,hca,?_⟩
        simpa only [h.displacementFrom_succ, heq, Nat.sub_self, Nat.zero_add] using hl


private theorem initial_frame (h : GapTerminalCoordinates n g l P Q) :
    phaseShift P true (h.initialCursor.val : ZMod n) =
      combCoordinatePlacement h.root (gapIntermediatePosition h.source h.target 1) := by
  rw [h.start]
  funext a
  by_cases ha : h.root a = 0
  · simp [combCoordinatePlacement, gapIntermediatePosition, ha,
      h.source_zero, h.target_zero]
  · simp [combCoordinatePlacement, gapIntermediatePosition, show ¬h.root a < 1 by omega]

/-- Preserve displacement debts rather than replacing each by the maximum
number of holes. The common cut still carries its actual initial cursor. -/
theorem route_to_target_frame_displacement
    (h : GapTerminalCoordinates n g l P Q) (hn : 1 < n) :
    ∃ (R : Placement n) (cf : Fin n) (word : List Letter),
      runLogged n hn P word = some (R, []) ∧
      phaseShift R true (cf.val : ZMod n) = combCoordinatePlacement h.root h.target ∧
      word.length ≤ l*(n-1)+h.displacement := by
  have hnorm := h.initial_frame
  have hn0 : n-1+1=n := by omega
  rcases h.initial_alignment with hzero | halign
  · obtain ⟨R,cf,u,a,hu,hR,ha,hca,hlen⟩ :=
      h.route_from_displacement hn l 1 0 (by omega) (by omega) (by omega)
        P h.initialCursor (by omega) hnorm
    rw [h.displacementFrom_start] at hlen
    have hm := Nat.mul_le_mul_right (n-1) ha
    exact ⟨R,cf,u,hu,hR,by nlinarith⟩
  · have hl1 : 1 ≤ l := h.roots_positive
    have fit := h.target_fits 1 hl1
    by_cases hmove : h.target 1 < h.source 1
    · obtain ⟨S,u,hu,hS,huLen⟩ := comb_phaseFreeSlide hn P h.initialCursor
        (by have := h.target_ge 1 hl1; omega) hmove (h.source_lt 1 hl1)
        (by rw [hnorm]; exact h.intermediate_source hl1)
        (by rw [hnorm]; exact h.intermediate_holes hl1)
      rw [hnorm, h.intermediate_move hl1 hmove] at hS
      let next : Fin n := ⟨h.target 1, h.target_lt 1 hl1⟩
      obtain ⟨R,cf,v,a,hv,hR,ha,hca,hvLen⟩ :=
        h.route_from_displacement hn (l-1) 2 1 (by omega) (by omega) (by omega)
          S next (by have := h.target_ge 1 hl1; dsimp [next]; omega) hS
      have hw : cursorWinding h.initialCursor.val (h.source 1-1) = 0 := by
        unfold cursorWinding
        split <;> omega
      rw [hw, Nat.mul_zero, Nat.add_zero] at huLen
      have hd : h.displacement = h.source 1-h.target 1+h.displacementFrom 2 (l-1) := by
        rw [← h.displacementFrom_start]
        have hh := h.displacementFrom_succ 1 (l-1)
        simpa only [show l-1+1=l by omega] using hh
      have hc := h.initialCursor.isLt
      change v.length+cf.val ≤ h.target 1+a*n+h.displacementFrom 2 (l-1) at hvLen
      refine ⟨R,cf,u++v,?_,hR,?_⟩
      · simp [runLogged_append, hu, hv]
      · simp only [List.length_append]
        have ha' : a+1 ≤ l := by omega
        have hm := Nat.mul_le_mul_right (n-1) ha'
        nlinarith
    · have he : h.target 1 = h.source 1 := by omega
      obtain ⟨R,cf,u,a,hu,hR,ha,hca,hlen⟩ :=
        h.route_from_displacement hn (l-1) 2 0 (by omega) (by omega) (by omega)
          P h.initialCursor (by omega) (hnorm.trans (h.intermediate_skip he))
      have hd : h.displacement = h.displacementFrom 2 (l-1) := by
        rw [← h.displacementFrom_start]
        have hh := h.displacementFrom_succ 1 (l-1)
        simpa only [show l-1+1=l by omega, he, Nat.sub_self, Nat.zero_add] using hh
      refine ⟨R,cf,u,hu,hR,?_⟩
      have hc := h.initialCursor.isLt
      have ha' : a+1 ≤ l := by omega
      have hm := Nat.mul_le_mul_right (n-1) ha'
      nlinarith

/-- Actual final-phase restoration with the common-cut displacement total
still visible in the route allowance. -/
theorem terminal_route_displacement
    (h : GapTerminalCoordinates n g l P Q) (hn : 1 < n) :
    ∃ word, runLogged n hn P word = some (Q, []) ∧
      word.length ≤ (l+1)*(n-1)+h.displacement := by
  obtain ⟨R,cf,u,hu,hR,hlen⟩ := h.route_to_target_frame_displacement hn
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
    simp only [List.length_append, pWord, List.length_replicate]
    rw [Nat.add_mul]
    simp only [Nat.one_mul]
    omega

/-- Forgetting individual displacement debts recovers the original rank
budget; all previous route signatures are retained. -/
theorem route_to_target_frame (h : GapTerminalCoordinates n g l P Q) (hn : 1 < n) :
    ∃ (R : Placement n) (cf : Fin n) (word : List Letter),
      runLogged n hn P word = some (R, []) ∧
      phaseShift R true (cf.val : ZMod n) = combCoordinatePlacement h.root h.target ∧
      word.length ≤ l*(n+g-1) := by
  have hd : h.displacement ≤ l*g := by
    rw [← h.displacementFrom_start]
    unfold displacementFrom
    calc
      _ ≤ ∑ j ∈ Finset.range l, g := by
        apply Finset.sum_le_sum
        intro j hj
        have hjl : 1+j ≤ l := by have := Finset.mem_range.mp hj; omega
        have := h.source_fits (1+j) hjl
        have := h.target_ge (1+j) hjl
        omega
      _ = l*g := by simp
  obtain ⟨R,cf,word,hrun,hnorm,hlen⟩ := h.route_to_target_frame_displacement hn
  refine ⟨R,cf,word,hrun,hnorm,?_⟩
  have hn0 : n-1+1=n := by omega
  have hunit : n+g-1=(n-1)+g := by omega
  rw [hunit, Nat.mul_add]
  omega

/-- Rank-sensitive terminal routing for distributed source holes. The
same root map is retained, and the exact literal phase is restored by a
single physical rotation suffix. -/
theorem terminal_route (h : GapTerminalCoordinates n g l P Q) (hn : 1 < n) :
    ∃ word, runLogged n hn P word = some (Q, []) ∧
      word.length ≤ l*(n+g-1)+(n-1) := by
  obtain ⟨R,cf,u,hu,hR,hlen⟩ := h.route_to_target_frame hn
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
    simp only [List.length_append, pWord, List.length_replicate]
    omega

end GapTerminalCoordinates
end RSR2History
