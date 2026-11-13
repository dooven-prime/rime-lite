import Paper44.ProperCarrierPrefix
import Paper44.ProperCarrierFibre
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Data.Subtype

/-! # Actual carrier-indexed prefix enumeration

The extra marker is a carrier coordinate, not another retained event. A
saturated prefix ending at checkpoint `b` has `r-b+1` compatible carriers
of absorbed size `r`. The marker records which one. Short prefixes already
determine their entire current carrier.

The parameter equivalences are composed with the actual-label range
equivalence. Thus the counts classify genuine generated labels, preserving
their carrier index. The final fibre corollaries count literal placements,
not histories. The all-sector observer quotient is assembled separately.
-/

namespace Paper44

open RegisteredAbsorptionChains

def padCode {a N : ℕ} (_h : a ≤ N) (c : Code a) : Code N :=
  fun i => if hi : i.val < a then c ⟨i.val, hi⟩ else none

@[simp] theorem padCode_at {a N : ℕ} (h : a ≤ N) (c : Code a) (i : Fin a) :
    padCode h c (Fin.castLE h i) = c i := by
  simp [padCode]

theorem padCode_zero {a N : ℕ} (h : a ≤ N) (c : Code a)
    (i : Fin N) (hi : a ≤ i.val) : padCode h c i = none := by
  simp [padCode, show ¬ i.val < a by omega]

theorem support_padCode {a N : ℕ} (h : a ≤ N) (c : Code a) :
    support (padCode h c) = (support c).map (Fin.castLEEmb h) := by
  classical
  ext i
  simp only [support, Finset.mem_filter, Finset.mem_univ, true_and, Finset.mem_map]
  constructor
  · intro hi
    have hia : i.val < a := by
      by_contra h'
      exact hi (padCode_zero h c i (by omega))
    exact ⟨⟨i.val, hia⟩, by simpa [padCode, hia] using hi, Fin.ext rfl⟩
  · rintro ⟨k, hk, rfl⟩
    simpa using hk

@[simp] theorem card_support_padCode {a N : ℕ} (h : a ≤ N) (c : Code a) :
    (support (padCode h c)).card = (support c).card := by
  rw [support_padCode, Finset.card_map]

theorem padCode_injective {a N : ℕ} (h : a ≤ N) :
    Function.Injective (padCode h) := by
  intro c d he
  funext i
  simpa using congrFun he (Fin.castLE h i)

def restrictCode {a N : ℕ} (h : a ≤ N) (c : Code N) : Code a :=
  fun i => c (Fin.castLE h i)

theorem padCode_restrictCode {a N : ℕ} (h : a ≤ N) (c : Code N)
    (hz : ∀ i : Fin N, a ≤ i.val → c i = none) :
    padCode h (restrictCode h c) = c := by
  funext i
  by_cases hi : i.val < a
  · simp [padCode, restrictCode, hi]
  · simp [padCode, hi, hz i (by omega)]

variable {n : ℕ} [NeZero n]

theorem padCode_absorbed_le (hn : 3 ≤ n) {a : ℕ} (ha : a ≤ n - 2) (c : Code a) :
    (decodeCode (padCode ha c) (by omega)).frontier.absorbed ≤ a := by
  have hs := decodeCodePrefix_skip (padCode ha c) (by omega) a ha
    (n - 2) (le_refl _) ha (by intro i hi _; exact padCode_zero ha c i hi)
  change (decodeCodePrefix (padCode ha c) (by omega) (n - 2) _).frontier.absorbed ≤ a
  rw [hs.1]
  exact (decodeCodePrefix (padCode ha c) (by omega) a ha).bound

abbrev ProperCarrierAt (r : ℕ) := {f : ProperCarrier n // f.val.absorbed = r}

/-- The marker `q` lies after all `j` retained checkpoints. Its displacement
from the last actual checkpoint records the extra right-side extension. -/
abbrev SaturatedCarrierParams (r j : ℕ) :=
  Sigma (fun q : Fin (r + 1) => {c : Code q.val // (support c).card = j})

abbrev ActualProperLabelsAt (r j : ℕ) :=
  Sigma (fun f : ProperCarrierAt (n := n) r => ActualProperPrefixLabel j f.val)

abbrev SaturatedCarrierFamily (hn : 3 ≤ n) (r j : ℕ) :=
  Sigma (fun f : ProperCarrierAt (n := n) r => CompatibleSaturatedCode hn j f.val)

abbrev ShortCarrierFamily (hn : 3 ≤ n) (r j : ℕ) :=
  Sigma (fun f : ProperCarrierAt (n := n) r => CompatibleShortCode hn j f.val)

noncomputable instance saturatedCarrierParamsFintype (r j : ℕ) :
    Fintype (SaturatedCarrierParams r j) := by
  classical
  exact Fintype.ofFinite _

theorem card_saturatedCarrierParams (r j : ℕ) :
    Nat.card (SaturatedCarrierParams r j) = 2 ^ j * (r + 1).choose (j + 1) := by
  classical
  change Nat.card (Sigma (fun q : Fin (r + 1) =>
    {c : Code q.val // (support c).card = j})) = _
  rw [Nat.card_sigma]
  have hterm (q : Fin (r + 1)) :
      Nat.card {c : Code q.val // (support c).card = j} = 2 ^ j * q.val.choose j := by
    rw [← Nat.card_congr (saturatedSparseEquiv q.val j), Nat.card_eq_fintype_card]
    exact card_terminalSaturated _ _
  simp_rw [hterm]
  rw [← Finset.mul_sum]
  have hsum : ∀ r, (∑ q : Fin (r + 1), q.val.choose j) = (r + 1).choose (j + 1) := by
    intro r
    induction r with
    | zero =>
        by_cases hj : j = 0
        · subst j; simp
        · simp [Nat.choose_eq_zero_of_lt (by omega : 0 < j),
            Nat.choose_eq_zero_of_lt (by omega : 1 < j + 1)]
    | succ r ih =>
        rw [Fin.sum_univ_castSucc]
        change (∑ q : Fin (r + 1), q.val.choose j) + (r + 1).choose j = _
        rw [ih, Nat.choose_succ_succ' (r + 1) j]
        ac_rfl
  rw [hsum r]

/-- Extend the retained frontier on either side. The marker is measured in
checkpoint coordinates, so the total extension is exactly `r`. -/
def markedCarrier (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2)
    (p : SaturatedCarrierParams r j) : ProperCarrierAt (n := n) r := by
  let c := padCode (show p.1.val ≤ n - 2 by omega) p.2.val
  let old := (decodeCode c (by omega)).frontier
  have hb : old.absorbed ≤ p.1.val := padCode_absorbed_le hn _ _
  have hlo := old.lo_valid
  have hhi := old.hi_valid
  have hcross := old.noncrossing
  have hab : old.absorbed = (old.lo - 2) + (n - old.hi) := rfl
  let f : CheckpointSourceFrontier n :=
    ⟨old.lo + (p.1.val - old.absorbed), old.hi - (r - p.1.val),
      by omega, by omega, by omega⟩
  exact ⟨⟨f, by dsimp [f]; omega⟩, by
    change (f.lo - 2) + (n - f.hi) = r
    dsimp [f]
    omega⟩

def saturatedCarrierMap (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2)
    (p : SaturatedCarrierParams r j) : SaturatedCarrierFamily hn r j := by
  let c := padCode (show p.1.val ≤ n - 2 by omega) p.2.val
  refine ⟨markedCarrier hn hr p, c, ?_, ?_, ?_⟩
  · simpa only [c, card_support_padCode] using p.2.property
  · change (decodeCode c _).frontier.lo ≤
      (decodeCode c _).frontier.lo + (p.1.val - (decodeCode c _).frontier.absorbed)
    omega
  · change (decodeCode c _).frontier.hi - (r - p.1.val) ≤ (decodeCode c _).frontier.hi
    omega

/-- Recovery of the marker uses both the complete retained code and the
current carrier, not the label alone. -/
theorem markedCarrier_marker (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2)
    (p : SaturatedCarrierParams r j) :
    let c := padCode (show p.1.val ≤ n - 2 by omega) p.2.val
    (decodeCode c (by omega)).frontier.absorbed +
      ((markedCarrier hn hr p).val.val.lo - (decodeCode c (by omega)).frontier.lo) = p.1.val := by
  have hb := padCode_absorbed_le hn (show p.1.val ≤ n - 2 by omega) p.2.val
  change (decodeCode (padCode _ p.2.val) _).frontier.absorbed +
    (((decodeCode (padCode _ p.2.val) _).frontier.lo +
      (p.1.val - (decodeCode (padCode _ p.2.val) _).frontier.absorbed)) -
        (decodeCode (padCode _ p.2.val) _).frontier.lo) = p.1.val
  omega

theorem saturatedCarrierMap_injective (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2) :
    Function.Injective (saturatedCarrierMap hn (j := j) hr) := by
  intro p q h
  have hf := congrArg (fun x : SaturatedCarrierFamily hn r j => x.1.val.val.lo) h
  have hc := congrArg (fun x : SaturatedCarrierFamily hn r j => x.2.val) h
  have hmp := markedCarrier_marker hn hr p
  have hmq := markedCarrier_marker hn hr q
  dsimp only at hmp hmq
  change (markedCarrier hn hr p).val.val.lo = (markedCarrier hn hr q).val.val.lo at hf
  change padCode (show p.1.val ≤ n - 2 by omega) p.2.val =
    padCode (show q.1.val ≤ n - 2 by omega) q.2.val at hc
  have hq : p.1 = q.1 := by
    apply Fin.ext
    rw [hc, hf] at hmp
    omega
  rcases p with ⟨p, c⟩
  rcases q with ⟨q, d⟩
  dsimp only at hq hc
  subst q
  have hcd : c = d := Subtype.ext (padCode_injective _ hc)
  subst d
  rfl

theorem saturatedCarrierMap_surjective (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2) :
    Function.Surjective (saturatedCarrierMap hn (j := j) hr) := by
  rintro ⟨f, c⟩
  let old := (decodeCode c.val (by omega)).frontier
  let q := old.absorbed + (f.val.val.lo - old.lo)
  have hlo := old.lo_valid
  have hhi := old.hi_valid
  have hfl := f.val.val.lo_valid
  have hfh := f.val.val.hi_valid
  have hcontain : old.lo ≤ f.val.val.lo ∧ f.val.val.hi ≤ old.hi := c.property.2
  have hab : old.absorbed = (old.lo - 2) + (n - old.hi) := rfl
  have hfab : (f.val.val.lo - 2) + (n - f.val.val.hi) = r := f.property
  have hq : q ≤ r := by dsimp [q]; omega
  have hqN : q ≤ n - 2 := by omega
  have hz : ∀ i : Fin (n - 2), q ≤ i.val → c.val i = none := by
    intro i hi
    apply code_zero_after_absorbed c.val (by omega) i
    change old.absorbed ≤ i.val
    dsimp [q] at hi
    omega
  have he : padCode hqN (restrictCode hqN c.val) = c.val :=
    padCode_restrictCode hqN c.val hz
  let p : SaturatedCarrierParams r j :=
    ⟨⟨q, by omega⟩, restrictCode hqN c.val, by
      rw [← card_support_padCode hqN, he]
      exact c.property.1⟩
  refine ⟨p, ?_⟩
  have hf : markedCarrier hn hr p = f := by
    apply Subtype.ext
    apply Subtype.ext
    apply sourceFrontier_ext
    · change (decodeCode (padCode hqN (restrictCode hqN c.val)) _).frontier.lo +
        (q - (decodeCode (padCode hqN (restrictCode hqN c.val)) _).frontier.absorbed) = _
      rw [he]
      change old.lo + (q - old.absorbed) = f.val.val.lo
      dsimp [q]
      omega
    · change (decodeCode (padCode hqN (restrictCode hqN c.val)) _).frontier.hi - (r - q) = _
      rw [he]
      change old.hi - (r - q) = f.val.val.hi
      dsimp [q]
      omega
  apply Sigma.ext hf
  apply (Subtype.heq_iff_coe_eq (by
    intro d
    change ((support d).card = j ∧
      (decodeCode d (by omega)).frontier.lo ≤ (markedCarrier hn hr p).val.val.lo ∧
        (markedCarrier hn hr p).val.val.hi ≤ (decodeCode d (by omega)).frontier.hi) ↔ _
    rw [hf])).mpr
  exact he

/-- The marked finite parameters classify the *actual*, carrier-indexed
saturated image through `properCarrierPrefixActualEquiv`. -/
noncomputable def saturatedCarrierEquiv (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2) :
    SaturatedCarrierParams r j ≃ SaturatedCarrierFamily hn r j :=
  Equiv.ofBijective (saturatedCarrierMap hn hr)
    ⟨saturatedCarrierMap_injective hn hr, saturatedCarrierMap_surjective hn hr⟩

abbrev PositiveShortCode (r j : ℕ) (hpos : 0 < r) :=
  {c : Code r // (support c).card < j ∧ c ⟨r - 1, by omega⟩ ≠ none}

noncomputable def positiveShortSparseEquiv (r j : ℕ) (hpos : 0 < r) :
    TerminalShort r j ≃ PositiveShortCode r j hpos := by
  cases r with
  | zero => omega
  | succ r =>
    exact Equiv.ofBijective (fun p => ⟨shortSparseCode p, by
      constructor
      · rw [shortSparseCode_card]; have := p.1.isLt; omega
      · change shortSparseCode p ⟨r + 1 - 1, by omega⟩ ≠ none
        have hi : (⟨r + 1 - 1, by omega⟩ : Fin (r + 1)) = Fin.last r := by
          apply Fin.ext
          simp
        rw [shortSparseCode, hi, appendLastSymbol_last]
        exact Option.some_ne_none _⟩)
      ⟨fun _ _ h => shortSparseCode_injective (congrArg Subtype.val h), by
        intro c
        obtain ⟨p, hp⟩ := shortSparseCode_surjective c.val c.property.1 c.property.2
        exact ⟨p, Subtype.ext hp⟩⟩

theorem padCode_absorbed_eq_last (hn : 3 ≤ n) {r : ℕ}
    (hr : r ≤ n - 2) (hpos : 0 < r) (c : Code r)
    (hlast : c ⟨r - 1, by omega⟩ ≠ none) :
    (decodeCode (padCode hr c) (by omega)).frontier.absorbed = r := by
  have hle := padCode_absorbed_le hn hr c
  have hnon : padCode hr c (Fin.castLE hr ⟨r - 1, by omega⟩) ≠ none := by
    simpa only [padCode_at] using hlast
  have hge := nonzero_le_lastCheckpoint (padCode hr c) (n - 2) (le_refl _)
    (Fin.castLE hr ⟨r - 1, by omega⟩) (by simp; omega) hnon
  rw [← decodeCodePrefix_absorbed (padCode hr c) (by omega)] at hge
  change r - 1 + 1 ≤ (decodeCode (padCode hr c) (by omega)).frontier.absorbed at hge
  omega

theorem code_nonzero_at_absorbed (hn : 3 ≤ n) {r : ℕ}
    (hr : r ≤ n - 2) (hpos : 0 < r) (c : Code (n - 2))
    (hab : (decodeCode c (by omega)).frontier.absorbed = r) :
    c ⟨r - 1, by omega⟩ ≠ none := by
  intro hz
  have hs := decodeCodePrefix_skip c (by omega) (r - 1) (by omega)
    (n - 2) (le_refl _) (by omega) (by
      intro i hi _
      by_cases hir : i.val = r - 1
      · have he : i = ⟨r - 1, by omega⟩ := Fin.ext hir
        simpa only [he] using hz
      · exact code_zero_after_absorbed c (by omega) i (by omega))
  have hb := (decodeCodePrefix c (by omega) (r - 1) (by omega)).bound
  have hsfront := hs.1
  change (decodeCode c (by omega)).frontier = _ at hsfront
  rw [← hsfront, hab] at hb
  omega

def shortCarrierMap (hn : 3 ≤ n) {r j : ℕ} (hr : r < n - 2) (hpos : 0 < r)
    (p : PositiveShortCode r j hpos) : ShortCarrierFamily hn r j := by
  let c := padCode (show r ≤ n - 2 by omega) p.val
  have hab : (decodeCode c (by omega)).frontier.absorbed = r :=
    padCode_absorbed_eq_last hn _ hpos p.val p.property.2
  have ht := (decodeCode c (by omega)).frontier.remaining_plus_absorbed
  rw [CheckpointSourceFrontier.remaining_card, hab] at ht
  refine ⟨⟨⟨(decodeCode c (by omega)).frontier, by omega⟩, hab⟩, c, ?_, rfl⟩
  simpa only [c, card_support_padCode] using p.property.1

theorem shortCarrierMap_injective (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    Function.Injective (shortCarrierMap hn (j := j) hr hpos) := by
  intro p q h
  apply Subtype.ext
  apply padCode_injective (show r ≤ n - 2 by omega)
  exact congrArg (fun x : ShortCarrierFamily hn r j => x.2.val) h

theorem shortCarrierMap_surjective (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    Function.Surjective (shortCarrierMap hn (j := j) hr hpos) := by
  rintro ⟨f, c⟩
  have hab : (decodeCode c.val (by omega)).frontier.absorbed = r := by
    rw [c.property.2]; exact f.property
  have hrN : r ≤ n - 2 := by omega
  have he : padCode hrN (restrictCode hrN c.val) = c.val :=
    padCode_restrictCode hrN c.val (by
      intro i hi; exact code_zero_after_absorbed c.val (by omega) i (by omega))
  let p : PositiveShortCode r j hpos := ⟨restrictCode hrN c.val, by
    constructor
    · rw [← card_support_padCode hrN, he]; exact c.property.1
    · exact code_nonzero_at_absorbed hn hrN hpos c.val hab⟩
  refine ⟨p, ?_⟩
  have hf : (shortCarrierMap hn hr hpos p).1 = f := by
    apply Subtype.ext
    apply Subtype.ext
    change (decodeCode (padCode hrN (restrictCode hrN c.val)) _).frontier = f.val.val
    rw [he]
    exact c.property.2
  apply Sigma.ext hf
  apply (Subtype.heq_iff_coe_eq (by
    intro d
    change ((support d).card < j ∧ (decodeCode d (by omega)).frontier =
      (shortCarrierMap hn hr hpos p).1.val.val) ↔ _
    rw [hf])).mpr
  exact he

noncomputable def shortCarrierEquiv (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    TerminalShort r j ≃ ShortCarrierFamily hn r j :=
  (positiveShortSparseEquiv r j hpos).trans
    (Equiv.ofBijective (shortCarrierMap hn hr hpos)
      ⟨shortCarrierMap_injective hn hr hpos, shortCarrierMap_surjective hn hr hpos⟩)

/-- Both the carrier and the retained complete ordered records are recovered.
The short and saturated phases are disjoint even at the same record depth. -/
noncomputable def properCarrierCountEquiv (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    ActualProperLabelsAt (n := n) r j ≃
      SaturatedCarrierParams r j ⊕ TerminalShort r j :=
  (Equiv.sigmaCongrRight (fun f : ProperCarrierAt (n := n) r =>
    (properCarrierPrefixActualEquiv hn j f.val).symm)).trans
    ((Equiv.sigmaSumDistrib _ _).trans
      (Equiv.sumCongr (saturatedCarrierEquiv hn hr).symm
        (shortCarrierEquiv hn hr hpos).symm))

theorem properCarrierCount_encode_decode (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r)
    (p : SaturatedCarrierParams r j ⊕ TerminalShort r j) :
    properCarrierCountEquiv hn hr hpos
      ((properCarrierCountEquiv hn hr hpos).symm p) = p :=
  (properCarrierCountEquiv hn hr hpos).apply_symm_apply p

theorem properCarrierCount_decode_encode (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r)
    (x : ActualProperLabelsAt (n := n) r j) :
    (properCarrierCountEquiv hn hr hpos).symm
      (properCarrierCountEquiv hn hr hpos x) = x :=
  (properCarrierCountEquiv hn hr hpos).symm_apply_apply x

/-- Lemma 3.1 for positive absorbed size. The left side is the sum of
actual compatible label images over distinct current proper carriers. -/
theorem card_actualProperLabelsAt (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    Nat.card (ActualProperLabelsAt (n := n) r j) =
      2 ^ j * (r + 1).choose (j + 1) +
        ∑ ell ∈ Finset.Icc 1 (j - 1), 2 ^ ell * (r - 1).choose (ell - 1) := by
  rw [Nat.card_congr (properCarrierCountEquiv hn hr hpos), Nat.card_sum,
    card_saturatedCarrierParams, Nat.card_eq_fintype_card, card_terminalShort]
  have hpaper := terminalPrefixCount_eq_paper r j
  unfold terminalPrefixCount at hpaper
  omega

def initialProperCarrier (hn : 3 ≤ n) : ProperCarrierAt (n := n) 0 :=
  ⟨⟨⟨2, n, le_refl _, by omega, le_refl _⟩, by change 2 < n; omega⟩, by
    simp [CheckpointSourceFrontier.absorbed]⟩

theorem properCarrierAt_zero_unique (hn : 3 ≤ n)
    (f : ProperCarrierAt (n := n) 0) : f = initialProperCarrier hn := by
  apply Subtype.ext
  apply Subtype.ext
  have hlo := f.val.val.lo_valid
  have hhi := f.val.val.hi_valid
  have hab : (f.val.val.lo - 2) + (n - f.val.val.hi) = 0 := f.property
  apply sourceFrontier_ext <;> dsimp [initialProperCarrier] <;> omega

/-- The registered-but-not-yet-absorbed boundary has one carrier and one
actual empty short label. It is not included in the positive final-checkpoint
short-code count. -/
theorem card_actualProperLabelsAt_zero (hn : 3 ≤ n) {j : ℕ} (hj : 0 < j) :
    Nat.card (ActualProperLabelsAt (n := n) 0 j) = 1 := by
  have hcard := card_actualProperPrefixLabel_zero hn j hj
    (initialProperCarrier hn).val (initialProperCarrier hn).property
  obtain ⟨label, hu⟩ := Nat.card_eq_one_iff_exists.mp hcard
  apply Nat.card_eq_one_iff_exists.mpr
  refine ⟨⟨initialProperCarrier hn, label⟩, ?_⟩
  rintro ⟨f, other⟩
  have hf := properCarrierAt_zero_unique hn f
  subst f
  exact congrArg (Sigma.mk (initialProperCarrier hn)) (hu other)

/-- Carrier-indexed actual labels together with their literal placement
fibres. Histories only witness membership and are not counted again. -/
abbrev ActualProperFibreAt (r j : ℕ) :=
  Sigma (fun x : ActualProperLabelsAt (n := n) r j =>
    ActualProperPlacements j x.1.val x.2)

theorem card_actualProperFibreAt (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hpos : 0 < r) :
    Nat.card (ActualProperFibreAt (n := n) r j) =
      (2 ^ j * (r + 1).choose (j + 1) +
        ∑ ell ∈ Finset.Icc 1 (j - 1), 2 ^ ell * (r - 1).choose (ell - 1)) *
        (n * (2 * (n - 2) - r).choose (n - 2 - r)) := by
  classical
  let : Finite (ActualProperLabelsAt (n := n) r j) :=
    Finite.of_equiv _ (properCarrierCountEquiv hn hr hpos).symm
  let := Fintype.ofFinite (ActualProperLabelsAt (n := n) r j)
  have : ∀ x : ActualProperLabelsAt (n := n) r j,
      Finite (ActualProperPlacements j x.1.val x.2) := by
    intro x
    unfold ActualProperPlacements
    infer_instance
  have hterm (x : ActualProperLabelsAt (n := n) r j) :
      Nat.card (ActualProperPlacements j x.1.val x.2) =
        n * (2 * (n - 2) - r).choose (n - 2 - r) :=
    card_actualProperPlacements_paper hn j x.1.val x.2 r x.1.property
  change Nat.card (Sigma (fun x : ActualProperLabelsAt (n := n) r j =>
    ActualProperPlacements j x.1.val x.2)) = _
  rw [Nat.card_sigma]
  simp_rw [hterm]
  rw [Finset.sum_const, Finset.card_univ, ← Nat.card_eq_fintype_card,
    card_actualProperLabelsAt hn hr hpos]
  simp

theorem card_actualProperFibreAt_zero (hn : 3 ≤ n) {j : ℕ} (hj : 0 < j) :
    Nat.card (ActualProperFibreAt (n := n) 0 j) =
      n * (2 * (n - 2)).choose (n - 2) := by
  classical
  have hc := card_actualProperLabelsAt_zero hn hj
  have : Finite (ActualProperLabelsAt (n := n) 0 j) :=
    Nat.finite_of_card_ne_zero (by omega)
  let := Fintype.ofFinite (ActualProperLabelsAt (n := n) 0 j)
  have : ∀ x : ActualProperLabelsAt (n := n) 0 j,
      Finite (ActualProperPlacements j x.1.val x.2) := by
    intro x
    unfold ActualProperPlacements
    infer_instance
  have hterm (x : ActualProperLabelsAt (n := n) 0 j) :
      Nat.card (ActualProperPlacements j x.1.val x.2) =
        n * (2 * (n - 2) - 0).choose (n - 2 - 0) :=
    card_actualProperPlacements_paper hn j x.1.val x.2 0 x.1.property
  change Nat.card (Sigma (fun x : ActualProperLabelsAt (n := n) 0 j =>
    ActualProperPlacements j x.1.val x.2)) = _
  rw [Nat.card_sigma]
  simp_rw [hterm]
  rw [Finset.sum_const, Finset.card_univ, ← Nat.card_eq_fintype_card, hc]
  simp

/-- The manuscript coefficient, with the empty-current-chain boundary
separated from the positive final-checkpoint formula. -/
def properCarrierPrefixCount (r j : ℕ) : ℕ :=
  if r = 0 then 1 else
    2 ^ j * (r + 1).choose (j + 1) +
      ∑ ell ∈ Finset.Icc 1 (j - 1), 2 ^ ell * (r - 1).choose (ell - 1)

theorem card_actualProperLabelsAt_all (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hj : 0 < j) :
    Nat.card (ActualProperLabelsAt (n := n) r j) = properCarrierPrefixCount r j := by
  by_cases hz : r = 0
  · subst r
    simpa [properCarrierPrefixCount] using
      card_actualProperLabelsAt_zero hn hj
  · simpa only [properCarrierPrefixCount, if_neg hz] using
      card_actualProperLabelsAt hn hr (show 0 < r by omega) (j := j)

theorem card_actualProperFibreAt_all (hn : 3 ≤ n) {r j : ℕ}
    (hr : r < n - 2) (hj : 0 < j) :
    Nat.card (ActualProperFibreAt (n := n) r j) =
      properCarrierPrefixCount r j *
        (n * (2 * (n - 2) - r).choose (n - 2 - r)) := by
  by_cases hz : r = 0
  · subst r
    simpa [properCarrierPrefixCount] using
      card_actualProperFibreAt_zero hn hj
  · simpa only [properCarrierPrefixCount, if_neg hz] using
      card_actualProperFibreAt hn hr (show 0 < r by omega) (j := j)

end Paper44
