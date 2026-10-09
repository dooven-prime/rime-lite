import Paper38.ReturnLayers
import Mathlib.GroupTheory.SpecificGroups.Dihedral

/-!
# Initial-factor separation in the ten-element dihedral group

Both systems have A = D10. Their first layers are the rotation and
reflection cosets; their second cumulative layers coincide. This is the
finite group part of the symbolic matched family, not an all-g raw replay.
-/

namespace Rime.Paper38

open scoped Pointwise

abbrev PentagonGroup := DihedralGroup 5

def rotationLayer : Finset PentagonGroup := Finset.univ.image DihedralGroup.r

def reflectionLayer : Finset PentagonGroup := Finset.univ.image DihedralGroup.sr

theorem initial_layers_disjoint : Disjoint rotationLayer reflectionLayer := by
  apply Finset.disjoint_left.mpr
  intro x hx hy
  obtain ⟨i, _, rfl⟩ := Finset.mem_image.mp hx
  obtain ⟨j, _, h⟩ := Finset.mem_image.mp hy
  cases h

theorem initial_layers_equal_card : rotationLayer.card = 5 ∧ reflectionLayer.card = 5 := by
  constructor
  · rw [rotationLayer, Finset.card_image_of_injective _ (fun _ _ h => DihedralGroup.r.inj h)]
    exact ZMod.card 5
  · rw [reflectionLayer, Finset.card_image_of_injective _ (fun _ _ h => DihedralGroup.sr.inj h)]
    exact ZMod.card 5

theorem initial_layers_differ : rotationLayer ≠ reflectionLayer := by
  intro h
  have hrot : DihedralGroup.r (0 : ZMod 5) ∈ rotationLayer :=
    Finset.mem_image.mpr ⟨0, Finset.mem_univ _, rfl⟩
  exact Finset.disjoint_left.mp initial_layers_disjoint hrot (h ▸ hrot)

theorem full_aggregate_mul_nonempty {G : Type*} [Group G] [Fintype G] [DecidableEq G]
    (B : Finset G) (hB : B.Nonempty) : Finset.univ * B = Finset.univ := by
  obtain ⟨b, hb⟩ := hB
  apply Finset.eq_univ_iff_forall.mpr
  intro x
  exact Finset.mem_mul.mpr ⟨x * b⁻¹, Finset.mem_univ _, b, hb, by simp⟩

theorem initial_separation_second_recovery :
    cumulativeLayer Finset.univ rotationLayer 0 ≠
      cumulativeLayer Finset.univ reflectionLayer 0 ∧
    cumulativeLayer Finset.univ rotationLayer 1 = Finset.univ ∧
    cumulativeLayer Finset.univ reflectionLayer 1 = Finset.univ := by
  have hr : rotationLayer.Nonempty := ⟨DihedralGroup.r 0, Finset.mem_image.mpr ⟨0, by simp, rfl⟩⟩
  have hs : reflectionLayer.Nonempty := ⟨DihedralGroup.sr 0, Finset.mem_image.mpr ⟨0, by simp, rfl⟩⟩
  refine ⟨initial_layers_differ, ?_, ?_⟩
  · simp [cumulativeLayer, full_aggregate_mul_nonempty rotationLayer hr]
  · simp [cumulativeLayer, full_aggregate_mul_nonempty reflectionLayer hs]

def pentagonRead : PentagonGroup → ZMod 5 → ZMod 5
  | .r k, i => i + k
  | .sr k, i => -i - k

theorem matched_survivor_reads_differ :
    (pentagonRead (.r 0) 2, pentagonRead (.r 0) 3, pentagonRead (.r 0) 4) ≠
      (pentagonRead (.sr 4) 2, pentagonRead (.sr 4) 3, pentagonRead (.sr 4) 4) := by
  decide

end Rime.Paper38
