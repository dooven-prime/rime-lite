import RSR2.Parameterized
import RSR2.Bell

/-!
# Executable-construction plan and exact raw-letter ledger

The plan is expanded only into the five primitive letters. This module proves
the plan's exact raw-letter identity and the source-alignment arithmetic. The
guarded execution bridge for the generated plan lives in `RSR2.Executable`;
identifying its endpoint with the canonical stacked placement remains open.
-/

namespace RSR2.Parametric

structure LoadInstruction (n : Nat) where
  atom : Fin n
  sourceTurns : Nat
  continueBlock : Bool
  deriving DecidableEq, Repr

def lowerBackCount (n : Nat) (q : Fin n) : Nat :=
  if q.val = 0 then 0 else n - q.val

def bitCost (b : Bool) : Nat := if b then 1 else 0

def instructionWord (first : Bool) (i : LoadInstruction n) : List Letter :=
  List.replicate (bitCost (!first)) (.p true) ++
  List.replicate i.sourceTurns (.p false) ++
  [.v] ++ List.replicate (bitCost i.continueBlock) (.d true)

def emitPlanAux : Bool → List (LoadInstruction n) → List Letter
  | _, [] => []
  | first, i :: rest => instructionWord first i ++ emitPlanAux false rest

def emitPlan (plan : List (LoadInstruction n)) : List Letter :=
  emitPlanAux true plan

theorem run_powers (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) (k : Nat) :
    run n hn P (List.replicate k (.p layer)) =
      some (rotateMany n (by omega) P layer k) := by
  induction k generalizing P with
  | zero => rfl
  | succ k ih =>
      simp only [List.replicate_succ, run, step, Option.bind_some]
      rw [ih]
      rfl

theorem run_aligns_atom (n : Nat) (hn : 1 < n) (P : Placement n)
    (a : Fin n) (q : Site n) (turns : Nat)
    (ha : P a = (false, q))
    (halign : (q.val + turns) % n = 0) :
    run n hn P (List.replicate turns (.p false)) =
      some (rotateMany n (by omega) P false turns) ∧
      (rotateMany n (by omega) P false turns) a = (false, site0 n (by omega)) := by
  rw [run_powers]
  constructor
  · rfl
  · rw [rotateMany_apply, ha]
    simp only [if_true]
    apply Prod.ext
    · rfl
    apply Fin.ext
    rw [nextMany_val]
    simpa [halign, site0]

def sourceRotationCost (plan : List (LoadInstruction n)) : Nat :=
  (plan.map LoadInstruction.sourceTurns).sum

def continuationCount (plan : List (LoadInstruction n)) : Nat :=
  (plan.map (fun i => bitCost i.continueBlock)).sum

def upperRotationCount : Bool → List (LoadInstruction n) → Nat
  | _, [] => 0
  | first, _ :: rest => bitCost (!first) + upperRotationCount false rest

def annotateMarked (n : Nat) (phase : Nat) : List (Fin n × Bool) → List (LoadInstruction n)
  | [] => []
  | (a, continues) :: rest =>
      let q : Fin n := ⟨(a.val + phase) % n, Nat.mod_lt _ (by have := a.isLt; omega)⟩
      let turns := lowerBackCount n q
      ⟨a, turns, continues⟩ :: annotateMarked n (phase + turns) rest

theorem upperRotationCount_false (plan : List (LoadInstruction n)) :
    upperRotationCount false plan = plan.length := by
  induction plan with
  | nil => rfl
  | cons i rest ih => simp [upperRotationCount, bitCost, ih, Nat.add_comm]

theorem upperRotationCount_true (plan : List (LoadInstruction n)) :
    upperRotationCount true plan = plan.length - 1 := by
  cases plan with
  | nil => rfl
  | cons i rest => simp [upperRotationCount, bitCost, upperRotationCount_false]

theorem lowerBackCount_le (n : Nat) (hn : 1 ≤ n) (q : Fin n) :
    lowerBackCount n q ≤ n - 1 := by
  unfold lowerBackCount
  split
  · omega
  · have hq : q.val < n := q.isLt
    omega

theorem lowerBackCount_aligns (n : Nat) (hn : 0 < n) (q : Fin n) :
    (q.val + lowerBackCount n q) % n = 0 := by
  unfold lowerBackCount
  by_cases hq : q.val = 0
  · simp [hq, Nat.mod_eq_of_lt (by omega : 0 < n)]
  · have hlt := q.isLt
    have hsum : q.val + (n - q.val) = n := by omega
    rw [if_neg hq, hsum, Nat.mod_self]

theorem instructionWord_length (first : Bool) (i : LoadInstruction n) :
    (instructionWord first i).length =
      bitCost (!first) + i.sourceTurns + 1 + bitCost i.continueBlock := by
  simp [instructionWord, bitCost, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]

theorem emitPlanAux_length (first : Bool) (plan : List (LoadInstruction n)) :
    (emitPlanAux first plan).length =
      sourceRotationCost plan + upperRotationCount first plan +
        plan.length + continuationCount plan := by
  induction plan generalizing first with
  | nil => simp [emitPlanAux, sourceRotationCost, continuationCount, upperRotationCount]
  | cons i rest ih =>
      rw [emitPlanAux, List.length_append, instructionWord_length, ih]
      cases first <;> cases rest <;>
        simp [sourceRotationCost, continuationCount, upperRotationCount,
          List.map_cons, List.sum_cons, bitCost, List.length_cons,
          Nat.add_assoc, Nat.add_left_comm, Nat.add_comm] <;> omega

theorem emitPlan_length (plan : List (LoadInstruction n)) :
    (emitPlan plan).length =
      sourceRotationCost plan + (plan.length - 1) + plan.length + continuationCount plan := by
  rw [emitPlan, emitPlanAux_length, upperRotationCount_true]

theorem emitPlan_length_eq_interleaved_cost (plan : List (LoadInstruction n))
    (hLength : plan.length = n) (b : Nat)
    (hn : 0 < n) (hb : b ≤ n)
    (hContinuations : continuationCount plan = n - b) :
    (emitPlan plan).length = sourceRotationCost plan + 3 * n - b - 1 := by
  rw [emitPlan_length, hLength, hContinuations]
  omega

theorem list_sum_bounded (xs : List Nat) (bound : Nat)
    (hbound : ∀ x ∈ xs, x ≤ bound) : xs.sum ≤ xs.length * bound := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      have hx := hbound x (by simp)
      have hxs : ∀ y ∈ xs, y ≤ bound := by
        intro y hy
        exact hbound y (by simp [hy])
      have ih' := ih hxs
      simp only [List.sum_cons, List.length_cons]
      rw [Nat.add_mul]
      simp only [Nat.one_mul]
      omega

theorem sourceRotationCost_le (plan : List (LoadInstruction n))
    (hbound : ∀ i ∈ plan, i.sourceTurns ≤ n - 1) :
    sourceRotationCost plan ≤ plan.length * (n - 1) := by
  unfold sourceRotationCost
  have h := list_sum_bounded (plan.map LoadInstruction.sourceTurns) (n - 1) (by
    intro turns hturns
    rcases List.mem_map.mp hturns with ⟨i, hi, rfl⟩
    exact hbound i hi)
  simpa using h

theorem emitPlan_interleaved_bound (plan : List (LoadInstruction n))
    (hn : 0 < n) (b : Nat) (hb : 1 ≤ b)
    (hb' : b ≤ n)
    (hLength : plan.length = n)
    (hContinuations : continuationCount plan = n - b)
    (hturns : ∀ i ∈ plan, i.sourceTurns ≤ n - 1) :
    (emitPlan plan).length ≤ n * n + 2 * n - b - 1 := by
  have hexact := emitPlan_length_eq_interleaved_cost plan hLength b hn hb' hContinuations
  have hsource := sourceRotationCost_le plan hturns
  rw [hLength] at hsource
  rw [hexact]
  have hn1 : n * (n - 1) + n = n * n := by
    calc
      n * (n - 1) + n = n * (n - 1) + n * 1 := by simp
      _ = n * ((n - 1) + 1) := by rw [Nat.mul_add]
      _ = n * n := by congr 1 <;> omega
  omega

def markBlock (xs : List (Fin n)) : List (Fin n × Bool) :=
  match xs with
  | [] => []
  | a :: rest => (a, false) :: rest.map (fun x => (x, true))

def markedReverseBlocks (blocks : List (List (Fin n))) : List (Fin n × Bool) :=
  (blocks.reverse.map (fun block => markBlock block.reverse)).flatten

theorem markBlock_atoms (xs : List (Fin n)) :
    (markBlock xs).map Prod.fst = xs := by
  induction xs with
  | nil => rfl
  | cons a rest =>
      simp [markBlock, Function.comp_def]

theorem markedReverseBlocks_atoms (blocks : List (List (Fin n))) :
    (markedReverseBlocks blocks).map Prod.fst =
      (blocks.reverse.map List.reverse).flatten := by
  induction blocks with
  | nil => rfl
  | cons b bs ih =>
      simp [markedReverseBlocks, markBlock_atoms, Function.comp_def,
        List.reverse_cons, List.map_append]

theorem flatten_reverse_blocks {α : Type} (blocks : List (List α)) :
    (blocks.reverse.map List.reverse).flatten = blocks.flatten.reverse := by
  have h := List.flatten_reverse (L := blocks.reverse)
  simpa using (congrArg List.reverse h).symm

theorem reverse_nodup {α : Type} : ∀ xs : List α, xs.Nodup → xs.reverse.Nodup
  | [], _ => by simp
  | x :: xs, h => by
      rw [List.reverse_cons]
      apply List.nodup_append.mpr
      refine ⟨reverse_nodup xs (List.nodup_cons.mp h).2, ?_, ?_⟩
      · simp
      · intro a ha b hb hab
        have ha' : a = x := by
          calc
            a = b := hab
            _ = x := by simpa using hb
        have hxin : x ∈ xs.reverse := by simpa [ha'] using ha
        exact (List.nodup_cons.mp h).1 (List.mem_reverse.mp hxin)

theorem markedReverseBlocks_atom_nodup (p : RSR2.OrderedPartition n) :
    ((markedReverseBlocks p.blocks).map Prod.fst).Nodup := by
  rw [markedReverseBlocks_atoms, flatten_reverse_blocks]
  have hflat : p.blocks.flatten.Nodup :=
    (List.Perm.nodup_iff p.flatten_perm).2 (List.nodup_finRange n)
  exact reverse_nodup _ hflat

def interleavedPlan (n : Nat) (blocks : List (List (Fin n))) :
    List (LoadInstruction n) :=
  annotateMarked n 0 (markedReverseBlocks blocks)

def markedContinuationCount (xs : List (Fin n × Bool)) : Nat :=
  (xs.map (fun item => bitCost item.2)).sum

def blockAtomCount {α : Type} (blocks : List (List α)) : Nat :=
  (blocks.map List.length).sum

theorem blockAtomCount_eq_flatten_length {α : Type}
    (blocks : List (List α)) :
    blockAtomCount blocks = blocks.flatten.length := by
  simp [blockAtomCount, List.length_flatten]

theorem annotateMarked_length (n : Nat) (phase : Nat)
    (xs : List (Fin n × Bool)) : (annotateMarked n phase xs).length = xs.length := by
  induction xs generalizing phase with
  | nil => rfl
  | cons x xs ih => cases x with | mk a cont => simp [annotateMarked, ih]

theorem annotateMarked_turns_le (n : Nat) (hn : 1 ≤ n) (phase : Nat)
    (xs : List (Fin n × Bool)) :
    ∀ i ∈ annotateMarked n phase xs, i.sourceTurns ≤ n - 1 := by
  induction xs generalizing phase with
  | nil => simp [annotateMarked]
  | cons x xs ih =>
      cases x with
      | mk a cont =>
          intro i hi
          simp only [annotateMarked, List.mem_cons] at hi
          rcases hi with hhead | htail
          · subst i
            let q : Fin n := ⟨(a.val + phase) % n, Nat.mod_lt _ (by have := a.isLt; omega)⟩
            exact lowerBackCount_le n hn q
          · exact ih (phase + lowerBackCount n ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩) i htail

theorem markBlock_length (n : Nat) (xs : List (Fin n)) :
    (markBlock xs).length = xs.length := by
  cases xs with
  | nil => rfl
  | cons a rest => simp [markBlock]

theorem markedReverseBlocks_length (n : Nat) (blocks : List (List (Fin n))) :
    (markedReverseBlocks blocks).length = blockAtomCount blocks := by
  unfold markedReverseBlocks blockAtomCount
  rw [List.length_flatten]
  simp only [List.map_map, Function.comp_def, List.length_map, List.length_reverse]
  rw [List.map_reverse, List.sum_reverse]
  simp [markBlock_length]

theorem markedContinuationCount_append (n : Nat)
    (xs ys : List (Fin n × Bool)) :
    markedContinuationCount (xs ++ ys) =
      markedContinuationCount xs + markedContinuationCount ys := by
  simp [markedContinuationCount, List.map_append, List.sum_append]

theorem sum_map_one_length {α : Type} (xs : List α) :
    (xs.map (fun _ => (1 : Nat))).sum = xs.length := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp [ih, Nat.add_comm]

theorem annotateMarked_continuations (n : Nat) (phase : Nat)
    (xs : List (Fin n × Bool)) :
    continuationCount (annotateMarked n phase xs) = markedContinuationCount xs := by
  induction xs generalizing phase with
  | nil => rfl
  | cons x xs ih =>
      cases x with
      | mk a cont =>
          change bitCost cont + continuationCount (annotateMarked n
            (phase + lowerBackCount n ⟨(a.val + phase) % n,
              Nat.mod_lt _ (by have := a.isLt; omega)⟩) xs) =
            bitCost cont + markedContinuationCount xs
          rw [ih]

theorem markBlock_continuationCount (n : Nat) (xs : List (Fin n))
    (hnonempty : xs ≠ []) :
    markedContinuationCount (markBlock xs) = xs.length - 1 := by
  cases xs with
  | nil => contradiction
  | cons a rest =>
      clear hnonempty
      have hmap :
          (rest.map (fun x => (x, true))).map (fun item => bitCost item.2) =
            rest.map (fun _ => (1 : Nat)) := by
        induction rest with
        | nil => rfl
        | cons x xs ih => simp [ih, bitCost]
      simp only [markBlock, markedContinuationCount, List.map_cons, List.sum_cons]
      rw [hmap, sum_map_one_length]
      simp [bitCost]

theorem markedBlockContinuation_sum (n : Nat) (blocks : List (List (Fin n)))
    (hnonempty : ∀ block ∈ blocks, block ≠ []) :
    markedContinuationCount ((blocks.map (fun block => markBlock block.reverse)).flatten) =
      (blocks.map (fun block => block.length - 1)).sum := by
  induction blocks with
  | nil => rfl
  | cons block rest ih =>
      have hne := hnonempty block (by simp)
      have hrest : ∀ b ∈ rest, b ≠ [] := by
        intro b hb
        exact hnonempty b (by simp [hb])
      simp only [List.map_cons, List.flatten_cons, markedContinuationCount_append,
        markBlock_continuationCount n block.reverse (by simpa using hne),
        List.sum_cons, List.length_reverse]
      exact congrArg (fun z => block.length - 1 + z) (ih hrest)

theorem markedReverseBlocks_continuations (n : Nat)
    (blocks : List (List (Fin n)))
    (hnonempty : ∀ block ∈ blocks, block ≠ []) :
    markedContinuationCount (markedReverseBlocks blocks) =
      blockAtomCount blocks - blocks.length := by
  unfold markedReverseBlocks blockAtomCount
  have hrev : ∀ block ∈ blocks.reverse, block ≠ [] := by
    intro block hb
    exact hnonempty block (List.mem_reverse.mp hb)
  rw [markedBlockContinuation_sum n blocks.reverse hrev]
  rw [List.map_reverse, List.sum_reverse]
  have hsum : (blocks.map List.length).sum =
      blocks.length + (blocks.map (fun block => block.length - 1)).sum := by
    induction blocks with
    | nil => rfl
    | cons block rest ih =>
        have hne := hnonempty block (by simp)
        have hlen : 1 ≤ block.length := by cases block with | nil => contradiction | cons => simp
        simp only [List.map_cons, List.sum_cons, List.length_cons]
        have hrest : ∀ b ∈ rest, b ≠ [] := by
          intro b hb
          exact hnonempty b (by simp [hb])
        have hrestrev : ∀ b ∈ rest.reverse, b ≠ [] := by
          intro b hb
          exact hrest b (List.mem_reverse.mp hb)
        rw [ih hrest hrestrev]
        omega
  omega

theorem interleavedPlan_continuations (n : Nat)
    (blocks : List (List (Fin n)))
    (hnonempty : ∀ block ∈ blocks, block ≠ []) :
    continuationCount (interleavedPlan n blocks) =
      blockAtomCount blocks - blocks.length := by
  rw [interleavedPlan, annotateMarked_continuations]
  exact markedReverseBlocks_continuations n blocks hnonempty

theorem interleavedPlan_length (n : Nat) (blocks : List (List (Fin n))) :
    (interleavedPlan n blocks).length = blockAtomCount blocks := by
  simp [interleavedPlan, annotateMarked_length, markedReverseBlocks_length]

theorem interleavedPlan_turns_le (n : Nat) (hn : 1 ≤ n)
    (blocks : List (List (Fin n))) :
    ∀ i ∈ interleavedPlan n blocks, i.sourceTurns ≤ n - 1 := by
  rw [interleavedPlan]
  exact annotateMarked_turns_le n hn 0 (markedReverseBlocks blocks)

theorem blocks_length_le_atomCount (n : Nat) :
    ∀ (blocks : List (List (Fin n))),
      (∀ block ∈ blocks, block ≠ []) →
        blocks.length ≤ blockAtomCount blocks
  | [], _ => by simp [blockAtomCount]
  | block :: rest, h => by
      have hblock : block ≠ [] := h block (by simp)
      have hrest : ∀ b ∈ rest, b ≠ [] := by
        intro b hb
        exact h b (by simp [hb])
      cases block with
      | nil => contradiction
      | cons a tail =>
          simp only [blockAtomCount, List.map_cons, List.sum_cons,
            List.length_cons]
          have ih := blocks_length_le_atomCount n rest hrest
          change rest.length ≤ (rest.map List.length).sum at ih
          omega

theorem orderedPartition_blockAtomCount (p : RSR2.OrderedPartition n) :
    blockAtomCount p.blocks = n := by
  rw [blockAtomCount_eq_flatten_length]
  simpa [List.length_range] using p.flatten_perm.length_eq

theorem interleavedPlan_length_eq_cost (n : Nat)
    (blocks : List (List (Fin n)))
    (hnonempty : ∀ block ∈ blocks, block ≠ [])
    (hatoms : blockAtomCount blocks = n)
    (hn : 0 < n) (hb : 1 ≤ blocks.length) :
    (emitPlan (interleavedPlan n blocks)).length =
      sourceRotationCost (interleavedPlan n blocks) +
        3 * n - blocks.length - 1 := by
  have hlen : (interleavedPlan n blocks).length = n := by
    rw [interleavedPlan_length, hatoms]
  have hcont : continuationCount (interleavedPlan n blocks) = n - blocks.length := by
    rw [interleavedPlan_continuations n blocks hnonempty, hatoms]
  have hblocks : blocks.length ≤ n := by
    have h := blocks_length_le_atomCount n blocks hnonempty
    omega
  exact emitPlan_length_eq_interleaved_cost
    (interleavedPlan n blocks) hlen blocks.length hn
    hblocks hcont

theorem interleavedPlan_length_bound (n : Nat)
    (blocks : List (List (Fin n)))
    (hnonempty : ∀ block ∈ blocks, block ≠ [])
    (hatoms : blockAtomCount blocks = n)
    (hn : 0 < n) (hb : 1 ≤ blocks.length) :
    (emitPlan (interleavedPlan n blocks)).length ≤
      n * n + 2 * n - blocks.length - 1 := by
  have hlen : (interleavedPlan n blocks).length = n := by
    rw [interleavedPlan_length, hatoms]
  have hcont : continuationCount (interleavedPlan n blocks) = n - blocks.length := by
    rw [interleavedPlan_continuations n blocks hnonempty, hatoms]
  have hblocks : blocks.length ≤ n := by
    have h := blocks_length_le_atomCount n blocks hnonempty
    omega
  have hturns := interleavedPlan_turns_le n (by omega) blocks
  exact emitPlan_interleaved_bound (interleavedPlan n blocks) hn
    blocks.length hb hblocks hlen hcont hturns

theorem orderedPartition_interleavedPlan_length_bound
    (p : RSR2.OrderedPartition n) (hn : 0 < n) :
    (emitPlan (interleavedPlan n p.blocks)).length ≤
      n * n + 2 * n - p.blockCount - 1 := by
  have hb := RSR2.blockCount_positive p hn
  have h := interleavedPlan_length_bound n p.blocks p.nonempty
    (orderedPartition_blockAtomCount p) hn hb
  simpa [RSR2.OrderedPartition.blockCount] using h

end RSR2.Parametric
