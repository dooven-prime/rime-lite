import RSR2History.PackedLowerProjection
import RSR2History.PhaseFreeFusion

/-! A phase-restored ordered fusion through a directed empty arc.
The same physical raw word has a lower path costing at most its raw length.
No singleton condition is imposed on the two named parent packets. -/
namespace RSR2History
open RSR2.Parametric

/-- Embed an arbitrary lower configuration in the unchanged physical machine.
Absent lower atoms are parked in the upper layer; only lower letters are used. -/
def lowerPlacement (n : Nat) (hn : 1 < n) (c : LowerConfiguration n) : Placement n :=
  fun a => match c a with
    | some q => (false,q)
    | none => (true,site0 n (by omega))

@[simp] theorem lowerConfiguration_lowerPlacement (n : Nat) (hn : 1 < n)
    (c : LowerConfiguration n) : lowerConfiguration (lowerPlacement n hn c) = c := by
  funext a
  cases hc : c a <;> simp [lowerPlacement, lowerConfiguration, hc]

/-- Relocate the entire current lower port-zero packet into the named site. -/
def lowerRelocatePort (n : Nat) (hn : 1 < n) (c : LowerConfiguration n)
    (q : Fin n) : LowerConfiguration n :=
  fun a => if c a = some (site0 n (by omega)) then some q else c a

theorem lowerConfiguration_relocatePort
    {n : Nat} [NeZero n] (hn : 1 < n) (c : LowerConfiguration n) (q : Fin n) :
    lowerConfiguration (relocateAt (lowerPlacement n hn c) false 0 (q.val : ZMod n)) =
      lowerRelocatePort n hn c q := by
  funext a
  cases hc : c a with
  | none => simp [lowerConfiguration, relocateAt, lowerPlacement, hc, lowerRelocatePort]
  | some r =>
      by_cases hr : r = site0 n (by omega)
      · simp [lowerConfiguration, relocateAt, lowerPlacement, hc, hr, lowerRelocatePort]
      · simp [lowerConfiguration, relocateAt, lowerPlacement, hc, hr, lowerRelocatePort]

section Macro
variable {n : Nat} [NeZero n]

/-- The actual lower control macro. Here `n-q.val` is strictly positive. -/
def packedLowerFusionWord (q : Fin n) : List Letter :=
  (FusionLogCompression.pdWord (n-q.val)).map (layerLetter false) ++ pWord false q.val

omit [NeZero n] in
theorem packedLowerFusionWord_length (q : Fin n) :
    (packedLowerFusionWord q).length = n+(n-q.val) := by
  simp only [packedLowerFusionWord, List.length_append, List.length_map,
    FusionLogCompression.pdWord_length, pWord, List.length_replicate]
  omega

private theorem mapped_pd_succ (k : Nat) :
    (FusionLogCompression.pdWord (k+1)).map (layerLetter false) =
      [.p false,.d false] ++ (FusionLogCompression.pdWord k).map (layerLetter false) := by
  induction k with
  | zero => simp [FusionLogCompression.pdWord, layerLetter]
  | succ k ih =>
      rw [FusionLogCompression.pdWord, List.map_append]
      change (FusionLogCompression.pdWord (k+1)).map (layerLetter false) ++
        [.p false,.d false] = [.p false,.d false] ++
        (FusionLogCompression.pdWord (k+1)).map (layerLetter false)
      rw [ih]
      simp only [List.cons_append, List.nil_append]
      have ih' : (FusionLogCompression.pdWord k).map (layerLetter false) ++
          [.p false,.d false] = [.p false,.d false] ++
          (FusionLogCompression.pdWord k).map (layerLetter false) := by
        simpa only [FusionLogCompression.pdWord, List.map_append, List.map_cons,
          List.map_nil, layerLetter] using ih
      exact congrArg (fun w => [.p false,.d false] ++ w) ih'

private theorem packedLowerFusionWord_eq_phaseFree (hn : 1 < n) (q : Fin n)
    (hq : q.val ≠ 0) :
    packedLowerFusionWord q =
      phaseFreeFusionWord false (q.val : ZMod n) 0 (n-q.val-1) ++ pWord false q.val := by
  have hqpos : 0 < q.val := by omega
  have hqz : (q.val : ZMod n) ≠ 0 := by
    intro h
    have hval := congrArg ZMod.val h
    rw [ZMod.val_natCast_of_lt q.isLt, ZMod.val_zero] at hval
    omega
  have hneg : (-(q.val : ZMod n)).val = n-q.val := by
    have : NeZero (q.val : ZMod n) := ⟨hqz⟩
    rw [ZMod.val_neg_of_ne_zero, ZMod.val_natCast_of_lt q.isLt]
  by_cases hf : n-q.val-1 = 0
  · have hd : n-q.val = 1 := by omega
    simp [packedLowerFusionWord, phaseFreeFusionWord, hneg, hd,
      FusionLogCompression.pdWord, layerLetter, pWord]
  · have hd : n-q.val = (n-q.val-1-1)+2 := by omega
    have h1 : ((1 : ZMod n)-0).val = 1 := by
      have : Fact (1<n) := ⟨hn⟩
      simp [ZMod.val_one]
    rw [packedLowerFusionWord, phaseFreeFusionWord, if_neg hf, h1, hd]
    rw [show n-q.val-1-1+2 = (n-q.val-1-1+1)+1 by omega]
    rw [mapped_pd_succ]
    simp only [FusionLogCompression.pdWord, List.map_append, List.map_cons,
      List.map_nil, layerLetter]
    simp [pWord, List.append_assoc]

/-- Physical correctness of the literal phase-restoring ordered fusion.
The directed arc from `q` to port zero must have no intervening packets. -/
theorem packedLowerFusionWord_spec (hn : 1 < n) (c : LowerConfiguration n)
    (q : Fin n) (hq : q.val ≠ 0)
    (hleft : (lowerPacket c q).Nonempty)
    (hright : (lowerPacket c (site0 n (by omega))).Nonempty)
    (hholes : ∀ r : Fin n, q.val < r.val → lowerPacket c r = ∅) :
    runLogged n hn (lowerPlacement n hn c) (packedLowerFusionWord q) =
      some (relocateAt (lowerPlacement n hn c) false 0 (q.val : ZMod n),
        [.fusion false (lowerPacket c q) (lowerPacket c (site0 n (by omega)))
          (lowerPacket c q ∪ lowerPacket c (site0 n (by omega)))]) := by
  let P := lowerPlacement n hn c
  have hp (r : Fin n) : packetAt P false r = lowerPacket c r := by
    rw [← lowerPacket_configuration, lowerConfiguration_lowerPlacement]
  let f := n-q.val-1
  have hfn : f ≤ n-2 := by dsimp [f]; omega
  have hgap : (0 : ZMod n) = (q.val : ZMod n)+1+(f : ZMod n) := by
    have he : q.val+1+f = n := by dsimp [f]; omega
    have hz := congrArg (fun k : Nat => (k : ZMod n)) he
    simpa using hz.symm
  have hh : ∀ i : Nat, 1 ≤ i → i ≤ f →
      packetAt P false (zsite ((0 : ZMod n)-(i : ZMod n))) = ∅ := by
    intro i hi hif
    have hin : i < n := by dsimp [f] at hif; omega
    have hiz : (i : ZMod n) ≠ 0 := by
      intro h
      have hv := congrArg ZMod.val h
      rw [ZMod.val_natCast_of_lt hin, ZMod.val_zero] at hv
      omega
    have hval : (zsite ((0 : ZMod n)-(i : ZMod n))).val = n-i := by
      simp only [zsite, zero_sub]
      have : NeZero (i : ZMod n) := ⟨hiz⟩
      rw [ZMod.val_neg_of_ne_zero, ZMod.val_natCast_of_lt hin]
    rw [hp]
    apply hholes
    rw [hval]
    dsimp [f] at hif
    omega
  have hfree := phaseFreeFusionWord_spec hn P false (q.val : ZMod n) 0 f hfn hgap
    (by simpa only [zsite_cast, hp] using hleft)
    (by simpa only [zsite_zero, hp] using hright) hh
  rw [packedLowerFusionWord_eq_phaseFree hn q hq, runLogged_append, hfree]
  simp only [Option.bind_some, runLogged_pWord, Option.map_some, List.append_nil]
  rw [phaseShift_add]
  simp only [neg_add_cancel, phaseShift_zero, zsite_cast, zsite_zero, hp]
  rfl

/-- The physical macro induces an exact-log lower path. Projection can only
erase idle lower letters, so its lower cost is bounded by the exact raw length. -/
theorem packedLowerFusionMacro_path (hn : 1 < n) (c : LowerConfiguration n)
    (q : Fin n) (hq : q.val ≠ 0)
    (hleft : (lowerPacket c q).Nonempty)
    (hright : (lowerPacket c (site0 n (by omega))).Nonempty)
    (hholes : ∀ r : Fin n, q.val < r.val → lowerPacket c r = ∅) :
    ∃ cost, PackedLowerPath n hn c
      [.fusion false (lowerPacket c q) (lowerPacket c (site0 n (by omega)))
        (lowerPacket c q ∪ lowerPacket c (site0 n (by omega)))]
      (lowerRelocatePort n hn c q) cost ∧ cost ≤ 2*n-1 := by
  have hw := packedLowerFusionWord_spec hn c q hq hleft hright hholes
  obtain ⟨cost, path, hcost⟩ := runLogged_packedLower_projection (packedLowerFusionWord q) hw
  refine ⟨cost, ?_, ?_⟩
  · simpa only [lowerConfiguration_lowerPlacement, lowerConfiguration_relocatePort,
      packedLowerLog_lowerFusion, packedLowerLog_nil] using path
  · have hcount : (packedLowerFusionWord q).count (.p false) +
        (packedLowerFusionWord q).count (.d false) ≤ (packedLowerFusionWord q).length := by
      have hall : ∀ w : List Letter, w.count (.p false) + w.count (.d false) ≤ w.length := by
        intro w
        induction w with
        | nil => simp
        | cons a w ih =>
          cases a with
          | p layer => cases layer <;> (simp_all; omega)
          | d layer => cases layer <;> (simp_all; omega)
          | v => simp_all; omega
      exact hall _
    rw [packedLowerFusionWord_length] at hcount
    omega


omit [NeZero n]

/-- Erasing the right singleton after its fusion is the same erased lower
configuration as deleting that singleton before the fusion. -/
theorem lowerDelete_lowerSlide_of_right_singleton
    (hn : 1 < n) (c : LowerConfiguration n) (b : Fin n)
    (valid : c.Valid) (hb : c b = some (site1 n hn)) :
    lowerDelete (lowerSlide n hn c) b = lowerDelete c b := by
  funext a
  by_cases hab : a = b
  · simp [lowerDelete, hab]
  · have hno : c a ≠ some (site1 n hn) := by
      intro ha
      exact hab (valid a b _ ha hb)
    simp [lowerDelete, hab, lowerSlide, hno]

/-- First-fusion refinement is feasible without assuming any optimized path:
rotate the right singleton from port one to port zero, delete it, and rotate
once more to restore every other literal coordinate. Its lower cost is `n`.
The atom at the left port need not be specified by this construction. -/
theorem packedLower_refine_first_fusion_path
    (hn : 1 < n) (c : LowerConfiguration n) (b : Fin n)
    (valid : c.Valid) (hb : c b = some (site1 n hn)) :
    PackedLowerPath n hn c [.transfer {b}] (lowerDelete c b) n := by
  let R := lowerRotateMany n hn c (n-1)
  have pre : LowerExtractionPath n hn c [] R (n-1) := lowerRotateMany_path c (n-1)
  have validR := pre.valid valid
  have cycle (q : Fin n) : next n (by omega) (nextMany n (by omega) q (n-1)) = q := by
    apply Fin.ext
    rw [next_val, nextMany_val, Nat.mod_add_mod]
    have he : q.val+(n-1)+1 = q.val+n := by omega
    rw [he]
    simp [Nat.mod_eq_of_lt q.isLt]
  have rb : R b = some (site0 n (by omega)) := by
    have hr := lowerRotateMany_apply (hn := hn) c (n-1) b (site1 n hn) hb
    have hsite : nextMany n (by omega) (site1 n hn) (n-1) = site0 n (by omega) := by
      apply Fin.ext
      simp only [nextMany_val, site1, site0]
      have he : 1+(n-1)=n := by omega
      simp [he]
    simpa only [R, hsite] using hr
  have packet : lowerPacket R (site0 n (by omega)) = {b} := by
    ext a
    simp only [lowerPacket, Finset.mem_filter, Finset.mem_univ, true_and,
      Finset.mem_singleton]
    exact ⟨fun ha => validR a b _ ha rb, fun ha => ha ▸ rb⟩
  have middle : PackedLowerPath n hn R [.transfer {b}] (lowerDelete R b) 0 := by
    have event := PackedLowerEvent.extract (n := n) (hn := hn) R (by rw [packet]; simp)
    have he : lowerErasePacket R (lowerPacket R (site0 n (by omega))) = lowerDelete R b := by
      rw [packet]
      funext a
      simp [lowerErasePacket, lowerDelete]
    rw [packet] at he event
    rw [he] at event
    exact .event event
  have final : lowerRotate n hn (lowerDelete R b) = lowerDelete c b := by
    funext a
    by_cases hab : a = b
    · simp [lowerRotate, lowerDelete, hab]
    · cases hc : c a with
      | none =>
        have hr : R a = none := lowerRotateMany_none (hn := hn) c (n-1) a hc
        simp [lowerRotate, lowerDelete, hab, hr, hc]
      | some q =>
        have hr : R a = some (nextMany n (by omega) q (n-1)) :=
          lowerRotateMany_apply c (n-1) a q hc
        simp [lowerRotate, lowerDelete, hab, hr, hc, cycle]
  have post : PackedLowerPath n hn (lowerDelete R b) [] (lowerDelete c b) 1 := by
    rw [← final]
    exact .prepare (.rotate _)
  have joined := (PackedLowerPath.prepare pre).trans (middle.trans post)
  simpa only [List.nil_append, List.append_nil, Nat.zero_add,
    show n-1+1=n by omega] using joined

end Macro
end RSR2History
