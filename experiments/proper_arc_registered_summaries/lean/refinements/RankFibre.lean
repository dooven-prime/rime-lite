import fibres.PlacementEquivalence

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Rank is read from the nonempty packet blocks of the literal placement. -/
def ActualRankCodePlacements (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r < n)
    (t : Fin (r-1)) (v : Code (n-r)) (s : ℕ) :=
  {P : ActualCodePlacements c hr t v // (placedBlocks P.val).card=s}

theorem placedBlocks_renamePlacement (e : ZMod n ≃ ZMod n)
    (P : Placement n (Finset (ZMod n))) :
    placedBlocks (renamePlacement e P)=(placedBlocks P).image (Finset.image e) := by
  classical
  ext B
  rw [mem_placedBlocks,Finset.mem_image]
  constructor
  · rintro ⟨hB,q,hq⟩
    obtain ⟨C,hC,himage⟩ := Option.map_eq_some_iff.mp hq
    refine ⟨C,(mem_placedBlocks P C).mpr ⟨?_,q,hC⟩,himage⟩
    rw [← himage,Finset.image_nonempty] at hB
    exact hB
  · rintro ⟨C,hC,rfl⟩
    obtain ⟨hne,q,hq⟩ := (mem_placedBlocks P C).mp hC
    exact ⟨hne.image e,q,by simp [renamePlacement,hq]⟩

theorem renamePlacement_rank (e : ZMod n ≃ ZMod n)
    (P : Placement n (Finset (ZMod n))) :
    (placedBlocks (renamePlacement e P)).card=(placedBlocks P).card := by
  rw [placedBlocks_renamePlacement]
  exact Finset.card_image_of_injective _ (Finset.image_injective e.injective)

theorem positiveFiberTarget_rank (c : ZMod n) {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n)
    (v : Code (n-r)) (hk : 0 < outsideCount hr v)
    (p : FiberParams n (outsideCount hr v)) :
    (placedBlocks (positiveFiberTarget c hr v hk p)).card=p.1.val+2 := by
  rw [positiveFiberTarget,renamePlacement_rank]
  exact (positiveFiberData hr v hk p).toLegal.blocks_card

/-- A sigma slice at one index contains precisely that index's native data. -/
def rankIndexSliceEquiv {I : Type*} (B : I → Type*) (i : I) :
    {p : Sigma B // p.1=i} ≃ B i where
  toFun p := p.property ▸ p.val.2
  invFun b := ⟨⟨i,b⟩,rfl⟩
  left_inv := by rintro ⟨⟨j,b⟩,h⟩; cases h; rfl
  right_inv b := rfl

noncomputable def rankParamsEquivSlice (k s : ℕ) (hs : 2 ≤ s ∧ s ≤ k+1) :
    RankFiberParams n k (s-1) ≃ {p : FiberParams n k // p.1.val+2=s} := by
  let i : Fin k := ⟨s-2,by omega⟩
  have hi : i.val+1=s-1 := by dsimp [i]; omega
  let e := (rankIndexSliceEquiv (fun j : Fin k => RankFiberParams n k (j.val+1)) i).symm
  have e' : RankFiberParams n k (s-1) ≃ {p : FiberParams n k // p.1=i} := by
    simpa only [hi] using e
  apply e'.trans (Equiv.subtypeEquivRight ?_)
  intro p
  constructor
  · intro hp
    rw [hp]
    dsimp [i]
    omega
  · intro hp
    apply Fin.ext
    dsimp [i]
    omega

/-- Restrict the actual positive-complement equivalence by its packet rank. -/
noncomputable def actualRankCodePlacementsEquiv (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v) (s : ℕ)
    (hs : 2 ≤ s ∧ s ≤ outsideCount ⟨hr.1,hr.2.le⟩ v+1) :
    RankFiberParams n (outsideCount ⟨hr.1,hr.2.le⟩ v) (s-1) ≃
      ActualRankCodePlacements c hr t v s := by
  apply (rankParamsEquivSlice (outsideCount ⟨hr.1,hr.2.le⟩ v) s hs).trans
  apply (positivePlacementFibreEquiv c hr t v hk).subtypeEquiv
  intro p
  rw [positivePlacementFibreEquiv_val,positiveFiberTarget_rank]

/-- Theorem 5.2, positive complement: count actual rank-s placements. -/
theorem card_actualRankCodePlacements (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : 0 < outsideCount ⟨hr.1,hr.2.le⟩ v) (s : ℕ)
    (hs : 2 ≤ s ∧ s ≤ outsideCount ⟨hr.1,hr.2.le⟩ v+1) :
    Nat.card (ActualRankCodePlacements c hr t v s)=
      s*(outsideCount ⟨hr.1,hr.2.le⟩ v-1).choose (s-2)*n.choose s := by
  rw [Nat.card_congr (actualRankCodePlacementsEquiv c hr t v hk s hs).symm,
    Nat.card_eq_fintype_card,card_rankFiberParams_paper n _ _ (by omega)]
  have h1 : s-1+1=s := by omega
  have h2 : s-1-1=s-2 := by omega
  rw [h1,h2]

theorem placedBlocks_fullCarrier (B : Finset (ZMod n)) (hne : B.Nonempty) (q : ZMod n) :
    placedBlocks (fullCarrierPlacement B q)={B} := by
  classical
  ext C
  rw [mem_placedBlocks,Finset.mem_singleton]
  constructor
  · rintro ⟨_,site,hsite⟩
    by_cases h : site=q
    · subst site
      simpa [fullCarrierPlacement] using hsite.symm
    · simp [fullCarrierPlacement,h] at hsite
  · rintro rfl
    exact ⟨hne,q,by simp [fullCarrierPlacement]⟩

theorem actual_full_carrier_rank (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0)
    (P : ActualCodePlacements c hr t v) : (placedBlocks P.val).card=1 := by
  obtain ⟨q,rfl⟩ := (fullPlacementFibreEquiv c hr t v hk).surjective P
  rw [fullPlacementFibreEquiv_val,placedBlocks_fullCarrier _ Finset.univ_nonempty]
  simp

noncomputable def actualFullRankCodePlacementsEquiv (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0) :
    ZMod n ≃ ActualRankCodePlacements c hr t v 1 :=
  (fullPlacementFibreEquiv c hr t v hk).trans
    (Equiv.subtypeUnivEquiv (actual_full_carrier_rank c hr t v hk)).symm

/-- The k=0 boundary has n rank-one phases, independently of positive ranks. -/
theorem card_actualFullRankCodePlacements (c : ZMod n) {r : ℕ}
    (hr : 2 ≤ r ∧ r < n) (t : Fin (r-1)) (v : Code (n-r))
    (hk : outsideCount ⟨hr.1,hr.2.le⟩ v=0) :
    Nat.card (ActualRankCodePlacements c hr t v 1)=n := by
  rw [Nat.card_congr (actualFullRankCodePlacementsEquiv c hr t v hk).symm,Nat.card_zmod]

end ProperArc.Chains
