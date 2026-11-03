import full_summary.Classification
import FutureEvent.ZeroCarrierAssembly

namespace FullSummary

open RegisteredAbsorptionChains FutureEvent

variable {n : ℕ} [NeZero n]

/-- Rotate source atoms 1,2 to the kernel and fuse them, spoiling future
registration of exactly {0,1}. The exponent is an actual nonnegative length. -/
def spoiledSeed : Execution n (ZMod n) :=
  run {0, 1} (singletonExecution n) (pWord (-(1 : ZMod n)).val ++ [.d])

theorem spoiledSeed_generated : PairGenerated (spoiledSeed (n := n)) := ⟨_, rfl⟩

theorem spoiledSeed_null (hn : 3 ≤ n) : PermanentlyUnregistered (spoiledSeed (n := n)) := by
  have hval1 : (1 : ZMod n).val = 1 := by
    simpa using ZMod.val_natCast_of_lt (n := n) (a := 1) (by omega)
  have hval2 : (2 : ZMod n).val = 2 := by
    simpa using ZMod.val_natCast_of_lt (n := n) (a := 2) (by omega)
  have h01 : (0 : ZMod n) ≠ 1 := by intro h; have hv := congrArg ZMod.val h; simp [hval1] at hv
  have h02 : (0 : ZMod n) ≠ 2 := by intro h; have hv := congrArg ZMod.val h; simp [hval2] at hv
  have h21 : (2 : ZMod n) ≠ 1 := by intro h; have hv := congrArg ZMod.val h; simp [hval1, hval2] at hv
  let initial := run {0, 1} (singletonExecution n) (pWord (-(1 : ZMod n)).val)
  have h0 : initial.placed 0 = some {1} := by
    dsimp [initial]
    rw [run_rotation]
    simp [rotate, singletonExecution]
  have h1 : initial.placed 1 = some {2} := by
    dsimp [initial]
    rw [run_rotation]
    norm_num [rotate, singletonExecution]
  have ho : initial.origin = none := by dsimp [initial]; rw [run_rotation]; rfl
  have hbad : ({1} : Finset (ZMod n)) ∪ {2} ≠ {0, 1} := by
    intro he
    have hz : (0 : ZMod n) ∈ ({1} : Finset (ZMod n)) ∪ {2} := by rw [he]; simp
    simp [h01, h02] at hz
  have hbad' : ({1, 2} : Finset (ZMod n)) ≠ {0, 1} := by simpa using hbad
  have hnone : (spoiledSeed (n := n)).origin = none := by
    change (run {0, 1} (singletonExecution n) (pWord (-(1 : ZMod n)).val ++ [.d])).origin = none
    rw [run_append]
    change (stepDefect {0, 1} initial).origin = none
    simp [stepDefect, h0, h1, ho, hbad']
  let f : ZMod n → ZMod n := fun a => collapsePosition (a - 1)
  have hp : (spoiledSeed (n := n)).placed = placementOfMap f := by
    have h := atomSite_run {0, 1} (singletonExecution n) (fun a : ZMod n => a)
      (pWord (-(1 : ZMod n)).val ++ [.d]) (by omega) singleton_seed_map
    have hmap : siteWord (pWord (-(1 : ZMod n)).val ++ [.d]) ∘ (fun a : ZMod n => a) = f := by
      funext a
      change siteWord (pWord (-(1 : ZMod n)).val ++ [.d]) a = f a
      rw [siteWord_append, siteWord_pWord]
      simp [siteWord, siteLetter, f, sub_eq_add_neg]
    exact h.trans (congrArg placementOfMap hmap)
  refine ⟨hnone, ?_⟩
  intro hr
  have hs := (generated_registerable_iff_singletons _ f hn spoiledSeed_generated hp hnone).mp hr
  apply h21
  apply hs.2 2
  dsimp [f]
  rw [show (2 : ZMod n) - 1 = 1 by ring]
  simp [collapsePosition]

end FullSummary
