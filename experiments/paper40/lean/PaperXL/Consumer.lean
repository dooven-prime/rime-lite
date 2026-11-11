import PaperXL.Core

namespace PaperXL

universe u v w x y

variable {S : Type u} {A : Type v} {Cmd : Type w} {V : Type x} {O : Type y}

structure Consumer (S : Type u) (A : Type v) (Cmd : Type w)
    (V : Type x) (O : Type y) where
  domain : S → Prop
  candidate : S → V
  report : S → O
  enabled : S → Cmd → Bool
  letter : Cmd → A

namespace Consumer

variable (M : RawSystem S A) (C : Consumer S A Cmd V O)

def sameFiber (x y : S) : Prop :=
  C.domain x ∧ C.domain y ∧ C.candidate x = C.candidate y

def R : Prop := ∀ x y, sameFiber C x y → C.report x = C.report y

def G : Prop := ∀ x y, sameFiber C x y →
  ∀ c, C.enabled x c = C.enabled y c

def T : Prop := ∀ x y, sameFiber C x y → ∀ c,
  C.enabled x c = true → C.enabled y c = true →
    C.candidate (M.step x (C.letter c)) =
      C.candidate (M.step y (C.letter c))

def Closed : Prop := ∀ x, C.domain x → ∀ c, C.enabled x c = true →
  C.domain (M.step x (C.letter c))

def QState : Type x := {v : V // ∃ s, C.domain s ∧ C.candidate s = v}

def lift (s : S) (hs : C.domain s) : QState C :=
  ⟨C.candidate s, ⟨s, hs, rfl⟩⟩

noncomputable def representative (v : QState C) : S :=
  Classical.choose v.property

theorem representative_spec (v : QState C) :
    C.domain (representative C v) ∧
      C.candidate (representative C v) = v.1 := by
  exact Classical.choose_spec v.property

structure QuotientWitness (hclosed : Closed M C) where
  reportQ : QState C → O
  enabledQ : QState C → Cmd → Bool
  nextQ : QState C → Cmd → Option (QState C)
  report_factor : ∀ s (hs : C.domain s),
    reportQ (lift C s hs) = C.report s
  enabled_factor : ∀ s (hs : C.domain s) c,
    enabledQ (lift C s hs) c = C.enabled s c
  next_factor : ∀ s (hs : C.domain s) c,
    (hc : C.enabled s c = true) →
      nextQ (lift C s hs) c =
        some (lift C (M.step s (C.letter c)) (hclosed s hs c hc))
  disabled_factor : ∀ s (hs : C.domain s) c,
    C.enabled s c = false → nextQ (lift C s hs) c = none

theorem R_of_quotient (W : QuotientWitness M C hclosed) : R C := by
  intro x y hxy
  rw [← W.report_factor x hxy.1, ← W.report_factor y hxy.2.1]
  apply congrArg W.reportQ
  apply Subtype.ext
  exact hxy.2.2

theorem G_of_quotient (W : QuotientWitness M C hclosed) : G C := by
  intro x y hxy c
  rw [← W.enabled_factor x hxy.1, ← W.enabled_factor y hxy.2.1]
  apply congrArg (fun z => W.enabledQ z c)
  apply Subtype.ext
  exact hxy.2.2

theorem T_of_quotient (W : QuotientWitness M C hclosed) : T M C := by
  intro x y hxy c hx hy
  have hstate : lift C x hxy.1 = lift C y hxy.2.1 := by
    apply Subtype.ext
    exact hxy.2.2
  have hnext := congrArg (fun z => W.nextQ z c) hstate
  have hnext' := congrArg (Option.map Subtype.val) hnext
  rw [W.next_factor x hxy.1 c hx, W.next_factor y hxy.2.1 c hy] at hnext'
  simp only [lift] at hnext'
  exact Option.some.inj hnext'

theorem quotient_of_RGT (hclosed : Closed M C)
    (hR : R C) (hG : G C) (hT : T M C) :
    Nonempty (QuotientWitness M C hclosed) := by
  classical
  let rep : QState C → S := representative C
  let reportQ : QState C → O := fun v => C.report (rep v)
  let enabledQ : QState C → Cmd → Bool := fun v c => C.enabled (rep v) c
  let nextQ : QState C → Cmd → Option (QState C) := fun v c =>
    if h : C.enabled (rep v) c = true then
      some (lift C (M.step (rep v) (C.letter c))
        (hclosed (rep v) (representative_spec C v).1 c h))
    else none
  have hreport : ∀ s (hs : C.domain s),
      reportQ (lift C s hs) = C.report s := by
    intro s hs
    have hr := representative_spec C (lift C s hs)
    have hf : sameFiber C s (rep (lift C s hs)) := ⟨hs, hr.1, hr.2.symm⟩
    exact (hR s (rep (lift C s hs)) hf).symm
  have henabled : ∀ s (hs : C.domain s) c,
      enabledQ (lift C s hs) c = C.enabled s c := by
    intro s hs c
    have hr := representative_spec C (lift C s hs)
    have hf : sameFiber C s (rep (lift C s hs)) := ⟨hs, hr.1, hr.2.symm⟩
    exact (hG s (rep (lift C s hs)) hf c).symm
  let W : QuotientWitness M C hclosed := {
    reportQ := reportQ
    enabledQ := enabledQ
    nextQ := nextQ
    report_factor := hreport
    enabled_factor := henabled
    next_factor := by
      intro s hs c hc
      have hr := representative_spec C (lift C s hs)
      have hf : sameFiber C s (rep (lift C s hs)) := ⟨hs, hr.1, hr.2.symm⟩
      have hg := hG s (rep (lift C s hs)) hf c
      have ht := hT s (rep (lift C s hs)) hf c hc (by simpa [hg] using hc)
      dsimp [nextQ]
      rw [dif_pos (hg.symm.trans hc)]
      congr 1
      apply Subtype.ext
      exact ht.symm
    disabled_factor := by
      intro s hs c hc
      have hr := representative_spec C (lift C s hs)
      have hf : sameFiber C s (rep (lift C s hs)) := ⟨hs, hr.1, hr.2.symm⟩
      have hg := hG s (rep (lift C s hs)) hf c
      dsimp [nextQ]
      rw [dif_neg (by simpa [hg] using hc)]
  }
  exact ⟨W⟩

theorem RGT_iff_quotient (hclosed : Closed M C) :
    R C ∧ G C ∧ T M C ↔ Nonempty (QuotientWitness M C hclosed) := by
  constructor
  · rintro ⟨hR, hG, hT⟩
    exact quotient_of_RGT M C hclosed hR hG hT
  · rintro ⟨W⟩
    exact ⟨R_of_quotient M C W, G_of_quotient M C W, T_of_quotient M C W⟩

end Consumer
end PaperXL
