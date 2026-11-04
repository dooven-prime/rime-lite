import ProperArc.OriginBoundary
import RegisteredAbsorptionChains.CodeChainUniqueness

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

/-- The source frame starts at zero; source translation is supplied separately.
The inherited frontier counts from two, so its index is shifted by `r-2`. -/
structure Prefix (r j : ℕ) where
  frontier : CheckpointSourceFrontier n
  chain : List (FusionRecord (ZMod n))
  initial_inside : r ≤ frontier.lo
  bound : frontier.absorbed ≤ r - 2 + j

def Prefix.initial (r : ℕ) (hr : 2 ≤ r ∧ r ≤ n) : Prefix (n := n) r 0 where
  frontier := ⟨r, n, hr.1, hr.2, le_rfl⟩
  chain := []
  initial_inside := le_rfl
  bound := by simp [CheckpointSourceFrontier.absorbed]

theorem Prefix.initial_carrier (r : ℕ) (hr : 2 ≤ r ∧ r ≤ n) :
    (Prefix.initial r hr).frontier.carrier = arc (0 : ZMod n) r := by
  ext a
  rw [CheckpointSourceFrontier.mem_carrier_iff, arc,
    mem_interval_iff 0 a 0 r hr.2]
  simp only [Prefix.initial, sub_zero, Nat.zero_le, true_and]
  have := a.val_lt
  omega

theorem Prefix.inside (r j : ℕ) (hr : r ≤ n) (x : Prefix (n := n) r j) :
    arc (0 : ZMod n) r ⊆ x.frontier.carrier := by
  intro a ha
  have ha' := (mem_interval_iff 0 a 0 r hr).mp ha
  rw [CheckpointSourceFrontier.mem_carrier_iff]
  simp only [sub_zero] at ha'
  exact Or.inl (lt_of_lt_of_le ha'.2 x.initial_inside)

def Prefix.advance {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (i : Fin (n-r)) (x : Prefix (n := n) r i.val) : Prefix (n := n) r (i.val+1) := by
  match v i with
  | none => exact ⟨x.frontier, x.chain, x.initial_inside, by have := x.bound; omega⟩
  | some side =>
      let f := x.frontier
      let b := r-2+i.val+1
      have hnxt : f.absorbed < b := by have := x.bound; dsimp [f, b]; omega
      have hmax : b ≤ n-2 := by have := i.isLt; dsimp [b]; omega
      let ell := b-f.absorbed
      let gap := (f.checkpoint_gap b hnxt hmax).2
      cases side with
      | false =>
          exact ⟨f.nextL ell gap,
            x.chain ++ [checkpointRecord false f.carrier (f.partnerL ell)],
            x.initial_inside, by
              simpa [f, ell, gap, b, Nat.add_assoc] using (f.nextL_checkpoint b hnxt hmax).le⟩
      | true =>
          refine ⟨f.nextR ell gap,
            x.chain ++ [checkpointRecord true f.carrier (f.partnerR ell)], ?_, ?_⟩
          · have := x.initial_inside
            change r ≤ f.lo + ell
            dsimp [f] at *
            omega
          · simpa [f, ell, gap, b, Nat.add_assoc] using (f.nextR_checkpoint b hnxt hmax).le

/-- Position `i` denotes the cumulative number `i+1` of atoms absorbed after
the proper arc was registered, not the number of selected events. -/
def decodePrefix {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    (j : ℕ) → j ≤ n-r → Prefix (n := n) r j
  | 0, _ => Prefix.initial r hr
  | j+1, _ => (decodePrefix hr v j (by omega)).advance hr v ⟨j, by omega⟩

def decodeCanonical {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :=
  decodePrefix hr v (n-r) le_rfl

def decodeCanonicalChain {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :=
  (decodeCanonical hr v).chain

def lastCheckpoint {m : ℕ} (v : Code m) : (j : ℕ) → j ≤ m → ℕ
  | 0, _ => 0
  | j+1, _ => match v ⟨j, by omega⟩ with
      | none => lastCheckpoint v j (by omega)
      | some _ => j+1

theorem decodePrefix_absorbed {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r)) :
    ∀ j (hj : j ≤ n-r),
      (decodePrefix hr v j hj).frontier.absorbed = r-2+lastCheckpoint v j hj := by
  intro j
  induction j with
  | zero => intro hj; simp [decodePrefix, Prefix.initial,
      CheckpointSourceFrontier.absorbed, lastCheckpoint]
  | succ j ih =>
      intro hj
      let i : Fin (n-r) := ⟨j, by omega⟩
      let f := (decodePrefix hr v j (by omega)).frontier
      have hnext : f.absorbed < r-2+j+1 := by
        have := (decodePrefix hr v j (by omega)).bound
        dsimp [f]; omega
      have hmax : r-2+j+1 ≤ n-2 := by omega
      cases hs : v i with
      | none => simpa [decodePrefix, Prefix.advance, lastCheckpoint, i, hs] using ih (by omega)
      | some side =>
          cases side with
          | false =>
              simpa [decodePrefix, Prefix.advance, lastCheckpoint, i, hs, f, Nat.add_assoc] using
                f.nextL_checkpoint _ hnext hmax
          | true =>
              simpa [decodePrefix, Prefix.advance, lastCheckpoint, i, hs, f, Nat.add_assoc] using
                f.nextR_checkpoint _ hnext hmax

end ProperArc.Chains
