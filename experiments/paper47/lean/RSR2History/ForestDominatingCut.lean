import RSR2History.ForestTerminalSource

/-! A common cyclic cut for two increasing named-root coordinate lists.
The minimum source-minus-target displacement gives nonnegative forward
coordinate differences after cutting both lists at the same named root.
This is a coordinate identity and does not emit a physical rotation. -/
namespace RSR2History
variable {n r : Nat} [NeZero n] [NeZero r]
/-- Positive forward offset from the same named root `q`, with the source
and target wrapping at the same root index. -/
def forestCutOffset (p : Fin r → Fin n) (q j : Fin r) : Nat :=
  (p (q+j)).val + (if (q+j).val < q.val then n else 0) - (p q).val
theorem forestCutOffset_lt (p : Fin r → Fin n) (hp : StrictMono p) (q j : Fin r) :
    forestCutOffset p q j < n := by
  unfold forestCutOffset
  split
  · have hh := hp (show q+j < q from by assumption)
    have ha := (p (q+j)).isLt
    have hb := (p q).isLt
    change (p (q+j)).val < (p q).val at hh
    omega
  · have hh := hp.monotone (show q ≤ q+j from by omega)
    have ha := (p (q+j)).isLt
    have hb := (p q).isLt
    change (p q).val ≤ (p (q+j)).val at hh
    omega
theorem forestCutOffset_zero (p : Fin r → Fin n) (hp : StrictMono p) (q : Fin r) :
    forestCutOffset p q 0 = 0 := by simp [forestCutOffset]
theorem forestCutOffset_strict (p : Fin r → Fin n) (hp : StrictMono p) (q : Fin r) :
    StrictMono (forestCutOffset p q) := by
  intro i j hij
  have hir := i.isLt
  have hjr := j.isLt
  have hqr := q.isLt
  have hij' : i.val < j.val := hij
  have vi : (q+i).val = (q.val+i.val)%r := rfl
  have vj : (q+j).val = (q.val+j.val)%r := rfl
  have hri : q.val+i.val < 2*r := by omega
  have hrj : q.val+j.val < 2*r := by omega
  have he_i : (q+i).val = if q.val+i.val < r then q.val+i.val else q.val+i.val-r := by
    rw [vi]
    split
    · exact Nat.mod_eq_of_lt (by assumption)
    · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
  have he_j : (q+j).val = if q.val+j.val < r then q.val+j.val else q.val+j.val-r := by
    rw [vj]
    split
    · exact Nat.mod_eq_of_lt (by assumption)
    · rw [Nat.mod_eq_sub_mod (by omega), Nat.mod_eq_of_lt (by omega)]
  unfold forestCutOffset
  split <;> split
  · have hh := hp (show q+i < q+j from by split at he_i <;> split at he_j <;> omega)
    change (p (q+i)).val < (p (q+j)).val at hh
    have hpi := (p (q+i)).isLt
    have hpj := (p (q+j)).isLt
    have hpq := (p q).isLt
    omega
  · split at he_i <;> split at he_j <;> omega
  · have hpi := (p (q+i)).isLt
    have hpj := (p (q+j)).isLt
    have hpq := (p q).isLt
    have hle := hp.monotone (show q ≤ q+i from by omega)
    change (p q).val ≤ (p (q+i)).val at hle
    have hlt := hp (show q+j < q from by assumption)
    change (p (q+j)).val < (p q).val at hlt
    omega
  · have hh := hp (show q+i < q+j from by split at he_i <;> split at he_j <;> omega)
    change (p (q+i)).val < (p (q+j)).val at hh
    have hpi := hp.monotone (show q ≤ q+i from by omega)
    have hpj := hp.monotone (show q ≤ q+j from by omega)
    change (p q).val ≤ (p (q+i)).val at hpi
    change (p q).val ≤ (p (q+j)).val at hpj
    omega
theorem forestCutOffset_sub_identity
    (x y : Fin r → Fin n) (hx : StrictMono x) (hy : StrictMono y)
    (q j : Fin r) :
    (forestCutOffset x q j : Int) - (forestCutOffset y q j : Int) =
      ((x (q+j)).val : Int) - (y (q+j)).val -
        ((x q).val : Int) + (y q).val := by
  unfold forestCutOffset
  split
  · have hxa := hx (show q+j < q from by assumption)
    have hya := hy (show q+j < q from by assumption)
    change (x (q+j)).val < (x q).val at hxa
    change (y (q+j)).val < (y q).val at hya
    have hxn := (x q).isLt
    have hyn := (y q).isLt
    rw [Nat.cast_sub (by omega : (x q).val ≤ (x (q+j)).val+n),
      Nat.cast_sub (by omega : (y q).val ≤ (y (q+j)).val+n)]
    push_cast
    ring
  · have hxa := hx.monotone (show q ≤ q+j from by omega)
    have hya := hy.monotone (show q ≤ q+j from by omega)
    change (x q).val ≤ (x (q+j)).val at hxa
    change (y q).val ≤ (y (q+j)).val at hya
    simp only [Nat.add_zero]
    rw [Nat.cast_sub hxa, Nat.cast_sub hya]
    ring

/-- One common cyclic cut suffices for all target forward offsets to be at
most the corresponding source forward offsets. No gap-wise ordering of the
original displayed coordinate lists is required. -/
theorem forest_dominating_cut
    (x y : Fin r → Fin n) (hx : StrictMono x) (hy : StrictMono y) :
    ∃ q : Fin r, ∀ j : Fin r, forestCutOffset y q j ≤ forestCutOffset x q j := by
  classical
  obtain ⟨q, _, hq⟩ := Finset.exists_min_image Finset.univ
    (fun a : Fin r => ((x a).val : Int) - (y a).val) (Finset.univ_nonempty)
  refine ⟨q, ?_⟩
  intro j
  have hh := hq (q+j) (Finset.mem_univ _)
  have he := forestCutOffset_sub_identity x y hx hy q j
  omega

theorem forestCutOffset_cast (p : Fin r → Fin n) (hp : StrictMono p) (q j : Fin r) :
    ((forestCutOffset p q j : Nat) : ZMod n) =
      ((p (q+j)).val : ZMod n) - ((p q).val : ZMod n) := by
  unfold forestCutOffset
  split
  · have hn := (p q).isLt
    rw [Nat.cast_sub (by omega : (p q).val ≤ (p (q+j)).val+n), Nat.cast_add]
    simp
  · have hh := hp.monotone (show q ≤ q+j from by omega)
    change (p q).val ≤ (p (q+j)).val at hh
    simp [Nat.cast_sub hh]
theorem forestCutOffset_lower (p : Fin r → Fin n) (hp : StrictMono p) (q j : Fin r) :
    j.val ≤ forestCutOffset p q j := by
  cases r with
  | zero => exact j.elim0
  | succ r =>
    induction j using Fin.induction with
    | zero => simp [forestCutOffset_zero p hp q]
    | succ i ih =>
      have hh := forestCutOffset_strict p hp q
        (show i.castSucc < i.succ from Fin.castSucc_lt_succ)
      simp only [Fin.val_succ]
      exact Nat.succ_le_of_lt (lt_of_le_of_lt ih hh)
theorem forestCutOffset_upper (p : Fin r → Fin n) (hp : StrictMono p) (q j : Fin r) :
    forestCutOffset p q j ≤ n-r+j.val := by
  let site : Fin r → Fin n := fun j => ⟨forestCutOffset p q j, forestCutOffset_lt p hp q j⟩
  have hs : StrictMono site := forestCutOffset_strict p hp q
  have hrn : r ≤ n := by simpa using Fintype.card_le_of_injective p hp.injective
  have hh : StrictMono (fun i : Fin r => (site i.rev).rev) := by
    intro i k hi
    exact Fin.rev_lt_rev.mpr (hs (Fin.rev_lt_rev.mpr hi))
  have lower : ∀ j : Fin r, j.val ≤ ((site j.rev).rev).val := by
    intro j
    cases r with
    | zero => exact j.elim0
    | succ r =>
      induction j using Fin.induction with
      | zero => simp
      | succ i ih =>
        have hf := hh (show i.castSucc < i.succ from Fin.castSucc_lt_succ)
        change ((site i.castSucc.rev).rev).val < ((site i.succ.rev).rev).val at hf
        simp only [Fin.val_succ]
        exact Nat.succ_le_of_lt (lt_of_le_of_lt ih hf)
  have hb := lower j.rev
  simp only [Fin.rev_rev, Fin.val_rev] at hb
  have hj := j.isLt
  have hpj := (site j).isLt
  dsimp [site] at hb hpj
  omega

end RSR2History
