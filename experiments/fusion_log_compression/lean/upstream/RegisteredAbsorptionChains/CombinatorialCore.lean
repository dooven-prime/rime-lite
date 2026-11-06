import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Nat.Choose.Basic

namespace RegisteredAbsorptionChains

-- `none`, `some false`, and `some true` encode 0, L, and R.
abbrev Side := Bool
abbrev Symbol := Option Side

abbrev Code (m : ℕ) := Fin m → Symbol

theorem card_code (m : ℕ) : Fintype.card (Code m) = 3 ^ m := by
  simp [Code, Symbol, Side]

/-- A checkpoint set with a canonical default away from its port choices. -/
structure ChainSkeleton (m : ℕ) where
  checkpoints : Finset (Fin m)
  side : Fin m → Side
  outside_default : ∀ i, i ∉ checkpoints → side i = false

private theorem ChainSkeleton.ext {m : ℕ} {a b : ChainSkeleton m}
    (hc : a.checkpoints = b.checkpoints) (hs : a.side = b.side) : a = b := by
  cases a with
  | mk ac as_ ah =>
    cases b with
    | mk bc bs bh =>
      dsimp at hc hs
      cases hc
      cases hs
      rfl

def support {m : ℕ} (c : Code m) : Finset (Fin m) :=
  Finset.univ.filter (fun i => c i ≠ none)

def decode {m : ℕ} (c : Code m) : ChainSkeleton m where
  checkpoints := support c
  side := fun i => (c i).getD false
  outside_default := by
    intro i hi
    have hc : c i = none := by
      by_contra hn
      exact hi (by simp [support, hn])
    simp [hc]

def encode {m : ℕ} (a : ChainSkeleton m) : Code m :=
  fun i => if i ∈ a.checkpoints then some (a.side i) else none

theorem encode_decode {m : ℕ} (c : Code m) : encode (decode c) = c := by
  funext i
  cases h : c i with
  | none => simp [encode, decode, support, h]
  | some b => simp [encode, decode, support, h]

theorem decode_encode {m : ℕ} (a : ChainSkeleton m) : decode (encode a) = a := by
  apply ChainSkeleton.ext
  · ext i
    simp [decode, support, encode]
  · funext i
    by_cases hi : i ∈ a.checkpoints
    · simp [decode, encode, hi]
    · simp [decode, encode, hi, a.outside_default i hi]

def chainEquiv (m : ℕ) : Code m ≃ ChainSkeleton m where
  toFun := decode
  invFun := encode
  left_inv := encode_decode
  right_inv := decode_encode

noncomputable instance (m : ℕ) : Fintype (ChainSkeleton m) :=
  Fintype.ofEquiv (Code m) (chainEquiv m)

theorem card_chainSkeleton (m : ℕ) : Fintype.card (ChainSkeleton m) = 3 ^ m := by
  rw [← Fintype.card_congr (chainEquiv m)]
  exact card_code m

end RegisteredAbsorptionChains
