import PaperXL.Consumer

namespace PaperXL

universe u v

structure GeneratedCover (S : Type u) (A : Type v) extends RawSystem S A where
  cover : List S
  complete : ∀ h : List A, RawSystem.run toRawSystem h ∈ cover

namespace GeneratedCover

variable {S : Type u} {A : Type v} (G : GeneratedCover S A)

theorem seed_mem : G.seed ∈ G.cover := by
  simpa only [RawSystem.run_nil] using G.complete []

def contains (s : S) : Prop := s ∈ G.cover

theorem endpoint_mem (h : List A) : G.run h ∈ G.cover := G.complete h

end GeneratedCover

end PaperXL
