import Paper44.ProperCarrierLabels

/-! # Proper-carrier retained-prefix classification

The saturated branch stores the exact prefix code and containment in a fixed
current carrier. The short branch is the whole current chain. The carrier is
an explicit index on both sides of the actual range equivalence.
-/

namespace Paper44

open PaperXL RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

theorem decodePrefix_frontier_monotone (c : Code (n - 2)) (hn : 2 ≤ n)
    (a : ℕ) (ha : a ≤ n - 2) :
    ∀ b (hb : b ≤ n - 2), a ≤ b →
      (decodeCodePrefix c hn a ha).frontier.lo ≤
          (decodeCodePrefix c hn b hb).frontier.lo ∧
        (decodeCodePrefix c hn b hb).frontier.hi ≤
          (decodeCodePrefix c hn a ha).frontier.hi := by
  intro b
  induction b with
  | zero =>
      intro hb hab
      have he : a = 0 := by omega
      subst a
      exact ⟨le_refl _, le_refl _⟩
  | succ b ih =>
      intro hb hab
      by_cases h : a ≤ b
      · obtain ⟨hlo, hhi⟩ := ih (by omega) h
        cases hc : c ⟨b, by omega⟩ with
        | none => simpa [decodeCodePrefix, DecodedCodePrefix.advance, hc] using And.intro hlo hhi
        | some side =>
            have hbd := (decodeCodePrefix c hn b (by omega)).bound
            have hpos : 0 < b + 1 - (decodeCodePrefix c hn b (by omega)).frontier.absorbed := by omega
            cases side <;>
              simp only [decodeCodePrefix, DecodedCodePrefix.advance, hc,
                CheckpointSourceFrontier.nextL, CheckpointSourceFrontier.nextR]
            all_goals constructor <;> omega
      · have he : a = b + 1 := by omega
        subst a
        exact ⟨le_refl _, le_refl _⟩

theorem take_code_with_containment (hn : 3 ≤ n) (c : Code (n - 2)) (j : ℕ) :
    ∃ d : Code (n - 2), decodeChain d (by omega) = (decodeChain c (by omega)).take j ∧
      (decodeCode d (by omega)).frontier.lo ≤ (decodeCode c (by omega)).frontier.lo ∧
      (decodeCode c (by omega)).frontier.hi ≤ (decodeCode d (by omega)).frontier.hi := by
  obtain ⟨l, hl, htake⟩ := decoded_take_is_prefix c (by omega) j (n - 2) (le_refl _)
  let d := truncateCode c l
  have hc := decodeCodePrefix_congr d c (by omega) l hl (by
    intro i hi; simp [d, truncateCode, hi])
  have hs := decodeCodePrefix_skip d (by omega) l hl (n - 2) (le_refl _) hl (by
    intro i hi _; simp [d, truncateCode, show ¬ i.val < l by omega])
  have hm := decodePrefix_frontier_monotone c (by omega) l hl (n - 2) (le_refl _) hl
  have he : (decodeCode d (by omega)).frontier = (decodeCodePrefix c (by omega) l hl).frontier :=
    hs.1.trans (congrArg DecodedCodePrefix.frontier hc)
  exact ⟨d, (decodeChain_truncate c (by omega) l hl).trans htake,
    by rw [he]; exact hm.1, by rw [he]; exact hm.2⟩

abbrev CompatibleSaturatedCode (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :=
  {c : Code (n - 2) // (support c).card = j ∧
    (decodeCode c (by omega)).frontier.lo ≤ f.val.lo ∧
    f.val.hi ≤ (decodeCode c (by omega)).frontier.hi}

abbrev CompatibleShortCode (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :=
  {c : Code (n - 2) // (support c).card < j ∧ (decodeCode c (by omega)).frontier = f.val}

abbrev ProperCarrierPrefixCode (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :=
  CompatibleSaturatedCode hn j f ⊕ CompatibleShortCode hn j f

def properSparseLabel (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :
    ProperCarrierPrefixCode hn j f →
      PrefixLabel (FusionRecord (ZMod n)) (FusionRecord (ZMod n))
  | .inl c => .registered (canonicalOrigin n) (decodeChain c.val (by omega)) .saturated
  | .inr c => .registered (canonicalOrigin n) (decodeChain c.val (by omega)) .short

theorem properSparseLabel_injective (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :
    Function.Injective (properSparseLabel hn j f) := by
  intro c d h
  cases c <;> cases d
  · congr 1; apply Subtype.ext
    exact decodeChain_injective (by omega) (PrefixLabel.registered.inj h).2.1
  · cases (PrefixLabel.registered.inj h).2.2
  · cases (PrefixLabel.registered.inj h).2.2
  · congr 1; apply Subtype.ext
    exact decodeChain_injective (by omega) (PrefixLabel.registered.inj h).2.1

theorem properSparseLabel_reachable (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (c : ProperCarrierPrefixCode hn j f) :
    ∃ s : CircularState n, s.val.origin.isSome = true ∧
      (∃ q, s.val.placed q = some f.val.carrier) ∧
      circularLabel j s.val = properSparseLabel hn j f c := by
  cases c with
  | inl c =>
      obtain ⟨d, tail, hf, hchain⟩ := complete_code_to_proper_frontier hn c.val f.val
        f.property c.property.2.1 c.property.2.2
      obtain ⟨s, hr, hq, hl⟩ := proper_code_label_reachable hn j f d hf
      have hlen : (decodeChain c.val (by omega)).length = j :=
        (decodeChain_length _ _).trans c.property.1
      refine ⟨s, hr, hq, hl.trans ?_⟩
      simp only [codePrefixLabel, hchain, retainedLabel, List.length_append, hlen,
        show ¬ j + tail.length < j by omega, if_false, properSparseLabel]
      rw [List.take_append_of_le_length (by omega), List.take_of_length_le (by omega)]
  | inr c =>
      obtain ⟨s, hr, hq, hl⟩ := proper_code_label_reachable hn j f c.val c.property.2
      have hlen : (decodeChain c.val (by omega)).length < j := by
        rw [decodeChain_length]; exact c.property.1
      refine ⟨s, hr, hq, hl.trans ?_⟩
      simp [codePrefixLabel, retainedLabel, hlen, properSparseLabel,
        List.take_of_length_le (show (decodeChain c.val (by omega)).length ≤ j by omega)]

theorem properSparseLabel_covers (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (label : ActualProperPrefixLabel j f) :
    ∃ c : ProperCarrierPrefixCode hn j f, properSparseLabel hn j f c = label.val := by
  obtain ⟨c, hf, hl⟩ := actual_proper_code hn j f label
  by_cases hshort : (decodeChain c (by omega)).length < j
  · refine ⟨.inr ⟨c, by rw [← decodeChain_length c (by omega)]; exact hshort, hf⟩, ?_⟩
    rw [← hl]
    simp [properSparseLabel, codePrefixLabel, retainedLabel, hshort,
      List.take_of_length_le (show (decodeChain c (by omega)).length ≤ j by omega)]
  · obtain ⟨d, hd, hlo, hhi⟩ := take_code_with_containment hn c j
    have hlen : (support d).card = j := by
      rw [← decodeChain_length d (by omega), hd, List.length_take, Nat.min_eq_left (by omega)]
    refine ⟨.inl ⟨d, hlen, by rw [← hf]; exact hlo, by rw [← hf]; exact hhi⟩, ?_⟩
    rw [← hl]
    simp [properSparseLabel, codePrefixLabel, retainedLabel, hshort, hd]

/-- Complete-record classification and real reachability, separately for each
current carrier. Saturated labels are not deduplicated across carriers. -/
noncomputable def properCarrierPrefixActualEquiv (hn : 3 ≤ n) (j : ℕ)
    (f : ProperCarrier n) :
    ProperCarrierPrefixCode hn j f ≃ ActualProperPrefixLabel j f :=
  Equiv.ofBijective (fun c => ⟨properSparseLabel hn j f c, properSparseLabel_reachable hn j f c⟩)
    ⟨fun _ _ h => properSparseLabel_injective hn j f (congrArg Subtype.val h), by
      intro label
      obtain ⟨c, hc⟩ := properSparseLabel_covers hn j f label
      exact ⟨c, Subtype.ext hc⟩⟩

theorem properCarrierPrefix_encode_decode (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (c : ProperCarrierPrefixCode hn j f) :
    (properCarrierPrefixActualEquiv hn j f).symm (properCarrierPrefixActualEquiv hn j f c) = c :=
  (properCarrierPrefixActualEquiv hn j f).symm_apply_apply c

theorem properCarrierPrefix_decode_encode (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n)
    (label : ActualProperPrefixLabel j f) :
    properCarrierPrefixActualEquiv hn j f ((properCarrierPrefixActualEquiv hn j f).symm label) = label :=
  (properCarrierPrefixActualEquiv hn j f).apply_symm_apply label

theorem card_actualProperPrefixLabel (hn : 3 ≤ n) (j : ℕ) (f : ProperCarrier n) :
    Nat.card (ActualProperPrefixLabel j f) =
      Nat.card (ProperCarrierPrefixCode hn j f) := by
  rw [Nat.card_congr (properCarrierPrefixActualEquiv hn j f)]

abbrev ActualProperPrefixFamily (j : ℕ) :=
  Sigma (fun f : ProperCarrier n => ActualProperPrefixLabel j f)

abbrev ProperCarrierPrefixFamily (hn : 3 ≤ n) (j : ℕ) :=
  Sigma (fun f : ProperCarrier n => ProperCarrierPrefixCode hn j f)

/-- The carrier index is retained by the range equivalence. This is the
dependent family used when summing labels over all current proper carriers;
it deliberately does not quotient equal label values at different carriers. -/
noncomputable def properCarrierPrefixFamilyEquiv (hn : 3 ≤ n) (j : ℕ) :
    ProperCarrierPrefixFamily hn j ≃ ActualProperPrefixFamily (n := n) j :=
  Equiv.sigmaCongrRight (fun f => properCarrierPrefixActualEquiv hn j f)

theorem properCarrierPrefixFamily_encode_decode (hn : 3 ≤ n) (j : ℕ)
    (x : ProperCarrierPrefixFamily hn j) :
    (properCarrierPrefixFamilyEquiv hn j).symm
      (properCarrierPrefixFamilyEquiv hn j x) = x :=
  (properCarrierPrefixFamilyEquiv hn j).symm_apply_apply x

theorem properCarrierPrefixFamily_decode_encode (hn : 3 ≤ n) (j : ℕ)
    (x : ActualProperPrefixFamily (n := n) j) :
    properCarrierPrefixFamilyEquiv hn j
      ((properCarrierPrefixFamilyEquiv hn j).symm x) = x :=
  (properCarrierPrefixFamilyEquiv hn j).apply_symm_apply x

/-- The empty-history boundary is separate from the positive-checkpoint
classification: zero absorbed atoms force every code symbol to be zero. -/
theorem proper_code_empty_of_absorbed_zero (hn : 3 ≤ n)
    (c : Code (n - 2)) (hf : (decodeCode c (by omega)).frontier.absorbed = 0) :
    c = fun _ => none := by
  funext i
  exact code_zero_after_absorbed c (by omega) i (by omega)

theorem proper_label_empty_of_absorbed_zero (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (f : ProperCarrier n) (hf : f.val.absorbed = 0)
    (label : ActualProperPrefixLabel j f) :
    label.val = .registered (canonicalOrigin n) [] .short := by
  obtain ⟨c, hc, hl⟩ := actual_proper_code hn j f label
  have hz := proper_code_empty_of_absorbed_zero hn c (by rw [hc, hf])
  have hlen : (decodeChain c (by omega)).length = 0 := by
    rw [decodeChain_length, hz]
    simp [support]
  have hchain := List.length_eq_zero_iff.mp hlen
  rw [← hl]
  simp [codePrefixLabel, retainedLabel, hchain, hj]

/-- The manuscript's `c_{0,j}=1`, for the actual compatible-label image,
not merely for a syntactic code type. -/
theorem card_actualProperPrefixLabel_zero (hn : 3 ≤ n) (j : ℕ) (hj : 0 < j)
    (f : ProperCarrier n) (hf : f.val.absorbed = 0) :
    Nat.card (ActualProperPrefixLabel j f) = 1 := by
  let c : Code (n - 2) := fun _ => none
  have hfront : (decodeCode c (by omega)).frontier = f.val := by
    have hs := decodeCodePrefix_skip c (by omega) 0 (by omega) (n - 2)
      (le_refl _) (by omega) (by intro i _ _; rfl)
    apply sourceFrontier_ext
    · have hlo := f.val.lo_valid
      have hhi := f.val.hi_valid
      have hab : (f.val.lo - 2) + (n - f.val.hi) = 0 := hf
      change (decodeCodePrefix c (by omega) (n - 2) _).frontier.lo = f.val.lo
      rw [hs.1]
      change 2 = f.val.lo
      omega
    · have hlo := f.val.lo_valid
      have hhi := f.val.hi_valid
      have hab : (f.val.lo - 2) + (n - f.val.hi) = 0 := hf
      change (decodeCodePrefix c (by omega) (n - 2) _).frontier.hi = f.val.hi
      rw [hs.1]
      change n = f.val.hi
      omega
  obtain ⟨s, hr, hq, hl⟩ := proper_code_label_reachable hn j f c hfront
  let label : ActualProperPrefixLabel j f := ⟨codePrefixLabel hn j c, s, hr, hq, hl⟩
  apply Nat.card_eq_one_iff_exists.mpr
  refine ⟨label, fun other => Subtype.ext ?_⟩
  exact (proper_label_empty_of_absorbed_zero hn j hj f hf other).trans
    (proper_label_empty_of_absorbed_zero hn j hj f hf label).symm

end Paper44
