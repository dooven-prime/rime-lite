import RSR2History.SingletonTransferCursorLift
import RSR2History.ReservedEventReplay

/-! A future-compatible event schedule carrying actual cursor costs, not budgets. -/
namespace RSR2History
open RSR2.Parametric

inductive SingletonUpperLog : List (EffectiveEvent n) → List (Fin n) → Prop
  | nil : SingletonUpperLog [] []
  | transfer (a : Fin n) {H z} (tail : SingletonUpperLog H z) :
      SingletonUpperLog (.transfer {a} :: H) (a :: z)
  | fusion (A B : Finset (Fin n)) {H z} (tail : SingletonUpperLog H z) :
      SingletonUpperLog (.fusion true A B (A ∪ B) :: H) z

inductive UpperCursorSchedule {n : Nat} (site : Nat → Fin n) :
    Nat → List (UpperFusionTree n) → Fin n → List (EffectiveEvent n) →
    Nat → List (UpperFusionTree n) → Fin n → Type where
  | nil {k xs ys cursor} (same : xs.IsRotated ys) :
      UpperCursorSchedule site k xs cursor [] k ys cursor
  | birth {k xs ys cursor H kfinal terminal finalCursor}
      (a : Fin n) (roots : List (UpperFusionTree n))
      (before : xs.IsRotated roots) (after : ys.IsRotated (.leaf k {a} :: roots))
      (tail : UpperCursorSchedule site (k+1) ys (site k) H kfinal terminal finalCursor) :
      UpperCursorSchedule site k xs cursor (.transfer {a} :: H) kfinal terminal finalCursor
  | fusion {k xs ys cursor H kfinal terminal finalCursor}
      (A B : UpperFusionTree n) (roots : List (UpperFusionTree n))
      (before : xs.IsRotated (A :: B :: roots))
      (after : ys.IsRotated (.merge A B :: roots))
      (anchor_gap : (site B.firstLeaf).val = (site A.firstLeaf).val + A.leaves.length)
      (tail : UpperCursorSchedule site k ys (site A.firstLeaf) H kfinal terminal finalCursor) :
      UpperCursorSchedule site k xs cursor
        (.fusion true A.packet B.packet (A.packet ∪ B.packet) :: H) kfinal terminal finalCursor

namespace UpperCursorSchedule
variable {n : Nat} {site : Nat → Fin n}
  {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
  {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}

def cost {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .birth (k := i) _ _ _ _ rest => cursorTurn n cursor.val (site i).val + 1 + rest.cost
  | .fusion A _ _ _ _ _ rest =>
      let f := A.leaves.length - 1
      cursorTurn n cursor.val ((site A.firstLeaf).val+f) + 2*f+1 + rest.cost

def debt {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .birth _ _ _ _ rest => rest.debt
  | .fusion A _ _ _ _ _ rest => (A.leaves.length - 1) + rest.debt

def windings {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .birth (k := i) _ _ _ _ rest => cursorWinding cursor.val (site i).val + rest.windings
  | .fusion A _ _ _ _ _ rest =>
      cursorWinding cursor.val ((site A.firstLeaf).val+(A.leaves.length-1)) + rest.windings

def birthZeros {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .birth (k := i) _ _ _ _ rest =>
      (if cursorWinding cursor.val (site i).val = 0 then 1 else 0) + rest.birthZeros
  | .fusion _ _ _ _ _ _ rest => rest.birthZeros

def fusionZeros {k kfinal : Nat} {xs terminal : List (UpperFusionTree n)}
    {cursor finalCursor : Fin n} {H : List (EffectiveEvent n)}
    (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) : Nat :=
  match s with
  | .nil _ => 0
  | .birth _ _ _ _ rest => rest.fusionZeros
  | .fusion A _ _ _ _ _ rest =>
      (if cursorWinding cursor.val ((site A.firstLeaf).val+(A.leaves.length-1)) = 0
        then 1 else 0) + rest.fusionZeros

theorem toPath (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    UpperForestPath k xs H kfinal terminal := by
  induction s with
  | nil same => exact .nil same
  | birth a roots before after rest ih => exact .cons (.transfer {a} roots before after) ih
  | fusion A B roots before after gap rest ih => exact .cons (.fusion A B roots before after) ih

theorem payment (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    s.cost + finalCursor.val = H.length + s.debt + n*s.windings + cursor.val := by
  induction s with
  | nil same => simp [cost, debt, windings]
  | @birth i xs ys c H kf terminal cf a roots before after rest ih =>
      have hp := transfer_cursor_payment c.isLt (site i).isLt
      simp only [cost, debt, windings, List.length_cons, Nat.mul_add]
      omega
  | @fusion i xs ys c H kf terminal cf A B roots before after gap rest ih =>
      have hsize := A.leaves_length_pos
      have hbound : (site A.firstLeaf).val + (A.leaves.length-1) < n := by
        have hb := (site B.firstLeaf).isLt
        omega
      have hp := fusion_cursor_payment c.isLt hbound
      simp only [cost, debt, windings, List.length_cons, Nat.mul_add]
      omega

theorem winding_partition (s : UpperCursorSchedule site k xs cursor H kfinal terminal finalCursor) :
    s.windings + s.birthZeros + s.fusionZeros = H.length := by
  induction s with
  | nil same => simp [windings, birthZeros, fusionZeros]
  | @birth i xs ys c H kf terminal cf a roots before after rest ih =>
      by_cases he : c.val < (site i).val <;>
        simp [windings, birthZeros, fusionZeros, cursorWinding, he] <;> omega
  | @fusion i xs ys c H kf terminal cf A B roots before after gap rest ih =>
      by_cases he : c.val < (site A.firstLeaf).val+(A.leaves.length-1) <;>
        simp [windings, birthZeros, fusionZeros, cursorWinding, he] <;> omega

end UpperCursorSchedule

end RSR2History
