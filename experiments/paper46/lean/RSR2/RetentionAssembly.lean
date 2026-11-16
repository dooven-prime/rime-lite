import RSR2.RetentionIntervals

/-! Actual lower-layer assembly of admissible retained blocks.  Safe interval
collapses fix every retained source site outside the block being assembled.
Completed packets are represented at sites belonging to their own blocks. -/
namespace RSR2.Parametric

theorem lower_safe_block_realizes (n : Nat) (hn : 1 < n)
    (family : List (List (Fin n))) (B : List (Fin n))
    (hB : B ∈ family) (hne : B ≠ [])
    (hadm : RetentionAdmissible n (by omega) family) :
    ∃ w f, LowerRealizes n hn w f ∧
      (∃ rep ∈ B, ∀ a ∈ B, f a = rep) ∧
      (∀ a, retainedAtoms family a → a ∉ B → f a = a) := by
  classical
  obtain ⟨cut,lo,hi,hle,hlo,_,hb,hsafe⟩ := retention_safe_interval n (by omega)
    (retainedAtoms family) B hne (fun a ha => ⟨B,hB,ha⟩) (hadm B hB)
  let collapse : Fin n → Fin n := fun q =>
    if lo.val ≤ q.val ∧ q.val ≤ hi.val then lo else q
  obtain ⟨w,hw⟩ := lower_interval_collapse_realizes n hn lo.val
    (hi.val-lo.val) (by have := hi.isLt; change lo.val ≤ hi.val at hle; omega)
  have hw' : LowerRealizes n hn w collapse := by
    have he : lo.val+(hi.val-lo.val)=hi.val := by
      change lo.val ≤ hi.val at hle; omega
    simpa only [collapse, he] using hw
  let f := fun a => cutSite n (by omega) cut
    (collapse (cutIndex n (by omega) cut a))
  have hrot : (fun q => nextMany n (by omega) q cut.val) =
      cutSite n (by omega) cut := by
    funext q
    apply Fin.ext
    rw [nextMany_val,cutSite_val,Nat.add_comm]
  have hr := (lower_rotation_realizes n hn (n-cut.val)).append hw'
  have hr' := hr.append (lower_rotation_realizes n hn cut.val)
  have hr'' : LowerRealizes n hn
      (pWord false (n-cut.val) ++ w ++ pWord false cut.val) f := by
    have he : (fun q => nextMany n (by omega)
        (collapse (nextMany n (by omega) q (n-cut.val))) cut.val) = f := by
      funext q
      exact congrFun hrot (collapse (cutIndex n (by omega) cut q))
    exact he ▸ hr'
  refine ⟨_,f,hr'',⟨cutSite n (by omega) cut lo,hlo,?_⟩,?_⟩
  · intro a ha
    have hh := hb a ha
    change lo.val ≤ (cutIndex n (by omega) cut a).val ∧
      (cutIndex n (by omega) cut a).val ≤ hi.val at hh
    simp only [f,collapse,if_pos hh]
  · intro a ha hnot
    have hh : ¬(lo.val ≤ (cutIndex n (by omega) cut a).val ∧
        (cutIndex n (by omega) cut a).val ≤ hi.val) := by
      intro h
      have hc := hsafe (cutIndex n (by omega) cut a) h.1 h.2
        (by simpa only [cutSite_cutIndex] using ha)
      exact hnot (by simpa only [cutSite_cutIndex] using hc)
    simp only [f,collapse,if_neg hh,cutSite_cutIndex]

def BlocksDisjoint (family : List (List α)) : Prop :=
  ∀ B ∈ family, ∀ C ∈ family, ∀ a, a ∈ B → a ∈ C → B=C

def MapsWithin (f : α → α) (family : List (List α)) : Prop :=
  ∀ B ∈ family, ∀ a ∈ B, f a ∈ B

def ConstantOnBlocks (f : α → α) (blocks : List (List α)) : Prop :=
  ∀ B ∈ blocks, ∀ a ∈ B, ∀ b ∈ B, f a=f b

/-- Assemble any sublist of the fixed admissible family.  The induction
preserves membership in every ambient block, not intermediate coordinates. -/
theorem lower_assemble_retained (n : Nat) (hn : 1 < n)
    (family : List (List (Fin n)))
    (hne : ∀ B ∈ family, B ≠ []) (hdisj : BlocksDisjoint family)
    (hadm : RetentionAdmissible n (by omega) family)
    (todo : List (List (Fin n))) (hsub : ∀ B ∈ todo, B ∈ family) :
    ∃ w f, LowerRealizes n hn w f ∧ MapsWithin f family ∧
      ConstantOnBlocks f todo := by
  induction todo with
  | nil =>
      refine ⟨[],id,?_,?_,?_⟩
      · intro P
        change some P = some _
        congr 1
        funext a
        simp [lowerRemap,id]
        intro h
        exact Prod.ext h rfl
      · exact fun _ _ _ ha => ha
      · intro B hB; simp at hB
  | cons B rest ih =>
      obtain ⟨w,f,hw,hwithin,hconst⟩ := ih (fun C hC => hsub C (by simp [hC]))
      have hBF := hsub B (by simp)
      obtain ⟨v,g,hv,⟨rep,hrep,hg⟩,hfix⟩ :=
        lower_safe_block_realizes n hn family B hBF (hne B hBF) hadm
      have hgw : MapsWithin g family := by
        intro C hC a ha
        by_cases he : C=B
        · subst C; rw [hg a ha]; exact hrep
        · have hnB : a ∉ B := fun h => he (hdisj C hC B hBF a ha h)
          rw [hfix a ⟨C,hC,ha⟩ hnB]; exact ha
      refine ⟨w++v,fun a => g (f a),hw.append hv,?_,?_⟩
      · intro C hC a ha
        exact hgw C hC (f a) (hwithin C hC a ha)
      · intro C hC a ha b hb
        change g (f a) = g (f b)
        rcases List.mem_cons.mp hC with he | he
        · subst C
          rw [hg (f a) (hwithin B hBF a ha),hg (f b) (hwithin B hBF b hb)]
        · exact congrArg g (hconst C he a ha b hb)

end RSR2.Parametric
