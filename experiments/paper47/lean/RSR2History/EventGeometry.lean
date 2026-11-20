import RSR2History.EventTransport

namespace RSR2History

open RSR2.Parametric

theorem layerSlots_head (n : Nat) (hn : 0 < n) (P : Placement n)
    (layer : Layer) (a : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P layer = a :: post) :
    packetAt P layer (site0 n hn) = a := by
  have h := congrArg (fun xs => xs[0]?) hslots
  simpa [layerSlots, site0, hn] using h

theorem layerSlots_second (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (a b : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P layer = a :: b :: post) :
    packetAt P layer (site1 n hn) = b := by
  have h := congrArg (fun xs => xs[1]?) hslots
  simpa [layerSlots, site1, hn] using h

theorem layerSlots_cons (n : Nat) (hn : 0 < n) (P : Placement n) (layer : Layer) :
    ∃ post, layerSlots P layer = packetAt P layer (site0 n hn) :: post := by
  have hlen := layerSlots_length P layer
  cases hs : layerSlots P layer with
  | nil => simp [hs] at hlen; omega
  | cons a post =>
      have ha := layerSlots_head n hn P layer a post hs
      exact ⟨post, by simp_all⟩

theorem layerSlots_cons_two (n : Nat) (hn : 1 < n) (P : Placement n) (layer : Layer) :
    ∃ post, layerSlots P layer = packetAt P layer (site0 n (by omega)) ::
      packetAt P layer (site1 n hn) :: post := by
  have hlen := layerSlots_length P layer
  cases hs : layerSlots P layer with
  | nil => simp [hs] at hlen; omega
  | cons a rest =>
      cases rest with
      | nil => simp [hs] at hlen; omega
      | cons b post =>
          have ha := layerSlots_head n (by omega) P layer a (b :: post) hs
          have hb := layerSlots_second n hn P layer a b post hs
          exact ⟨post, by simp_all⟩

theorem layerSlots_collapse_head (n : Nat) (hn : 1 < n) (P : Placement n)
    (layer : Layer) (a b : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P layer = a :: b :: post) :
    layerSlots (collapse n hn P layer) layer = (a ∪ b) :: ∅ :: post := by
  have ha := layerSlots_head n (by omega) P layer a (b :: post) hslots
  have hb := layerSlots_second n hn P layer a b post hslots
  apply List.ext_getElem
  · have := congrArg List.length hslots
    simp only [layerSlots_length, List.length_cons] at *
    omega
  · intro q hq hq'
    rw [layerSlots_getElem, packetAt_collapse]
    rcases q with _ | q
    · rw [if_pos (show (⟨0, by simpa using hq⟩ : Fin n) = site0 n (by omega) from rfl)]
      change packetAt P layer (site0 n (by omega)) ∪ packetAt P layer (site1 n hn) = _
      rw [ha, hb]
      rfl
    · rcases q with _ | q
      · simp [site0, site1]
      · have hz : (⟨q+2, by simpa using hq⟩ : Fin n) ≠ site0 n (by omega) := by
          intro h; have := congrArg Fin.val h; simp [site0] at this
        have ho : (⟨q+2, by simpa using hq⟩ : Fin n) ≠ site1 n hn := by
          intro h; have := congrArg Fin.val h; simp [site1] at this
        simp only [if_neg hz, if_neg ho, List.getElem_cons_succ]
        have h := congrArg (fun xs => xs[q+2]?) hslots
        have hqn : q+2 < n := by simpa using hq
        have hpost : q < post.length := by simpa using hq'
        simpa [layerSlots, hqn, List.getElem?_eq_getElem hpost] using h

theorem packetAt_lift_lower (n : Nat) (hn : 0 < n) (P : Placement n) (q : Fin n) :
    packetAt (liftPacket n hn P) false q =
      if q = site0 n hn then ∅ else packetAt P false q := by
  apply Finset.ext
  intro a
  by_cases hq : q = site0 n hn <;> by_cases ha : P a = (false, site0 n hn)
  all_goals simp [liftPacket, ha, hq, mem_packetAt]
  all_goals exact Ne.symm hq

theorem packetAt_lift_upper (n : Nat) (hn : 0 < n) (P : Placement n) (q : Fin n) :
    packetAt (liftPacket n hn P) true q =
      if q = site0 n hn then packetAt P true q ∪ packetAt P false q
      else packetAt P true q := by
  apply Finset.ext
  intro a
  by_cases hq : q = site0 n hn <;> by_cases ha : P a = (false, site0 n hn)
  all_goals simp [liftPacket, ha, hq, mem_packetAt]
  all_goals exact Ne.symm hq

theorem layerSlots_lift_lower (n : Nat) (hn : 0 < n) (P : Placement n)
    (a : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hslots : layerSlots P false = a :: post) :
    layerSlots (liftPacket n hn P) false = ∅ :: post := by
  apply List.ext_getElem
  · have := congrArg List.length hslots
    simp only [layerSlots_length, List.length_cons] at *
    omega
  · intro q hq hq'
    rw [layerSlots_getElem, packetAt_lift_lower]
    rcases q with _ | q
    · simp [site0]
    · have hz : (⟨q+1, by simpa using hq⟩ : Fin n) ≠ site0 n hn := by
        intro h; have := congrArg Fin.val h; simp [site0] at this
      simp only [if_neg hz, List.getElem_cons_succ]
      have h := congrArg (fun xs => xs[q+1]?) hslots
      have hqn : q+1 < n := by simpa using hq
      have hpost : q < post.length := by simpa using hq'
      simpa [layerSlots, hqn, List.getElem?_eq_getElem hpost] using h

theorem layerSlots_lift_upper (n : Nat) (hn : 0 < n) (P : Placement n)
    (a : Finset (Fin n)) (post : List (Finset (Fin n)))
    (hlo : packetAt P false (site0 n hn) = a)
    (hslots : layerSlots P true = ∅ :: post) :
    layerSlots (liftPacket n hn P) true = a :: post := by
  have hempty := layerSlots_head n hn P true ∅ post hslots
  apply List.ext_getElem
  · have := congrArg List.length hslots
    simp only [layerSlots_length, List.length_cons] at *
    omega
  · intro q hq hq'
    rw [layerSlots_getElem, packetAt_lift_upper]
    rcases q with _ | q
    · rw [if_pos (show (⟨0, by simpa using hq⟩ : Fin n) = site0 n hn from rfl)]
      change packetAt P true (site0 n hn) ∪ packetAt P false (site0 n hn) = a
      rw [hempty, hlo, Finset.empty_union]
    · have hz : (⟨q+1, by simpa using hq⟩ : Fin n) ≠ site0 n hn := by
        intro h; have := congrArg Fin.val h; simp [site0] at this
      simp only [if_neg hz, List.getElem_cons_succ]
      have h := congrArg (fun xs => xs[q+1]?) hslots
      have hqn : q+1 < n := by simpa using hq
      have hpost : q < post.length := by simpa using hq'
      simpa [layerSlots, hqn, List.getElem?_eq_getElem hpost] using h

end RSR2History
