import RSR2History.UpperLoadingLift
import RSR2History.LoggedExecution

/-!
# Physical simulation for one upper loading anchor

The tracked packet is already in the upper layer. Actual guarded `step`
updates its integer lift by `x ↦ x + 1` on `p₁`, by `upperDefectLift` on
`d₁`, and leaves it fixed on all other letters. The projection theorem below
keeps this ghost calculation tied to the real placement executor.
-/

namespace RSR2History
open RSR2.Parametric

structure UpperAnchorState (n : Nat) where
  packet : Finset (Fin n)
  coord : Int
  slides : Nat

def UpperAnchorMatches (n : Nat) (P : Placement n) (anchor : UpperAnchorState n) : Prop :=
  ∀ a ∈ anchor.packet,
    (P a).1 = true ∧ anchor.coord % (n : Int) = ((P a).2.val : Int)

def upperAnchorUpdate (n : Nat) (anchor : UpperAnchorState n) : Letter →
    UpperAnchorState n
  | .p true => { anchor with coord := anchor.coord + 1 }
  | .d true =>
      { anchor with
        coord := upperDefectLift n anchor.coord
        slides := anchor.slides +
          if anchor.coord % (n : Int) = 1 then 1 else 0 }
  | _ => anchor

def upperLiftProjection : List Letter → List UpperLiftOp
  | [] => []
  | .p true :: rest => .rotate :: upperLiftProjection rest
  | .d true :: rest => .silentSlide :: upperLiftProjection rest
  | _ :: rest => upperLiftProjection rest

def upperAnchorAdvance (n : Nat) (ops : List UpperLiftOp)
    (anchor : UpperAnchorState n) : UpperAnchorState n :=
  { anchor with
    coord := upperLiftRun n ops anchor.coord
    slides := anchor.slides + upperLiftSlideHits n ops anchor.coord }

theorem upperLiftRun_append (n : Nat) (ops rest : List UpperLiftOp) (x : Int) :
    upperLiftRun n (ops ++ rest) x =
      upperLiftRun n rest (upperLiftRun n ops x) := by
  induction ops generalizing x with
  | nil => rfl
  | cons op ops ih =>
      cases op <;> simp [upperLiftRun, ih]

theorem upperLiftSlideHits_append (n : Nat) (ops rest : List UpperLiftOp) (x : Int) :
    upperLiftSlideHits n (ops ++ rest) x =
      upperLiftSlideHits n ops x +
        upperLiftSlideHits n rest (upperLiftRun n ops x) := by
  induction ops generalizing x with
  | nil => simp [upperLiftRun, upperLiftSlideHits]
  | cons op ops ih =>
      cases op <;> simp [upperLiftRun, upperLiftSlideHits, ih, Nat.add_assoc]

theorem upperAnchorAdvance_append (n : Nat) (ops rest : List UpperLiftOp)
    (anchor : UpperAnchorState n) :
    upperAnchorAdvance n (ops ++ rest) anchor =
      upperAnchorAdvance n rest (upperAnchorAdvance n ops anchor) := by
  cases anchor
  simp only [upperAnchorAdvance, UpperAnchorState.mk.injEq]
  rw [upperLiftRun_append, upperLiftSlideHits_append]
  simp [Nat.add_assoc]

theorem upperLiftProjection_cons (letter : Letter) (rest : List Letter) :
    upperLiftProjection (letter :: rest) =
      upperLiftProjection [letter] ++ upperLiftProjection rest := by
  cases letter with
  | p layer => cases layer <;> rfl
  | d layer => cases layer <;> rfl
  | v => rfl

theorem upperAnchorUpdate_eq_advance (n : Nat) (anchor : UpperAnchorState n)
    (letter : Letter) :
    upperAnchorUpdate n anchor letter =
      upperAnchorAdvance n (upperLiftProjection [letter]) anchor := by
  cases letter with
  | p layer => cases layer <;> rfl
  | d layer => cases layer <;> rfl
  | v => rfl

theorem upperDefectLift_nonnegative {n : Nat} {x : Int} (hx : 0 ≤ x) :
    0 ≤ upperDefectLift n x :=
  upperDefectLift_ge_birth (by simp) hx

private theorem upper_rotation_matches (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) {x : Int}
    (hl : (P a).1 = true) (hx : x % (n : Int) = ((P a).2.val : Int)) :
    (rotate n (by omega) P true a).1 = true ∧
      (x + 1) % (n : Int) = ((rotate n (by omega) P true a).2.val : Int) := by
  constructor
  · simp [RSR2.Parametric.rotate, hl]
  · simp only [RSR2.Parametric.rotate, hl, if_pos, next_val]
    rw [Int.add_emod, hx]
    have hnInt : (1 : Int) < (n : Int) := by exact_mod_cast hn
    have hnonneg : (0 : Int) ≤ 1 := by omega
    have hlt : (1 : Int) < (n : Int) := by exact_mod_cast hn
    rw [Int.emod_eq_of_lt hnonneg hlt]
    norm_cast

private theorem upper_defect_matches (n : Nat) (hn : 1 < n)
    (P : Placement n) (a : Fin n) {x : Int}
    (hl : (P a).1 = true) (hx : x % (n : Int) = ((P a).2.val : Int)) :
    (collapse n hn P true a).1 = true ∧
      upperDefectLift n x % (n : Int) = ((collapse n hn P true a).2.val : Int) := by
  have hport : P a = (true, site1 n hn) ↔ x % (n : Int) = 1 := by
    constructor
    · intro he
      have hs : (P a).2.val = 1 := by simp [he, site1] at hx ⊢
      rw [hx, hs]
      simp
    · intro he
      have hs : (P a).2.val = 1 := by
        have h := hx.symm.trans he
        exact_mod_cast h
      apply Prod.ext hl
      apply Fin.ext
      simpa [site1] using hs
  by_cases hhit : x % (n : Int) = 1
  · have he := hport.mpr hhit
    constructor
    · simp [collapse, he]
    · simp [upperDefectLift, hhit, collapse, he, Int.sub_emod, site0]
  · have he : P a ≠ (true, site1 n hn) := fun h => hhit (hport.mp h)
    constructor
    · simp [collapse, he, hl]
    · simp only [upperDefectLift, if_neg hhit]
      simp [collapse, he]
      exact hx

theorem upperAnchorUpdate_matches (n : Nat) (hn : 1 < n)
    {P Q : Placement n} {letter : Letter} {anchor : UpperAnchorState n}
    (hs : step n hn P letter = some Q) (h : UpperAnchorMatches n P anchor) :
    UpperAnchorMatches n Q (upperAnchorUpdate n anchor letter) := by
  cases letter with
  | p layer =>
      rw [step_p] at hs
      have hQ : rotate n (by omega) P layer = Q := Option.some.inj hs
      subst Q
      cases layer with
      | false =>
          intro a ha
          obtain ⟨hl, hx⟩ := h a ha
          simpa [upperAnchorUpdate, RSR2.Parametric.rotate, hl] using And.intro hl hx
      | true =>
          intro a ha
          obtain ⟨hl, hx⟩ := h a ha
          exact upper_rotation_matches n hn P a hl hx
  | d layer =>
      rw [step_d] at hs
      have hQ : collapse n hn P layer = Q := Option.some.inj hs
      subst Q
      cases layer with
      | false =>
          intro a ha
          obtain ⟨hl, hx⟩ := h a ha
          have heq : P a ≠ (false, site1 n hn) := by
            intro heq
            have := congrArg Prod.fst heq
            simp [hl] at this
          simpa [upperAnchorUpdate, collapse, heq, hl] using And.intro hl hx
      | true =>
          intro a ha
          obtain ⟨hl, hx⟩ := h a ha
          exact upper_defect_matches n hn P a hl hx
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
      intro a ha
      obtain ⟨hl, hx⟩ := h a ha
      have hne : P a ≠ (false, site0 n (by omega)) := by
        intro heq
        have := congrArg Prod.fst heq
        simp [hl] at this
      simpa [upperAnchorUpdate, liftPacket, hne] using And.intro hl hx

noncomputable def runWithUpperAnchor (n : Nat) (hn : 1 < n) : Placement n →
    UpperAnchorState n → List Letter → Option (Placement n × UpperAnchorState n)
  | P, anchor, [] => some (P, anchor)
  | P, anchor, letter :: rest =>
      (step n hn P letter).bind fun Q =>
        runWithUpperAnchor n hn Q (upperAnchorUpdate n anchor letter) rest

theorem runWithUpperAnchor_project (n : Nat) (hn : 1 < n) (P : Placement n)
    (anchor : UpperAnchorState n) (word : List Letter) :
    (runWithUpperAnchor n hn P anchor word).map Prod.fst = run n hn P word := by
  induction word generalizing P anchor with
  | nil => rfl
  | cons letter rest ih =>
      simp only [runWithUpperAnchor, run, Option.map_bind]
      congr 1
      funext Q
      exact ih Q (upperAnchorUpdate n anchor letter)

theorem runWithUpperAnchor_logged_exists (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (anchor anchor' : UpperAnchorState n) (word : List Letter)
    (hrun : runWithUpperAnchor n hn P anchor word = some (Q, anchor')) :
    ∃ events, runLogged n hn P word = some (Q, events) := by
  apply runLogged_exists_of_run n hn
  have hp := runWithUpperAnchor_project n hn P anchor word
  rw [hrun] at hp
  simpa using hp.symm

theorem runWithUpperAnchor_matches (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (anchor anchor' : UpperAnchorState n) (word : List Letter)
    (hstart : UpperAnchorMatches n P anchor)
    (hrun : runWithUpperAnchor n hn P anchor word = some (Q, anchor')) :
    UpperAnchorMatches n Q anchor' := by
  induction word generalizing P anchor with
  | nil =>
      simp only [runWithUpperAnchor, Option.some.injEq, Prod.mk.injEq] at hrun
      rcases hrun with ⟨rfl, rfl⟩
      exact hstart
  | cons letter rest ih =>
      simp only [runWithUpperAnchor] at hrun
      cases hs : step n hn P letter with
      | none => simp [hs] at hrun
      | some R =>
          simp only [hs, Option.bind_some] at hrun
          exact ih R (upperAnchorUpdate n anchor letter)
            (upperAnchorUpdate_matches n hn hs hstart) hrun

theorem runWithUpperAnchor_lift (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (anchor anchor' : UpperAnchorState n) (word : List Letter)
    (hrun : runWithUpperAnchor n hn P anchor word = some (Q, anchor')) :
    anchor' = upperAnchorAdvance n (upperLiftProjection word) anchor := by
  induction word generalizing P anchor with
  | nil =>
      simp only [runWithUpperAnchor, Option.some.injEq, Prod.mk.injEq] at hrun
      rcases hrun with ⟨rfl, rfl⟩
      rfl
  | cons letter rest ih =>
      simp only [runWithUpperAnchor] at hrun
      cases hs : step n hn P letter with
      | none => simp [hs] at hrun
      | some R =>
          simp only [hs, Option.bind_some] at hrun
          have htail := ih R (upperAnchorUpdate n anchor letter) hrun
          rw [htail, upperLiftProjection_cons, upperAnchorAdvance_append,
            upperAnchorUpdate_eq_advance]

/-- The explicit interface still needed to extract an upper-loading barrier
from a delayed-chain event log. Its fields separate actual execution facts
from the cyclic insertion certificate and the packed endpoint geometry. -/
structure UpperLoadingBarrierCertificate (n : Nat) (hn : 1 < n) where
  word : List Letter
  start : Placement n
  stop : Placement n
  anchorPacket : Finset (Fin n)
  lastPacket : Finset (Fin n)
  lastBirth : Int
  lastLift : Int
  anchorStart : UpperAnchorState n
  anchorStop : UpperAnchorState n
  anchorStartsAtZero : anchorStart.coord = 0
  anchorStartsWithoutSlides : anchorStart.slides = 0
  anchorNonempty : anchorPacket.Nonempty
  lastPacketNonempty : lastPacket.Nonempty
  anchorStartMatches : UpperAnchorMatches n start anchorStart
  anchorExecution : runWithUpperAnchor n hn start anchorStart word =
    some (stop, anchorStop)
  anchorStopMatches : UpperAnchorMatches n stop anchorStop
  lastPacketAtLift : ∀ a ∈ lastPacket,
    (stop a).1 = true ∧ lastLift % (n : Int) = ((stop a).2.val : Int)
  arrivals : UpperBirthChain n n lastBirth
  lastBirth_le_lastLift : lastBirth ≤ lastLift
  anchorStopPeriodic : ∃ q : Int, anchorStop.coord = (n : Int) * q
  packedCycle : lastLift = anchorStop.coord + ((n : Int) - 1)

theorem upperLiftRotations_projection (word : List Letter) :
    upperLiftRotations (upperLiftProjection word) = word.count (.p true) := by
  induction word with
  | nil => simp [upperLiftProjection, upperLiftRotations]
  | cons letter rest ih =>
      cases letter with
      | p layer =>
          cases layer <;> simp [upperLiftProjection, upperLiftRotations, ih]
      | d layer =>
          cases layer <;> simp [upperLiftProjection, upperLiftRotations, ih]
      | v => simp [upperLiftProjection, ih]

theorem upperAnchorAdvance_cost_identity (n : Nat) (ops : List UpperLiftOp)
    (anchor : UpperAnchorState n) :
    (upperAnchorAdvance n ops anchor).coord +
        ((upperAnchorAdvance n ops anchor).slides : Int) =
      anchor.coord + (anchor.slides : Int) +
        (upperLiftRotations ops : Int) := by
  have h := upperLiftRun_eq_start_add_rotations_sub_slideHits n ops anchor.coord
  simp only [upperAnchorAdvance, Nat.cast_add] at *
  omega

theorem runWithUpperAnchor_rotations_lower_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (anchor anchor' : UpperAnchorState n) (word : List Letter)
    (hstartCoord : anchor.coord = 0) (hstartSlides : anchor.slides = 0)
    (hrun : runWithUpperAnchor n hn P anchor word = some (Q, anchor'))
    (hfinal : (n : Int) * ((n : Int) - 1) ≤ anchor'.coord) :
    n * (n - 1) + anchor'.slides ≤ word.count (.p true) := by
  have hlift := runWithUpperAnchor_lift n hn P Q anchor anchor' word hrun
  have hcost := upperAnchorAdvance_cost_identity n (upperLiftProjection word) anchor
  rw [← hlift] at hcost
  rw [hstartCoord, hstartSlides, upperLiftRotations_projection] at hcost
  have hcast : ((n * (n - 1) : Nat) : Int) =
      (n : Int) * ((n : Int) - 1) := by
    have hn1 : 1 ≤ n := by omega
    simp [Nat.cast_sub hn1]
  have htotal :
      ((n * (n - 1) + anchor'.slides : Nat) : Int) ≤
        (anchor'.coord + (anchor'.slides : Int)) := by
    rw [Nat.cast_add, hcast]
    nlinarith [hfinal]
  rw [hcost] at htotal
  simp only [Int.zero_add] at htotal
  have hNat : n * (n - 1) + anchor'.slides ≤
      0 + word.count (.p true) := by exact_mod_cast htotal
  simpa using hNat

theorem UpperLoadingBarrierCertificate.rotations_lower_bound
    {n : Nat} {hn : 1 < n} (cert : UpperLoadingBarrierCertificate n hn) :
    n * (n - 1) + cert.anchorStop.slides ≤ cert.word.count (.p true) := by
  have hanchor := upperLoading_anchor_lower_bound (by omega : 2 ≤ n)
    cert.anchorStopPeriodic cert.arrivals cert.lastBirth_le_lastLift cert.packedCycle
  exact runWithUpperAnchor_rotations_lower_bound n hn cert.start cert.stop
    cert.anchorStart cert.anchorStop cert.word cert.anchorStartsAtZero
    cert.anchorStartsWithoutSlides cert.anchorExecution hanchor

theorem UpperLoadingBarrierCertificate.logged_execution_exists
    {n : Nat} {hn : 1 < n} (cert : UpperLoadingBarrierCertificate n hn) :
    ∃ events, runLogged n hn cert.start cert.word = some (cert.stop, events) :=
  runWithUpperAnchor_logged_exists n hn cert.start cert.stop cert.anchorStart
    cert.anchorStop cert.word cert.anchorExecution

end RSR2History
