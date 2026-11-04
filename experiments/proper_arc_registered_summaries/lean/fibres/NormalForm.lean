import fibres.Carrier

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Pure naming of an ordered placement with a specified present carrier.
Reachability is supplied later by the actual proper-arc history. -/
theorem ordered_fiber_naming (P : Placement n (Finset (ZMod n)))
    (f : CheckpointSourceFrontier n) (ordered : SourceOrdered P)
    (present : ∃ q, P q=some f.carrier) (remaining : f.lo<f.hi) :
    ∃ (s : ℕ) (hs : NeZero s), letI : NeZero s := hs
      ∃ named : LegalNamedPlacement n s (ZMod n),
        named.placed=P ∧ named.PositivelyOrdered ∧ OrderedOutsideNaming f named := by
  obtain ⟨qC,hC⟩ := present
  have hz : (0 : ZMod n) ∈ f.carrier := by simp [CheckpointSourceFrontier.carrier, selectedPair]
  have hCmem : f.carrier ∈ placedBlocks P :=
    (mem_placedBlocks P f.carrier).mpr ⟨⟨0,hz⟩,qC,hC⟩
  have hlo : f.lo<n := by have := f.hi_valid; omega
  have hrem : (f.lo : ZMod n) ∈ f.remaining := by
    rw [CheckpointSourceFrontier.remaining, mem_sourceInterval_iff f.lo f.hi f.hi_valid]
    simp [ZMod.val_natCast_of_lt hlo, remaining]
  obtain ⟨B,hBmem,haB⟩ := sourceOrdered_blocks_cover P ordered (f.lo : ZMod n)
  have hBne : B≠f.carrier := by
    intro h
    exact (f.not_mem_carrier_iff_remaining _).mpr hrem (h ▸ haB)
  let s := (placedBlocks P).card
  have hs2 : 2 ≤ s := by
    have h := Finset.one_lt_card.mpr ⟨B,hBmem,f.carrier,hCmem,hBne⟩
    omega
  letI : NeZero s := ⟨by omega⟩
  let named := canonicalLegalNamed P P ordered ordered rfl
  have hplaced : named.placed=P := rfl
  let state : Execution n (ZMod n) := ⟨P,none,[]⟩
  have hcarrier : named.block 0=f.carrier :=
    canonical_named_carrier state ordered f.carrier ⟨qC,hC⟩ hz
  have hkeys : StrictMono (namedSourceKey named) := canonical_namedSourceKey_strict P ordered
  have hout (i : Fin s) (hi : 0 < i.val) :
      LinearSourceConvex (named.block (i.val : ZMod s)) ∧
      named.block (i.val : ZMod s) ⊆ f.remaining := by
    have hi0 : (i.val : ZMod s)≠0 := by
      intro h
      have hv := congrArg ZMod.val h
      rw [ZMod.val_natCast_of_lt i.isLt,ZMod.val_zero] at hv
      omega
    have hsites := named.position_injective.ne hi0
    have hcarrierSite : state.placed (named.position 0)=some f.carrier := by
      change P (named.position 0)=some f.carrier
      exact (congrFun hplaced (named.position 0)).symm.trans
        (by simpa only [hcarrier] using named.placed_at 0)
    have houtsideSite : state.placed (named.position (i.val : ZMod s))=
        some (named.block (i.val : ZMod s)) := by
      change P _=_
      exact (congrFun hplaced _).symm.trans (named.placed_at _)
    obtain ⟨_,hlinear,hsubset⟩ := actual_outside_packet_linear state f.carrier
      (named.block (i.val : ZMod s)) (named.position 0) (named.position (i.val : ZMod s))
      ordered hsites.symm hcarrierSite houtsideSite hz
    refine ⟨hlinear,?_⟩
    intro a ha
    exact (f.not_mem_carrier_iff_remaining a).mp (Finset.mem_sdiff.mp (hsubset ha)).2
  refine ⟨s,inferInstance,named,rfl,canonicalLegalNamed_positive P P ordered ordered rfl,
    ⟨hs2,hcarrier,hkeys,?_,?_⟩⟩
  · intro i hi; exact (hout i hi).1
  · intro i hi; exact (hout i hi).2

theorem ordered_fiber_normal_form (P : Placement n (Finset (ZMod n)))
    (f : CheckpointSourceFrontier n) (ordered : SourceOrdered P)
    (present : ∃ q, P q=some f.carrier) (remaining : f.lo<f.hi) :
    ∃ (t : ℕ) (data : ValidFiberPlacement n t), data.u=f.lo ∧ data.v=f.hi ∧ P=data.target := by
  obtain ⟨s,hs,named,hplaced,hpositive,hnaming⟩ := ordered_fiber_naming P f ordered present remaining
  letI : NeZero s := hs
  have hs2 := hnaming.count
  obtain ⟨t,ht⟩ : ∃ t, s=t+1 := ⟨s-1,by omega⟩
  subst s
  let cut := hnaming.toCutNamed remaining
  let data := cut.toValidFiberPlacement hpositive remaining
  exact ⟨t,data,rfl,rfl,hplaced.symm.trans (cut.toValidFiberPlacement_target hpositive remaining).symm⟩

/-- Every actual proper-arc endpoint has one of the inherited pure fibre
targets after source normalization, with the same decoded carrier. -/
theorem actual_fiber_normal_form (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r<n)
    (word : List Letter) (v : Code (n-r))
    (registered : (run (arc c r) (singletonExecution n) word).origin.isSome=true)
    (decoded : (run (arc c r) (singletonExecution n) word).chain=decodeChain c ⟨hr.1,hr.2.le⟩ v)
    (hk : 0<outsideCount ⟨hr.1,hr.2.le⟩ v) :
    ∃ (t : ℕ) (data : ValidFiberPlacement n t),
      data.u=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.lo ∧
      data.v=(decodeCanonical ⟨hr.1,hr.2.le⟩ v).frontier.hi ∧
      (run (arc c r) (singletonExecution n) word).placed=renamePlacement (sourceShift c) data.target := by
  obtain ⟨ho,hpresent⟩ := normalized_code_carrier c hr word v registered decoded
  obtain ⟨t,data,hu,hv,hp⟩ := ordered_fiber_normal_form _ _ ho hpresent (by exact Nat.lt_of_sub_pos hk)
  refine ⟨t,data,hu,hv,?_⟩
  rw [← normalized_run c r word]
  change renamePlacement (sourceShift c) _=renamePlacement (sourceShift c) data.target
  rw [hp]

theorem rank_params_outside_bound {k t : ℕ} (hk : 0<k) (ht : 0<t)
    (p : RankFiberParams n k t) : t ≤ k := by
  have h : t-1 ≤ k-1 := by
    have hcard := Finset.card_le_univ (s := p.2.1.val)
    simpa only [p.2.1.property, Fintype.card_fin] using hcard
  omega

end ProperArc.Chains
