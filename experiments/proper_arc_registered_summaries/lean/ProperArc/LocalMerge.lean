import ProperArc.ArcGeometry

namespace ProperArc

open RegisteredAbsorptionChains

variable {n : ℕ} [NeZero n]

def localFusion (j : ZMod n) (P : Placement n (Finset (ZMod n))) :
    Placement n (Finset (ZMod n)) :=
  fun q => if q = j then
    match P j, P (j + 1) with
    | none, other => other
    | other, none => other
    | some U, some V => some (U ∪ V)
    else if q = j + 1 then none else P q

omit [NeZero n] in
theorem localFusion_eq_rotated (j : ZMod n) (P : Placement n (Finset (ZMod n))) :
    localFusion j P = rotate j (fusionPlacement (rotate (-j) P)) := by
  funext q
  have h0 : q - j = 0 ↔ q = j := sub_eq_zero
  have h1 : q - j = 1 ↔ q = j + 1 := by constructor <;> intro h <;> linear_combination h
  simp only [localFusion, rotate, fusionPlacement, h0, h1]
  simp only [sub_neg_eq_add, zero_add]
  rw [add_comm (1 : ZMod n) j]
  simp only [sub_add_cancel]
  split_ifs <;> cases P j <;> cases P (j + 1) <;> rfl

/-- A local macro may really fuse packets. It preserves the selected records
when the fusion creates neither the selected set nor an already registered
carrier. This is not a fusion-free claim. -/
theorem run_local_unregistered (F : Finset (ZMod n)) (s : Execution n (ZMod n))
    (j : ZMod n) (U V : Finset (ZMod n))
    (h0 : s.placed j = some U) (h1 : s.placed (j + 1) = some V)
    (horigin : s.origin = none) (hnot : U ∪ V ≠ F) :
    run F s (localLetters j) = { s with placed := localFusion j s.placed } := by
  have hrotate0 : (rotate (-j) s.placed) 0 = some U := by simpa [rotate] using h0
  have hrotate1 : (rotate (-j) s.placed) 1 = some V := by simpa [rotate, add_comm] using h1
  rw [localLetters, run_append, run_append]
  rw [run_rotation F s (-j)]
  change run F (stepDefect F { s with placed := rotate (-j) s.placed }) (pWord j.val) = _
  have hmid : stepDefect F { s with placed := rotate (-j) s.placed } =
      { s with placed := fusionPlacement (rotate (-j) s.placed) } := by
    simp [stepDefect, hrotate0, hrotate1, horigin, hnot]
  rw [hmid]
  rw [run_rotation]
  rw [← localFusion_eq_rotated]

end ProperArc
