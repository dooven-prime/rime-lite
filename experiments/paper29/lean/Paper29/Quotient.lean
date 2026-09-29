import Mathlib.Data.Finset.Image

/-!
# Same-lineage spectator quotient

The exact Conf_{2,3} projection uses one lineage map for both the candidate
pair and all three spectators.  Naturality below does not allow independently
chosen witnesses for the two parts.
-/

namespace Rime.Paper29

structure SplitConfig (α : Type u) [DecidableEq α] where
  pair : Finset α
  spectators : Finset α

def projectConfig [DecidableEq Lineage] [DecidableEq Coord]
    (lineage : Lineage → Coord) (source : SplitConfig Lineage) :
    SplitConfig Coord where
  pair := source.pair.image lineage
  spectators := source.spectators.image lineage

def mapConfig [DecidableEq Coord] [DecidableEq Coord']
    (action : Coord → Coord') (state : SplitConfig Coord) :
    SplitConfig Coord' where
  pair := state.pair.image action
  spectators := state.spectators.image action

/-- Projection commutes with an action when both colors use the same map. -/
theorem projectConfig_comp
    [DecidableEq Lineage] [DecidableEq Coord] [DecidableEq Coord']
    (action : Coord → Coord') (lineage : Lineage → Coord)
    (source : SplitConfig Lineage) :
    projectConfig (action ∘ lineage) source =
      mapConfig action (projectConfig lineage source) := by
  cases source
  simp [projectConfig, mapConfig, Finset.image_image, Function.comp_def]

/-- Pointwise equality of the one lineage witness preserves the quotient. -/
theorem projectConfig_congr
    [DecidableEq Lineage] [DecidableEq Coord]
    (left right : Lineage → Coord) (source : SplitConfig Lineage)
    (h : left = right) :
    projectConfig left source = projectConfig right source := by
  cases h
  rfl

end Rime.Paper29
