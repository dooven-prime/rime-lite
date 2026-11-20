import RSR2History.BudgetedSilentPreparation
import FusionLogCompression.M1Batch

/-! Actual phase-restored words on the unchanged guarded executor. -/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

def zsite (q : ZMod n) : Fin n := ⟨q.val, ZMod.val_lt q⟩

@[simp] theorem zsite_cast (q : Fin n) : zsite (q.val : ZMod n) = q := by
  apply Fin.ext
  simp [zsite, Nat.mod_eq_of_lt q.isLt]

@[simp] theorem zsite_val_cast (q : ZMod n) : ((zsite q).val : ZMod n) = q := by
  simp [zsite]

@[simp] theorem zsite_inj {q r : ZMod n} : zsite q = zsite r ↔ q = r := by
  constructor
  · intro h
    simpa using congrArg (fun x : Fin n => (x.val : ZMod n)) h
  · exact congrArg zsite

@[simp] theorem zsite_zero : zsite (0 : ZMod n) = site0 n (Nat.pos_of_ne_zero (NeZero.ne n)) := by
  apply Fin.ext
  simp [zsite, site0]

theorem zsite_one (hn : 1 < n) : zsite (1 : ZMod n) = site1 n hn := by
  have : Fact (1 < n) := ⟨hn⟩
  apply Fin.ext
  exact ZMod.val_one n

def phaseShift (P : Placement n) (layer : Layer) (amount : ZMod n) : Placement n :=
  fun a => if (P a).1 = layer then
    (layer, zsite ((P a).2.val + amount)) else P a

@[simp] theorem phaseShift_zero (P : Placement n) (layer : Layer) :
    phaseShift P layer 0 = P := by
  funext a
  by_cases h : (P a).1 = layer
  · simp only [phaseShift, if_pos h, add_zero, zsite_cast]
    exact Prod.ext h.symm rfl
  · simp [phaseShift, h]

theorem phaseShift_add (P : Placement n) (layer : Layer) (a b : ZMod n) :
    phaseShift (phaseShift P layer a) layer b = phaseShift P layer (a+b) := by
  funext atom
  by_cases h : (P atom).1 = layer <;> simp [phaseShift, h, add_assoc]

theorem phaseShift_commute (P : Placement n) (a b : ZMod n) :
    phaseShift (phaseShift P false a) true b =
      phaseShift (phaseShift P true b) false a := by
  funext atom
  cases h : (P atom).1 <;> simp [phaseShift, h]

theorem rotateMany_eq_phaseShift (hn : 0 < n) (P : Placement n) (layer : Layer) (k : Nat) :
    rotateMany n hn P layer k = phaseShift P layer (k : ZMod n) := by
  funext a
  rw [rotateMany_apply]
  by_cases h : (P a).1 = layer
  · simp only [phaseShift, h, if_pos, Prod.mk.injEq, true_and]
    apply Fin.ext
    simp [nextMany_val, zsite, ZMod.val_add, ZMod.val_natCast,
      Nat.mod_eq_of_lt (P a).2.isLt, Nat.add_mod_mod]
  · simp [phaseShift, h]

theorem runLogged_pWord (hn : 1 < n) (P : Placement n) (layer : Layer) (k : Nat) :
    runLogged n hn P (pWord layer k) = some (phaseShift P layer (k : ZMod n), []) := by
  induction k generalizing P with
  | zero => simp [pWord, runLogged]
  | succ k ih =>
      have hp : rotate n (by omega) P layer = phaseShift P layer 1 := by
        simpa [rotateMany] using rotateMany_eq_phaseShift (by omega) P layer 1
      simp only [pWord] at ih ⊢
      simp only [List.replicate_succ, runLogged, step_p, Option.bind_some,
        emittedEvents, ih, Option.map_some, List.nil_append]
      rw [hp, phaseShift_add]
      congr 2
      simp [Nat.cast_add, add_comm]

theorem runLogged_phase (hn : 1 < n) (P : Placement n) (layer : Layer) (amount : ZMod n) :
    runLogged n hn P (pWord layer amount.val) = some (phaseShift P layer amount, []) := by
  simpa using runLogged_pWord hn P layer amount.val

theorem packetAt_phaseShift (P : Placement n) (layer : Layer) (amount q : ZMod n) :
    packetAt (phaseShift P layer amount) layer (zsite q) =
      packetAt P layer (zsite (q-amount)) := by
  ext a
  simp only [mem_packetAt, phaseShift]
  by_cases h : (P a).1 = layer
  · simp only [if_pos h, Prod.mk.injEq, true_and, zsite_inj]
    rw [Prod.ext_iff]
    simp only [h, true_and]
    have he : (P a).2 = zsite (q-amount) ↔ ((P a).2.val : ZMod n) = q-amount := by
      rw [← zsite_cast (P a).2, zsite_inj]
      simp
    rw [he]
    exact eq_sub_iff_add_eq.symm
  · have h0 : P a ≠ (layer, zsite q) := fun he => h (congrArg Prod.fst he)
    have h1 : P a ≠ (layer, zsite (q-amount)) := fun he => h (congrArg Prod.fst he)
    simp [h, h0, h1]

theorem packetAt_phaseShift_other (P : Placement n) (layer other : Layer)
    (hne : other ≠ layer) (amount : ZMod n) (q : Fin n) :
    packetAt (phaseShift P layer amount) other q = packetAt P other q := by
  ext a
  by_cases h : (P a).1 = layer
  · have hno : P a ≠ (other, q) := fun he => hne ((congrArg Prod.fst he).symm.trans h)
    simp [phaseShift, mem_packetAt, h, Ne.symm hne, hno]
  · simp [phaseShift, h]

theorem inverse_phase_cost (q : ZMod n) : (-q).val + q.val ≤ n := by
  by_cases h : q = 0
  · simp [h]
  · have : NeZero q := ⟨h⟩
    rw [ZMod.val_neg_of_ne_zero]
    have := ZMod.val_lt q
    omega

def transferAt (P : Placement n) (source target : ZMod n) : Placement n :=
  fun a => if P a = (false, zsite source) then (true, zsite target) else P a

def relocateAt (P : Placement n) (layer : Layer) (source target : ZMod n) : Placement n :=
  fun a => if P a = (layer, zsite source) then (layer, zsite target) else P a

def reservedTransferWord (source target : ZMod n) : List Letter :=
  pWord false (-source).val ++ (pWord true (-target).val ++ ([.v] ++
    (pWord true target.val ++ pWord false source.val)))

theorem reservedTransferWord_length_le (source target : ZMod n) :
    (reservedTransferWord source target).length ≤ 2*n+1 := by
  have hs := inverse_phase_cost source
  have ht := inverse_phase_cost target
  simp only [reservedTransferWord, List.length_append, pWord, List.length_replicate,
    List.length_singleton]
  omega

theorem transfer_phase_restored (P : Placement n) (source target : ZMod n) :
    phaseShift (phaseShift (liftPacket n (Nat.pos_of_ne_zero (NeZero.ne n))
      (phaseShift (phaseShift P false (-source)) true (-target))) true target)
      false source = transferAt P source target := by
  funext a
  cases he : P a with
  | mk layer q =>
      cases layer with
      | false =>
          by_cases hq : q = zsite source
          · simp [phaseShift, liftPacket, transferAt, he, hq, site0]
          · have hc : (q.val : ZMod n) - source ≠ 0 := by
              intro h
              have h' : (q.val : ZMod n) = source := sub_eq_zero.mp h
              exact hq (by simpa using congrArg zsite h')
            have hz : zsite ((q.val : ZMod n) - source) ≠ site0 n
                (Nat.pos_of_ne_zero (NeZero.ne n)) := by
              rw [← zsite_zero]
              exact fun h => hc (zsite_inj.mp h)
            simp [phaseShift, liftPacket, transferAt, he, hq,
              show zsite ((q.val : ZMod n) + -source) ≠ site0 n
                (Nat.pos_of_ne_zero (NeZero.ne n)) by simpa [sub_eq_add_neg] using hz,
              add_assoc]
      | true => simp [phaseShift, liftPacket, transferAt, he, add_assoc]

/-- A whole-packet transfer with both phases restored. The only effective
event is the exact source packet, and other atom locations are literal-fixed. -/
theorem reservedTransferWord_spec (hn : 1 < n) (P : Placement n)
    (source target : ZMod n)
    (hsource : (packetAt P false (zsite source)).Nonempty)
    (hempty : packetAt P true (zsite target) = ∅) :
    runLogged n hn P (reservedTransferWord source target) =
      some (transferAt P source target, [.transfer (packetAt P false (zsite source))]) ∧
      (reservedTransferWord source target).length ≤ 2*n+1 := by
  let L := phaseShift P false (-source)
  let R := phaseShift L true (-target)
  have hlo : packetAt R false (site0 n (by omega)) = packetAt P false (zsite source) := by
    change packetAt (phaseShift L true (-target)) false _ = _
    rw [packetAt_phaseShift_other _ _ _ (by decide)]
    rw [← zsite_zero, packetAt_phaseShift]
    simp
  have hup : packetAt R true (site0 n (by omega)) = ∅ := by
    rw [← zsite_zero]
    change packetAt (phaseShift L true (-target)) true _ = _
    rw [packetAt_phaseShift]
    simp only [sub_neg_eq_add, zero_add]
    rw [packetAt_phaseShift_other _ _ _ (by decide)]
    exact hempty
  have hg : liftGuard n (by omega) R := by
    constructor
    · exact (packetAt_nonempty _ _ _).mp (hlo.symm ▸ hsource)
    · intro hocc
      have := (packetAt_nonempty R true (site0 n (by omega))).mpr hocc
      simp [hup] at this
  have hv : step n hn R .v = some (liftPacket n (by omega) R) := by
    simp [step, hg]
  dsimp only [R, L] at hv hlo
  refine ⟨?_, reservedTransferWord_length_le source target⟩
  have hfinal := transfer_phase_restored P source target
  simp only [reservedTransferWord, runLogged_append, runLogged_phase,
    Option.bind_some, runLogged, hv, Option.map_some, emittedEvents,
    List.nil_append, List.append_nil, hlo]
  exact congrArg (fun Q => some (Q, [EffectiveEvent.transfer (packetAt P false (zsite source))]))
    hfinal

theorem packetAt_relocateAt (P : Placement n) (layer : Layer)
    (source target q : ZMod n) :
    packetAt (relocateAt P layer source target) layer (zsite q) =
      if q = target then packetAt P layer (zsite source) ∪ packetAt P layer (zsite q)
      else if q = source then ∅ else packetAt P layer (zsite q) := by
  ext a
  by_cases ht : q = target <;> by_cases hs : q = source <;>
    by_cases ha : P a = (layer, zsite source)
  all_goals simp_all [relocateAt, mem_packetAt] <;> aesop

theorem packetAt_relocateAt_other (P : Placement n) (layer other : Layer)
    (hne : other ≠ layer) (source target : ZMod n) (q : Fin n) :
    packetAt (relocateAt P layer source target) other q = packetAt P other q := by
  ext a
  by_cases ha : P a = (layer, zsite source)
  · simp [relocateAt, mem_packetAt, ha, Ne.symm hne]
  · simp [relocateAt, mem_packetAt, ha]

theorem layerView_relocateAt (P : Placement n) (layer : Layer)
    (source target : ZMod n) (hempty : packetAt P layer (zsite target) = ∅) :
    layerView (relocateAt P layer source target) layer =
      fun q => if q = target then layerView P layer source
        else if q = source then none else layerView P layer q := by
  funext q
  change (if packetAt (relocateAt P layer source target) layer (zsite q) = ∅
    then none else some (packetAt (relocateAt P layer source target) layer (zsite q))) = _
  rw [packetAt_relocateAt]
  by_cases ht : q = target
  · subst q
    change packetAt P layer ⟨target.val, ZMod.val_lt target⟩ = ∅ at hempty
    simp [hempty, layerView, zsite]
  · by_cases hs : q = source
    · subst q; simp [ht]
    · simp [ht, hs, layerView, zsite]

/-- A mapped M1 batch moves just the designated packet; all other literal
sites, including temporarily traversed future reservations, are restored. -/
theorem reservedBatchWord_spec (hn : 3 ≤ n) (P : Placement n) (layer : Layer)
    (source : ZMod n) (f : Nat) (hf : 1 ≤ f) (hfn : f ≤ n-2)
    (hsource : (packetAt P layer (zsite source)).Nonempty)
    (hholes : ∀ i : Nat, 1 ≤ i → i ≤ f →
      packetAt P layer (zsite (source-i)) = ∅) :
    runLogged n (by omega) P ((FusionLogCompression.batchWord source f).map (layerLetter layer)) =
      some (relocateAt P layer source (source-f), []) ∧
      ((FusionLogCompression.batchWord source f).map (layerLetter layer)).length ≤ 2*n+f := by
  let s : RegisteredAbsorptionChains.Execution n (Fin n) := ⟨layerView P layer, none, []⟩
  have hb : s.placed source = some (packetAt P layer (zsite source)) := by
    have hb := hsource.ne_empty
    change packetAt P layer ⟨source.val, ZMod.val_lt source⟩ ≠ ∅ at hb
    simp [s, layerView, zsite, hb]
  have hh : ∀ i : Nat, 1 ≤ i → i ≤ f → s.placed (source-i) = none := by
    intro i hi hif
    exact (layerView_eq_none P layer (source-i)).mpr (hholes i hi hif)
  obtain ⟨hfree, hrun, hcost⟩ := FusionLogCompression.batchWord_spec
    ∅ s source (packetAt P layer (zsite source)) f hn hf hfn hb hh
  obtain ⟨Q, hQ, hview, hother⟩ := layerWord_simulation (by omega) P layer s _ rfl hfree
  have heq : Q = relocateAt P layer source (source-f) := by
    apply layerSlots_ext
    intro other
    by_cases ho : other = layer
    · subst other
      apply layerView_eq_slots
      rw [hview, hrun]
      change FusionLogCompression.batchTarget (layerView P layer) source f = _
      rw [layerView_relocateAt P layer source (source-f) (hholes f hf (by omega))]
      rfl
    · rw [hother other ho]
      apply List.ext_getElem
      · simp
      · intro q hq hq'
        rw [layerSlots_getElem, layerSlots_getElem]
        exact (packetAt_relocateAt_other P layer other ho source (source-f) _).symm
  exact ⟨heq ▸ hQ, by simpa using hcost⟩

theorem collapse_phase_restored (hn : 1 < n) (P : Placement n)
    (layer : Layer) (q : ZMod n) :
    phaseShift (collapse n hn (phaseShift P layer (-q)) layer) layer q =
      relocateAt P layer (q+1) q := by
  funext a
  cases he : P a with
  | mk other r =>
    by_cases hl : other = layer
    · subst other
      by_cases hs : r = zsite (q+1)
      · have hc : (r.val : ZMod n) - q = 1 := by
          simp [hs]
        have hz : zsite ((r.val : ZMod n) + -q) = site1 n hn := by
          rw [← sub_eq_add_neg, hc, zsite_one hn]
        simp [phaseShift, collapse, relocateAt, he, hs, zsite_one hn, site0]
      · have hz : zsite ((r.val : ZMod n) + -q) ≠ site1 n hn := by
          rw [← zsite_one hn]
          intro he
          have he' := zsite_inj.mp he
          have hval : (r.val : ZMod n) = q+1 := by linear_combination he'
          exact hs (by simpa using congrArg zsite hval)
        simp [phaseShift, collapse, relocateAt, he, hs, hz, add_assoc]
    · simp [phaseShift, collapse, relocateAt, he, hl]

def phaseFusionWord (layer : Layer) (q : ZMod n) : List Letter :=
  pWord layer (-q).val ++ ([.d layer] ++ pWord layer q.val)

theorem phaseFusionWord_spec (hn : 1 < n) (P : Placement n) (layer : Layer)
    (q : ZMod n)
    (hleft : (packetAt P layer (zsite q)).Nonempty)
    (hright : (packetAt P layer (zsite (q+1))).Nonempty) :
    runLogged n hn P (phaseFusionWord layer q) =
      some (relocateAt P layer (q+1) q,
        [.fusion layer (packetAt P layer (zsite q))
          (packetAt P layer (zsite (q+1)))
          (packetAt P layer (zsite q) ∪ packetAt P layer (zsite (q+1)))]) ∧
      (phaseFusionWord layer q).length ≤ n+1 := by
  let R := phaseShift P layer (-q)
  have h0 : packetAt R layer (site0 n (by omega)) = packetAt P layer (zsite q) := by
    rw [← zsite_zero, packetAt_phaseShift]
    simp
  have h1 : packetAt R layer (site1 n hn) = packetAt P layer (zsite (q+1)) := by
    rw [← zsite_one hn, packetAt_phaseShift]
    congr 2
    ring
  have hbusy : occupiedAt R layer (site0 n (by omega)) ∧ occupiedAt R layer (site1 n hn) :=
    ⟨(packetAt_nonempty _ _ _).mp (h0.symm ▸ hleft),
      (packetAt_nonempty _ _ _).mp (h1.symm ▸ hright)⟩
  dsimp only [R] at h0 h1 hbusy
  constructor
  · simp only [phaseFusionWord, runLogged_append, runLogged_phase,
      Option.bind_some, runLogged, step_d, Option.map_some, emittedEvents,
      if_pos hbusy, List.nil_append, List.append_nil, h0, h1]
    rw [collapse_phase_restored hn]
  · have hc := inverse_phase_cost q
    simp only [phaseFusionWord, List.length_append, pWord, List.length_replicate,
      List.length_cons, List.length_nil]
    omega

theorem relocateAt_compose_empty (P : Placement n) (layer : Layer)
    (source via target : ZMod n) (hempty : packetAt P layer (zsite via) = ∅) :
    relocateAt (relocateAt P layer source via) layer via target =
      relocateAt P layer source target := by
  funext a
  by_cases hs : P a = (layer, zsite source)
  · simp [relocateAt, hs]
  · have hv : P a ≠ (layer, zsite via) := by
      intro he
      have hm := (mem_packetAt P layer (zsite via) a).mpr he
      simp [hempty] at hm
    simp [relocateAt, hs, hv]

omit [NeZero n] in
theorem gap_sites_distinct (hn : 1 < n) (q : ZMod n) (f : Nat) (hf : f ≤ n-2) :
    q ≠ q+1+(f : ZMod n) ∧ q ≠ q+1 := by
  have h1 : (1 : ZMod n) ≠ 0 := by
    intro h
    have := ZMod.one_eq_zero_iff.mp h
    omega
  constructor
  · intro h
    have hz : ((f+1 : Nat) : ZMod n) = 0 := by
      push_cast
      linear_combination -h
    have hnat := congrArg ZMod.val hz
    rw [ZMod.val_natCast_of_lt (by omega : f+1 < n), ZMod.val_zero] at hnat
    omega
  · intro h
    apply h1
    linear_combination -h

def reservedFusionWord (layer : Layer) (left right : ZMod n) (f : Nat) : List Letter :=
  (if f = 0 then [] else (FusionLogCompression.batchWord right f).map (layerLetter layer)) ++
    phaseFusionWord layer left

/-- One exact ordered fusion, with the left anchor retained, the right
anchor freed, and every other literal atom position unchanged. -/
theorem reservedFusionWord_spec (hn : 1 < n) (P : Placement n) (layer : Layer)
    (left right : ZMod n) (f : Nat) (hfn : f ≤ n-2)
    (hgap : right = left+1+(f : ZMod n))
    (hleft : (packetAt P layer (zsite left)).Nonempty)
    (hright : (packetAt P layer (zsite right)).Nonempty)
    (hholes : ∀ i : Nat, 1 ≤ i → i ≤ f →
      packetAt P layer (zsite (right-i)) = ∅) :
    runLogged n hn P (reservedFusionWord layer left right f) =
      some (relocateAt P layer right left,
        [.fusion layer (packetAt P layer (zsite left)) (packetAt P layer (zsite right))
          (packetAt P layer (zsite left) ∪ packetAt P layer (zsite right))]) ∧
      (reservedFusionWord layer left right f).length ≤ 4*n := by
  by_cases hf : f = 0
  · subst f
    have hr : right = left+1 := by simpa using hgap
    obtain ⟨hrun, hlen⟩ := phaseFusionWord_spec hn P layer left hleft (by simpa [hr] using hright)
    exact ⟨by simpa [reservedFusionWord, hr] using hrun,
      by simpa [reservedFusionWord] using
        hlen.trans (by omega : n+1 ≤ 4*n)⟩
  · have hn3 : 3 ≤ n := by omega
    have hvia : right-(f : ZMod n) = left+1 := by rw [hgap]; ring
    have hempty : packetAt P layer (zsite (left+1)) = ∅ := by
      rw [← hvia]
      exact hholes f (by omega) (by omega)
    obtain ⟨hbatch, hcost⟩ := reservedBatchWord_spec hn3 P layer right f (by omega) hfn hright hholes
    rw [hvia] at hbatch
    let Q := relocateAt P layer right (left+1)
    have hleft' : packetAt Q layer (zsite left) = packetAt P layer (zsite left) := by
      have hd := gap_sites_distinct hn left f hfn
      rw [show Q = relocateAt P layer right (left+1) from rfl, packetAt_relocateAt,
        if_neg hd.2, if_neg (hgap ▸ hd.1)]
    have hright' : packetAt Q layer (zsite (left+1)) = packetAt P layer (zsite right) := by
      simp [Q, packetAt_relocateAt, hempty]
    obtain ⟨hfusion, hfcost⟩ := phaseFusionWord_spec hn Q layer left
      (hleft'.symm ▸ hleft) (hright'.symm ▸ hright)
    have hfinal : relocateAt Q layer (left+1) left = relocateAt P layer right left :=
      relocateAt_compose_empty P layer right (left+1) left hempty
    dsimp only [Q] at hfusion hleft' hright' hfinal
    refine ⟨?_, ?_⟩
    · simp only [reservedFusionWord, if_neg hf, runLogged_append, hbatch,
        Option.bind_some, hfusion, Option.map_some, List.nil_append]
      simp only [hleft', hright', hfinal]
    · simp only [reservedFusionWord, if_neg hf, List.length_append]
      omega

end RSR2History
