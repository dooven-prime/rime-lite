import FusionLogAllR.RawAllRLowerBound

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! # First raw-word consequences of equality in the all-right budget

Equality forces the literal registration prefix to be `[d]` and makes each
actual right-fusion interval and the final tail attain its local rotation
bound. These statements do not order the remaining slide steps and do not
assert uniqueness of the complete raw word.
-/

private theorem word_eq_single_defect_of_counts (word : List Letter)
    (hp : word.count .p = 0) (hd : word.count .d = 1) : word = [.d] := by
  have hlength : word.length = 1 := by
    have h := count_p_add_count_d word
    omega
  cases word with
  | nil => simp at hlength
  | cons letter rest =>
      have hrest : rest = [] := List.length_eq_zero_iff.mp (by
        simp only [List.length_cons] at hlength
        omega)
      subst rest
      cases letter <;> simp_all

theorem AllRTraceExtraction.minimal_registrationPrefix
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.registrationPrefix = [.d] := by
  obtain ⟨_, hp, _, _⟩ := cert.minimal_length_budget hn hmin
  exact word_eq_single_defect_of_counts _ hp cert.prefixD

theorem RealizesAllR.minimal_starts_with_defect
    {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (3 * n * (n - 1)) / 2 - 1) :
    ∃ post, word = .d :: post := by
  obtain ⟨cert, hword⟩ := allRTraceExtraction_of_realizes hn h
  have hcert : cert.word.length = (3 * n * (n - 1)) / 2 - 1 := by
    simpa [hword] using hmin
  refine ⟨cert.interWord ++ cert.tail, ?_⟩
  rw [← hword, cert.word_eq, cert.minimal_registrationPrefix hn hcert]
  rfl

/-- When the sum of the interval rotation bounds is attained, the actual
decomposition supplies exactly `k` segments, each with `n` rotation letters.
Each segment is followed by its specified effective fusion letter. -/
theorem RightFusionIntervals.exact_rotation_segments
    {n : ℕ} [NeZero n] {F : Finset (ZMod n)} {a : ZMod n} {k : ℕ}
    {s t : Execution n (ZMod n)} {word : List Letter}
    (intervals : RightFusionIntervals F a k s t word)
    (hn : 2 ≤ n) (ordered : SourceOrdered s.placed)
    (hcount : word.count .p = k * n) :
    ∃ segments : List (List Letter),
      segments.length = k ∧
      word = segments.flatMap (fun segment => segment ++ [.d]) ∧
      ∀ segment ∈ segments, segment.count .p = n := by
  induction intervals with
  | nil s => exact ⟨[], rfl, rfl, by simp⟩
  | @cons k s u restWord segment hstart hhole hend hright rest ih =>
      have hmidOrder := run_ordered F s segment hn ordered
      have hnextOrder := step_ordered F (run F s segment) .d hn hmidOrder
      have hrestBound := rest.rotation_lower_bound hn hnextOrder
      obtain ⟨C, hC, haC⟩ : ∃ C, s.placed 0 = some C ∧ a ∈ C := by
        cases h0 : s.placed 0 with
        | none => simp [h0] at hstart
        | some C => exact ⟨C, rfl, by simpa [h0] using hstart⟩
      obtain ⟨D, hD, haD⟩ :
          ∃ D, (run F s segment).placed 0 = some D ∧ a ∈ D := by
        cases h0 : (run F s segment).placed 0 with
        | none => simp [h0] at hend
        | some D => exact ⟨D, rfl, by simpa [h0] using hend⟩
      have hsegmentBound := actual_interFusion_rotation_lower_bound
        F s segment a C D hn ordered hC haC hhole hD haD hright
      have htotal : segment.count .p + restWord.count .p = (k + 1) * n := by
        simpa using hcount
      have hsegment : segment.count .p = n := by
        rw [Nat.succ_mul] at htotal
        omega
      have hrest : restWord.count .p = k * n := by
        rw [Nat.succ_mul] at htotal
        omega
      obtain ⟨segments, hlength, hword, hall⟩ := ih hnextOrder hrest
      refine ⟨segment :: segments, by simp [hlength], ?_, ?_⟩
      · simp [hword]
      · simpa only [List.mem_cons, forall_eq_or_imp] using And.intro hsegment hall

theorem AllRTraceExtraction.minimal_interval_and_tail_rotations
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    cert.interWord.count .p = (n - 2) * n ∧ cert.tail.count .p = n - 1 := by
  obtain ⟨_, _, hp, _⟩ := cert.minimal_length_budget hn hmin
  have hi := cert.intervals.rotation_lower_bound (by omega) cert.ordered
  have hrun := cert.intervals.run_eq
  have htOrder : SourceOrdered cert.afterInter.placed :=
    hrun ▸ run_ordered cert.F cert.start cert.interWord (by omega) cert.ordered
  obtain ⟨C, hC, haC⟩ := cert.afterPacket
  obtain ⟨D, hD, haD⟩ := cert.tailEnd
  have ht := actual_tail_rotation_lower_bound cert.F cert.afterInter cert.tail
    cert.carrier C D (by omega) htOrder hC haC hD haD
  have h₁ : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
  have h₂ : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
  have hpoly : pMin n = (n - 2) * n + (n - 1) := by
    have heq : n * (n - 1) = (n - 2) * n + n := by nlinarith
    unfold pMin
    omega
  rw [hpoly, List.count_append] at hp
  constructor <;> omega

theorem AllRTraceExtraction.minimal_exact_rotation_segments
    {n : ℕ} [NeZero n] (cert : AllRTraceExtraction n) (hn : 3 ≤ n)
    (hmin : cert.word.length = (3 * n * (n - 1)) / 2 - 1) :
    ∃ segments : List (List Letter),
      segments.length = n - 2 ∧
      cert.interWord = segments.flatMap (fun segment => segment ++ [.d]) ∧
      (∀ segment ∈ segments, segment.count .p = n) ∧
      cert.tail.count .p = n - 1 := by
  obtain ⟨hi, ht⟩ := cert.minimal_interval_and_tail_rotations hn hmin
  obtain ⟨segments, hlength, hword, hall⟩ :=
    cert.intervals.exact_rotation_segments (by omega) cert.ordered hi
  exact ⟨segments, hlength, hword, hall, ht⟩

/-- A consequence at the raw target interface: no annotation is required
from the caller. This fixes interval rotation counts, not slide order. -/
theorem RealizesAllR.minimal_rotation_decomposition
    {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word)
    (hmin : word.length = (3 * n * (n - 1)) / 2 - 1) :
    ∃ (segments : List (List Letter)) (tail : List Letter),
      word = [.d] ++ segments.flatMap (fun segment => segment ++ [.d]) ++ tail ∧
      segments.length = n - 2 ∧
      (∀ segment ∈ segments, segment.count .p = n) ∧
      tail.count .p = n - 1 := by
  obtain ⟨cert, hword⟩ := allRTraceExtraction_of_realizes hn h
  have hcert : cert.word.length = (3 * n * (n - 1)) / 2 - 1 := by
    simpa [hword] using hmin
  obtain ⟨segments, hlength, hsegments, hall, htail⟩ :=
    cert.minimal_exact_rotation_segments hn hcert
  refine ⟨segments, cert.tail, ?_, hlength, hall, htail⟩
  rw [← hword, cert.word_eq, cert.minimal_registrationPrefix hn hcert, hsegments]


end FusionLogAllR
