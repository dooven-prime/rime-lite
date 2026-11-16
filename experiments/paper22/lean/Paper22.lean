import Paper22.Arithmetic
import Paper22.TypedBridges

/-!
# Paper XXII: arithmetic and typed-bridge Lean companion

This entry point covers the all-parameter continuant/Fibonacci inequality and
the finite integer-matrix identities in manuscript Appendix A. It does not
formalize the Farey-geometric classification or its registry decompositions.
-/

namespace Rime.Paper22

theorem continuant_fibonacci_envelope :
    ∀ runs : List Nat, (∀ q ∈ runs, 0 < q) →
      continuant runs ≤ Nat.fib (runs.sum + 1) :=
  continuant_le_fib

end Rime.Paper22
