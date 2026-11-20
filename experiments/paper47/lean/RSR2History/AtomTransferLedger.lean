import RSR2History.SingleBlockTwoTransfers

/-! Each source atom crosses layers at most once, on the original executor. -/

namespace RSR2History
open RSR2.Parametric
variable {n : Nat}

def atomTransferCount (a : Fin n) (H : List (EffectiveEvent n)) : Nat :=
  (H.map (fun | .fusion _ _ _ _ => 0 | .transfer B => if a ∈ B then 1 else 0)).sum

@[simp] theorem atomTransferCount_append (a : Fin n) (H K : List (EffectiveEvent n)) :
    atomTransferCount a (H++K) = atomTransferCount a H + atomTransferCount a K := by
  simp [atomTransferCount]

@[simp] theorem atomTransferCount_transfer_cons (a : Fin n) (B : Finset (Fin n))
    (H : List (EffectiveEvent n)) :
    atomTransferCount a (.transfer B :: H) = (if a ∈ B then 1 else 0) + atomTransferCount a H := rfl

@[simp] theorem atomTransferCount_fusion_cons (a : Fin n) (layer : Layer)
    (A B C : Finset (Fin n)) (H : List (EffectiveEvent n)) :
    atomTransferCount a (.fusion layer A B C :: H) = atomTransferCount a H := by
  simp [atomTransferCount]

theorem atomTransferCount_le (a : Fin n) (H : List (EffectiveEvent n)) :
    atomTransferCount a H ≤ logTransferCount H := by
  induction H with
  | nil => rfl
  | cons e H ih =>
      cases e with
      | fusion layer A B C => simpa [atomTransferCount, logTransferCount] using ih
      | transfer B =>
          by_cases hm : a ∈ B <;> simp [atomTransferCount, logTransferCount, hm] at * <;> omega

theorem step_atomTransfer_balance (hn : 1 < n) (P Q : Placement n)
    (letter : Letter) (a : Fin n) (hs : step n hn P letter = some Q) :
    (if (Q a).1 then 1 else 0) = (if (P a).1 then 1 else 0) +
      atomTransferCount a (emittedEvents n hn P letter) := by
  classical
  cases letter with
  | p layer =>
      have hQ : Q = rotate n (by omega) P layer := by simpa [step_p] using hs.symm
      rw [hQ]
      have hfst : (rotate n (by omega) P layer a).1 = (P a).1 := by
        by_cases h : (P a).1 = layer
        · simpa only [rotate, if_pos h] using h.symm
        · simp [rotate, h]
      simp [hfst, emittedEvents, atomTransferCount]
  | d layer =>
      have hQ : Q = collapse n hn P layer := by simpa [step_d] using hs.symm
      rw [hQ]
      have he : atomTransferCount a (emittedEvents n hn P (.d layer)) = 0 := by
        simp only [emittedEvents]
        split <;> simp [atomTransferCount]
      rw [he, Nat.add_zero]
      by_cases h : P a = (layer, site1 n hn)
      · simp [collapse, h]
      · simp [collapse, h]
  | v =>
      have hQ := ((step_v_eq_some_iff n hn P Q).mp hs).2
      rw [hQ]
      by_cases h : P a = (false, site0 n (by omega))
      · simp [liftPacket, emittedEvents, atomTransferCount, mem_packetAt, h]
      · simp [liftPacket, emittedEvents, atomTransferCount, mem_packetAt, h]

theorem runLogged_atomTransfer_balance (hn : 1 < n) (word : List Letter)
    {P Q : Placement n} {H : List (EffectiveEvent n)}
    (hr : runLogged n hn P word = some (Q, H)) (a : Fin n) :
    (if (Q a).1 then 1 else 0) = (if (P a).1 then 1 else 0) + atomTransferCount a H := by
  induction word generalizing P H with
  | nil =>
      have he : P = Q ∧ H = [] := by simpa [runLogged, eq_comm] using hr
      simp [he.1, he.2, atomTransferCount]
  | cons letter word ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hr
      | some R =>
          cases ht : runLogged n hn R word with
          | none => simp [runLogged, hs, ht] at hr
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = H := by
                simpa [runLogged, hs, ht] using hr
              have hb := step_atomTransfer_balance hn P R letter a hs
              have hi := ih (by simpa [he.1] using ht)
              rw [← he.2, atomTransferCount_append]
              omega

theorem singleton_fullUpper_atomTransferCount (hn : 1 < n) (word : List Letter)
    {Q : Placement n} {H : List (EffectiveEvent n)}
    (hr : runLogged n hn (seed n) word = some (Q, H))
    (hu : ∀ a, (Q a).1 = true) (a : Fin n) : atomTransferCount a H = 1 := by
  have hb := runLogged_atomTransfer_balance hn word hr a
  simpa [seed, hu a] using hb.symm

end RSR2History
