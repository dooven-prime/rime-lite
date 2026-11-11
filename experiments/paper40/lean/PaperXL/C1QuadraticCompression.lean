import PaperXL.C1RunCorrespondence
import FusionLogInterpretation.ArbitraryInitialReplay

/-!
# Quadratic representative words for the C1-compatible Paper XL model

This module is the first composition layer between the M4-C representative
word theorem and Paper XL's complete circular state.  It only claims the
declared C1-compatible fragment (`n >= 3`, `2 <= m <= n`); registration
metadata and the R/G/T certificate transfer remain separate interfaces in
`C1QuadraticRGT`.
-/

namespace PaperXL

open RegisteredAbsorptionChains
open FusionLogCompression
open FusionLogInterpretation
open FusionLogReplay

variable {n m : Nat}

/-- Natural-number encoding of the `7/2 * n * (n - 1)` quadratic bound. -/
def c1QuadraticHistoryBudget (n : Nat) : Nat :=
  7 * n * (n - 1) / 2

def rawLetterOf : Letter → RawLetter
  | .p => .p
  | .d => .d

theorem rawLetterOf_c1LetterOf (a : RawLetter) :
    rawLetterOf (c1LetterOf a) = a := by
  cases a <;> rfl

theorem c1LetterOf_rawLetterOf (a : Letter) :
    c1LetterOf (rawLetterOf a) = a := by
  cases a <;> rfl

theorem map_rawLetterOf_c1LetterOf (w : List RawLetter) :
    (w.map c1LetterOf).map rawLetterOf = w := by
  induction w with
  | nil => rfl
  | cons a w ih => simp [rawLetterOf_c1LetterOf, ih]

theorem map_c1LetterOf_rawLetterOf (w : List Letter) :
    (w.map rawLetterOf).map c1LetterOf = w := by
  induction w with
  | nil => rfl
  | cons a w ih => simp [c1LetterOf_rawLetterOf, ih]

theorem c1Run_eq_rawRun [NeZero n]
    (E : CircularEnvironment n m) (w : List RawLetter) :
    c1Run E (CircularLogState.seedState E) w =
      RawSystem.run (CircularLogState.rawSystem E) w := by
  simp [c1Run, RawSystem.run, CircularLogState.rawSystem]

theorem c1SeedOccupied_nonempty [NeZero n]
    (E : CircularEnvironment n m) :
    (occupiedSites (c1PlacementOf E (CircularLogState.seedState E))).Nonempty := by
  classical
  have hm : 0 < m := lt_of_lt_of_le (by decide : 0 < 2) E.hm_lower
  let i : Fin m := ⟨0, hm⟩
  let q : ZMod n := (ZMod.finEquiv n) (E.seed i)
  refine ⟨q, ?_⟩
  simp only [occupiedSites, Finset.mem_filter, Finset.mem_univ, true_and]
  simp [c1PlacementOf, c1PacketAtZMod, c1PacketAt, q, i]
  exact ⟨i, rfl⟩

theorem c1SeedOccupied_card [NeZero n]
    (E : CircularEnvironment n m) :
    (occupiedSites (c1PlacementOf E (CircularLogState.seedState E))).card = m := by
  classical
  let sites : Finset (ZMod n) :=
    Finset.univ.image (fun i : Fin m => (ZMod.finEquiv n) (E.seed i))
  have hsites :
      occupiedSites (c1PlacementOf E (CircularLogState.seedState E)) = sites := by
    ext q
    simp only [occupiedSites, Finset.mem_filter, Finset.mem_univ, true_and]
    by_cases hp : (c1PacketAtZMod E (CircularLogState.seedState E) q).Nonempty
    · have hsome : c1PlacementOf E (CircularLogState.seedState E) q =
          some (c1PacketAtZMod E (CircularLogState.seedState E) q) := by
        simp [c1PlacementOf, hp]
      have hi : q ∈ sites := by
        obtain ⟨i, hi⟩ := hp
        have hsite : E.seed i = (ZMod.finEquiv n).symm q := by
          simpa [c1PacketAtZMod, CircularLogState.seedState] using hi
        apply Finset.mem_image.mpr
        refine ⟨i, Finset.mem_univ _, ?_⟩
        rw [hsite]
        simp
      simp [hsome, hi]
    · have hnone : c1PlacementOf E (CircularLogState.seedState E) q = none := by
        simp [c1PlacementOf, hp]
      constructor
      · intro hq
        exfalso
        exact hq hnone
      · intro hq
        exfalso
        obtain ⟨i, _, hi⟩ := Finset.mem_image.mp hq
        have hsite : E.seed i = (ZMod.finEquiv n).symm q := by
          apply (ZMod.finEquiv n).injective
          rw [hi]
          simp
        apply hp
        refine ⟨i, ?_⟩
        simpa [c1PacketAtZMod, CircularLogState.seedState] using hsite
  rw [hsites, Finset.card_image_of_injective _]
  · simp
  · intro i j hij
    apply E.seed_injective
    apply (ZMod.finEquiv n).injective
    exact hij

theorem c1OccupiedSites_card_le [NeZero n]
    (E : CircularEnvironment n m) (s : CircularLogState n m) :
    (occupiedSites (c1PlacementOf E s)).card ≤ m := by
  classical
  let imageSites : Finset (ZMod n) :=
    Finset.univ.image (fun i : Fin m => (ZMod.finEquiv n) (s.site i))
  have hsub : occupiedSites (c1PlacementOf E s) ⊆ imageSites := by
    intro q hq
    have hqn : c1PlacementOf E s q ≠ none := by
      simpa [occupiedSites] using hq
    have hp : (c1PacketAtZMod E s q).Nonempty := by
      by_contra hne
      have hnone : c1PlacementOf E s q = none := by
        simp [c1PlacementOf, hne]
      exact hqn hnone
    obtain ⟨i, hi⟩ := hp
    apply Finset.mem_image.mpr
    refine ⟨i, Finset.mem_univ _, ?_⟩
    have hsite : s.site i = (ZMod.finEquiv n).symm q := by
      simpa [c1PacketAtZMod] using hi
    rw [hsite]
    simp
  have hcard : imageSites.card ≤ m := by
    dsimp [imageSites]
    simpa using (Finset.card_image_le :
      (Finset.univ.image (fun i : Fin m => (ZMod.finEquiv n) (s.site i))).card ≤
        (Finset.univ : Finset (Fin m)).card)
  exact (Finset.card_le_card hsub).trans hcard

theorem normalFormBudget_le_quadratic [NeZero n]
    {t s : Nat} (hn : 3 ≤ n) (ht : t ≤ n) (hs : 1 ≤ s) (hst : s ≤ t) :
    2 * normalFormBudget n t s ≤ 7 * n * (n - 1) := by
  have hchoose : 2 * Nat.choose (t - s) 2 ≤
      (t - s) * (t - s - 1) := by
    rw [Nat.choose_two_right]
    exact Nat.mul_div_le _ _
  simp only [normalFormBudget]
  have hns : 1 ≤ n := by omega
  have hts : t - s + s = t := Nat.sub_add_cancel hst
  have hnt : n - t + t = n := Nat.sub_add_cancel ht
  have hn1 : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
  have hs1 : s - 1 + 1 = s := Nat.sub_add_cancel hs
  have h3ns : s ≤ 3 * n := by omega
  have h3nssub : 3 * n - s + s = 3 * n := Nat.sub_add_cancel h3ns
  by_cases hd : t - s = 0
  · simp [hd] at *
    nlinarith
  · have hdpos : 1 ≤ t - s := by omega
    have hd1 : t - s - 1 + 1 = t - s := Nat.sub_add_cancel hdpos
    nlinarith

theorem c1QuadraticCompression [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (hn : 3 ≤ n) (w : List RawLetter) :
    ∃ v : List RawLetter,
      RawSystem.run (CircularLogState.rawSystem E) v =
        RawSystem.run (CircularLogState.rawSystem E) w ∧
      v.length ≤ normalFormBudget n m
        (occupiedSites (c1PlacementOf E
          (RawSystem.run (CircularLogState.rawSystem E) w))).card := by
  let seed : CircularLogState n m := CircularLogState.seedState E
  let actual : LoggedExecution n (Fin m) := c1LoggedExecutionOf E seed
  obtain ⟨representative, hlog, hplace, hcost⟩ :=
    arbitrary_initial_log_endpoint_representative (F := (∅ : Finset (Fin m)))
      actual (w.map c1LetterOf) hn (c1SeedOccupied_nonempty E)
  let v : List RawLetter := representative.map rawLetterOf
  have hrunRep := c1RunCorrespondence_initial E h seed v
  have hrunWord := c1RunCorrespondence_initial E h seed w
  have hv : v.map c1LetterOf = representative := by
    simpa [v] using (map_c1LetterOf_rawLetterOf representative)
  refine ⟨v, ?_, ?_⟩
  · have hobs : c1Observation E (c1Run E seed v) =
        c1Observation E (c1Run E seed w) := by
      apply Prod.ext
      · change (c1Run E seed v).events.map codeFusionRecord =
          (c1Run E seed w).events.map codeFusionRecord
        have hrepLog :
            (runLogged ∅ actual (v.map c1LetterOf)).fullLog =
              (c1Run E seed v).events.map codeFusionRecord := by
          simpa [actual] using hrunRep.2
        have hlog' :
            (runLogged ∅ actual (v.map c1LetterOf)).fullLog =
              (runLogged ∅ actual (w.map c1LetterOf)).fullLog := by
          rw [hv]
          exact hlog
        exact hrepLog.symm.trans (hlog'.trans hrunWord.2)
      · change c1PlacementOf E (c1Run E seed v) =
          c1PlacementOf E (c1Run E seed w)
        have hrepPlace :
            (runLogged ∅ actual (v.map c1LetterOf)).state.placed =
              c1PlacementOf E (c1Run E seed v) := by
          simpa [actual] using hrunRep.1
        have hplace' :
            (runLogged ∅ actual (v.map c1LetterOf)).state.placed =
              (runLogged ∅ actual (w.map c1LetterOf)).state.placed := by
          rw [hv]
          exact hplace
        exact hrepPlace.symm.trans (hplace'.trans hrunWord.1)
    have hstate : c1Run E seed v = c1Run E seed w :=
      c1Observation_injective E hobs
    simpa [c1Run_eq_rawRun E, seed] using hstate
  · have hstart : (occupiedSites actual.state.placed).card = m := by
      change (occupiedSites (c1PlacementOf E (CircularLogState.seedState E))).card = m
      exact c1SeedOccupied_card E
    have hend : (occupiedSites (run ∅ actual.state (w.map c1LetterOf)).placed).card =
        (occupiedSites (c1PlacementOf E
          (RawSystem.run (CircularLogState.rawSystem E) w))).card := by
      have hrunWordState :
          (run ∅ actual.state (w.map c1LetterOf)).placed =
            c1PlacementOf E (c1Run E seed w) := by
        simpa only [runLogged_state] using hrunWord.1
      rw [hrunWordState, c1Run_eq_rawRun E w]
    simpa [v, hstart, hend] using hcost

theorem c1QuadraticCompression_global [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (hn : 3 ≤ n) (w : List RawLetter) :
    ∃ v : List RawLetter,
      RawSystem.run (CircularLogState.rawSystem E) v =
        RawSystem.run (CircularLogState.rawSystem E) w ∧
      2 * v.length ≤ 7 * n * (n - 1) := by
  obtain ⟨v, hrun, hcost⟩ := c1QuadraticCompression E h hn w
  let s := (occupiedSites (c1PlacementOf E
    (RawSystem.run (CircularLogState.rawSystem E) w))).card
  have hspos : 1 ≤ s := by
    have hm : 0 < m := lt_of_lt_of_le (by decide : 0 < 2) E.hm_lower
    have hi : (occupiedSites (c1PlacementOf E
        (RawSystem.run (CircularLogState.rawSystem E) w))).Nonempty := by
      refine ⟨(ZMod.finEquiv n)
        ((RawSystem.run (CircularLogState.rawSystem E) w).site ⟨0, hm⟩), ?_⟩
      simp only [occupiedSites, Finset.mem_filter, Finset.mem_univ, true_and]
      simp [c1PlacementOf, c1PacketAtZMod, c1PacketAt]
    have hcardpos : 0 <
        (occupiedSites (c1PlacementOf E
          (RawSystem.run (CircularLogState.rawSystem E) w))).card :=
      Finset.card_pos.mpr hi
    dsimp [s]
    exact hcardpos
  have hst : s ≤ m := by
    exact c1OccupiedSites_card_le E _
  have ht : m ≤ n := E.hm_le
  have hbudget : 2 * normalFormBudget n m s ≤ 7 * n * (n - 1) :=
    normalFormBudget_le_quadratic hn ht hspos hst
  refine ⟨v, hrun, ?_⟩
  exact (Nat.mul_le_mul_left 2 hcost).trans hbudget

theorem c1QuadraticCompression_budget [NeZero n]
    (E : CircularEnvironment n m) (h : C1Compatible E)
    (hn : 3 ≤ n) (w : List RawLetter) :
    ∃ v : List RawLetter,
      RawSystem.run (CircularLogState.rawSystem E) v =
        RawSystem.run (CircularLogState.rawSystem E) w ∧
      v.length ≤ c1QuadraticHistoryBudget n := by
  obtain ⟨v, hrun, hquad⟩ := c1QuadraticCompression_global E h hn w
  refine ⟨v, hrun, ?_⟩
  apply (Nat.le_div_iff_mul_le (by decide : 0 < 2)).2
  simpa [Nat.mul_comm] using hquad

end PaperXL
