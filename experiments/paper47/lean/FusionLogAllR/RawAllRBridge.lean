import FusionLogAllR.PhysicalGapSimulation

namespace FusionLogAllR

open FusionLogCompression
open RegisteredAbsorptionChains

/-! # The raw all-right target and its directional consequence

The target is defined by its complete ordered fusion log and literal final
placement.  It contains no assumed interval decomposition, directional run
predicate, or gap certificate.  `completeFusionLog` is a chronological view
of the frozen `runLogged` semantics, with an explicit equivalence below.
-/

def completeFusionLog {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n)) :
    List Letter → List (FusionRecord (ZMod n))
  | [] => []
  | .p :: rest => completeFusionLog F (step F s .p) rest
  | .d :: rest =>
      match s.placed 0, s.placed 1 with
      | some A, some B =>
          ⟨A, B, A ∪ B⟩ :: completeFusionLog F (step F s .d) rest
      | _, _ => completeFusionLog F (step F s .d) rest

theorem runLogged_fullLog_eq_completeFusionLog {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : LoggedExecution n (ZMod n))
    (word : List Letter) :
    (runLogged F s word).fullLog =
      s.fullLog ++ completeFusionLog F s.state word := by
  induction word generalizing s with
  | nil => simp [runLogged, completeFusionLog]
  | cons letter rest ih =>
      change (runLogged F (loggedStep F s letter) rest).fullLog = _
      rw [ih, loggedStep_state]
      cases letter with
      | p => rfl
      | d =>
          cases h0 : s.state.placed 0 <;> cases h1 : s.state.placed 1 <;>
            simp [completeFusionLog, loggedStep, h0, h1, List.append_assoc]

theorem completeFusionLog_append {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (u v : List Letter) :
    completeFusionLog F s (u ++ v) =
      completeFusionLog F s u ++ completeFusionLog F (run F s u) v := by
  induction u generalizing s with
  | nil => rfl
  | cons letter rest ih =>
      cases letter with
      | p => simpa [completeFusionLog, run] using ih (step F s .p)
      | d =>
          cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
            simp [completeFusionLog, h0, h1, run, ih]

theorem rightCarrierRun_of_completeFusionLog_left {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n)
    (s : Execution n (ZMod n)) (word : List Letter)
    (hlog : ∀ rho ∈ completeFusionLog F s word, a ∈ rho.left) :
    RightCarrierRun F a s word := by
  induction word generalizing s with
  | nil => trivial
  | cons letter rest ih =>
      cases letter with
      | p => exact ih (step F s .p) hlog
      | d =>
          constructor
          · intro h0 h1
            cases hp0 : s.placed 0 with
            | none => exact (h0 hp0).elim
            | some A =>
                cases hp1 : s.placed 1 with
                | none => exact (h1 hp1).elim
                | some B =>
                    have h := hlog ⟨A, B, A ∪ B⟩ (by
                      simp [completeFusionLog, hp0, hp1])
                    simpa [hp0] using h
          · apply ih
            intro rho hrho
            apply hlog rho
            cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
              simp [completeFusionLog, h0, h1, hrho]

theorem rightCarrierRun_append {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n)
    (s : Execution n (ZMod n)) (u v : List Letter) :
    RightCarrierRun F a s (u ++ v) ↔
      RightCarrierRun F a s u ∧ RightCarrierRun F a (run F s u) v := by
  induction u generalizing s with
  | nil => simp [RightCarrierRun, run]
  | cons letter rest ih =>
      cases letter <;> simp [RightCarrierRun, run, ih, and_assoc]

theorem completeFusionLog_eq_nil_iff_fusionFree {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (word : List Letter) :
    completeFusionLog F s word = [] ↔ FusionFree F s word := by
  induction word generalizing s with
  | nil => simp [completeFusionLog, FusionFree]
  | cons letter rest ih =>
      cases letter with
      | p => exact ih (step F s .p)
      | d =>
          cases h0 : s.placed 0 <;> cases h1 : s.placed 1 <;>
            simp [completeFusionLog, FusionFree, h0, h1, ih]

/-- Locate the first actual effective defect in the raw word. The prefix
is fusion-free, and both ordered parents are read from its actual endpoint. -/
theorem completeFusionLog_first {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (word : List Letter) (rho : FusionRecord (ZMod n))
    (records : List (FusionRecord (ZMod n)))
    (hlog : completeFusionLog F s word = rho :: records) :
    ∃ pre post, word = pre ++ .d :: post ∧
      FusionFree F s pre ∧
      (run F s pre).placed 0 = some rho.left ∧
      (run F s pre).placed 1 = some rho.right ∧
      rho.result = rho.left ∪ rho.right ∧
      completeFusionLog F (step F (run F s pre) .d) post = records := by
  induction word generalizing s with
  | nil => simp [completeFusionLog] at hlog
  | cons letter rest ih =>
      cases letter with
      | p =>
          obtain ⟨pre, post, hw, hf, h0, h1, hu, hl⟩ := ih (step F s .p) hlog
          exact ⟨.p :: pre, post, by simp [hw], hf, h0, h1, hu, hl⟩
      | d =>
          cases h0 : s.placed 0 with
          | none =>
              have hl : completeFusionLog F (step F s .d) rest = rho :: records := by
                simpa [completeFusionLog, h0] using hlog
              obtain ⟨pre, post, hw, hf, hp0, hp1, hu, hl⟩ := ih (step F s .d) hl
              exact ⟨.d :: pre, post, by simp [hw], ⟨Or.inl h0, hf⟩,
                hp0, hp1, hu, hl⟩
          | some A =>
              cases h1 : s.placed 1 with
              | none =>
                  have hl : completeFusionLog F (step F s .d) rest = rho :: records := by
                    simpa [completeFusionLog, h0, h1] using hlog
                  obtain ⟨pre, post, hw, hf, hp0, hp1, hu, hl⟩ := ih (step F s .d) hl
                  exact ⟨.d :: pre, post, by simp [hw], ⟨Or.inr h1, hf⟩,
                    hp0, hp1, hu, hl⟩
              | some B =>
                  have hl : (⟨A, B, A ∪ B⟩ : FusionRecord (ZMod n)) ::
                      completeFusionLog F (step F s .d) rest = rho :: records := by
                    simpa [completeFusionLog, h0, h1] using hlog
                  obtain ⟨hrho, hrest⟩ := List.cons.inj hl
                  subst rho
                  exact ⟨[], rest, rfl, trivial, h0, h1, rfl, hrest⟩

/-- The log itself determines the actual inter-fusion decomposition. No
equality between independently chosen intermediate placements is assumed. -/
theorem rightFusionIntervals_of_completeFusionLog {n : ℕ} [NeZero n]
    (F : Finset (ZMod n)) (a : ZMod n) (hn : 2 ≤ n)
    (records : List (FusionRecord (ZMod n)))
    (s : Execution n (ZMod n)) (word : List Letter)
    (hstart : a ∈ (s.placed 0).getD ∅) (hhole : s.placed 1 = none)
    (hlog : completeFusionLog F s word = records)
    (hleft : ∀ rho ∈ records, a ∈ rho.left) :
    ∃ inter tail afterInter,
      word = inter ++ tail ∧
      RightFusionIntervals F a records.length s afterInter inter ∧
      a ∈ (afterInter.placed 0).getD ∅ ∧
      FusionFree F afterInter tail := by
  induction records generalizing s word with
  | nil =>
      exact ⟨[], word, s, rfl, .nil s, hstart,
        (completeFusionLog_eq_nil_iff_fusionFree F s word).mp hlog⟩
  | cons rho records ih =>
      obtain ⟨pre, post, hw, _, h0, h1, _, hpost⟩ :=
        completeFusionLog_first F s word rho records hlog
      have ha : a ∈ rho.left := hleft rho (by simp)
      have hnext : a ∈ ((step F (run F s pre) .d).placed 0).getD ∅ := by
        rw [show (step F (run F s pre) .d).placed =
          fusionPlacement (run F s pre).placed from stepDefect_placed F _]
        simpa [fusionPlacement, h0, h1] using Finset.mem_union_left rho.right ha
      obtain ⟨inter, tail, afterInter, hwpost, hintervals, hmarked, hfree⟩ :=
        ih (step F (run F s pre) .d) post hnext
          (defect_port_one_empty F _ hn) hpost
          (fun r hr => hleft r (by simp [hr]))
      refine ⟨pre ++ [.d] ++ inter, tail, afterInter, ?_, ?_, hmarked, hfree⟩
      · simp [hw, hwpost, List.append_assoc]
      · exact .cons pre hstart hhole (by simpa [h0] using ha)
          (by simp [h1]) hintervals

def rightFusionLog {n : ℕ} (C : Finset (ZMod n)) :
    List (ZMod n) → List (FusionRecord (ZMod n))
  | [] => []
  | a :: rest => ⟨C, {a}, C ∪ {a}⟩ :: rightFusionLog (C ∪ {a}) rest

theorem rightFusionLog_length {n : ℕ} (C : Finset (ZMod n))
    (partners : List (ZMod n)) :
    (rightFusionLog C partners).length = partners.length := by
  induction partners generalizing C with
  | nil => rfl
  | cons a rest ih => simp [rightFusionLog, ih]

theorem rightFusionLog_left_mem {n : ℕ} (C : Finset (ZMod n))
    (partners : List (ZMod n)) (a : ZMod n) (ha : a ∈ C) :
    ∀ rho ∈ rightFusionLog C partners, a ∈ rho.left := by
  induction partners generalizing C with
  | nil => simp [rightFusionLog]
  | cons b rest ih =>
      intro rho hrho
      rcases List.mem_cons.mp hrho with rfl | hrho
      · exact ha
      · exact ih (C ∪ {b}) (Finset.mem_union_left _ ha) rho hrho

def allRSelectedPair (n : ℕ) : Finset (ZMod n) := {0, 1}

def allRRegistration (n : ℕ) : FusionRecord (ZMod n) :=
  ⟨{0}, {1}, allRSelectedPair n⟩

def allRPartners (n : ℕ) : List (ZMod n) :=
  (List.range (n - 2)).map (fun i => ((i + 2 : ℕ) : ZMod n))

def allRPostLog (n : ℕ) : List (FusionRecord (ZMod n)) :=
  rightFusionLog (allRSelectedPair n) (allRPartners n)

def allRLog (n : ℕ) : List (FusionRecord (ZMod n)) :=
  allRRegistration n :: allRPostLog n

theorem allRPostLog_length (n : ℕ) : (allRPostLog n).length = n - 2 := by
  simp [allRPostLog, allRPartners, rightFusionLog_length]

theorem allRLog_left_mem (n : ℕ) :
    ∀ rho ∈ allRLog n, (0 : ZMod n) ∈ rho.left := by
  intro rho hrho
  rcases List.mem_cons.mp hrho with rfl | hrho
  · simp [allRRegistration]
  · exact rightFusionLog_left_mem (allRSelectedPair n) (allRPartners n) 0
      (by simp [allRSelectedPair]) rho hrho

def allREndpoint {n : ℕ} [NeZero n] : Placement n (Finset (ZMod n)) :=
  fun q => if q = ((n - 1 : ℕ) : ZMod n) then some Finset.univ else none

/-- The specified complete all-R log, including its registration event,
and the rank-one literal endpoint at site `n-1`.  No extraction facts are
part of the definition. -/
structure RealizesAllR {n : ℕ} [NeZero n] (word : List Letter) : Prop where
  log_eq : completeFusionLog (allRSelectedPair n) (singletonExecution n) word = allRLog n
  endpoint_eq : (run (allRSelectedPair n) (singletonExecution n) word).placed = allREndpoint

theorem RealizesAllR.rightCarrierRun {n : ℕ} [NeZero n]
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    RightCarrierRun (allRSelectedPair n) 0 (singletonExecution n) word := by
  apply rightCarrierRun_of_completeFusionLog_left
  simpa [h.log_eq] using allRLog_left_mem n

/-- For any actual registration prefix decomposition, directionality on
the post-registration suffix follows from the raw target log. -/
theorem RealizesAllR.post_rightCarrierRun {n : ℕ} [NeZero n]
    {word pre post : List Letter} (h : RealizesAllR (n := n) word)
    (hword : word = pre ++ post) :
    RightCarrierRun (allRSelectedPair n) 0
      (run (allRSelectedPair n) (singletonExecution n) pre) post := by
  have hr := h.rightCarrierRun
  rw [hword, rightCarrierRun_append] at hr
  exact hr.2

end FusionLogAllR
