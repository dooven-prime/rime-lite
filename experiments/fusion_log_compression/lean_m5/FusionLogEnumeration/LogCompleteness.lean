import FusionLogEnumeration.ScheduleAdmission
import FusionLogEnumeration.SurvivorConverse

namespace FusionLogEnumeration

open RegisteredAbsorptionChains FusionLogCompression FusionLogReplay FusionLogInterpretation
  FusionLogSchedule

variable {α : Type*} [DecidableEq α] {n : ℕ} [NeZero n]

namespace LiteralPacketStart

variable {O : MarkedCircle α} [NeZero O.rank]

private theorem label_subset_of_index_mem (start : LiteralPacketStart O n)
    (A : Finset α) (decoded : expandBlock (siteLabels start.initial) (start.indexBlock A) = A)
    {z : ZMod n} (member : z ∈ start.indexBlock A) :
    siteLabels start.initial
      ((occupiedRounding (occupiedSites start.initial) start.occupied_nonempty).position z) ⊆ A := by
  let lift := occupiedRounding (occupiedSites start.initial) start.occupied_nonempty
  have fixed := occupiedRounding_fixed (occupiedSites start.initial) start.occupied_nonempty
    (lift.position z) (occupiedRounding_image _ _ z)
  have atRound : lift.position z ∈ start.indexBlock A := by
    simp only [indexBlock, Finset.mem_filter, Finset.mem_univ, true_and]
    change (siteLabels start.initial (lift.position (lift.position z)) ∩ A).Nonempty
    rw [fixed]
    exact (Finset.mem_filter.mp member).2
  intro a ha
  rw [← decoded]
  exact Finset.mem_biUnion.mpr ⟨lift.position z, atRound, ha⟩

/-- A source-site edge crossing two decoded, disjoint current blocks crosses
one original named boundary. This is the reverse of the neighbour admission
interface; it rules out extra contraction logs in actual executions. -/
theorem index_edge_original_boundary (start : LiteralPacketStart O n)
    {A B : Finset α} (disjoint : Disjoint A B)
    (decodedA : expandBlock (siteLabels start.initial) (start.indexBlock A) = A)
    (decodedB : expandBlock (siteLabels start.initial) (start.indexBlock B) = B)
    (edge : SourceAtomAdjacent (start.indexBlock A) (start.indexBlock B)) :
    ∃ a ∈ O.boundaries, a ∈ A ∧ O.boundarySuccessor a ∈ B := by
  obtain ⟨z, hzA, hzB⟩ := edge
  let lift := occupiedRounding (occupiedSites start.initial) start.occupied_nonempty
  have subA := start.label_subset_of_index_mem A decodedA hzA
  have subB := start.label_subset_of_index_mem B decodedB hzB
  have different : lift.position z ≠ lift.position (z + 1) := by
    intro same
    obtain ⟨a, ha⟩ := siteLabels_nonempty start.initial start.packetPartition
      (lift.position z) (occupiedRounding_image _ _ z)
    exact (Finset.disjoint_left.mp disjoint) (subA ha) (subB (same ▸ ha))
  have occupied : z + 1 ∈ occupiedSites start.initial := by
    by_contra hole
    exact different (occupiedRounding_position_step_of_hole _ _ z hole).symm
  have fixed : lift.position (z + 1) = z + 1 := occupiedRounding_fixed _ _ _ occupied
  have existsName : ∃ j : ZMod O.rank, start.named.position j = z + 1 := by
    apply start.named.only_named
    rw [← start.initial_eq_named]
    exact (Finset.mem_filter.mp occupied).2
  obtain ⟨j, hj⟩ := existsName
  let i : ZMod O.rank := j - 1
  have ij : i + 1 = j := by dsimp [i]; abel
  let frame := (start.named.admit start.positiveOrder).toGapFrame
  have initial : start.initial = frame.decode := by
    rw [NamedCyclicPlacement.toGapFrame_decode]
    exact start.initial_eq_named
  have zAt : z = frame.position i + (frame.gap i : ZMod n) := by
    have next := frame.next_eq i
    rw [ij] at next
    change start.named.position j = _ at next
    rw [hj] at next
    linear_combination next
  have previous : lift.position z = start.named.position i := by
    rw [zAt]
    apply occupiedRounding_position_through_holes
    · rw [initial]
      simp [occupiedSites, frame.decode_at]
    · intro t ht bound
      have empty := frame.faithful i t (by omega) bound
      rw [← initial] at empty
      simp [occupiedSites, empty]
  let idx : Fin O.rank := ⟨i.val, ZMod.val_lt i⟩
  have castIdx : (idx.val : ZMod O.rank) = i := ZMod.natCast_zmod_val i
  have castNext : ((O.nextIndex idx).val : ZMod O.rank) = j := by
    simp [MarkedCircle.nextIndex, castIdx, ij]
  have nameA : siteLabels start.initial (lift.position z) = O.packets[idx].atoms := by
    rw [previous]
    have atSite := start.named.placed_at i
    rw [← start.initial_eq_named] at atSite
    simp only [siteLabels, atSite, Option.getD_some]
    rw [← castIdx]
    exact start.circleBlocks idx
  have nameB : siteLabels start.initial (lift.position (z + 1)) =
      O.packets[O.nextIndex idx].atoms := by
    rw [fixed, ← hj]
    have atSite := start.named.placed_at j
    rw [← start.initial_eq_named] at atSite
    simp only [siteLabels, atSite, Option.getD_some]
    rw [← castNext]
    exact start.circleBlocks (O.nextIndex idx)
  refine ⟨O.packets[idx].boundary, (O.boundaryEquiv idx).2, ?_, ?_⟩
  · apply subA
    rw [nameA]
    exact O.packets[idx].boundary_mem
  · rw [O.boundarySuccessor_at]
    apply subB
    rw [nameB]
    exact O.packets[O.nextIndex idx].boundary_mem

end LiteralPacketStart

namespace MarkedCircle

theorem frontAt_right (C : MarkedCircle α) (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    (C.frontAt i hr).right = C.packets[C.nextIndex i] := by
  have value : ((C.rotate i.val).packets[1]'(by change 1 < (C.rotate i.val).rank; simp; omega)) =
      (C.frontAt i hr).right := by
    simp only [(C.frontAt i hr).eq, List.getElem_cons_succ, List.getElem_cons_zero]
  simpa [MarkedCircle.rotate, List.getElem_rotate, nextIndex, rank, Nat.add_comm] using value.symm

/-- The successor certificate also survives the final rank-two contraction;
at rank one its outgoing edge returns to the same unique packet. -/
theorem BoundarySuccessorInvariant.contract_allRanks
    {labels : Finset α} {next : α → α} {C : MarkedCircle α}
    (inv : BoundarySuccessorInvariant labels next C)
    (i : Fin C.rank) (hr : 2 ≤ C.rank) :
    BoundarySuccessorInvariant labels next (C.contract i hr) := by
  by_cases large : 3 ≤ C.rank
  · exact inv.contract i hr large
  let R := C.rotate i.val
  let f := C.frontAt i hr
  have old := inv.rotate i.val
  have two : R.rank = 2 := by simp [R]; omega
  have twoC : C.rank = 2 := by omega
  have rest : f.rest = [] := by
    have length := congrArg List.length f.eq
    change R.rank = _ at length
    simp only [List.length_cons] at length
    exact List.length_eq_zero_iff.mp (by omega)
  have edge₀ := old.outgoing (⟨0, by omega⟩ : Fin R.rank)
  have edge₁ := old.outgoing (⟨1, by omega⟩ : Fin R.rank)
  have first : next f.left.boundary ∈ f.right.atoms := by
    simpa [nextIndex, twoC, f.eq] using edge₀
  have second : next f.right.boundary ∈ f.left.atoms := by
    simpa [nextIndex, twoC, f.eq] using edge₁
  constructor
  · intro p hp a ha hpa different
    change p ∈ _ :: f.rest at hp
    rw [rest, List.mem_singleton] at hp
    subst p
    rcases Finset.mem_union.mp hpa with left | right
    · by_cases same : a = f.left.boundary
      · exact Finset.mem_union_right _ (same ▸ first)
      · exact Finset.mem_union_left _
          (old.internal f.left (by rw [f.eq]; simp) a ha left same)
    · exact Finset.mem_union_right _
        (old.internal f.right (by rw [f.eq]; simp) a ha right different)
  · intro j
    have zero : j.val = 0 := by
      have hj := j.isLt
      change j.val < f.rest.length + 1 at hj
      simp [rest] at hj
      omega
    let merged : MarkedPacket α := ⟨f.right.boundary, f.left.atoms ∪ f.right.atoms,
      Finset.mem_union_right _ f.right.boundary_mem⟩
    change next (merged :: f.rest)[j.val].boundary ∈
      ((merged :: f.rest)[(j.val + 1) % (f.rest.length + 1)]'
        (Nat.mod_lt _ (by omega))).atoms
    simpa [rest, zero, merged] using
      (Finset.mem_union_left f.right.atoms second)

/-- An original boundary crossing distinct current blocks determines the
ordered positive neighbour pair, including either direction at rank two. -/
theorem BoundarySuccessorInvariant.edge_neighbours
    {labels : Finset α} {next : α → α} {C : MarkedCircle α}
    (inv : BoundarySuccessorInvariant labels next C)
    {i j : Fin C.rank} (different : i ≠ j)
    (edge : ∃ a ∈ labels, a ∈ C.packets[i].atoms ∧ next a ∈ C.packets[j].atoms) :
    C.nextIndex i = j := by
  obtain ⟨a, ha, left, right⟩ := edge
  have boundary : a = C.packets[i].boundary := by
    by_contra h
    exact (Finset.disjoint_left.mp (C.packet_disjoint different))
      (inv.internal _ (List.getElem_mem _) a ha left h) right
  have following := inv.outgoing i
  rw [← boundary] at following
  by_contra h
  exact (Finset.disjoint_left.mp (C.packet_disjoint h)) following right

end MarkedCircle

namespace LiteralPacketStart

variable {O : MarkedCircle α} [NeZero O.rank]

/-- Completeness of M5 record admission: every M4-D source-index contraction
trace decodes to an M5 contraction log. No physical realization is assumed. -/
theorem indexedTrace_logRun (start : LiteralPacketStart O n)
    {C : MarkedCircle α}
    (model : MarkedCircle.IndexedCircle start.indexBlock (siteLabels start.initial) C)
    (inv : MarkedCircle.BoundarySuccessorInvariant O.boundaries O.boundarySuccessor C)
    {events : List (FusionRecord (ZMod n))} {last : IndexPackets n}
    (trace : AbstractTrace (C.packetAtoms.image start.indexBlock) events last) :
    LogRun C (events.map (expandRecord (siteLabels start.initial))) := by
  induction events generalizing C with
  | nil => exact .nil C
  | cons event rest ih =>
    cases trace with
    | @cons packets last A B rest left right distinct boundary tail =>
      obtain ⟨leftAtoms, leftMem, rfl⟩ := Finset.mem_image.mp left
      obtain ⟨rightAtoms, rightMem, rfl⟩ := Finset.mem_image.mp right
      obtain ⟨p, hp, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp leftMem)
      obtain ⟨q, hq, rfl⟩ := List.mem_map.mp (List.mem_toFinset.mp rightMem)
      obtain ⟨i, hi, rfl⟩ := List.mem_iff_getElem.mp hp
      obtain ⟨j, hj, rfl⟩ := List.mem_iff_getElem.mp hq
      let li : Fin C.rank := ⟨i, hi⟩
      let ri : Fin C.rank := ⟨j, hj⟩
      have different : li ≠ ri := by
        intro same
        have packetEq : C.packets[i].atoms = C.packets[j].atoms :=
          congrArg (fun k : Fin C.rank => C.packets[k].atoms) same
        exact distinct (congrArg start.indexBlock packetEq)
      have hr : 2 ≤ C.rank := by
        have ine := Fin.val_ne_of_ne different
        have ilt := li.isLt
        have jlt := ri.isLt
        omega
      have decodedI := model.decodes C.packets[i] (List.getElem_mem hi)
      have decodedJ := model.decodes C.packets[j] (List.getElem_mem hj)
      have edge := start.index_edge_original_boundary (C.packet_disjoint different)
        decodedI decodedJ boundary
      have follows : C.nextIndex li = ri := inv.edge_neighbours different edge
      have eventEq : C.event li hr =
          expandRecord (siteLabels start.initial)
            ⟨start.indexBlock C.packets[i].atoms, start.indexBlock C.packets[j].atoms,
              start.indexBlock C.packets[i].atoms ∪ start.indexBlock C.packets[j].atoms⟩ := by
        simp only [MarkedCircle.event, expandRecord, expandBlock_union,
          C.frontAt_left, C.frontAt_right, follows, Fin.getElem_fin, li, ri,
          decodedI, decodedJ]
      have nextSet : (C.contract li hr).packetAtoms.image start.indexBlock =
          mergePackets (C.packetAtoms.image start.indexBlock) (start.indexBlock C.packets[i].atoms)
            (start.indexBlock C.packets[j].atoms) := by
        rw [model.contract_indexPackets start.indexBlock_union]
        simp only [MarkedCircle.event, C.frontAt_left, C.frontAt_right, follows,
          Fin.getElem_fin, li, ri]
      rw [← nextSet] at tail
      have next := ih (model.contract start.indexBlock_union li hr)
        (inv.contract_allRanks li hr) tail
      rw [List.map_cons, ← eventEq]
      exact .cons hr li next

theorem admissibleSchedule_logRun (start : LiteralPacketStart O n)
    {events : List (FusionRecord α)}
    (schedule : AdmissibleSchedule start.initial start.occupied_nonempty events) :
    LogRun O events := by
  have trace := schedule.abstractTrace
  rw [← start.initial_indexPacketSet] at trace
  have decoded := start.indexedTrace_logRun start.indexedCircle
    O.boundarySuccessorInvariant_initial trace
  rwa [schedule.records] at decoded

/-- Arbitrary actual complete logs, not just a chosen M5 family, enter the
record-only M5 admission relation. -/
theorem jointlyAttainable_logRun (start : LiteralPacketStart O n)
    (F : Finset α) {events : List (FusionRecord α)} {target : Placement n (Finset α)}
    (hn : 3 ≤ n) (actual : JointlyAttainable F start.execution events target) :
    LogRun O events := by
  obtain ⟨schedule, _⟩ :=
    (joint_realization_iff F start.execution events target hn start.occupied_nonempty).mp actual
  exact start.admissibleSchedule_logRun schedule

end LiteralPacketStart

end FusionLogEnumeration
