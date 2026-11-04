import RegisteredAbsorptionChains.SourceOrderInvariant
import Mathlib.Tactic

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- Source addresses are offset by `c`; the interval endpoints remain in the
aligned physical frame. Source wraparound does not change their order. -/
def interval (c : ZMod n) (lo hi : ℕ) : Finset (ZMod n) :=
  (Finset.Ico lo hi).image (fun i : ℕ => c + (i : ZMod n))

def arc (c : ZMod n) (r : ℕ) : Finset (ZMod n) := interval c 0 r

theorem mem_interval_iff (c a : ZMod n) (lo hi : ℕ) (hhi : hi ≤ n) :
    a ∈ interval c lo hi ↔ lo ≤ (a - c).val ∧ (a - c).val < hi := by
  constructor
  · intro ha
    obtain ⟨i, hiI, rfl⟩ := Finset.mem_image.mp ha
    have hi' := Finset.mem_Ico.mp hiI
    rw [add_sub_cancel_left, ZMod.val_natCast_of_lt (show i < n by omega)]
    exact hi'
  · intro ha
    refine Finset.mem_image.mpr ⟨(a - c).val, Finset.mem_Ico.mpr ha, ?_⟩
    rw [ZMod.natCast_zmod_val]
    abel

omit [NeZero n] in
theorem card_interval (c : ZMod n) (lo hi : ℕ) (hhi : hi ≤ n) :
    (interval c lo hi).card = hi - lo := by
  unfold interval
  rw [Finset.card_image_iff.mpr]
  · simp
  · intro a ha b hb hab
    have ha' := Finset.mem_Ico.mp ha
    have hb' := Finset.mem_Ico.mp hb
    have heq := congrArg ZMod.val (add_left_cancel hab)
    simpa only [ZMod.val_natCast_of_lt (show a < n by omega),
      ZMod.val_natCast_of_lt (show b < n by omega)] using heq

omit [NeZero n] in
theorem card_arc (c : ZMod n) (r : ℕ) (hr : r ≤ n) : (arc c r).card = r := by
  simpa [arc] using card_interval c 0 r hr

theorem interval_union (c : ZMod n) (lo mid hi : ℕ)
    (hl : lo ≤ mid) (hm : mid ≤ hi) (hh : hi ≤ n) :
    interval c lo mid ∪ interval c mid hi = interval c lo hi := by
  ext a
  rw [Finset.mem_union, mem_interval_iff c a lo mid (by omega),
    mem_interval_iff c a mid hi hh, mem_interval_iff c a lo hi hh]
  omega

theorem interval_disjoint (c : ZMod n) (lo mid hi : ℕ) (hh : hi ≤ n) (hm : mid ≤ hi) :
    Disjoint (interval c lo mid) (interval c mid hi) := by
  apply Finset.disjoint_left.mpr
  intro a ha hb
  have hl := (mem_interval_iff c a lo mid (by omega)).mp ha
  have hr := (mem_interval_iff c a mid hi hh).mp hb
  omega

def originRecord (c : ZMod n) (r t : ℕ) : FusionRecord (ZMod n) :=
  ⟨interval c 0 t, interval c t r, arc c r⟩

theorem originRecord_union (c : ZMod n) (r t : ℕ) (ht : t ≤ r) (hr : r ≤ n) :
    (originRecord c r t).left ∪ (originRecord c r t).right = arc c r :=
  interval_union c 0 t r (Nat.zero_le _) ht hr

omit [NeZero n] in
theorem originRecord_injective (c : ZMod n) (r : ℕ) (hr : r ≤ n) :
    Function.Injective (fun t : Fin (r - 1) => originRecord c r (t.val + 1)) := by
  intro s t h
  have hc := congrArg (fun record : FusionRecord (ZMod n) => record.left.card) h
  change (interval c 0 (s.val + 1)).card = (interval c 0 (t.val + 1)).card at hc
  rw [card_interval c 0 _ (by omega), card_interval c 0 _ (by omega)] at hc
  apply Fin.ext
  omega

end ProperArc
