import FusionLogCompression
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

namespace FusionLogAllR

/-! # The all-right target: first arithmetic interfaces

This module is deliberately separate from the frozen M1--M3 package.  It
records the two local ingredients used by the all-right optimality proof:
the interval rotation budget and the hole potential.  The interval ledger is
an explicit certificate for the geometric facts still to be connected to the
raw `Execution` semantics; the potential lemmas themselves are unconditional
list identities.
-/

open FusionLogCompression
open scoped BigOperators

def pMin (n : ℕ) : ℕ := n * (n - 1) - 1

def slideTarget (pre : List ℤ) (x y : ℤ) (tail : List ℤ) : List ℤ :=
  pre ++ (x - 1) :: (y + 1) :: tail

def slideSource (pre : List ℤ) (x y : ℤ) (tail : List ℤ) : List ℤ :=
  pre ++ x :: y :: tail

def holePotential : List ℤ → ℤ
  | [] => 0
  | x :: xs => (xs.length : ℤ) * x + holePotential xs

def carrierBackslideTarget (x : ℤ) (middle : List ℤ) (y : ℤ) : List ℤ :=
  (x + 1) :: middle ++ [y - 1]

def carrierBackslideSource (x : ℤ) (middle : List ℤ) (y : ℤ) : List ℤ :=
  x :: middle ++ [y]

def fusionTarget (g1 : ℤ) (tail : List ℤ) : List ℤ :=
  (g1 + 1) :: tail

def fusionSource (g1 : ℤ) (tail : List ℤ) : List ℤ :=
  0 :: g1 :: tail

theorem holePotential_append (xs ys : List ℤ) :
    holePotential (xs ++ ys) =
      holePotential xs + (ys.length : ℤ) * xs.sum + holePotential ys := by
  induction xs with
  | nil => simp [holePotential]
  | cons x xs ih =>
      simp only [List.cons_append, holePotential, List.sum_cons,
        List.length_append, Nat.cast_add]
      rw [ih]
      ring

theorem holePotential_slide (pre : List ℤ) (x y : ℤ) (tail : List ℤ) :
    holePotential (slideTarget pre x y tail) =
      holePotential (slideSource pre x y tail) - 1 := by
  simp only [slideTarget, slideSource]
  rw [holePotential_append, holePotential_append]
  simp [holePotential, List.length_cons]
  ring

theorem holePotential_backslide (x : ℤ) (middle : List ℤ) (y : ℤ) :
    holePotential (carrierBackslideTarget x middle y) =
      holePotential (carrierBackslideSource x middle y) + middle.length + 1 := by
  simp only [carrierBackslideTarget, carrierBackslideSource]
  rw [holePotential_append, holePotential_append]
  simp [holePotential, List.sum_cons, List.length_cons]
  ring

theorem holePotential_fusion (g1 : ℤ) (tail : List ℤ) :
    holePotential (fusionTarget g1 tail) =
      holePotential (fusionSource g1 tail) + tail.length := by
  simp [fusionTarget, fusionSource, holePotential]
  ring

def triangular (m : ℕ) : ℕ := m * (m - 1) / 2

def allRSlides (n : ℕ) : ℕ := (n - 1) * (n - 2) / 2

theorem triangular_sum (m : ℕ) :
    (∑ i ∈ Finset.range m, i) = triangular m := by
  simpa [triangular] using (Finset.sum_range_id m)

/-! A rotation certificate records the interval consequences of the all-R
geometry. `interRot` counts rotations on each of the `n-2` inter-fusion
intervals; `tailRot` counts rotations after the last fusion.
The lower bounds are the exact facts supplied by the port argument:
each inter-fusion interval makes a positive full turn, while the tail reaches
site `n-1`.
-/
structure RotationCertificate (n : ℕ) where
  interRot : Fin (n - 2) → ℕ
  interBack : Fin (n - 2) → ℕ
  tailRot : ℕ
  tailBack : ℕ
  interLower : ∀ i, n + interBack i ≤ interRot i
  tailLower : n - 1 + tailBack ≤ tailRot

def RotationCertificate.totalRot (c : RotationCertificate n) : ℕ :=
  (∑ i, c.interRot i) + c.tailRot

def RotationCertificate.totalBack (c : RotationCertificate n) : ℕ :=
  (∑ i, c.interBack i) + c.tailBack

theorem rotation_lower_bound (n : ℕ) (hn : 3 ≤ n) (c : RotationCertificate n) :
    pMin n + c.totalBack ≤ c.totalRot := by
  unfold pMin RotationCertificate.totalRot RotationCertificate.totalBack
  have hinter : ∀ i : Fin (n - 2),
      n + c.interBack i ≤ c.interRot i := c.interLower
  have hsum :
      (∑ i : Fin (n - 2), (n + c.interBack i)) ≤
        (∑ i : Fin (n - 2), c.interRot i) := by
    apply Finset.sum_le_sum
    intro i hi
    exact hinter i
  have htail := c.tailLower
  simp only [Finset.sum_add_distrib] at hsum
  have hconst : (∑ _i : Fin (n - 2), n) = (n - 2) * n := by
    simp [Nat.mul_comm]
  rw [hconst] at hsum
  have hpoly : n * (n - 1) - 1 = (n - 2) * n + (n - 1) := by
    have h₁ : n - 1 + 1 = n := Nat.sub_add_cancel (by omega)
    have h₂ : n - 2 + 2 = n := Nat.sub_add_cancel (by omega)
    have hp : n * (n - 1) = (n - 2) * n + n := by nlinarith
    omega
  omega

/-! The telescoping form of the hole-potential proof.  The certificate
contains the endpoint balance after summing the local slide, backslide and
fusion changes.  The theorem extracts the exact required number of external
slides; no execution claim is hidden in this arithmetic interface.
-/
def weightedBackslide {n : ℕ} (b : Fin (n - 1) → ℕ) : ℤ :=
  ∑ i : Fin (n - 1), (i.1 : ℤ) * b i

def fusionPotentialChange (n : ℕ) : ℤ :=
  - (n - 2 : ℤ) + (allRSlides n : ℤ)

structure PotentialCertificate (n : ℕ) where
  slides : ℕ
  backslide : Fin (n - 1) → ℕ
  initial : ℤ
  final : ℤ
  balance :
    final = initial - slides +
      weightedBackslide backslide + fusionPotentialChange n

theorem hole_potential_identity (n : ℕ) (c : PotentialCertificate n)
    (hinitial : c.initial = (n - 2 : ℤ))
    (hfinal : c.final = 0) :
    (c.slides : ℤ) = (allRSlides n : ℤ) + weightedBackslide c.backslide := by
  have hb := c.balance
  rw [hfinal, hinitial, fusionPotentialChange] at hb
  omega

end FusionLogAllR
