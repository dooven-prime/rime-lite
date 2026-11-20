import RSR2History.LayerExecutionAdapter

namespace RSR2History
open RSR2.Parametric
open RegisteredAbsorptionChains (GapFrame)

/-- The number of nonempty packets on the indicated layer. -/
def layerRank (P : Placement n) (layer : Layer) : Nat :=
  (cyclicSignature P layer).length

@[simp] theorem layerRank_eq_occupied_length (P : Placement n) (layer : Layer) :
    layerRank P layer = (occupiedSites P layer).length := by
  simp [layerRank, signature_eq_occupied_map]

theorem layerRank_le (P : Placement n) (layer : Layer) : layerRank P layer ≤ n := by
  rw [layerRank_eq_occupied_length]
  exact (List.length_filter_le _ _).trans_eq List.length_finRange

/-- Raw-letter cost of a silent placement on one layer, including empty layers. -/
def layerBudget (n rank : Nat) : Nat :=
  if rank = 0 then 0 else (3*n-rank)*(rank-1)+(n-1)

def silentBudget (n : Nat) (P : Placement n) : Nat :=
  layerBudget n (layerRank P false) + layerBudget n (layerRank P true)

private theorem frame_short {n r : Nat} [NeZero n] [NeZero r]
    (hn : 1 < n) (start target : GapFrame n r (Fin n))
    (blocks : start.block = target.block) :
    ∃ word, RegisteredAbsorptionChains.FusionFree ∅
        ⟨start.decode, none, []⟩ word ∧
      (RegisteredAbsorptionChains.run ∅ ⟨start.decode, none, []⟩ word).placed =
        target.decode ∧
      word.length ≤ layerBudget n r := by
  have hr : 0 < r := Nat.pos_of_ne_zero (NeZero.ne r)
  have hrn : r ≤ n := by
    simpa using Fintype.card_le_of_injective start.position start.position_injective
  by_cases hone : r = 1
  · subst r
    have hg : start.gap = target.gap := by
      funext j
      have hj : j = 0 := Subsingleton.elim _ _
      subst j
      have hs := start.gap_total
      have ht := target.gap_total
      have hsum (f : ZMod 1 → Nat) : (∑ j, f j) = f 0 := by
        calc
          _ = ∑ _j : ZMod 1, f 0 := Finset.sum_congr rfl (fun j _ => congrArg f (Subsingleton.elim j 0))
          _ = f 0 := by simp
      rw [hsum] at hs ht
      exact hs.trans ht.symm
    obtain ⟨word, hf, he, hl⟩ := FusionLogCompression.gapFramePlacement_phase
      ∅ ⟨start.decode, none, []⟩ start target rfl hg blocks
    exact ⟨word, hf, congrArg RegisteredAbsorptionChains.Execution.placed he,
      by simpa [layerBudget] using hl⟩
  · by_cases hfull : r = n
    · subst r
      have hg : start.gap = target.gap := by
        funext i
        have hs := start.gap_total
        have ht := target.gap_total
        have hls := Finset.single_le_sum (fun j _ => Nat.zero_le (start.gap j))
          (Finset.mem_univ i)
        have hlt := Finset.single_le_sum (fun j _ => Nat.zero_le (target.gap j))
          (Finset.mem_univ i)
        omega
      obtain ⟨word, hf, he, hl⟩ := FusionLogCompression.gapFramePlacement_phase
        ∅ ⟨start.decode, none, []⟩ start target rfl hg blocks
      refine ⟨word, hf, congrArg RegisteredAbsorptionChains.Execution.placed he, ?_⟩
      simp only [layerBudget, if_neg (NeZero.ne n)]
      omega
    · obtain ⟨word, hf, he, hl⟩ := FusionLogCompression.gapFramePlacement_short
        ∅ ⟨start.decode, none, []⟩ start target (by omega) (by omega) rfl blocks
      exact ⟨word, hf, congrArg RegisteredAbsorptionChains.Execution.placed he,
        by simpa [layerBudget, NeZero.ne r] using hl⟩

theorem layerView_eq_slots {n : Nat} [NeZero n] {P Q : Placement n} {layer : Layer}
    (h : layerView P layer = layerView Q layer) : layerSlots P layer = layerSlots Q layer := by
  apply List.ext_getElem
  · simp
  · intro k hk hk'
    simp only [layerSlots_getElem]
    have hk : k < n := by simpa using hk
    have he := congrFun h (k : ZMod n)
    simp only [layerView, ZMod.val_natCast, Nat.mod_eq_of_lt hk] at he
    by_cases hp : packetAt P layer ⟨k, hk⟩ = ∅ <;>
      by_cases hq : packetAt Q layer ⟨k, hk⟩ = ∅ <;> simp_all

/-- Bounded silent routing on exactly one layer; the opposite layer is literal-fixed. -/
theorem layer_silent_short (n : Nat) (hn : 1 < n) (P Q : Placement n) (layer : Layer)
    (hsig : (cyclicSignature P layer).IsRotated (cyclicSignature Q layer)) :
    ∃ R word, runLogged n hn P word = some (R, []) ∧
      layerSlots R layer = layerSlots Q layer ∧
      (∀ other, other ≠ layer → layerSlots R other = layerSlots P other) ∧
      word.length ≤ layerBudget n (layerRank P layer) := by
  classical
  have : NeZero n := ⟨by omega⟩
  by_cases hempty : (occupiedSites P layer).length = 0
  · have hq : (occupiedSites Q layer).length = 0 := by
      have he := congrArg List.length hsig.choose_spec
      simpa [signature_eq_occupied_map, hempty] using he.symm
    have hslot (S : Placement n) (hS : (occupiedSites S layer).length = 0) :
        layerSlots S layer = List.replicate n ∅ := by
      apply List.ext_getElem
      · simp
      · intro k hk hk'
        simp only [layerSlots_getElem, List.getElem_replicate]
        by_contra hb
        have hm : (⟨k, by simpa using hk⟩ : Fin n) ∈ occupiedSites S layer := by
          simp [occupiedSites, hb]
        have hnil := List.eq_nil_of_length_eq_zero hS
        simp [hnil] at hm
    refine ⟨P, [], rfl, (hslot P hempty).trans (hslot Q hq).symm, fun _ _ => rfl, ?_⟩
    simp [layerBudget, layerRank_eq_occupied_length, hempty]
  · have : NeZero (occupiedSites P layer).length := ⟨hempty⟩
    obtain ⟨start, target, hs, ht, hb⟩ := common_layer_frames P Q layer rfl hsig
    obtain ⟨word, hf, he, hl⟩ := frame_short hn start target hb
    obtain ⟨R, hr, hv, ho⟩ := layerWord_simulation hn P layer
      ⟨start.decode, none, []⟩ word hs hf
    refine ⟨R, word.map (layerLetter layer), hr, ?_, ho, ?_⟩
    · apply layerView_eq_slots
      exact hv.trans (he.trans ht)
    · simpa using hl

/-- H1 with its sharp rank-sensitive single-ring raw-letter budgets. -/
theorem silent_preparation_short (n : Nat) (hn : 1 < n) (P Q : Placement n)
    (hsig : SameCyclicSignatures P Q) :
    ∃ word, runLogged n hn P word = some (Q, []) ∧ word.length ≤ silentBudget n P := by
  obtain ⟨R, lower, hl, hlayer, hother, hcostl⟩ := layer_silent_short n hn P Q false (hsig false)
  have hupper : cyclicSignature R true = cyclicSignature P true := by
    unfold cyclicSignature
    rw [hother true (by decide)]
  obtain ⟨S, upper, hu, hulayer, huother, hcostu⟩ :=
    layer_silent_short n hn R Q true (by rw [hupper]; exact hsig true)
  have hSQ : S = Q := by
    apply layerSlots_ext
    intro layer
    cases layer with
    | false => exact (huother false (by decide)).trans hlayer
    | true => exact hulayer
  subst S
  refine ⟨lower++upper, ?_, ?_⟩
  · simp [runLogged_append, hl, hu]
  · have he : layerRank R true = layerRank P true := congrArg List.length hupper
    simp only [List.length_append, silentBudget]
    rw [he] at hcostu
    omega

theorem layerBudget_le (n rank : Nat) (hn : 0 < n) (hr : rank ≤ n) :
    layerBudget n rank ≤ (2*n+1)*(n-1) := by
  unfold layerBudget
  split
  · omega
  · rename_i hpos
    have h1 : 1 ≤ rank := by omega
    have h2 : rank ≤ 3*n := by omega
    have hn1 : n-1+1 = n := by omega
    have hr1 : rank-1+1 = rank := by omega
    have hsub : 3*n-rank+rank = 3*n := Nat.sub_add_cancel h2
    nlinarith [Nat.zero_le ((n-rank)*(2*n-rank+1)), Nat.sub_add_cancel hr,
      Nat.sub_add_cancel (show rank ≤ 2*n by omega)]

theorem silentBudget_le (n : Nat) (hn : 0 < n) (P : Placement n) :
    silentBudget n P ≤ 2*(2*n+1)*(n-1) := by
  have h0 := layerBudget_le n (layerRank P false) hn (layerRank_le P false)
  have h1 := layerBudget_le n (layerRank P true) hn (layerRank_le P true)
  unfold silentBudget
  nlinarith

end RSR2History
