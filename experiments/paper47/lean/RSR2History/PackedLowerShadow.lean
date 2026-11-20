import RSR2History.PackedLowerExtraction
import RSR2History.EventResourceLedger

/-!
Exact atom erasure and shadow simulations for packed lower paths. The
simulation transforms every ordered parent and whole-packet extraction
field; it is not merely a statement about occupancy or terminal partitions.
-/
namespace RSR2History
open RSR2.Parametric

variable {n : Nat}

/-- Add `b` to the packet containing `a`, or leave both absent. -/
def lowerShadow (a b : Fin n) (c : LowerConfiguration n) : LowerConfiguration n :=
  fun x => if x = b then c a else c x

/-- The exact packet-field map induced by an absent atom's shadow. -/
def shadowLowerPacket (a b : Fin n) (B : Finset (Fin n)) : Finset (Fin n) :=
  if a ∈ B then insert b B else B

def shadowLowerEvent (a b : Fin n) : EffectiveEvent n → EffectiveEvent n
  | .fusion layer A B C => .fusion layer (shadowLowerPacket a b A)
      (shadowLowerPacket a b B) (shadowLowerPacket a b C)
  | .transfer B => .transfer (shadowLowerPacket a b B)

def eraseLowerEvent (b : Fin n) : EffectiveEvent n → EffectiveEvent n
  | .fusion layer A B C => .fusion layer (A.erase b) (B.erase b) (C.erase b)
  | .transfer B => .transfer (B.erase b)

@[simp] theorem lowerShadow_apply_self (a b : Fin n) (c : LowerConfiguration n) :
    lowerShadow a b c b = c a := by simp [lowerShadow]

@[simp] theorem lowerShadow_empty (a b : Fin n) :
    lowerShadow a b (lowerExtractionEmpty n) = lowerExtractionEmpty n := by
  funext x; simp [lowerShadow, lowerExtractionEmpty]

@[simp] theorem lowerDelete_apply_self (c : LowerConfiguration n) (b : Fin n) :
    lowerDelete c b b = none := by simp [lowerDelete]

@[simp] theorem lowerDelete_empty (b : Fin n) :
    lowerDelete (lowerExtractionEmpty n) b = lowerExtractionEmpty n := by
  funext x; simp [lowerDelete, lowerExtractionEmpty]

@[simp] theorem lowerPacket_delete (c : LowerConfiguration n) (b q : Fin n) :
    lowerPacket (lowerDelete c b) q = (lowerPacket c q).erase b := by
  ext x; by_cases hx : x = b <;> simp [lowerPacket, lowerDelete, hx]

theorem lowerPacket_shadow (a b : Fin n) (c : LowerConfiguration n)
    (_hab : a ≠ b) (hb : c b = none) (q : Fin n) :
    lowerPacket (lowerShadow a b c) q = shadowLowerPacket a b (lowerPacket c q) := by
  ext x
  simp only [lowerPacket, Finset.mem_filter, Finset.mem_univ, true_and]
  by_cases ha : c a = some q
  · have ham : a ∈ Finset.filter (fun x => c x = some q) Finset.univ := by simp [ha]
    simp only [shadowLowerPacket, ham, if_pos, Finset.mem_insert, Finset.mem_filter,
      Finset.mem_univ, true_and, lowerShadow]
    by_cases hx : x = b
    · simp [hx, ha]
    · simp [hx]
  · have ham : a ∉ Finset.filter (fun x => c x = some q) Finset.univ := by simp [ha]
    simp only [shadowLowerPacket, ham, lowerShadow]
    by_cases hx : x = b
    · simp [hx, ha, hb]
    · simp [hx]

theorem shadowLowerPacket_union (a b : Fin n) (A B : Finset (Fin n)) :
    shadowLowerPacket a b (A ∪ B) = shadowLowerPacket a b A ∪ shadowLowerPacket a b B := by
  ext x
  by_cases ha : a ∈ A <;> by_cases hb : a ∈ B <;>
    simp [shadowLowerPacket, ha, hb]

theorem shadowLowerPacket_nonempty (a b : Fin n) {B : Finset (Fin n)}
    (hB : B.Nonempty) : (shadowLowerPacket a b B).Nonempty := by
  unfold shadowLowerPacket
  split_ifs
  · exact Finset.insert_nonempty _ _
  · exact hB

theorem lowerShadow_rotate (a b : Fin n) (hn : 1 < n) (c : LowerConfiguration n) :
    lowerRotate n hn (lowerShadow a b c) = lowerShadow a b (lowerRotate n hn c) := by
  funext x; by_cases hx : x = b <;> simp [lowerRotate, lowerShadow, hx]

theorem lowerShadow_slide (a b : Fin n) (hn : 1 < n) (c : LowerConfiguration n) :
    lowerSlide n hn (lowerShadow a b c) = lowerShadow a b (lowerSlide n hn c) := by
  funext x; by_cases hx : x = b <;> simp [lowerSlide, lowerShadow, hx]

theorem lowerDelete_rotate (b : Fin n) (hn : 1 < n) (c : LowerConfiguration n) :
    lowerRotate n hn (lowerDelete c b) = lowerDelete (lowerRotate n hn c) b := by
  funext x; by_cases hx : x = b <;> simp [lowerRotate, lowerDelete, hx]

theorem lowerDelete_slide (b : Fin n) (hn : 1 < n) (c : LowerConfiguration n) :
    lowerSlide n hn (lowerDelete c b) = lowerDelete (lowerSlide n hn c) b := by
  funext x; by_cases hx : x = b <;> simp [lowerSlide, lowerDelete, hx]

theorem lowerShadow_erasePacket (a b : Fin n) (c : LowerConfiguration n)
    (_hb : c b = none) (B : Finset (Fin n)) (hbB : b ∉ B) :
    lowerErasePacket (lowerShadow a b c) (shadowLowerPacket a b B) =
      lowerShadow a b (lowerErasePacket c B) := by
  funext x
  by_cases hx : x = b
  · subst x
    by_cases ha : a ∈ B <;> simp [lowerErasePacket, lowerShadow, shadowLowerPacket, ha, hbB]
  · by_cases ha : a ∈ B <;>
      simp [lowerErasePacket, lowerShadow, shadowLowerPacket, hx, ha]

theorem lowerDelete_erasePacket (b : Fin n) (c : LowerConfiguration n)
    (B : Finset (Fin n)) :
    lowerErasePacket (lowerDelete c b) (B.erase b) = lowerDelete (lowerErasePacket c B) b := by
  funext x; by_cases hx : x = b <;> simp [lowerErasePacket, lowerDelete, hx]

theorem lowerShadow_lowerDelete (a b : Fin n) (c : LowerConfiguration n)
    (hab : a ≠ b) (hco : c a = c b) :
    lowerShadow a b (lowerDelete c b) = c := by
  funext x
  by_cases hx : x = b
  · subst x; simp [lowerShadow, lowerDelete, hab, hco]
  · simp [lowerShadow, lowerDelete, hx]

/-- An absent atom is not recreated by any packed path. -/
theorem PackedLowerPath.absent {hn : 1 < n} {c d : LowerConfiguration n}
    {H : List (EffectiveEvent n)} {cost : Nat} (path : PackedLowerPath n hn c H d cost)
    {b : Fin n} (hb : c b = none) : d b = none := by
  induction path with
  | prepare path =>
      have hs := path.support b
      by_contra hd
      exact hs.mp hd |>.1 hb
  | event step =>
      cases step with
      | fusion left right => simp [lowerSlide, hb]
      | extract nonempty => simp [lowerErasePacket, lowerPacket, hb]
  | trans first last ihFirst ihLast => exact ihLast (ihFirst hb)

/-- A deletion-free preparation preserves equality of two coordinates. -/
theorem LowerExtractionPath.cohabiting_no_deletion {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) (hz : z = [])
    {a b : Fin n} (hco : c a = c b) : d a = d b := by
  induction path with
  | refl => exact hco
  | rotate c => simp [lowerRotate, hco]
  | slide c empty occupied => simp [lowerSlide, hco]
  | delete => cases hz
  | trans first last ihFirst ihLast =>
      obtain ⟨hf, hl⟩ := List.append_eq_nil_iff.mp hz
      exact ihLast hl (ihFirst hf hco)

/-- Packed fusions and whole-packet deletion never split cohabiting atoms. -/
theorem PackedLowerEvent.cohabiting {hn : 1 < n} {c d : LowerConfiguration n}
    {e : EffectiveEvent n} {cost : Nat} (step : PackedLowerEvent n hn c e d cost)
    {a b : Fin n} (hco : c a = c b) : d a = d b := by
  cases step with
  | fusion left right => simp [lowerSlide, hco]
  | extract nonempty => simp [lowerErasePacket, lowerPacket, hco]

theorem PackedLowerPath.cohabiting {hn : 1 < n} {c d : LowerConfiguration n}
    {H : List (EffectiveEvent n)} {cost : Nat} (path : PackedLowerPath n hn c H d cost)
    {a b : Fin n} (hco : c a = c b) : d a = d b := by
  induction path with
  | prepare path => exact path.cohabiting_no_deletion rfl hco
  | event step => exact step.cohabiting hco
  | trans first last ihFirst ihLast => exact ihLast (ihFirst hco)

/-- Every silent preparation can add an absent shadow without changing cost
or the empty event log. -/
theorem LowerExtractionPath.shadow_no_deletion {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) (hz : z = [])
    (a b : Fin n) (hb : c b = none) :
    LowerExtractionPath n hn (lowerShadow a b c) [] (lowerShadow a b d) cost := by
  induction path with
  | refl c => exact .refl _
  | rotate c => simpa only [lowerShadow_rotate] using LowerExtractionPath.rotate (hn := hn) (lowerShadow a b c)
  | slide c empty occupied =>
      have hempty : ∀ x, lowerShadow a b c x ≠ some (site0 n (by omega)) := by
        intro x; by_cases hx : x = b <;> simp [lowerShadow, hx, empty]
      have hoccupied : ∃ x, lowerShadow a b c x = some (site1 n hn) := by
        obtain ⟨x, hx⟩ := occupied
        have hxb : x ≠ b := by intro h; subst x; simp [hb] at hx
        exact ⟨x, by simpa [lowerShadow, hxb] using hx⟩
      simpa only [lowerShadow_slide] using LowerExtractionPath.slide _ hempty hoccupied
  | delete => cases hz
  | trans first last ihFirst ihLast =>
      obtain ⟨hf, hl⟩ := List.append_eq_nil_iff.mp hz
      have hmid : _ := not_ne_iff.mp (by
        intro h
        exact (first.support b).mp h |>.1 hb)
      simpa using (ihFirst hf hb).trans (ihLast hl hmid)

/-- Exact event-field simulation, including the ordered parents. -/
theorem PackedLowerEvent.shadow {hn : 1 < n} {c d : LowerConfiguration n}
    {e : EffectiveEvent n} {cost : Nat} (step : PackedLowerEvent n hn c e d cost)
    (a b : Fin n) (hab : a ≠ b) (hb : c b = none) :
    PackedLowerEvent n hn (lowerShadow a b c) (shadowLowerEvent a b e)
      (lowerShadow a b d) cost := by
  cases step with
  | fusion left right =>
      have left' := shadowLowerPacket_nonempty a b left
      have right' := shadowLowerPacket_nonempty a b right
      rw [← lowerPacket_shadow a b c hab hb] at left' right'
      simpa only [shadowLowerEvent, ← lowerShadow_slide, lowerPacket_shadow a b c hab hb,
        shadowLowerPacket_union] using PackedLowerEvent.fusion (lowerShadow a b c) left' right'
  | extract nonempty =>
      have nb : b ∉ lowerPacket c (site0 n (by omega)) := by simp [lowerPacket, hb]
      have ne := shadowLowerPacket_nonempty a b nonempty
      rw [← lowerPacket_shadow a b c hab hb] at ne
      simpa only [shadowLowerEvent, lowerPacket_shadow a b c hab hb,
        lowerShadow_erasePacket a b c hb _ nb] using
          PackedLowerEvent.extract (lowerShadow a b c) ne

/-- Complete same-cost shadow tail simulation. No final-state-only quotient
is used: the entire structured event list is transformed field by field. -/
theorem PackedLowerPath.shadow {hn : 1 < n} {c d : LowerConfiguration n}
    {H : List (EffectiveEvent n)} {cost : Nat} (path : PackedLowerPath n hn c H d cost)
    (a b : Fin n) (hab : a ≠ b) (hb : c b = none) :
    PackedLowerPath n hn (lowerShadow a b c) (H.map (shadowLowerEvent a b))
      (lowerShadow a b d) cost := by
  induction path with
  | prepare path => exact .prepare (path.shadow_no_deletion rfl a b hb)
  | event step => exact .event (step.shadow a b hab hb)
  | trans first last ihFirst ihLast =>
      simpa only [List.map_append] using (ihFirst hb).trans (ihLast (first.absent hb))


/-- Silent preparation also allows erasing one of two cohabiting atoms. -/
theorem LowerExtractionPath.erase_cohabiting_no_deletion {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) (hz : z = [])
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    LowerExtractionPath n hn (lowerDelete c b) [] (lowerDelete d b) cost := by
  induction path with
  | refl c => exact .refl _
  | rotate c =>
      simpa only [lowerDelete_rotate] using LowerExtractionPath.rotate (hn := hn) (lowerDelete c b)
  | slide c empty occupied =>
      have hempty : ∀ x, lowerDelete c b x ≠ some (site0 n (by omega)) := by
        intro x; by_cases hx : x = b <;> simp [lowerDelete, hx, empty]
      have hoccupied : ∃ x, lowerDelete c b x = some (site1 n hn) := by
        obtain ⟨x, hx⟩ := occupied
        by_cases hxb : x = b
        · subst x
          exact ⟨a, by simpa [lowerDelete, hab, hco] using hx⟩
        · exact ⟨x, by simpa [lowerDelete, hxb] using hx⟩
      simpa only [lowerDelete_slide] using LowerExtractionPath.slide _ hempty hoccupied
  | delete => cases hz
  | trans first last ihFirst ihLast =>
      obtain ⟨hf, hl⟩ := List.append_eq_nil_iff.mp hz
      simpa using (ihFirst hf hco).trans
        (ihLast hl (first.cohabiting_no_deletion hf hco))

theorem lowerPacket_erase_cohabiting_nonempty {c : LowerConfiguration n}
    (a b q : Fin n) (hab : a ≠ b) (hco : c a = c b)
    (nonempty : (lowerPacket c q).Nonempty) : ((lowerPacket c q).erase b).Nonempty := by
  obtain ⟨x, hx⟩ := nonempty
  by_cases hxb : x = b
  · subst x
    refine ⟨a, ?_⟩
    simpa [lowerPacket, hab, hco] using hx
  · exact ⟨x, by simp [hxb, hx]⟩

private theorem erase_union (b : Fin n) (A B : Finset (Fin n)) :
    (A ∪ B).erase b = A.erase b ∪ B.erase b := by
  ext x
  simp only [Finset.mem_erase, Finset.mem_union]
  tauto

/-- Erasing a cohabiting atom preserves both ordered fusion parents and each
complete extracted packet, after exactly deleting that atom from the fields. -/
theorem PackedLowerEvent.erase_cohabiting {hn : 1 < n}
    {c d : LowerConfiguration n} {e : EffectiveEvent n} {cost : Nat}
    (step : PackedLowerEvent n hn c e d cost)
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    PackedLowerEvent n hn (lowerDelete c b) (eraseLowerEvent b e)
      (lowerDelete d b) cost := by
  cases step with
  | fusion left right =>
      have left' := lowerPacket_erase_cohabiting_nonempty a b _ hab hco left
      have right' := lowerPacket_erase_cohabiting_nonempty a b _ hab hco right
      rw [← lowerPacket_delete] at left' right'
      simpa only [eraseLowerEvent, lowerPacket_delete, erase_union,
        lowerDelete_slide] using PackedLowerEvent.fusion (lowerDelete c b) left' right'
  | extract nonempty =>
      have ne := lowerPacket_erase_cohabiting_nonempty a b _ hab hco nonempty
      rw [← lowerPacket_delete] at ne
      simpa only [eraseLowerEvent, lowerPacket_delete, lowerDelete_erasePacket] using
        PackedLowerEvent.extract (lowerDelete c b) ne

/-- Full erasure simulation: event identities and lower cost are retained
exactly, and all future port guards follow from cohabitation. -/
theorem PackedLowerPath.erase_cohabiting {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost)
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    PackedLowerPath n hn (lowerDelete c b) (H.map (eraseLowerEvent b))
      (lowerDelete d b) cost := by
  induction path with
  | prepare path => exact .prepare (path.erase_cohabiting_no_deletion rfl a b hab hco)
  | event step => exact .event (step.erase_cohabiting a b hab hco)
  | trans first last ihFirst ihLast =>
      simpa only [List.map_append] using (ihFirst hco).trans (ihLast (first.cohabiting hco))

theorem shadowLowerPacket_erase (a b : Fin n) (hab : a ≠ b)
    (B : Finset (Fin n)) (hco : a ∈ B ↔ b ∈ B) :
    shadowLowerPacket a b (B.erase b) = B := by
  by_cases ha : a ∈ B
  · have hb := hco.mp ha
    simp [shadowLowerPacket, hab, ha, Finset.insert_erase hb]
  · have hb : b ∉ B := by tauto
    simp [shadowLowerPacket, ha, Finset.erase_eq_of_notMem hb]

theorem lowerPacket_cohabiting_membership {c : LowerConfiguration n}
    {a b : Fin n} (hco : c a = c b) (q : Fin n) :
    a ∈ lowerPacket c q ↔ b ∈ lowerPacket c q := by simp [lowerPacket, hco]

/-- The exact erase/shadow round trip for one actual event includes all
three ordered fusion fields, not just the union. -/
theorem PackedLowerEvent.shadow_erase_event {hn : 1 < n}
    {c d : LowerConfiguration n} {e : EffectiveEvent n} {cost : Nat}
    (step : PackedLowerEvent n hn c e d cost)
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    shadowLowerEvent a b (eraseLowerEvent b e) = e := by
  cases step with
  | fusion left right =>
      have h0 := lowerPacket_cohabiting_membership hco (site0 n (by omega))
      have h1 := lowerPacket_cohabiting_membership hco (site1 n hn)
      have hu : a ∈ lowerPacket c (site0 n (by omega)) ∪ lowerPacket c (site1 n hn) ↔
          b ∈ lowerPacket c (site0 n (by omega)) ∪ lowerPacket c (site1 n hn) := by
        simp only [Finset.mem_union]; tauto
      simp only [eraseLowerEvent, shadowLowerEvent, shadowLowerPacket_erase a b hab _ h0,
        shadowLowerPacket_erase a b hab _ h1, shadowLowerPacket_erase a b hab _ hu]
  | extract nonempty =>
      simp only [eraseLowerEvent, shadowLowerEvent,
        shadowLowerPacket_erase a b hab _ (lowerPacket_cohabiting_membership hco _)]

/-- Exact complete-log round trip along the same cohabiting tail. -/
theorem PackedLowerPath.shadow_erase_log {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost)
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    (H.map (eraseLowerEvent b)).map (shadowLowerEvent a b) = H := by
  induction path with
  | prepare path => rfl
  | event step => simpa using step.shadow_erase_event a b hab hco
  | trans first last ihFirst ihLast =>
      simp only [List.map_append, ihFirst hco, ihLast (first.cohabiting hco)]

/-- Erasing a cohabiting atom and then shadowing it recovers the literal
entire path, including its exact event list and unchanged cost. -/
theorem PackedLowerPath.erase_shadow_roundtrip {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost)
    (a b : Fin n) (hab : a ≠ b) (hco : c a = c b) :
    PackedLowerPath n hn (lowerShadow a b (lowerDelete c b)) H
      (lowerShadow a b (lowerDelete d b)) cost := by
  have erased := path.erase_cohabiting a b hab hco
  have lifted := erased.shadow a b hab (by simp)
  simpa only [path.shadow_erase_log a b hab hco] using lifted


@[simp] theorem lowerDelete_lowerShadow (a b : Fin n) (c : LowerConfiguration n)
    (hb : c b = none) : lowerDelete (lowerShadow a b c) b = c := by
  funext x
  by_cases hx : x = b
  · subst x; simp [lowerDelete, hb]
  · simp [lowerDelete, lowerShadow, hx]

@[simp] theorem logFusionCount_map_eraseLowerEvent (b : Fin n)
    (H : List (EffectiveEvent n)) :
    logFusionCount (H.map (eraseLowerEvent b)) = logFusionCount H := by
  simp only [logFusionCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

@[simp] theorem logLayerFusionCount_map_eraseLowerEvent (b : Fin n)
    (layer : Layer) (H : List (EffectiveEvent n)) :
    logLayerFusionCount layer (H.map (eraseLowerEvent b)) = logLayerFusionCount layer H := by
  simp only [logLayerFusionCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

@[simp] theorem logTransferCount_map_eraseLowerEvent (b : Fin n)
    (H : List (EffectiveEvent n)) :
    logTransferCount (H.map (eraseLowerEvent b)) = logTransferCount H := by
  simp only [logTransferCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

@[simp] theorem logFusionCount_map_shadowLowerEvent (a b : Fin n)
    (H : List (EffectiveEvent n)) :
    logFusionCount (H.map (shadowLowerEvent a b)) = logFusionCount H := by
  simp only [logFusionCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

@[simp] theorem logLayerFusionCount_map_shadowLowerEvent (a b : Fin n)
    (layer : Layer) (H : List (EffectiveEvent n)) :
    logLayerFusionCount layer (H.map (shadowLowerEvent a b)) = logLayerFusionCount layer H := by
  simp only [logLayerFusionCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

@[simp] theorem logTransferCount_map_shadowLowerEvent (a b : Fin n)
    (H : List (EffectiveEvent n)) :
    logTransferCount (H.map (shadowLowerEvent a b)) = logTransferCount H := by
  simp only [logTransferCount, List.map_map]
  congr 1
  apply List.map_congr_left
  intro e he
  cases e <;> rfl

end RSR2History
