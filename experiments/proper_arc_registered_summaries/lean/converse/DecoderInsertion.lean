import chains.ActualChains
import RegisteredAbsorptionChains.ActualChainRange

namespace ProperArc.Chains

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

theorem advance_congr {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v w : Code (n-r))
    (i : Fin (n-r)) (x : Prefix (n := n) r i.val) (h : v i = w i) :
    x.advance hr v i = x.advance hr w i := by
  unfold Prefix.advance
  rw [h]

theorem advance_none {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (i : Fin (n-r)) (x : Prefix (n := n) r i.val) (h : v i = none) :
    (x.advance hr v i).frontier = x.frontier ∧ (x.advance hr v i).chain = x.chain := by
  unfold Prefix.advance
  rw [h]
  exact ⟨rfl, rfl⟩

theorem decodePrefix_congr {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v w : Code (n-r)) :
    ∀ j (hj : j ≤ n-r), (∀ i : Fin (n-r), i.val < j → v i = w i) →
      decodePrefix hr v j hj = decodePrefix hr w j hj := by
  intro j
  induction j with
  | zero => intro _ _; rfl
  | succ j ih =>
      intro hj heq
      have hj' : j ≤ n-r := by omega
      have hp := ih hj' (by intro i hi; exact heq i (by omega))
      let i : Fin (n-r) := ⟨j, by omega⟩
      change (decodePrefix hr v j hj').advance hr v i =
        (decodePrefix hr w j hj').advance hr w i
      rw [hp]
      exact advance_congr hr v w i _ (heq i (by simp [i]))

theorem decodePrefix_skip {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (j : ℕ) (hj : j ≤ n-r) :
    ∀ k (hk : k ≤ n-r), j ≤ k →
      (∀ i : Fin (n-r), j ≤ i.val → i.val < k → v i = none) →
      (decodePrefix hr v k hk).frontier = (decodePrefix hr v j hj).frontier ∧
      (decodePrefix hr v k hk).chain = (decodePrefix hr v j hj).chain := by
  intro k
  induction k with
  | zero =>
      intro hk hjk _
      have : j = 0 := by omega
      subst j
      exact ⟨rfl, rfl⟩
  | succ k ih =>
      intro hk hjk hz
      by_cases hbelow : j ≤ k
      · have hk' : k ≤ n-r := by omega
        obtain ⟨hf, hc⟩ := ih hk' hbelow (by intro i hji hik; exact hz i hji (by omega))
        let i : Fin (n-r) := ⟨k, by omega⟩
        have hzi : v i = none := hz i hbelow (by simp [i])
        change ((decodePrefix hr v k hk').advance hr v i).frontier = _ ∧
          ((decodePrefix hr v k hk').advance hr v i).chain = _
        obtain ⟨hsf, hsc⟩ := advance_none hr v i _ hzi
        exact ⟨hsf.trans hf, hsc.trans hc⟩
      · have : j = k+1 := by omega
        subst j
        exact ⟨rfl, rfl⟩

def insertCheckpoint {m : ℕ} (v : Code m) (b : ℕ) (side : Bool) : Code m :=
  fun i => if i.val+1=b then some side else v i

theorem decodePrefix_insert {r : ℕ} (hr : 2 ≤ r ∧ r ≤ n) (v : Code (n-r))
    (j b : ℕ) (hj : j ≤ n-r) (hb : b ≤ n-r) (hjb : j < b) (side : Bool)
    (hsuffix : ∀ i : Fin (n-r), j ≤ i.val → v i = none)
    (habs : (decodePrefix hr v j hj).frontier.absorbed = r-2+j) :
    let v' := insertCheckpoint v b side
    let old := decodePrefix hr v j hj
    let fresh := decodePrefix hr v' b hb
    (∀ i : Fin (n-r), b ≤ i.val → v' i = none) ∧
    fresh.chain = old.chain ++ [checkpointRecord side old.frontier.carrier
      (if side then old.frontier.partnerR (b-j) else old.frontier.partnerL (b-j))] ∧
    fresh.frontier.carrier = old.frontier.carrier ∪
      (if side then old.frontier.partnerR (b-j) else old.frontier.partnerL (b-j)) ∧
    fresh.frontier.absorbed = r-2+b := by
  let v' := insertCheckpoint v b side
  let old := decodePrefix hr v j hj
  let fresh := decodePrefix hr v' b hb
  have hbpos : 1 ≤ b := by omega
  have hbefore : ∀ i : Fin (n-r), i.val < b-1 → v' i = v i := by
    intro i hi
    simp [v', insertCheckpoint, show i.val+1 ≠ b by omega]
  have hcongr : decodePrefix hr v' (b-1) (by omega) =
      decodePrefix hr v (b-1) (by omega) :=
    decodePrefix_congr hr v' v (b-1) (by omega) hbefore
  have hskip := decodePrefix_skip hr v j hj (b-1) (by omega) (by omega)
    (by intro i hji _; exact hsuffix i hji)
  have hat : v' ⟨b-1, by omega⟩ = some side := by
    simp [v', insertCheckpoint, Nat.sub_add_cancel hbpos]
  have hafter : ∀ i : Fin (n-r), b ≤ i.val → v' i = none := by
    intro i hbi
    simp [v', insertCheckpoint, show i.val+1 ≠ b by omega, hsuffix i (by omega)]
  have hfc : fresh.chain =
      ((decodePrefix hr v' (b-1) (by omega)).advance hr v' ⟨b-1, by omega⟩).chain := by
    cases b with | zero => omega | succ k => rfl
  have hff : fresh.frontier =
      ((decodePrefix hr v' (b-1) (by omega)).advance hr v' ⟨b-1, by omega⟩).frontier := by
    cases b with | zero => omega | succ k => rfl
  have hbound : b-j ≤ old.frontier.hi-old.frontier.lo := by
    have htotal := old.frontier.remaining_plus_absorbed
    rw [old.frontier.remaining_card, habs] at htotal
    omega
  have hlen : r-2+(b-1)+1-(decodePrefix hr v j hj).frontier.absorbed = b-j := by
    rw [habs]
    omega
  have hchain : fresh.chain = old.chain ++ [checkpointRecord side old.frontier.carrier
      (if side then old.frontier.partnerR (b-j) else old.frontier.partnerL (b-j))] := by
    rw [hfc, hcongr]
    cases side <;> simp [Prefix.advance, hat, hskip.1, hskip.2, hlen, old]
  have hcarrier : fresh.frontier.carrier = old.frontier.carrier ∪
      (if side then old.frontier.partnerR (b-j) else old.frontier.partnerL (b-j)) := by
    rw [hff, hcongr]
    cases side with
    | false =>
        simp only [Prefix.advance, hat, hskip.1, hlen]
        exact old.frontier.carrier_nextL (b-j) hbound
    | true =>
        simp only [Prefix.advance, hat, hskip.1, hlen]
        exact old.frontier.carrier_nextR (b-j) hbound
  have hsize : fresh.frontier.absorbed = r-2+b := by
    rw [hff, hcongr]
    cases side with
    | false =>
        simp only [Prefix.advance, hat, hskip.1, hlen]
        rw [old.frontier.absorbed_nextL, habs]
        omega
    | true =>
        simp only [Prefix.advance, hat, hskip.1, hlen]
        rw [old.frontier.absorbed_nextR, habs]
        omega
  exact ⟨hafter, hchain, hcarrier, hsize⟩

end ProperArc.Chains
