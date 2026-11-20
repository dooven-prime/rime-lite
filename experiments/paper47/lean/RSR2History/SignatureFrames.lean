import RSR2History.EventGeometry

namespace RSR2History

open RSR2.Parametric

theorem cyclicSignature_length_le (P : Placement n) (layer : Layer) :
    (cyclicSignature P layer).length ≤ n := by
  simpa [cyclicSignature, stripEmpty] using
    List.length_filter_le (fun a : Finset (Fin n) => a != ∅) (layerSlots P layer)

theorem cyclicSignature_packet_nonempty (P : Placement n) (layer : Layer)
    {block : Finset (Fin n)} (h : block ∈ cyclicSignature P layer) : block.Nonempty := by
  have hb : block ≠ ∅ := by simpa [cyclicSignature, stripEmpty] using (List.mem_filter.mp h).2
  exact Finset.nonempty_iff_ne_empty.mpr hb

theorem rotated_signature_nonempty {P : Placement n} {layer : Layer}
    {blocks : List (Finset (Fin n))}
    (h : (cyclicSignature P layer).IsRotated blocks) :
    ∀ block ∈ blocks, block ≠ ∅ := by
  intro block hb
  exact (cyclicSignature_packet_nonempty P layer (h.mem_iff.mpr hb)).ne_empty

theorem stripEmpty_of_nonempty {blocks : List (Finset (Fin n))}
    (h : ∀ block ∈ blocks, block ≠ ∅) : stripEmpty ∅ blocks = blocks := by
  exact List.filter_eq_self.mpr (by simpa using h)

theorem stripEmpty_append_empty (blocks : List (Finset (Fin n))) (k : Nat) :
    stripEmpty ∅ (blocks ++ List.replicate k ∅) = stripEmpty ∅ blocks := by
  simp [stripEmpty]

/-- Request literal slots on one layer, with coverage and disjointness
inherited from the same actual placement via the checked route realizer. -/
theorem prepare_layer_slots {n : Nat} (hn : 1 < n) (P : Placement n)
    (layer : Layer) (slots : List (Finset (Fin n)))
    (hlen : slots.length = n)
    (hcycle : (cyclicSignature P layer).IsRotated (stripEmpty ∅ slots)) :
    ∃ R, SilentReachable n hn P R ∧ layerSlots R layer = slots ∧
      ∀ other, other ≠ layer → layerSlots R other = layerSlots P other := by
  have hr : SlotRoute ∅ (layerSlots P layer) slots :=
    (slotRoute_iff _ _ _).mpr ⟨by simpa using hlen.symm, hcycle⟩
  exact hr.realize hn P layer rfl

theorem prepare_packed_layer {n : Nat} (hn : 1 < n) (P : Placement n)
    (layer : Layer) (blocks : List (Finset (Fin n)))
    (hcycle : (cyclicSignature P layer).IsRotated blocks) :
    ∃ R, SilentReachable n hn P R ∧
      layerSlots R layer = blocks ++ List.replicate (n-blocks.length) ∅ ∧
      ∀ other, other ≠ layer → layerSlots R other = layerSlots P other := by
  have hb : blocks.length ≤ n := by
    rw [← hcycle.perm.length_eq]
    exact cyclicSignature_length_le P layer
  have hfilter := stripEmpty_of_nonempty (rotated_signature_nonempty hcycle)
  apply prepare_layer_slots hn P layer
  · simp; omega
  · rw [stripEmpty_append_empty, hfilter]
    exact hcycle

end RSR2History
