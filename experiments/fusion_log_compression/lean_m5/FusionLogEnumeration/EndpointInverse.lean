import FusionLogEnumeration.EndpointGeometry

namespace FusionLogEnumeration

open RegisteredAbsorptionChains

variable {α : Type*} [DecidableEq α]
variable {n s : ℕ} [NeZero n] [NeZero s]

/-- Read endpoint coordinates from the placement data, independently of any
execution or compatibility witness. -/
noncomputable def coordinatesOfNamed (named : LegalNamedPlacement n s α) :
    EndpointChoices n s := by
  classical
  let pos : ZMod s → Fin n := fun i => (ZMod.finEquiv n).symm (named.position i)
  have inj : Function.Injective pos :=
    (ZMod.finEquiv n).symm.injective.comp named.position_injective
  refine ⟨⟨Finset.univ.image pos, ?_⟩, pos 0, ?_⟩
  · rw [Finset.card_image_of_injective _ inj]
    simp
  · exact Finset.mem_image.mpr ⟨0, Finset.mem_univ _, rfl⟩

theorem coordinatesOfNamed_relativeSite (named : LegalNamedPlacement n s α)
    (i : ZMod s) :
    EndpointChoices.relativeSite (coordinatesOfNamed named).2.1
      ((ZMod.finEquiv n).symm (named.position i)) =
      (ZMod.finEquiv n).symm (named.position i - named.position 0) := by
  simp [EndpointChoices.relativeSite, coordinatesOfNamed]

theorem coordinatesOfNamed_distance (named : LegalNamedPlacement n s α)
    (positive : named.PositivelyOrdered) (i : Fin s) :
    EndpointChoices.relativeDistance (coordinatesOfNamed named) i =
      (ZMod.finEquiv n).symm (named.position (i.val : ZMod s) - named.position 0) := by
  let f : Fin s → Fin n := fun j =>
    (ZMod.finEquiv n).symm (named.position (j.val : ZMod s) - named.position 0)
  have member : ∀ j, f j ∈ EndpointChoices.relativeSites (coordinatesOfNamed named) := by
    intro j
    apply Finset.mem_image.mpr
    refine ⟨(ZMod.finEquiv n).symm (named.position (j.val : ZMod s)), ?_, ?_⟩
    · exact Finset.mem_image.mpr ⟨(j.val : ZMod s), Finset.mem_univ _, rfl⟩
    · exact coordinatesOfNamed_relativeSite named _
  have mono : StrictMono f := by
    intro j k hjk
    have hval (l : Fin s) : (f l).val = named.offset l.val := by
      let x := named.position (l.val : ZMod s) - named.position 0
      have hround : ZMod.finEquiv n ((ZMod.finEquiv n).symm x) = x :=
        (ZMod.finEquiv n).apply_symm_apply x
      have hcast := congrArg ZMod.val hround
      have hfin : ((ZMod.finEquiv n).symm x).val = x.val := by
        rw [← EndpointChoices.finEquiv_val ((ZMod.finEquiv n).symm x)]
        exact hcast
      change ((ZMod.finEquiv n).symm
        (named.position (l.val : ZMod s) - named.position 0)).val = _
      rw [hfin]
      simp [x, LegalNamedPlacement.offset, l.isLt]
    have step : ∀ a b : ℕ, a ≤ b → b < s → named.offset a ≤ named.offset b := by
      intro a b hab hbs
      induction b, hab using Nat.le_induction with
      | base => exact le_rfl
      | succ b hab ih =>
          exact le_trans (ih (by omega)) (positive b (by omega)).le
    change (f j).val < (f k).val
    rw [hval, hval]
    exact lt_of_lt_of_le (positive j.val j.isLt)
      (step (j.val + 1) k.val (by exact hjk) k.isLt)
  have unique := Finset.orderEmbOfFin_unique
    (EndpointChoices.relativeSites_card (coordinatesOfNamed named)) member mono
  exact (congrFun unique i).symm

theorem coordinatesOfNamed_position (named : LegalNamedPlacement n s α)
    (positive : named.PositivelyOrdered) (i : ZMod s) :
    EndpointChoices.position (coordinatesOfNamed named) i = named.position i := by
  have hcast : (((ZMod.finEquiv s).symm i).val : ZMod s) = i := by
    have hval : ((ZMod.finEquiv s).symm i).val = i.val := by
      rw [← EndpointChoices.finEquiv_val ((ZMod.finEquiv s).symm i)]
      exact congrArg ZMod.val ((ZMod.finEquiv s).apply_symm_apply i)
    exact (congrArg (fun k : ℕ => (k : ZMod s)) hval).trans
      (ZMod.natCast_zmod_val i)
  have hanchor : ZMod.finEquiv n (coordinatesOfNamed named).2.1 = named.position 0 := by
    simp [coordinatesOfNamed]
  unfold EndpointChoices.position EndpointChoices.positionAt
  rw [coordinatesOfNamed_distance named positive ((ZMod.finEquiv s).symm i)]
  rw [hanchor, (ZMod.finEquiv n).apply_symm_apply, hcast]
  abel

/-- The inverse restores packet identities at every physical site, not only
the occupied-site set or the final unordered source partition. -/
theorem decode_coordinatesOfNamed (named : LegalNamedPlacement n s α)
    (positive : named.PositivelyOrdered) :
    (decodeEndpointChoices (LiteralPacketCycle.ofNamed named)
      (coordinatesOfNamed named)).placed = named.placed := by
  funext q
  by_cases occupied : named.placed q = none
  · have absent : placementOfCycleBlocks named.block
        (EndpointChoices.position (coordinatesOfNamed named)) q = none := by
      classical
      simp only [placementOfCycleBlocks]
      split_ifs with h
      · obtain ⟨i, hi⟩ := h
        rw [coordinatesOfNamed_position named positive] at hi
        have atSite := named.placed_at i
        rw [hi, occupied] at atSite
        contradiction
      · rfl
    exact absent.trans occupied.symm
  · obtain ⟨i, rfl⟩ := named.only_named q occupied
    rw [named.placed_at]
    have hp := coordinatesOfNamed_position named positive i
    rw [← hp]
    exact placementOfCycleBlocks_at _ _ (EndpointChoices.position_injective _) _

theorem decodeEndpointChoices_relativeSite (choice : EndpointChoices n s)
    (i : Fin s) :
    EndpointChoices.relativeSite choice.2.1
      ((ZMod.finEquiv n).symm
        (EndpointChoices.position choice (i.val : ZMod s))) =
      choice.relativeDistance i := by
  apply (ZMod.finEquiv n).injective
  simp [EndpointChoices.relativeSite, EndpointChoices.position_fin]

theorem endpointChoices_ext {x y : EndpointChoices n s}
    (sites : x.1.1 = y.1.1) (anchor : x.2.1 = y.2.1) : x = y := by
  rcases x with ⟨⟨xs, hx⟩, ⟨xa, ha⟩⟩
  rcases y with ⟨⟨ys, hy⟩, ⟨ya, hb⟩⟩
  dsimp at sites anchor
  subst ys
  subst ya
  rfl

theorem coordinatesOfNamed_decode (cycle : LiteralPacketCycle s α)
    (choice : EndpointChoices n s) :
    coordinatesOfNamed (decodeEndpointChoices cycle choice) = choice := by
  classical
  let named := decodeEndpointChoices cycle choice
  let coordinates := coordinatesOfNamed named
  have hs : 0 < s := Nat.pos_of_ne_zero (NeZero.ne s)
  have hsub : coordinates.1.1 ⊆ choice.1.1 := by
    intro q hq
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hq
    let j := (ZMod.finEquiv s).symm i
    have hidx : (j.val : ZMod s) = i := by
      have hval : j.val = i.val := by
        rw [← EndpointChoices.finEquiv_val j]
        exact congrArg ZMod.val ((ZMod.finEquiv s).apply_symm_apply i)
      exact (congrArg (fun k : ℕ => (k : ZMod s)) hval).trans
        (ZMod.natCast_zmod_val i)
    have hrel : EndpointChoices.relativeSite choice.2.1
        ((ZMod.finEquiv n).symm (named.position i)) =
        choice.relativeDistance j := by
      rw [← hidx]
      change EndpointChoices.relativeSite choice.2.1
        ((ZMod.finEquiv n).symm
          (EndpointChoices.position choice (j.val : ZMod s))) = _
      exact decodeEndpointChoices_relativeSite choice j
    have hsite : EndpointChoices.relativeSite choice.2.1
        ((ZMod.finEquiv n).symm (named.position i)) ∈ choice.relativeSites := by
      rw [hrel]
      exact Finset.orderEmbOfFin_mem _
        (EndpointChoices.relativeSites_card choice) j
    obtain ⟨r, hr, hrelr⟩ := Finset.mem_image.mp hsite
    have sameSite := EndpointChoices.relativeSite_injective choice.2.1
      hrelr
    rw [← sameSite]
    exact hr
  have hcard : coordinates.1.1.card = choice.1.1.card :=
    coordinates.1.2.trans choice.1.2.symm
  have hsitesVal : coordinates.1.1 = choice.1.1 :=
    Finset.eq_of_subset_of_card_le hsub (le_of_eq hcard.symm)
  apply endpointChoices_ext hsitesVal
  change (ZMod.finEquiv n).symm (named.position 0) = choice.2.1
  dsimp only [named]
  rw [decodeEndpointChoices_anchor cycle choice hs]
  exact (ZMod.finEquiv n).symm_apply_apply _

theorem coordinatesOfNamed_congr (first second : LegalNamedPlacement n s α)
    (placed : first.placed = second.placed) (blocks : first.block = second.block) :
    coordinatesOfNamed first = coordinatesOfNamed second := by
  have positions : first.position = second.position := by
    funext i
    have hi : second.placed (first.position i) = some (second.block i) := by
      rw [← placed, first.placed_at, blocks]
    obtain ⟨j, hj⟩ := second.only_named (first.position i) (by simp [hi])
    have hblock : second.block j = second.block i := by
      have atJ := second.placed_at j
      rw [hj, hi] at atJ
      exact (Option.some.inj atJ).symm
    have hji : j = i := by
      by_contra ne
      obtain ⟨a, ha⟩ := second.block_nonempty j
      exact Finset.disjoint_left.mp (second.block_disjoint j i ne) ha
        (hblock ▸ ha)
    simpa only [hji] using hj.symm
  apply endpointChoices_ext
  · change Finset.univ.image (fun i => (ZMod.finEquiv n).symm (first.position i)) =
      Finset.univ.image (fun i => (ZMod.finEquiv n).symm (second.position i))
    rw [positions]
  · change (ZMod.finEquiv n).symm (first.position 0) =
      (ZMod.finEquiv n).symm (second.position 0)
    rw [positions]

end FusionLogEnumeration
