namespace PaperXL

universe u v

structure RawSystem (S : Type u) (A : Type v) where
  step : S → A → S
  seed : S

namespace RawSystem

variable {S : Type u} {A : Type v} (M : RawSystem S A)

def run : List A → S := List.foldl M.step M.seed

@[simp] theorem run_nil : M.run [] = M.seed := rfl

theorem run_append (h k : List A) :
    M.run (h ++ k) = List.foldl M.step (M.run h) k := by
  simp [run, List.foldl_append]

theorem run_append_one (h : List A) (a : A) :
    M.run (h ++ [a]) = M.step (M.run h) a := by
  simp [run, List.foldl_append]

end RawSystem

end PaperXL
