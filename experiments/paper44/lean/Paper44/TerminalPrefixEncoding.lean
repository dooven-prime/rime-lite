import Paper44.CircularPrefixCounting
import Mathlib.Data.Finset.Sort

/-! # Sparse checkpoint encodings

The Bool vector is indexed by the increasing order of the chosen checkpoints.
These equivalences retain port bindings, including the final full-carrier event.
-/

namespace Paper44

open RegisteredAbsorptionChains

noncomputable def sparseCode {N ell : ℕ} (p : TerminalSaturated N ell) : Code N :=
  fun i => if hi : i ∈ p.1.val then
    some (p.2 ((p.1.val.orderIsoOfFin p.1.property).symm ⟨i, hi⟩)) else none

theorem support_sparseCode {N ell : ℕ} (p : TerminalSaturated N ell) :
    support (sparseCode p) = p.1.val := by
  classical
  ext i
  simp [support, sparseCode]

theorem sparseCode_injective {N ell : ℕ} :
    Function.Injective (sparseCode (N := N) (ell := ell)) := by
  classical
  rintro ⟨⟨S, hS⟩, b⟩ ⟨⟨T, hT⟩, d⟩ heq
  have hST : S = T := by
    simpa only [support_sparseCode] using congrArg support heq
  subst T
  have hbd : b = d := by
    funext k
    let q := S.orderIsoOfFin hS k
    have h := congrFun heq q.val
    have h' : some (b ((S.orderIsoOfFin hS).symm q)) =
        some (d ((S.orderIsoOfFin hS).symm q)) := by
      simpa only [sparseCode, dif_pos q.property] using h
    simpa only [q, OrderIso.symm_apply_apply] using Option.some.inj h'
  subst d
  rfl

theorem sparseCode_surjective {N ell : ℕ} (c : Code N)
    (hc : (support c).card = ell) :
    ∃ p : TerminalSaturated N ell, sparseCode p = c := by
  classical
  let S : Select N ell := ⟨support c, hc⟩
  let b : Fin ell → Bool := fun k =>
    (c (S.val.orderIsoOfFin S.property k).val).getD false
  refine ⟨⟨S, b⟩, ?_⟩
  funext i
  by_cases hi : i ∈ support c
  · have hci : c i ≠ none := (Finset.mem_filter.mp hi).2
    simp only [sparseCode, S, dif_pos hi, b, OrderIso.apply_symm_apply]
    cases h : c i with
    | none => exact False.elim (hci h)
    | some side => simp
  · have hci : c i = none := by simpa [support] using hi
    simp [sparseCode, S, hi, hci]

noncomputable def saturatedSparseEquiv (N j : ℕ) :
    TerminalSaturated N j ≃ {c : Code N // (support c).card = j} :=
  Equiv.ofBijective (fun p => ⟨sparseCode p, by rw [support_sparseCode]; exact p.1.property⟩)
    ⟨fun _ _ h => sparseCode_injective (congrArg Subtype.val h), by
      intro c
      obtain ⟨p, hp⟩ := sparseCode_surjective c.val c.property
      exact ⟨p, Subtype.ext hp⟩⟩

def appendLastSymbol {N : ℕ} (c : Code N) (side : Bool) : Code (N + 1) :=
  Fin.lastCases (some side) c

@[simp] theorem appendLastSymbol_castSucc {N : ℕ} (c : Code N)
    (side : Bool) (i : Fin N) : appendLastSymbol c side i.castSucc = c i := by
  simp [appendLastSymbol]

@[simp] theorem appendLastSymbol_last {N : ℕ} (c : Code N) (side : Bool) :
    appendLastSymbol c side (Fin.last N) = some side := by
  simp [appendLastSymbol]

theorem support_appendLastSymbol {N : ℕ} (c : Code N) (side : Bool) :
    support (appendLastSymbol c side) =
      insert (Fin.last N) ((support c).map Fin.castSuccEmb) := by
  classical
  ext i
  refine Fin.lastCases ?_ (fun k => ?_) i
  · simp [support]
  · have hk : k.val ≠ N := by omega
    simp only [support, Finset.mem_filter, Finset.mem_univ, true_and,
      Finset.mem_insert, Finset.mem_map, appendLastSymbol_castSucc]
    constructor
    · intro h
      exact Or.inr ⟨k, by simpa [support] using h, rfl⟩
    · rintro (h | ⟨a, ha, heq⟩)
      · exact False.elim (hk (congrArg Fin.val h))
      · have hak : a = k := Fin.ext (congrArg (fun x : Fin (N + 1) => x.val) heq)
        simpa [hak, support] using ha

@[simp] theorem card_support_appendLastSymbol {N : ℕ} (c : Code N) (side : Bool) :
    (support (appendLastSymbol c side)).card = (support c).card + 1 := by
  classical
  rw [support_appendLastSymbol, Finset.card_insert_of_notMem]
  · simp
  · simp

noncomputable def shortSparseCode {N j : ℕ} (p : TerminalShort (N + 1) j) :
    Code (N + 1) :=
  appendLastSymbol (sparseCode (⟨p.2.1, fun i => p.2.2 i.castSucc⟩ :
    TerminalSaturated N p.1.val)) (p.2.2 (Fin.last p.1.val))

theorem shortSparseCode_card {N j : ℕ} (p : TerminalShort (N + 1) j) :
    (support (shortSparseCode p)).card = p.1.val + 1 := by
  rw [shortSparseCode, card_support_appendLastSymbol, support_sparseCode]
  exact congrArg (· + 1) p.2.1.property

theorem shortSparseCode_injective {N j : ℕ} :
    Function.Injective (shortSparseCode (N := N) (j := j)) := by
  classical
  rintro ⟨ell, S, b⟩ ⟨len, T, d⟩ heq
  have hel : ell = len := Fin.ext (by
    have h := congrArg (fun c => (support c).card) heq
    rw [shortSparseCode_card, shortSparseCode_card] at h
    change ell.val + 1 = len.val + 1 at h
    omega)
  subst len
  have hinit : (⟨S, fun i => b i.castSucc⟩ : TerminalSaturated N ell.val) =
      ⟨T, fun i => d i.castSucc⟩ := by
    apply sparseCode_injective
    funext i
    simpa [shortSparseCode] using congrFun heq i.castSucc
  have hST : S = T := congrArg Prod.fst hinit
  subst T
  have hbd : b = d := by
    funext i
    refine Fin.lastCases ?_ (fun k => ?_) i
    · simpa [shortSparseCode] using congrFun heq (Fin.last N)
    · exact congrFun (congrArg Prod.snd hinit) k
  subst d
  rfl

theorem shortSparseCode_surjective {N j : ℕ} (c : Code (N + 1))
    (hc : (support c).card < j) (hlast : c (Fin.last N) ≠ none) :
    ∃ p : TerminalShort (N + 1) j, shortSparseCode p = c := by
  classical
  let prior : Code N := fun i => c i.castSucc
  obtain ⟨side, hside⟩ := Option.ne_none_iff_exists'.mp hlast
  have hext : appendLastSymbol prior side = c := by
    funext i
    refine Fin.lastCases ?_ (fun _ => by simp [prior]) i
    simpa using hside.symm
  have hcard : (support prior).card + 1 = (support c).card := by
    rw [← hext, card_support_appendLastSymbol]
  let ell : Fin (j - 1) := ⟨(support prior).card, by omega⟩
  obtain ⟨p, hp⟩ := sparseCode_surjective prior (show (support prior).card = ell.val from rfl)
  refine ⟨⟨ell, p.1, Fin.lastCases side p.2⟩, ?_⟩
  change appendLastSymbol (sparseCode _) _ = c
  simpa [hp] using hext

/-- Canonical sparse representatives of the two terminal prefix phases. -/
abbrev TerminalSparseCode (N j : ℕ) :=
  {c : Code (N + 1) // (support c).card = j} ⊕
    {c : Code (N + 1) // (support c).card < j ∧ c (Fin.last N) ≠ none}

noncomputable def terminalSparseEquiv (N j : ℕ) :
    TerminalPrefixCode (N + 1) j ≃ TerminalSparseCode N j :=
  Equiv.sumCongr (saturatedSparseEquiv (N + 1) j)
    (Equiv.ofBijective (fun p => ⟨shortSparseCode p, by
      constructor
      · rw [shortSparseCode_card]; have := p.1.isLt; omega
      · simp [shortSparseCode]⟩)
      ⟨fun _ _ h => shortSparseCode_injective (congrArg Subtype.val h), by
        intro c
        obtain ⟨p, hp⟩ := shortSparseCode_surjective c.val c.property.1 c.property.2
        exact ⟨p, Subtype.ext hp⟩⟩)

abbrev PositiveTerminalSparseCode (N j : ℕ) (hN : 0 < N) :=
  {c : Code N // (support c).card = j} ⊕
    {c : Code N // (support c).card < j ∧ c ⟨N - 1, by omega⟩ ≠ none}

noncomputable def positiveTerminalSparseEquiv (N j : ℕ) (hN : 0 < N) :
    TerminalPrefixCode N j ≃ PositiveTerminalSparseCode N j hN := by
  cases N with
  | zero => omega
  | succ N => exact terminalSparseEquiv N j

end Paper44
