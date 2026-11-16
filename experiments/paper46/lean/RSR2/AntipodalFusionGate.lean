import RSR2.LowerRestrictedOrder
import RSR2.PortCostSharpness

/-!
# Antipodal target purity and the lower fusion gate

All statements concern the original guarded executor. Target purity is read
backwards from the final same-packet relation; no loading order, intermediate
physical coordinates, or restriction to singleton transfers is imposed.
-/

namespace RSR2.Parametric

def antipodalLeft (m : Nat) (i : Fin m) : Fin (2 * m) :=
  ⟨i.val, by omega⟩

def antipodalRight (m : Nat) (i : Fin m) : Fin (2 * m) :=
  ⟨i.val + m, by omega⟩

def antipodalLabel (m : Nat) (a : Fin (2 * m)) : Nat := a.val % m

/-- No current packet combines atoms from different target pairs. -/
def AntipodalPure (m : Nat) (P : Placement (2 * m)) : Prop :=
  ∀ a b, samePacket P a b → antipodalLabel m a = antipodalLabel m b

/-- The final unordered partition, with no layer or physical-site requirement. -/
def AntipodalEndpoint (m : Nat) (P : Placement (2 * m)) : Prop :=
  ∀ a b, samePacket P a b ↔ antipodalLabel m a = antipodalLabel m b

theorem antipodalLabel_left (m : Nat) (i : Fin m) :
    antipodalLabel m (antipodalLeft m i) = i.val := by
  exact Nat.mod_eq_of_lt i.isLt

theorem antipodalLabel_right (m : Nat) (i : Fin m) :
    antipodalLabel m (antipodalRight m i) = i.val := by
  simp [antipodalLabel, antipodalRight, Nat.mod_eq_of_lt i.isLt]

theorem antipodal_atom_cases (m : Nat) (a : Fin (2 * m)) :
    ∃ i : Fin m, a = antipodalLeft m i ∨ a = antipodalRight m i := by
  by_cases h : a.val < m
  · exact ⟨⟨a.val, h⟩, Or.inl (Fin.ext rfl)⟩
  · refine ⟨⟨a.val - m, by have := a.isLt; omega⟩, Or.inr ?_⟩
    apply Fin.ext
    simp only [antipodalRight]
    omega

theorem antipodal_equal_label_cases (m : Nat) (a b : Fin (2 * m))
    (hlabel : antipodalLabel m a = antipodalLabel m b) :
    a = b ∨ ∃ i : Fin m,
      (a = antipodalLeft m i ∧ b = antipodalRight m i) ∨
      (a = antipodalRight m i ∧ b = antipodalLeft m i) := by
  obtain ⟨i, ha⟩ := antipodal_atom_cases m a
  obtain ⟨j, hb⟩ := antipodal_atom_cases m b
  rcases ha with rfl | rfl <;> rcases hb with rfl | rfl
  all_goals
    have hij : i = j := Fin.ext (by
      simpa only [antipodalLabel_left, antipodalLabel_right] using hlabel)
    subst j
  · exact Or.inl rfl
  · exact Or.inr ⟨i, Or.inl ⟨rfl, rfl⟩⟩
  · exact Or.inr ⟨i, Or.inr ⟨rfl, rfl⟩⟩
  · exact Or.inl rfl

theorem AntipodalPure.of_run (m : Nat) (hm : 0 < m)
    (P Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) P word = some Q)
    (hpure : AntipodalPure m Q) : AntipodalPure m P := by
  intro a b hab
  exact hpure a b (run_samePacket_mono (2 * m) (by omega) P Q word hrun a b hab)

/-- A complete lower pair forbids any other complete pair from remaining
below. This is a geometric fact about every pure source-ordered placement. -/
theorem antipodal_complete_lower_pair_blocks_other
    (m : Nat) (hm : 0 < m) (P : Placement (2 * m))
    (horder : LowerRestrictedOrdered P) (hpure : AntipodalPure m P)
    (i j : Fin m) (hne : i ≠ j)
    (hi : (P (antipodalLeft m i)).1 = false)
    (hpair : samePacket P (antipodalLeft m i) (antipodalRight m i)) :
    (P (antipodalLeft m j)).1 = true ∨
      (P (antipodalRight m j)).1 = true := by
  have hn : 0 < 2 * m := by omega
  have hli : sourceAtom (2 * m) hn (i.val : Int) = antipodalLeft m i :=
    sourceAtom_fin (2 * m) hn (antipodalLeft m i)
  have hri : sourceAtom (2 * m) hn ((i.val : Int) + m) = antipodalRight m i := by
    simpa only [antipodalRight, Int.natCast_add] using
      sourceAtom_fin (2 * m) hn (antipodalRight m i)
  have hlj : sourceAtom (2 * m) hn (j.val : Int) = antipodalLeft m j :=
    sourceAtom_fin (2 * m) hn (antipodalLeft m j)
  have hrj : sourceAtom (2 * m) hn ((j.val : Int) + m) = antipodalRight m j := by
    simpa only [antipodalRight, Int.natCast_add] using
      sourceAtom_fin (2 * m) hn (antipodalRight m j)
  have hwrap : sourceAtom (2 * m) hn ((j.val : Int) + 2 * m) =
      antipodalLeft m j := by
    simpa [Int.natCast_mul] using
      (sourceAtom_periodic (2 * m) hn (j.val : Int)).trans hlj
  have hright : (P (antipodalRight m i)).1 = false := by rw [← hpair]; exact hi
  have hinterval := lowerRestrictedOrdered_packet_cyclic_interval (2 * m) hn P
    horder (i.val : Int) ((i.val : Int) + m) (by omega) (by omega)
    (by simpa only [hli] using hi) (by simpa only [hri] using hright)
    (by simpa only [hli, hri, samePacket] using hpair)
  have hdistinct : i.val ≠ j.val := fun h => hne (Fin.ext h)
  have hnotleft : P (antipodalLeft m j) ≠ P (antipodalLeft m i) := by
    intro h
    have hlabel := hpure _ _ h
    simp only [antipodalLabel_left] at hlabel
    omega
  have hnotright : P (antipodalRight m j) ≠ P (antipodalLeft m i) := by
    intro h
    have hlabel := hpure _ _ h
    simp only [antipodalLabel_left, antipodalLabel_right] at hlabel
    omega
  cases hjl : (P (antipodalLeft m j)).1 with
  | true => exact Or.inl rfl
  | false =>
      cases hjr : (P (antipodalRight m j)).1 with
      | true => exact Or.inr rfl
      | false =>
          exfalso
          by_cases hij : i.val < j.val
          · rcases hinterval with hfirst | hsecond
            · apply hnotleft
              simpa only [hlj, hli] using hfirst (j.val : Int)
                (by omega) (by have := j.isLt; omega) (by simpa only [hlj] using hjl)
            · apply hnotright
              simpa only [hrj, hli] using hsecond ((j.val : Int) + m)
                (by omega) (by have := j.isLt; omega) (by simpa only [hrj] using hjr)
          · rcases hinterval with hfirst | hsecond
            · apply hnotright
              simpa only [hrj, hli] using hfirst ((j.val : Int) + m)
                (by have := i.isLt; omega) (by omega) (by simpa only [hrj] using hjr)
            · apply hnotleft
              simpa only [hwrap, hli] using hsecond ((j.val : Int) + 2 * m)
                (by have := i.isLt; omega) (by omega) (by simpa only [hwrap] using hjl)

/-- Every target pair that is still entirely below has already merged.
The property is preserved by all subsequent successful actions. -/
def AntipodalLowerResolved (m : Nat) (P : Placement (2 * m)) : Prop :=
  ∀ i : Fin m,
    (P (antipodalLeft m i)).1 = false →
    (P (antipodalRight m i)).1 = false →
    samePacket P (antipodalLeft m i) (antipodalRight m i)

theorem antipodal_lowerResolved_of_complete_pair
    (m : Nat) (hm : 0 < m) (P : Placement (2 * m))
    (horder : LowerRestrictedOrdered P) (hpure : AntipodalPure m P)
    (i : Fin m) (hi : (P (antipodalLeft m i)).1 = false)
    (hpair : samePacket P (antipodalLeft m i) (antipodalRight m i)) :
    AntipodalLowerResolved m P := by
  intro j hjl hjr
  by_cases hij : i = j
  · simpa only [hij] using hpair
  · rcases antipodal_complete_lower_pair_blocks_other m hm P horder hpure
      i j hij hi hpair with h | h
    · rw [h] at hjl; contradiction
    · rw [h] at hjr; contradiction

private theorem step_lower_preimage (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (hs : step n hn P letter = some Q) (a : Fin n)
    (hq : (Q a).1 = false) : (P a).1 = false := by
  cases letter with
  | p layer =>
      have he : Q = rotate n (by omega) P layer := by
        simpa only [step_p, Option.some.injEq] using hs.symm
      rw [he] at hq
      unfold rotate at hq
      split at hq <;> simp_all
  | d layer =>
      have he : Q = collapse n hn P layer := by
        simpa only [step_d, Option.some.injEq] using hs.symm
      rw [he] at hq
      unfold collapse at hq
      split at hq
      · rename_i hp
        exact (congrArg Prod.fst hp).trans hq
      · exact hq
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
      unfold liftPacket at hq
      split at hq
      · contradiction
      · exact hq

theorem AntipodalLowerResolved.step (m : Nat) (hm : 0 < m)
    (P Q : Placement (2 * m)) (letter : Letter)
    (hs : step (2 * m) (by omega) P letter = some Q)
    (hresolved : AntipodalLowerResolved m P) : AntipodalLowerResolved m Q := by
  intro i hil hir
  have hleft := step_lower_preimage (2 * m) (by omega) P Q letter hs _ hil
  have hright := step_lower_preimage (2 * m) (by omega) P Q letter hs _ hir
  apply run_samePacket_mono (2 * m) (by omega) P Q [letter]
    (by simp [run, hs])
  exact hresolved i hleft hright

private theorem lowerFusionCharge_pair (m : Nat) (hm : 0 < m)
    (P Q : Placement (2 * m)) (letter : Letter)
    (hs : step (2 * m) (by omega) P letter = some Q)
    (hpure : AntipodalPure m Q)
    (hc : lowerFusionCharge (2 * m) (by omega) P letter = 1) :
    ∃ i : Fin m,
      (P (antipodalLeft m i) = (false, site0 (2 * m) (by omega)) ∧
       P (antipodalRight m i) = (false, site1 (2 * m) (by omega))) ∨
      (P (antipodalRight m i) = (false, site0 (2 * m) (by omega)) ∧
       P (antipodalLeft m i) = (false, site1 (2 * m) (by omega))) := by
  classical
  cases letter with
  | p _ => simp [lowerFusionCharge] at hc
  | v => simp [lowerFusionCharge] at hc
  | d layer =>
      cases layer with
      | true => simp [lowerFusionCharge] at hc
      | false =>
          have he : collapse (2 * m) (by omega) P false = Q := by
            simpa only [step_d, Option.some.injEq] using hs
          have hports : occupiedAt P false (site0 (2 * m) (by omega)) ∧
              occupiedAt P false (site1 (2 * m) (by omega)) := by
            by_cases hports : occupiedAt P false (site0 (2 * m) (by omega)) ∧
                occupiedAt P false (site1 (2 * m) (by omega))
            · exact hports
            · simp [lowerFusionCharge, hports] at hc
          obtain ⟨⟨a, ha⟩, ⟨b, hb⟩⟩ := hports
          have hsame : samePacket Q a b := by
            rw [← he]
            exact (collapse_samePacket_iff (2 * m) (by omega) P false a b).mpr
              (Or.inr (Or.inl ⟨ha, hb⟩))
          rcases antipodal_equal_label_cases m a b (hpure a b hsame) with hab | ⟨i, h⟩
          · subst b
            have hv := congrArg (fun loc => loc.2.val) (ha.symm.trans hb)
            simp [site0, site1] at hv
          · rcases h with ⟨rfl, rfl⟩ | ⟨rfl, rfl⟩
            · exact ⟨i, Or.inl ⟨ha, hb⟩⟩
            · exact ⟨i, Or.inr ⟨ha, hb⟩⟩

theorem antipodal_fusion_resolves_lower (m : Nat) (hm : 0 < m)
    (P Q : Placement (2 * m)) (letter : Letter)
    (hs : step (2 * m) (by omega) P letter = some Q)
    (horder : LowerRestrictedOrdered Q) (hpure : AntipodalPure m Q)
    (hc : lowerFusionCharge (2 * m) (by omega) P letter = 1) :
    AntipodalLowerResolved m Q := by
  obtain ⟨i, hports⟩ := lowerFusionCharge_pair m hm P Q letter hs hpure hc
  have hletter : letter = .d false := by
    cases letter with
    | p _ => simp [lowerFusionCharge] at hc
    | v => simp [lowerFusionCharge] at hc
    | d layer => cases layer <;> simp_all [lowerFusionCharge]
  subst letter
  have he : collapse (2 * m) (by omega) P false = Q := by
    simpa only [step_d, Option.some.injEq] using hs
  have hpair : samePacket Q (antipodalLeft m i) (antipodalRight m i) := by
    rw [← he]
    exact (collapse_samePacket_iff (2 * m) (by omega) P false _ _).mpr
      (Or.inr (hports.imp id (fun h => ⟨h.2, h.1⟩)))
  have hleft : (Q (antipodalLeft m i)).1 = false := by
    rw [← he]
    rcases hports with ⟨hl, _⟩ | ⟨_, hl⟩ <;>
      simp [collapse, hl, site0, site1]
  exact antipodal_lowerResolved_of_complete_pair m hm Q horder hpure i hleft hpair

theorem antipodal_resolved_fusionCharge_zero (m : Nat) (hm : 0 < m)
    (P Q : Placement (2 * m)) (letter : Letter)
    (hs : step (2 * m) (by omega) P letter = some Q)
    (hpure : AntipodalPure m Q) (hresolved : AntipodalLowerResolved m P) :
    lowerFusionCharge (2 * m) (by omega) P letter = 0 := by
  have hle := lowerFusionCharge_le_one (2 * m) (by omega) P letter
  by_cases hz : lowerFusionCharge (2 * m) (by omega) P letter = 0
  · exact hz
  · have hc : lowerFusionCharge (2 * m) (by omega) P letter = 1 := by omega
    obtain ⟨i, hports⟩ := lowerFusionCharge_pair m hm P Q letter hs hpure hc
    rcases hports with ⟨hl, hr⟩ | ⟨hr, hl⟩
    all_goals
      have hsame := hresolved i (congrArg Prod.fst hl) (congrArg Prod.fst hr)
      have hv := congrArg (fun loc => loc.2.val) (hl.symm.trans (hsame.trans hr))
      simp [site0, site1] at hv

theorem runWithLowerPacketLedger_antipodalResolved_fusions_zero
    (m : Nat) (hm : 0 < m) (P Q : Placement (2 * m))
    (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger (2 * m) (by omega) P word =
      some (Q, fusions, nonfusions))
    (hpure : AntipodalPure m Q) (hresolved : AntipodalLowerResolved m P) :
    fusions = 0 := by
  induction word generalizing P fusions nonfusions with
  | nil =>
      have h : P = Q ∧ 0 = fusions ∧ 0 = nonfusions := by
        simpa only [runWithLowerPacketLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      omega
  | cons letter rest ih =>
      cases hs : step (2 * m) (by omega) P letter with
      | none => simp [runWithLowerPacketLedger, hs] at hrun
      | some P' =>
          cases ht : runWithLowerPacketLedger (2 * m) (by omega) P' rest with
          | none => simp [runWithLowerPacketLedger, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, f, z⟩
              have h : R = Q ∧ lowerFusionCharge (2 * m) (by omega) P letter + f = fusions ∧
                  lowerNonfusionCharge (2 * m) (by omega) P letter + z = nonfusions := by
                simpa only [runWithLowerPacketLedger, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have ht' : runWithLowerPacketLedger (2 * m) (by omega) P' rest =
                  some (Q, f, z) := by simpa only [h.1] using ht
              have hplain : run (2 * m) (by omega) P' rest = some Q := by
                have hp := runWithLowerPacketLedger_project (2 * m) (by omega) P' rest
                rw [ht'] at hp
                exact hp.symm
              have hpure' := AntipodalPure.of_run m hm P' Q rest hplain hpure
              have hc := antipodal_resolved_fusionCharge_zero m hm P P' letter hs hpure' hresolved
              have hf := ih P' f z ht' (hresolved.step m hm P P' letter hs)
              omega

/-- Target purity and the lower restricted order bound effective lower
fusions along the original guarded word. The initial placement is arbitrary
subject to that order, and whole-packet elevators remain allowed. -/
theorem runWithLowerPacketLedger_antipodal_fusions_le_one
    (m : Nat) (hm : 0 < m) (P Q : Placement (2 * m))
    (word : List Letter) (fusions nonfusions : Nat)
    (hrun : runWithLowerPacketLedger (2 * m) (by omega) P word =
      some (Q, fusions, nonfusions))
    (hpure : AntipodalPure m Q) (horder : LowerRestrictedOrdered P) :
    fusions ≤ 1 := by
  induction word generalizing P fusions nonfusions with
  | nil =>
      have h : P = Q ∧ 0 = fusions ∧ 0 = nonfusions := by
        simpa only [runWithLowerPacketLedger, Option.some.injEq, Prod.mk.injEq] using hrun
      omega
  | cons letter rest ih =>
      cases hs : step (2 * m) (by omega) P letter with
      | none => simp [runWithLowerPacketLedger, hs] at hrun
      | some P' =>
          cases ht : runWithLowerPacketLedger (2 * m) (by omega) P' rest with
          | none => simp [runWithLowerPacketLedger, hs, ht] at hrun
          | some result =>
              rcases result with ⟨R, f, z⟩
              have h : R = Q ∧ lowerFusionCharge (2 * m) (by omega) P letter + f = fusions ∧
                  lowerNonfusionCharge (2 * m) (by omega) P letter + z = nonfusions := by
                simpa only [runWithLowerPacketLedger, hs, ht, Option.bind_some,
                  Option.map_some, Option.some.injEq, Prod.mk.injEq] using hrun
              have ht' : runWithLowerPacketLedger (2 * m) (by omega) P' rest =
                  some (Q, f, z) := by simpa only [h.1] using ht
              have hplain : run (2 * m) (by omega) P' rest = some Q := by
                have hp := runWithLowerPacketLedger_project (2 * m) (by omega) P' rest
                rw [ht'] at hp
                exact hp.symm
              have hpure' := AntipodalPure.of_run m hm P' Q rest hplain hpure
              have horder' := lowerRestrictedOrdered_step (2 * m) (by omega) P P' letter horder hs
              by_cases hc : lowerFusionCharge (2 * m) (by omega) P letter = 0
              · have hf := ih P' f z ht' horder'
                omega
              · have hone : lowerFusionCharge (2 * m) (by omega) P letter = 1 := by
                  have hle := lowerFusionCharge_le_one (2 * m) (by omega) P letter
                  omega
                have hresolved := antipodal_fusion_resolves_lower m hm P P' letter hs horder' hpure' hone
                have hf := runWithLowerPacketLedger_antipodalResolved_fusions_zero
                  m hm P' Q rest f z ht' hpure hresolved
                omega

/-- Every successful implementation of the antipodal unordered partition
has a faithful lower-packet ledger containing at most one effective fusion. -/
theorem antipodal_lower_fusion_gate
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    ∃ fusions nonfusions,
      runWithLowerPacketLedger (2 * m) (by omega) (seed (2 * m)) word =
        some (Q, fusions, nonfusions) ∧ fusions ≤ 1 := by
  obtain ⟨f, z, hl, _, _⟩ := run_exists_lowerPacketLedger (2 * m) (by omega)
    (seed (2 * m)) Q word hrun
  refine ⟨f, z, hl, ?_⟩
  exact runWithLowerPacketLedger_antipodal_fusions_le_one m hm _ Q word f z hl
    (fun a b h => (htarget a b).mp h) (lowerRestrictedOrdered_seed (2 * m))

theorem antipodal_endpoint_lower_coincide
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m))
    (horder : LowerRestrictedOrdered Q) (htarget : AntipodalEndpoint m Q)
    (a b : Fin (2 * m)) (ha : (Q a).1 = false) (hb : (Q b).1 = false) :
    samePacket Q a b := by
  have hlocation : ∀ c : Fin (2 * m), ∃ i : Fin m, Q c = Q (antipodalLeft m i) := by
    intro c
    obtain ⟨i, hc⟩ := antipodal_atom_cases m c
    refine ⟨i, ?_⟩
    rcases hc with rfl | rfl
    · rfl
    · exact (htarget _ _).mpr (by simp only [antipodalLabel_left, antipodalLabel_right])
  obtain ⟨i, hi⟩ := hlocation a
  obtain ⟨j, hj⟩ := hlocation b
  have hil : (Q (antipodalLeft m i)).1 = false := by rw [← hi]; exact ha
  have hjl : (Q (antipodalLeft m j)).1 = false := by rw [← hj]; exact hb
  have hpairi : samePacket Q (antipodalLeft m i) (antipodalRight m i) :=
    (htarget _ _).mpr (by simp only [antipodalLabel_left, antipodalLabel_right])
  have hpairj : samePacket Q (antipodalLeft m j) (antipodalRight m j) :=
    (htarget _ _).mpr (by simp only [antipodalLabel_left, antipodalLabel_right])
  have hij : i = j := by
    by_cases hij : i = j
    · exact hij
    · have hjr : (Q (antipodalRight m j)).1 = false := by rw [← hpairj]; exact hjl
      rcases antipodal_complete_lower_pair_blocks_other m hm Q horder
        (fun c d h => (htarget c d).mp h) i j hij hil hpairi with h | h
      · rw [h] at hjl; contradiction
      · rw [h] at hjr; contradiction
  subst j
  exact hi.trans hj.symm

private theorem lowerPacketCount_le_one_of_coincide
    (n : Nat) (P : Placement n)
    (hcoincide : ∀ a b, (P a).1 = false → (P b).1 = false → samePacket P a b) :
    lowerPacketCount P ≤ 1 := by
  classical
  by_cases hnonempty : ∃ a, (P a).1 = false
  · obtain ⟨a, ha⟩ := hnonempty
    let q : Site n := (P a).2
    have hq : occupiedAt P false q := ⟨a, Prod.ext ha rfl⟩
    have hother : ∀ r : Site n, r ≠ q → ¬ occupiedAt P false r := by
      intro r hne ⟨b, hb⟩
      have hbLower : (P b).1 = false := congrArg Prod.fst hb
      have he := congrArg Prod.snd (hcoincide a b ha hbLower)
      have her : q = r := he.trans (congrArg Prod.snd hb)
      exact hne her.symm
    have hrest : ((List.finRange n).erase q).countP
        (fun r => decide (occupiedAt P false r)) = 0 := by
      apply List.countP_eq_zero.mpr
      intro r hr
      have hne : r ≠ q := by
        intro he
        subst r
        exact (List.nodup_finRange n).not_mem_erase hr
      simp [hother r hne]
    have hperm := (List.perm_cons_erase (List.mem_finRange q)).countP_eq
      (fun r => decide (occupiedAt P false r))
    have hcount : lowerPacketCount P = 1 := by
      unfold lowerPacketCount
      rw [hperm]
      simp [hrest, hq]
    omega
  · have hzero : lowerPacketCount P = 0 := by
      apply List.countP_eq_zero.mpr
      intro q _
      have hnot : ¬ occupiedAt P false q := by
        intro ⟨a, ha⟩
        exact hnonempty ⟨a, congrArg Prod.fst ha⟩
      simp [hnot]
    omega

theorem antipodal_endpoint_lowerPacketCount_le_one
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m))
    (horder : LowerRestrictedOrdered Q) (htarget : AntipodalEndpoint m Q) :
    lowerPacketCount Q ≤ 1 := by
  apply lowerPacketCount_le_one_of_coincide
  exact antipodal_endpoint_lower_coincide m hm Q horder htarget

/-- These bounds concern the same original history, not its transfer mass
or a replacement loading strategy. -/
theorem antipodal_run_verticalCount_lower_bound
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    2 * m - 2 ≤ verticalCount word := by
  obtain ⟨f, z, hl, hf⟩ := antipodal_lower_fusion_gate m hm Q word hrun htarget
  have hbalance := (runWithLowerPacketLedger_balance (2 * m) (by omega)
    (seed (2 * m)) Q word f z hl).1
  have horder := singleton_run_lowerRestrictedOrdered (2 * m) (by omega) word Q hrun
  have hpackets := antipodal_endpoint_lowerPacketCount_le_one m hm Q horder htarget
  rw [seed_lowerPacketCount] at hbalance
  omega

theorem antipodal_endpoint_atom_has_mate
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m))
    (htarget : AntipodalEndpoint m Q) (a : Fin (2 * m)) :
    ∃ b, a ≠ b ∧ samePacket Q a b := by
  obtain ⟨i, ha⟩ := antipodal_atom_cases m a
  rcases ha with rfl | rfl
  · refine ⟨antipodalRight m i, ?_, (htarget _ _).mpr ?_⟩
    · intro he
      have hv := congrArg Fin.val he
      simp only [antipodalLeft, antipodalRight] at hv
      omega
    · simp only [antipodalLabel_left, antipodalLabel_right]
  · refine ⟨antipodalLeft m i, ?_, (htarget _ _).mpr ?_⟩
    · intro he
      have hv := congrArg Fin.val he
      simp only [antipodalLeft, antipodalRight] at hv
      omega
    · simp only [antipodalLabel_left, antipodalLabel_right]

theorem antipodal_run_lowerRotationCount_lower_bound
    (m : Nat) (hm : 2 ≤ m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    2 * m - 2 ≤ lowerRotationCount word := by
  let a : Fin (2 * m) := ⟨2, by omega⟩
  obtain ⟨b, hne, hsame⟩ := antipodal_endpoint_atom_has_mate m (by omega) Q htarget a
  exact singleton_run_mergedAtom_rotation_lower_bound (2 * m) (by omega)
    Q word a b (by change 1 < 2; decide) hne hrun hsame

theorem antipodal_run_upperRotationCount_lower_bound
    (m : Nat) (hm : 0 < m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    2 * m - 3 ≤ rawUpperRotationCount word := by
  have hv := antipodal_run_verticalCount_lower_bound m hm Q word hrun htarget
  have hb := singleton_run_upperPortVacancy_bound (2 * m) (by omega) Q word hrun
  omega

theorem antipodal_run_lowerPortCost_lower_bound
    (m : Nat) (hm : 2 ≤ m) (Q : Placement (2 * m)) (word : List Letter)
    (hrun : run (2 * m) (by omega) (seed (2 * m)) word = some Q)
    (htarget : AntipodalEndpoint m Q) :
    4 * m - 3 ≤ lowerPortCost word := by
  obtain ⟨f, z, hl, _⟩ := antipodal_lower_fusion_gate m (by omega) Q word hrun htarget
  have hb := runWithLowerPacketLedger_port_balance (2 * m) (by omega)
    (seed (2 * m)) Q word f z hl
  have hp := antipodal_endpoint_lowerPacketCount_le_one m (by omega) Q
    (singleton_run_lowerRestrictedOrdered (2 * m) (by omega) word Q hrun) htarget
  have hr := antipodal_run_lowerRotationCount_lower_bound m hm Q word hrun htarget
  rw [seed_lowerPacketCount] at hb
  omega

end RSR2.Parametric
