import FusionLogAllR.AllROptimality

namespace FusionLogAllR

/-! # A derived, rather than assumed, hole-potential ledger

These are finite gap-vector rewrites. They do not assert that every raw
all-R execution has already been converted to such a trace. That geometric
extraction is a separate obligation. Once a trace is supplied, its balance
and the total fusion contribution follow by induction; no endpoint balance
equation is an input.
-/

inductive HoleTransition : List ℤ → List ℤ → Type
  | stationary (g : List ℤ) : HoleTransition g g
  | slide (pre : List ℤ) (x y : ℤ) (tail : List ℤ) :
      HoleTransition (slideSource pre x y tail) (slideTarget pre x y tail)
  | backslide (x : ℤ) (middle : List ℤ) (y : ℤ) :
      HoleTransition (carrierBackslideSource x middle y)
        (carrierBackslideTarget x middle y)
  | rankOneBackslide (g : ℤ) : HoleTransition [g] [g]
  | fusion (g : ℤ) (tail : List ℤ) :
      HoleTransition (fusionSource g tail) (fusionTarget g tail)

structure HoleLedger where
  slides : ℕ := 0
  backslides : ℕ := 0
  weightedBack : ℕ := 0
  fusionGain : ℕ := 0
  deriving Repr

def HoleLedger.add (a b : HoleLedger) : HoleLedger :=
  ⟨a.slides + b.slides, a.backslides + b.backslides,
    a.weightedBack + b.weightedBack, a.fusionGain + b.fusionGain⟩

def HoleTransition.ledger {g h : List ℤ} : HoleTransition g h → HoleLedger
  | .stationary _ => ⟨0, 0, 0, 0⟩
  | .slide _ _ _ _ => ⟨1, 0, 0, 0⟩
  | .backslide _ middle _ => ⟨0, 1, middle.length + 1, 0⟩
  | .rankOneBackslide _ => ⟨0, 1, 0, 0⟩
  | .fusion _ tail => ⟨0, 0, 0, tail.length⟩

theorem HoleTransition.potential_change {g h : List ℤ}
    (t : HoleTransition g h) :
    holePotential h = holePotential g - t.ledger.slides +
      t.ledger.weightedBack + t.ledger.fusionGain := by
  cases t with
  | stationary g => simp [ledger]
  | slide pre x y tail => simpa [ledger] using holePotential_slide pre x y tail
  | backslide x middle y =>
      simpa [ledger, Nat.cast_add, Nat.cast_one, add_assoc] using
        holePotential_backslide x middle y
  | rankOneBackslide g => simp [ledger]
  | fusion g tail => simpa [ledger] using holePotential_fusion g tail

theorem triangular_succ (m : ℕ) : triangular (m + 1) = triangular m + m := by
  rw [← triangular_sum, ← triangular_sum, Finset.sum_range_succ]

theorem HoleTransition.fusion_budget {g h : List ℤ}
    (t : HoleTransition g h) :
    triangular (g.length - 1) = t.ledger.fusionGain + triangular (h.length - 1) := by
  cases t with
  | stationary g => simp [ledger]
  | slide pre x y tail => simp [ledger, slideSource, slideTarget]
  | backslide x middle y =>
      simp [ledger, carrierBackslideSource, carrierBackslideTarget]
  | rankOneBackslide g => simp [ledger]
  | fusion g tail =>
      simpa [ledger, fusionSource, fusionTarget, Nat.add_comm] using
        triangular_succ tail.length

inductive HoleTrace : List ℤ → List ℤ → Type
  | nil (g : List ℤ) : HoleTrace g g
  | cons {g h k : List ℤ} (t : HoleTransition g h) (rest : HoleTrace h k) :
      HoleTrace g k

def HoleTrace.ledger {g h : List ℤ} : HoleTrace g h → HoleLedger
  | .nil _ => ⟨0, 0, 0, 0⟩
  | .cons t rest => t.ledger.add rest.ledger

theorem HoleTrace.potential_balance {g h : List ℤ} (t : HoleTrace g h) :
    holePotential h = holePotential g - t.ledger.slides +
      t.ledger.weightedBack + t.ledger.fusionGain := by
  induction t with
  | nil g => simp [ledger]
  | cons first rest ih =>
      have hfirst := first.potential_change
      simp only [ledger, HoleLedger.add, Nat.cast_add]
      omega

theorem HoleTrace.fusion_budget {g h : List ℤ} (t : HoleTrace g h) :
    triangular (g.length - 1) = t.ledger.fusionGain + triangular (h.length - 1) := by
  induction t with
  | nil g => simp [ledger]
  | cons first rest ih =>
      have hfirst := first.fusion_budget
      simp only [ledger, HoleLedger.add]
      omega

def initialGaps (n : ℕ) : List ℤ := 1 :: List.replicate (n - 2) 0

theorem holePotential_replicate_zero (m : ℕ) :
    holePotential (List.replicate m 0) = 0 := by
  induction m with
  | zero => rfl
  | succ m ih => simp [List.replicate_succ, holePotential, ih]

theorem initialGaps_potential (n : ℕ) :
    holePotential (initialGaps n) = (n - 2 : ℕ) := by
  simp [initialGaps, holePotential, holePotential_replicate_zero]

theorem triangular_eq_allRSlides (n : ℕ) :
    triangular (n - 1) = allRSlides n := by
  have hsub : n - 1 - 1 = n - 2 := by omega
  simp [triangular, allRSlides, hsub]

/-- The exact slide count, now derived from the whole finite rewrite trace.
Rank-one tail backslides have weight zero and remain in `ledger.backslides`. -/
theorem HoleTrace.allR_slide_identity {n : ℕ} (hn : 3 ≤ n) (q : ℤ)
    (t : HoleTrace (initialGaps n) [q]) :
    t.ledger.slides = allRSlides n + t.ledger.weightedBack := by
  have hpotential := t.potential_balance
  have hfusion := t.fusion_budget
  have hlength : (initialGaps n).length - 1 = n - 2 := by simp [initialGaps]
  rw [hlength] at hfusion
  simp only [List.length_singleton, Nat.sub_self, triangular, Nat.zero_mul,
    Nat.zero_div, Nat.add_zero] at hfusion
  have hinit := initialGaps_potential n
  have htri := triangular_succ (n - 2)
  have hn₁ : n - 2 + 1 = n - 1 := by omega
  rw [hn₁, triangular_eq_allRSlides] at htri
  change triangular (n - 2) = t.ledger.fusionGain at hfusion
  rw [hfusion] at htri
  simp only [holePotential, List.length_nil, Nat.cast_zero, zero_mul,
    add_zero] at hpotential
  rw [hinit] at hpotential
  omega

end FusionLogAllR
