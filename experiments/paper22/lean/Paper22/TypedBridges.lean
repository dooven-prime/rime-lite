import Mathlib

/-!
# Exact integer bridge table

The matrices and bilinear determinant identities in Appendix A are checked
here over `Int`. The geometric interpretation of their correction lengths as
Farey flag edges remains a manuscript-level argument.
-/

namespace Rime.Paper22

structure Mat2 where
  a11 : Int
  a12 : Int
  a21 : Int
  a22 : Int
  deriving DecidableEq, Repr

def matMul (A B : Mat2) : Mat2 :=
  ⟨A.a11 * B.a11 + A.a12 * B.a21,
   A.a11 * B.a12 + A.a12 * B.a22,
   A.a21 * B.a11 + A.a22 * B.a21,
   A.a21 * B.a12 + A.a22 * B.a22⟩

def matDet (A : Mat2) : Int := A.a11 * A.a22 - A.a12 * A.a21

def matApply (A : Mat2) (v : Int × Int) : Int × Int :=
  (A.a11 * v.1 + A.a12 * v.2, A.a21 * v.1 + A.a22 * v.2)

def matInvSL2 (A : Mat2) : Mat2 := ⟨A.a22, -A.a12, -A.a21, A.a11⟩

def S : Mat2 := ⟨0, -1, 1, 0⟩
def N : Mat2 := ⟨-1, -1, 1, 0⟩
def M : Mat2 := ⟨0, -1, 1, 1⟩
def P : Mat2 := ⟨1, 0, 0, 1⟩
def L : Mat2 := ⟨1, 0, 1, 1⟩

def bridgeNM : Mat2 := ⟨1, 1, -1, 0⟩
def bridgeNP : Mat2 := ⟨0, 1, -1, -1⟩
def bridgeMP : Mat2 := ⟨1, 1, -1, 0⟩
def bridgeNL : Mat2 := ⟨1, 1, -2, -1⟩
def bridgeML : Mat2 := ⟨2, 1, -1, 0⟩
def bridgePL : Mat2 := ⟨1, 0, 1, 1⟩

def detPair (u v : Int × Int) : Int := u.1 * v.2 - u.2 * v.1

theorem bridge_matrices_correct :
    matMul (matInvSL2 N) M = bridgeNM ∧
    matMul (matInvSL2 N) P = bridgeNP ∧
    matMul (matInvSL2 M) P = bridgeMP ∧
    matMul (matInvSL2 N) L = bridgeNL ∧
    matMul (matInvSL2 M) L = bridgeML ∧
    matMul (matInvSL2 P) L = bridgePL := by
  decide

theorem bridge_determinants (a b c d : Int) :
    detPair (matApply N (a, b)) (matApply M (c, d)) = -a*c - b*c - b*d ∧
    detPair (matApply N (a, b)) (matApply P (c, d)) = -a*c - a*d - b*d ∧
    detPair (matApply M (a, b)) (matApply P (c, d)) = -a*c - b*c - b*d ∧
    detPair (matApply N (a, b)) (matApply L (c, d)) = -2*a*c - a*d - b*c - b*d ∧
    detPair (matApply M (a, b)) (matApply L (c, d)) = -a*c - 2*b*c - b*d ∧
    detPair (matApply P (a, b)) (matApply L (c, d)) = a*c + a*d - b*c := by
  have hNM : detPair (matApply N (a, b)) (matApply M (c, d)) =
      -a*c - b*c - b*d := by
    simp [detPair, matApply, N, M]
    ring_nf
  have hNP : detPair (matApply N (a, b)) (matApply P (c, d)) =
      -a*c - a*d - b*d := by
    simp [detPair, matApply, N, P]
    ring_nf
  have hMP : detPair (matApply M (a, b)) (matApply P (c, d)) =
      -a*c - b*c - b*d := by
    simp [detPair, matApply, M, P]
    ring_nf
  have hNL : detPair (matApply N (a, b)) (matApply L (c, d)) =
      -2*a*c - a*d - b*c - b*d := by
    simp [detPair, matApply, N, L]
    ring_nf
  have hML : detPair (matApply M (a, b)) (matApply L (c, d)) =
      -a*c - 2*b*c - b*d := by
    simp [detPair, matApply, M, L]
    ring_nf
  have hPL : detPair (matApply P (a, b)) (matApply L (c, d)) =
      a*c + a*d - b*c := by
    simp [detPair, matApply, P, L]
    ring_nf
  exact ⟨hNM, hNP, hMP, hNL, hML, hPL⟩

theorem typedBridgeTableCorrect :
    matDet S = 1 ∧ matDet N = 1 ∧ matDet M = 1 ∧
    matDet P = 1 ∧ matDet L = 1 ∧
    (∀ v, matApply P v = v) ∧
    matMul (matInvSL2 N) M = bridgeNM ∧
    matMul (matInvSL2 N) P = bridgeNP ∧
    matMul (matInvSL2 M) P = bridgeMP ∧
    matMul (matInvSL2 N) L = bridgeNL ∧
    matMul (matInvSL2 M) L = bridgeML ∧
    matMul (matInvSL2 P) L = bridgePL := by
  refine ⟨by decide, by decide, by decide, by decide, by decide, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · intro v
    cases v with
    | mk x y => simp [matApply, P]
  · exact bridge_matrices_correct.1
  · exact bridge_matrices_correct.2.1
  · exact bridge_matrices_correct.2.2.1
  · exact bridge_matrices_correct.2.2.2.1
  · exact bridge_matrices_correct.2.2.2.2.1
  · exact bridge_matrices_correct.2.2.2.2.2

end Rime.Paper22
