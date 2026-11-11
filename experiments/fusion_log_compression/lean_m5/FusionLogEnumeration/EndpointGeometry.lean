import FusionLogEnumeration.EndpointCounting
import RegisteredAbsorptionChains.GapNamedPlacement
import Mathlib.Data.Finset.Sort

namespace FusionLogEnumeration

open RegisteredAbsorptionChains

variable {α : Type*} [DecidableEq α]

/-- A fixed positively ordered cycle of literal packets. The coverage field is
separate because `MarkedCircle` records disjointness but not an ambient atom
universe. -/
structure LiteralPacketCycle (s : ℕ) (α : Type*) [DecidableEq α]
    [NeZero s] where
  block : ZMod s → Finset α
  block_nonempty : ∀ i, (block i).Nonempty
  block_disjoint : ∀ i j, i ≠ j → Disjoint (block i) (block j)
  atom_covered : ∀ a : α, ∃ i, a ∈ block i

namespace LiteralPacketCycle

noncomputable def ofNamed {n s : ℕ} [NeZero n] [NeZero s]
    (named : LegalNamedPlacement n s α) : LiteralPacketCycle s α where
  block := named.block
  block_nonempty := named.block_nonempty
  block_disjoint := named.block_disjoint
  atom_covered := named.atom_covered

@[simp] theorem ofNamed_block {n s : ℕ} [NeZero n] [NeZero s]
    (named : LegalNamedPlacement n s α) (i : ZMod s) :
    (ofNamed named).block i = named.block i := rfl

end LiteralPacketCycle

namespace EndpointChoices

variable {n s : ℕ} [NeZero n] [NeZero s]

/-- Express a physical site as its forward distance from the selected anchor. -/
def relativeSite (anchor site : Fin n) : Fin n :=
  (ZMod.finEquiv n).symm ((ZMod.finEquiv n site) - (ZMod.finEquiv n anchor))

theorem relativeSite_injective (anchor : Fin n) :
    Function.Injective (relativeSite (n := n) anchor) := by
  intro x y h
  apply (ZMod.finEquiv n).injective
  have h' := congrArg (ZMod.finEquiv n) h
  simp [relativeSite] at h'
  exact congrArg (ZMod.finEquiv n) h'

@[simp] theorem relativeSite_anchor (anchor : Fin n) :
    relativeSite (n := n) anchor anchor = 0 := by
  simp [relativeSite]

def relativeSites (choice : EndpointChoices n s) : Finset (Fin n) :=
  choice.1.1.image (relativeSite (n := n) choice.2.1)

theorem relativeSites_card (choice : EndpointChoices n s) :
    (relativeSites choice).card = s := by
  rw [relativeSites, Finset.card_image_of_injective _
    (relativeSite_injective (n := n) choice.2.1), choice.1.2]

theorem zero_mem_relativeSites (choice : EndpointChoices n s) :
    (0 : Fin n) ∈ relativeSites choice := by
  apply Finset.mem_image.mpr
  exact ⟨choice.2.1, choice.2.2, relativeSite_anchor (n := n) choice.2.1⟩

def relativeDistance (choice : EndpointChoices n s) (i : Fin s) : Fin n :=
  (relativeSites choice).orderEmbOfFin (relativeSites_card choice) i

theorem relativeDistance_strictMono (choice : EndpointChoices n s) :
    StrictMono (relativeDistance choice) :=
  (Finset.orderEmbOfFin (relativeSites choice) (relativeSites_card choice)).strictMono

theorem relativeDistance_zero (choice : EndpointChoices n s) (hs : 0 < s) :
    relativeDistance choice ⟨0, hs⟩ = 0 := by
  unfold relativeDistance
  rw [Finset.orderEmbOfFin_zero (relativeSites_card choice) hs]
  apply Fin.ext
  have hmin := Finset.min'_le (relativeSites choice) 0
    (zero_mem_relativeSites choice)
  exact Nat.eq_zero_of_le_zero (by simpa using hmin)

theorem finEquiv_val (i : Fin n) : (ZMod.finEquiv n i).val = i.val := by
  cases n with
  | zero => exact (NeZero.ne 0 rfl).elim
  | succ n => rfl

def positionAt (choice : EndpointChoices n s) (i : Fin s) : ZMod n :=
  (ZMod.finEquiv n choice.2.1) +
    (ZMod.finEquiv n (relativeDistance choice i))

theorem positionAt_injective (choice : EndpointChoices n s) :
    Function.Injective (positionAt choice) := by
  intro i j h
  have hd : relativeDistance choice i = relativeDistance choice j := by
    apply (ZMod.finEquiv n).injective
    exact add_left_cancel h
  exact (Finset.orderEmbOfFin (relativeSites choice)
    (relativeSites_card choice)).injective hd

def position (choice : EndpointChoices n s) (i : ZMod s) : ZMod n :=
  positionAt choice ((ZMod.finEquiv s).symm i)

theorem position_injective (choice : EndpointChoices n s) :
    Function.Injective (position choice) := by
  intro i j h
  apply (ZMod.finEquiv s).symm.injective
  exact positionAt_injective choice h

theorem position_zero (choice : EndpointChoices n s) (hs : 0 < s) :
    position choice 0 = ZMod.finEquiv n choice.2.1 := by
  unfold position
  have hidx : (ZMod.finEquiv s).symm (0 : ZMod s) = ⟨0, hs⟩ := by
    apply (ZMod.finEquiv s).injective
    simp
  rw [hidx, positionAt, relativeDistance_zero choice hs]
  simp

theorem position_fin (choice : EndpointChoices n s) (i : Fin s) :
    position choice (i.val : ZMod s) =
      (ZMod.finEquiv n choice.2.1) +
        (ZMod.finEquiv n (relativeDistance choice i)) := by
  unfold position
  have hidx : (ZMod.finEquiv s).symm (i.val : ZMod s) = i := by
    apply (ZMod.finEquiv s).injective
    calc
      (ZMod.finEquiv s) ((ZMod.finEquiv s).symm (i.val : ZMod s)) =
          (i.val : ZMod s) := Equiv.apply_symm_apply _ _
      _ = ZMod.finEquiv s i := by
        simpa only [finEquiv_val] using
          (ZMod.natCast_zmod_val (ZMod.finEquiv s i))
  rw [hidx, positionAt]

theorem position_offset_value (choice : EndpointChoices n s) (i : Fin s) :
    ((position choice (i.val : ZMod s) - position choice 0).val) =
      (relativeDistance choice i).val := by
  have hs : 0 < s := Nat.pos_of_ne_zero (NeZero.ne s)
  rw [position_fin, position_zero choice hs]
  have hsub : (ZMod.finEquiv n choice.2.1) +
      ZMod.finEquiv n (relativeDistance choice i) -
      ZMod.finEquiv n choice.2.1 = ZMod.finEquiv n (relativeDistance choice i) := by
    abel
  rw [hsub, finEquiv_val]

def siteOffset (choice : EndpointChoices n s) (k : ℕ) : ℕ :=
  if k < s then (position choice (k : ZMod s) - position choice 0).val else n

theorem siteOffset_eq_relativeDistance (choice : EndpointChoices n s)
    (k : ℕ) (hk : k < s) :
    siteOffset choice k = (relativeDistance choice ⟨k, hk⟩).val := by
  rw [siteOffset, if_pos hk, position_offset_value choice ⟨k, hk⟩]

theorem siteOffset_end (choice : EndpointChoices n s) : siteOffset choice s = n := by
  simp [siteOffset]

theorem siteOffset_strict (choice : EndpointChoices n s) :
    ∀ k : ℕ, k < s → siteOffset choice k < siteOffset choice (k + 1) := by
  intro k hk
  by_cases hnext : k + 1 < s
  · have i : Fin s := ⟨k, hk⟩
    have j : Fin s := ⟨k + 1, hnext⟩
    rw [siteOffset_eq_relativeDistance choice k hk,
      siteOffset_eq_relativeDistance choice (k + 1) hnext]
    exact relativeDistance_strictMono choice (Fin.mk_lt_mk.mpr (by omega))
  · have hend : k + 1 = s := by omega
    rw [siteOffset_eq_relativeDistance choice k hk, hend, siteOffset_end]
    exact (relativeDistance choice ⟨k, hk⟩).isLt

end EndpointChoices

noncomputable def placementOfCycleBlocks {n s : ℕ} [NeZero n] [NeZero s]
    (block : ZMod s → Finset α) (position : ZMod s → ZMod n) :
    Placement n (Finset α) := by
  classical
  exact fun q => if h : ∃ i, position i = q then
    some (block (Classical.choose h)) else none

theorem placementOfCycleBlocks_at {n s : ℕ} [NeZero n] [NeZero s]
    (block : ZMod s → Finset α) (position : ZMod s → ZMod n)
    (injective : Function.Injective position) (i : ZMod s) :
    placementOfCycleBlocks block position (position i) = some (block i) := by
  classical
  let h : ∃ j, position j = position i := ⟨i, rfl⟩
  have hc : Classical.choose h = i := injective (Classical.choose_spec h)
  simp [placementOfCycleBlocks, h, hc]

theorem placementOfCycleBlocks_only_named {n s : ℕ} [NeZero n] [NeZero s]
    (block : ZMod s → Finset α) (position : ZMod s → ZMod n) (q : ZMod n)
    (occupied : placementOfCycleBlocks block position q ≠ none) :
    ∃ i, position i = q := by
  classical
  by_contra h
  simp [placementOfCycleBlocks, not_exists.mp h] at occupied

/-- Decode occupied-site/anchor coordinates as the unique named packet layout
whose cycle order is the fixed `LiteralPacketCycle`. -/
noncomputable def decodeEndpointChoices {n s : ℕ} [NeZero n] [NeZero s]
    (cycle : LiteralPacketCycle s α) (choice : EndpointChoices n s) :
    LegalNamedPlacement n s α := by
  let pos := EndpointChoices.position choice
  exact {
    placed := placementOfCycleBlocks cycle.block pos
    position := pos
    block := cycle.block
    position_injective := EndpointChoices.position_injective choice
    placed_at := placementOfCycleBlocks_at cycle.block pos
      (EndpointChoices.position_injective choice)
    only_named := placementOfCycleBlocks_only_named cycle.block pos
    block_nonempty := cycle.block_nonempty
    block_disjoint := cycle.block_disjoint
    atom_covered := cycle.atom_covered }

theorem decodeEndpointChoices_positive {n s : ℕ} [NeZero n] [NeZero s]
    (cycle : LiteralPacketCycle s α) (choice : EndpointChoices n s) :
    (decodeEndpointChoices cycle choice).PositivelyOrdered := by
  intro k hk
  change EndpointChoices.siteOffset choice k < EndpointChoices.siteOffset choice (k + 1)
  exact EndpointChoices.siteOffset_strict choice k hk

theorem decodeEndpointChoices_anchor {n s : ℕ} [NeZero n] [NeZero s]
    (cycle : LiteralPacketCycle s α) (choice : EndpointChoices n s)
    (hs : 0 < s) :
    (decodeEndpointChoices cycle choice).position 0 = ZMod.finEquiv n choice.2.1 :=
  EndpointChoices.position_zero choice hs

end FusionLogEnumeration
