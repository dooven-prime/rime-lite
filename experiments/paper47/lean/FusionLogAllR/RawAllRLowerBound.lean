import FusionLogAllR.RawAllRCertificate

namespace FusionLogAllR

open RegisteredAbsorptionChains

/-! # Raw-word lower bound for the specified all-right target

The hypothesis is exactly `RealizesAllR`: equality of the complete ordered
fusion log and of the literal endpoint. No execution annotation is supplied
by the caller; `allRTraceExtraction_of_realizes` constructs it from the word.
This lower bound does not itself assert an attaining word or uniqueness.
-/

theorem RealizesAllR.word_length_lower_bound
    {n : ℕ} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} (h : RealizesAllR (n := n) word) :
    (3 * n * (n - 1)) / 2 - 1 ≤ word.length := by
  obtain ⟨cert, hword⟩ := allRTraceExtraction_of_realizes hn h
  simpa [hword] using cert.word_length_lower_bound_closed hn

end FusionLogAllR
