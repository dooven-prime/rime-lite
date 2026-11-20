import RSR2History.UpperReservedReplay

/-!
An exact physical slide with its ending phase retained as a cursor.  The
packet identity and every other normalized site are preserved literally.
-/
namespace RSR2History
open RSR2.Parametric
variable {n : Nat} [NeZero n]

private theorem map_singleRing_pWord_slide (layer : Layer) (k : Nat) :
    (RegisteredAbsorptionChains.pWord k).map (layerLetter layer) = pWord layer k := by
  induction k with
  | zero => rfl
  | succ k ih =>
    simp only [RegisteredAbsorptionChains.pWord,
      List.map_append, List.map_cons, List.map_nil, layerLetter]
    rw [ih]
    simpa [pWord] using (List.replicate_succ' (n := k) (a := Letter.p layer)).symm

private theorem runLogged_unphase_slide_suffix (hn : 1 < n) (P Q : Placement n)
    (word : List Letter) (layer : Layer) (amount : ZMod n)
    (hrun : runLogged n hn P (word ++ pWord layer amount.val) = some (Q, [])) :
    runLogged n hn P word = some (phaseShift Q layer (-amount), []) := by
  rw [runLogged_append] at hrun
  cases hw : runLogged n hn P word with
  | none => simp [hw] at hrun
  | some result =>
    obtain ⟨R, events⟩ := result
    simp only [hw, Option.bind_some, runLogged_phase, Option.map_some,
      List.append_nil, Option.some.injEq, Prod.mk.injEq] at hrun
    rcases hrun with ⟨hQ, hH⟩
    have hR : phaseShift Q layer (-amount) = R := by
      rw [← hQ, phaseShift_add]
      simp
    rw [← hR, ← hH]

def phaseFreeSlideWord (layer : Layer) (source : ZMod n) (f : Nat) : List Letter :=
  pWord layer (1-source).val ++ [.d layer] ++
    (FusionLogCompression.pdWord (f-1)).map (layerLetter layer)

theorem phaseFreeSlideWord_length (layer : Layer) (source : ZMod n)
    (f : Nat) :
    (phaseFreeSlideWord layer source f).length =
      (1-source).val + 1 + 2*(f-1) := by
  simp only [phaseFreeSlideWord, List.length_append, pWord,
    List.length_replicate, List.length_singleton, List.length_map,
    FusionLogCompression.pdWord_length]

/-- Removing only the actual restoring suffix of a certified silent batch
retains its exact physical endpoint and leaves the resulting phase explicit. -/
theorem phaseFreeSlideWord_spec (hn : 3 ≤ n) (P : Placement n) (layer : Layer)
    (source : ZMod n) (f : Nat) (hf : 1 ≤ f) (hfn : f ≤ n-2)
    (hsource : (packetAt P layer (zsite source)).Nonempty)
    (hholes : ∀ i : Nat, 1 ≤ i → i ≤ f →
      packetAt P layer (zsite (source-i)) = ∅) :
    runLogged n (by omega) P (phaseFreeSlideWord layer source f) =
      some (phaseShift (relocateAt P layer source (source-f)) layer (-(source-f)), []) := by
  have hsplit :
      (FusionLogCompression.batchWord source f).map (layerLetter layer) =
        phaseFreeSlideWord layer source f ++ pWord layer (source-f).val := by
    simp [FusionLogCompression.batchWord, phaseFreeSlideWord, List.map_append,
      map_singleRing_pWord_slide, layerLetter]
  obtain ⟨hbatch, _⟩ := reservedBatchWord_spec hn P layer source f hf hfn hsource hholes
  rw [hsplit] at hbatch
  exact runLogged_unphase_slide_suffix (by omega) P _ _ layer (source-f) hbatch

/-- Move one named root across an empty interval without restoring the old
cursor. Its normalized location becomes `y`, and no event is emitted. -/
theorem comb_phaseFreeSlide
    (hn : 1 < n) (P : Placement n) (cursor : Fin n)
    {x y : Nat} (hy : 0 < y) (hyx : y < x) (hxn : x < n)
    (hsource : (packetAt (phaseShift P true (cursor.val : ZMod n)) true
      (zsite (x : ZMod n))).Nonempty)
    (hholes : ∀ q : Nat, y ≤ q → q < x →
      packetAt (phaseShift P true (cursor.val : ZMod n)) true (zsite (q : ZMod n)) = ∅) :
    ∃ (R : Placement n) (word : List Letter),
      runLogged n hn P word = some (R, []) ∧
      phaseShift R true (y : ZMod n) =
        relocateAt (phaseShift P true (cursor.val : ZMod n)) true
          (x : ZMod n) (y : ZMod n) ∧
      word.length + y = cursor.val + n*cursorWinding cursor.val (x-1) + (x-y) := by
  let c : ZMod n := cursor.val
  let source : ZMod n := (x : ZMod n)-c
  let f := x-y
  have hf : 1 ≤ f := by dsimp [f]; omega
  have hfn : f ≤ n-2 := by dsimp [f]; omega
  have hsource' : (packetAt P true (zsite source)).Nonempty := by
    simpa only [packetAt_phaseShift, source, c] using hsource
  have hholes' : ∀ i : Nat, 1 ≤ i → i ≤ f →
      packetAt P true (zsite (source-i)) = ∅ := by
    intro i hi hif
    have hib : i ≤ x := by dsimp [f] at hif; omega
    have hq : packetAt (phaseShift P true c) true (zsite ((x-i : Nat) : ZMod n)) = ∅ :=
      hholes (x-i) (by dsimp [f] at hif; omega) (by omega)
    rw [packetAt_phaseShift] at hq
    have he : ((x-i : Nat) : ZMod n)-c = source-(i : ZMod n) := by
      rw [Nat.cast_sub hib]
      dsimp [source]
      ring
    simpa only [he] using hq
  let R := phaseShift (relocateAt P true source (source-(f : ZMod n))) true
    (-(source-(f : ZMod n)))
  refine ⟨R, phaseFreeSlideWord true source f, ?_, ?_, ?_⟩
  · exact phaseFreeSlideWord_spec (by omega) P true source f hf hfn hsource' hholes'
  · dsimp [R]
    rw [phaseShift_add]
    have hfcast : (f : ZMod n) = (x : ZMod n)-(y : ZMod n) := by
      dsimp [f]
      exact Nat.cast_sub (by omega)
    have he : -(source-(f : ZMod n))+(y : ZMod n) = c := by
      rw [hfcast]
      dsimp [source]
      ring
    rw [he, phaseShift_relocate_upper]
    simp only [source, hfcast]
    congr 2 <;> ring
  · have htarget : x-1 < n := by omega
    have hturn : (1-source).val = cursorTurn n cursor.val (x-1) := by
      rw [cursorTurn_eq_zmod_val cursor.isLt htarget]
      congr 1
      have hx1 : ((x-1 : Nat) : ZMod n) = (x : ZMod n)-1 := by
        rw [Nat.cast_sub (by omega : 1 ≤ x)]
        simp
      rw [hx1]
      dsimp [source, c]
      ring
    rw [phaseFreeSlideWord_length, hturn]
    have hp := cursorTurn_payment cursor.isLt htarget
    dsimp [f]
    omega

/-- Linear per-root payment, keeping the same actual silent word. -/
theorem comb_phaseFreeSlide_le
    (hn : 1 < n) (P : Placement n) (cursor : Fin n)
    {x y : Nat} (hy : 0 < y) (hyx : y < x) (hxn : x < n)
    (hsource : (packetAt (phaseShift P true (cursor.val : ZMod n)) true
      (zsite (x : ZMod n))).Nonempty)
    (hholes : ∀ q : Nat, y ≤ q → q < x →
      packetAt (phaseShift P true (cursor.val : ZMod n)) true (zsite (q : ZMod n)) = ∅) :
    ∃ (R : Placement n) (word : List Letter),
      runLogged n hn P word = some (R, []) ∧
      phaseShift R true (y : ZMod n) =
        relocateAt (phaseShift P true (cursor.val : ZMod n)) true
          (x : ZMod n) (y : ZMod n) ∧
      word.length + y ≤ cursor.val + n + (x-y) := by
  obtain ⟨R, word, hw, hr, hp⟩ := comb_phaseFreeSlide hn P cursor hy hyx hxn hsource hholes
  refine ⟨R, word, hw, hr, ?_⟩
  have hwind : cursorWinding cursor.val (x-1) ≤ 1 := by
    unfold cursorWinding
    split_ifs <;> omega
  nlinarith

end RSR2History
