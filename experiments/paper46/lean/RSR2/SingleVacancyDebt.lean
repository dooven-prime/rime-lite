import RSR2.ForcedPreparationDebts

/-!
# Endpoint-forced repeated vacancy debt

Only atom 1 is allowed to leave the lower layer.  All atoms remain in
different packets.  Before that deletion, every lower site is occupied.
After it, there is exactly one lower vacancy.  A productive lower defect
moves that vacancy from 0 to 1 and recreates an `n-1` rotation debt.

The certificate below is an observer of the original guarded executor; no
restriction is imposed on the word or its upper-layer scheduling.
-/

namespace RSR2.Parametric

/-- Forward distance of a vacancy to the sync port. -/
def vacancyReturnDebt (n : Nat) (h : Fin n) : Nat :=
  if h.val = 0 then 0 else n - h.val

/-- Positive circular distance from a vacancy to a retained anchor. -/
def vacancyAnchorGap (n : Nat) (h a : Fin n) : Nat :=
  if h.val ≤ a.val then a.val - h.val else n + a.val - h.val

theorem vacancyAnchorGap_rotate (n : Nat) (hn : 0 < n) (h a : Fin n) :
    vacancyAnchorGap n (next n hn h) (next n hn a) =
      vacancyAnchorGap n h a := by
  unfold vacancyAnchorGap
  by_cases hh : h.val + 1 < n <;> by_cases ha : a.val + 1 < n
  all_goals simp only [next, hh, ha, ↓reduceDIte, Fin.val_mk]
  all_goals split <;> (try split) <;> omega

theorem vacancyReturnDebt_rotate (n : Nat) (hn : 0 < n) (h : Fin n) :
    vacancyReturnDebt n h ≤ 1 + vacancyReturnDebt n (next n hn h) := by
  unfold vacancyReturnDebt
  by_cases hh : h.val + 1 < n
  all_goals simp only [next, hh, ↓reduceDIte, Fin.val_mk]
  all_goals split <;> split <;> omega

private theorem next_exists (n : Nat) (hn : 0 < n) (q : Fin n) :
    ∃ r, next n hn r = q := by
  by_cases hq : q.val = 0
  · refine ⟨⟨n - 1, by omega⟩, ?_⟩
    apply Fin.ext
    simp [next, show ¬ (n - 1 + 1 < n) by omega, hq]
  · refine ⟨⟨q.val - 1, by omega⟩, ?_⟩
    apply Fin.ext
    simp [next, show q.val - 1 + 1 < n by omega]
    omega

private theorem occupied_rotate_lower_next (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Fin n) :
    occupiedAt (rotate n hn P false) false (next n hn q) ↔
      occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    by_cases hl : (P a).1 = false
    · simp only [hl, if_true, Prod.mk.injEq, true_and] at ha
      exact ⟨a, Prod.ext hl (next_injective n hn ha)⟩
    · simp only [hl] at ha
      exact False.elim (hl (congrArg Prod.fst ha))
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, rotate, ha]⟩

private theorem step_lower_of_lower (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (a : Fin n)
    (hs : step n hn P letter = some Q) (hq : (Q a).1 = false) :
    (P a).1 = false := by
  cases letter with
  | p layer =>
      have he : Q = rotate n (by omega) P layer := by
        simpa only [step_p, Option.some.injEq] using hs.symm
      rw [he] at hq
      unfold rotate at hq
      split at hq <;> simp_all
  | d layer =>
      have he : Q = collapse n hn P layer := by
        simpa only [step_d, Option.some.injEq] using hs.symm
      rw [he] at hq
      unfold collapse at hq
      split at hq
      · rename_i hp
        have hl := congrArg Prod.fst hp
        exact hl.trans hq
      · exact hq
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
      unfold liftPacket at hq
      split at hq
      · contradiction
      · exact hq

theorem run_lower_of_terminal_lower (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter) (a : Fin n)
    (hrun : run n hn P word = some Q) (hq : (Q a).1 = false) :
    (P a).1 = false := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      exact he ▸ hq
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          exact step_lower_of_lower n hn P R letter a hs (ih R ht)

/-- Before the sole permitted transfer, or after it with its actual vacancy.
The full stage is not an assumed canonical placement: it permits any phase. -/
inductive SingleVacancyRep (n : Nat) (hn : 1 < n) (P : Placement n) where
  | full
      (lower : ∀ a, (P a).1 = false)
      (occupied : ∀ q, occupiedAt P false q)
      (adjacent : (P (site1 n hn)).2 =
        next n (by omega) (P (site0 n (by omega))).2)
  | deleted (hole : Fin n)
      (missing : ∀ q, occupiedAt P false q ↔ q ≠ hole)
      (upper : (P (site1 n hn)).1 = true)
      (lower : ∀ a, a ≠ site1 n hn → (P a).1 = false)

def SingleVacancyRep.debt {n : Nat} {hn : 1 < n} {P : Placement n} :
    SingleVacancyRep n hn P → Nat
  | .full _ _ _ => (n - 2) * (n - 1) +
      vacancyReturnDebt n (P (site1 n hn)).2
  | .deleted h _ _ _ =>
      (vacancyAnchorGap n h (P (site0 n (by omega))).2 - 1) * (n - 1) +
        vacancyReturnDebt n h

/-- Remaining productive vacancy moves, without counting ineffective defects. -/
def SingleVacancyRep.slidesRemaining {n : Nat} {hn : 1 < n} {P : Placement n} :
    SingleVacancyRep n hn P → Nat
  | .full _ _ _ => n - 2
  | .deleted h _ _ _ => vacancyAnchorGap n h (P (site0 n (by omega))).2 - 1

def SingleVacancyRep.transferRemaining {n : Nat} {hn : 1 < n} {P : Placement n} :
    SingleVacancyRep n hn P → Nat
  | .full _ _ _ => 1
  | .deleted _ _ _ _ => 0

/-- A rotation at the ready port cannot pay any outstanding debt. -/
def SingleVacancyRep.rotationPayment {n : Nat} {hn : 1 < n} {P : Placement n}
    (rep : SingleVacancyRep n hn P) (letter : Letter) : Nat :=
  if letter = .p false then
    match rep with
    | .full _ _ _ => if (P (site1 n hn)).2.val = 0 then 0 else 1
    | .deleted h _ _ _ => if h.val = 0 then 0 else 1
  else 0

/-- Counts precisely a lower `d` with its sole vacancy at port 0. -/
def SingleVacancyRep.slidePayment {n : Nat} {hn : 1 < n} {P : Placement n}
    (rep : SingleVacancyRep n hn P) (letter : Letter) : Nat :=
  if letter = .d false then
    match rep with
    | .full _ _ _ => 0
    | .deleted h _ _ _ => if h.val = 0 then 1 else 0
  else 0

private theorem vacancyReturnDebt_paid_rotate (n : Nat) (hn : 0 < n) (h : Fin n) :
    vacancyReturnDebt n h ≤ (if h.val = 0 then 0 else 1) +
      vacancyReturnDebt n (next n hn h) := by
  by_cases hh : h.val = 0
  · simp [vacancyReturnDebt, hh]
  · simpa [hh] using vacancyReturnDebt_rotate n hn h

theorem SingleVacancyRep.rotationPayment_le {n : Nat} {hn : 1 < n}
    {P : Placement n} (rep : SingleVacancyRep n hn P) (letter : Letter) :
    rep.rotationPayment letter ≤ lowerRotationCharge letter := by
  cases rep <;> simp only [rotationPayment, lowerRotationCharge]
  all_goals split <;> (try split) <;> omega

def singleton_singleVacancyRep (n : Nat) (hn : 1 < n) :
    SingleVacancyRep n hn (seed n) := by
  refine .full (fun _ => rfl) (fun q => ⟨q, rfl⟩) ?_
  exact (next_zero n hn).symm

private theorem upper_rotate_lower_packet (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Fin n) :
    occupiedAt (rotate n hn P true) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, rotate, ha]⟩

private theorem upper_collapse_lower_packet (n : Nat) (hn : 1 < n)
    (P : Placement n) (q : Fin n) :
    occupiedAt (collapse n hn P true) false q ↔ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, collapse, ha]⟩

private theorem collapse_lower_packet (n : Nat) (hn : 1 < n)
    (P : Placement n) (q : Fin n) :
    occupiedAt (collapse n hn P false) false q ↔
      (q = site0 n (by omega) ∧
        (occupiedAt P false (site0 n (by omega)) ∨
          occupiedAt P false (site1 n hn))) ∨
      (q ≠ site0 n (by omega) ∧ q ≠ site1 n hn ∧ occupiedAt P false q) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · rename_i hp
      have hq : q = site0 n (by omega) := (congrArg Prod.snd ha).symm
      exact Or.inl ⟨hq, Or.inr ⟨a, hp⟩⟩
    · rename_i hp
      by_cases hq : q = site0 n (by omega)
      · exact Or.inl ⟨hq, Or.inl ⟨a, by simpa [packet, hq] using ha⟩⟩
      · refine Or.inr ⟨hq, ?_, a, ha⟩
        intro hq1
        exact hp (by simpa [hq1] using ha)
  · rintro (⟨rfl, ha | ha⟩ | ⟨h0, h1, a, ha⟩)
    · obtain ⟨a, ha⟩ := ha
      change P a = (false, site0 n (by omega)) at ha
      exact ⟨a, by simp [packet, collapse, ha, site0, site1, Fin.mk.injEq]⟩
    · obtain ⟨a, ha⟩ := ha
      change P a = (false, site1 n hn) at ha
      exact ⟨a, by simp [packet, collapse, ha]⟩
    · change P a = (false, q) at ha
      exact ⟨a, by simp [packet, collapse, ha, h1]⟩

private theorem lift_lower_packet (n : Nat) (hn : 0 < n)
    (P : Placement n) (q : Fin n) :
    occupiedAt (liftPacket n hn P) false q ↔
      q ≠ site0 n hn ∧ occupiedAt P false q := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet liftPacket at ha
    split at ha
    · exact False.elim (Bool.noConfusion (congrArg Prod.fst ha))
    · rename_i hp
      exact ⟨fun hq => hp (by simpa [hq] using ha), a, ha⟩
  · rintro ⟨hq, a, ha⟩
    change P a = (false, q) at ha
    exact ⟨a, by simp [packet, liftPacket, ha, hq]⟩

private theorem lower_fusion_not_injective (n : Nat) (hn : 1 < n)
    (P : Placement n)
    (h0 : occupiedAt P false (site0 n (by omega)))
    (h1 : occupiedAt P false (site1 n hn)) :
    ¬ Function.Injective (collapse n hn P false) := by
  rintro hi
  obtain ⟨a, ha⟩ := h0
  obtain ⟨b, hb⟩ := h1
  change P a = (false, site0 n (by omega)) at ha
  change P b = (false, site1 n hn) at hb
  have he : collapse n hn P false a = collapse n hn P false b := by
    simp [collapse, ha, hb, site0, site1, Fin.mk.injEq]
  have hab := hi he
  have hv := congrArg (fun a => (P a).2.val) hab
  simp [ha, hb, site0, site1] at hv

/-- Every real successful step either preserves the outstanding debt or pays
at most one unit by `p0`.  Injectivity and retention are terminal obligations,
passed backwards from the same execution, not restrictions on a scheduler. -/
theorem singleVacancyRep_step_payments (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (rep : SingleVacancyRep n hn P)
    (hs : step n hn P letter = some Q)
    (hinj : Function.Injective Q)
    (hkeep : ∀ a, a ≠ site1 n hn → (Q a).1 = false) :
    ∃ nextRep : SingleVacancyRep n hn Q,
      rep.debt ≤ rep.rotationPayment letter + nextRep.debt ∧
      rep.slidesRemaining ≤ rep.slidePayment letter + nextRep.slidesRemaining ∧
      rep.transferRemaining = (if letter = .v then 1 else 0) +
        nextRep.transferRemaining := by
  have h01 : site0 n (by omega) ≠ site1 n hn := by
    simp [site0, site1, Fin.mk.injEq]
  cases rep with
  | full lower occupied adjacent =>
      cases letter with
      | p layer =>
          have he : Q = rotate n (by omega) P layer := by
            simpa only [step_p, Option.some.injEq] using hs.symm
          subst Q
          cases layer with
          | false =>
              have hl : ∀ a, (rotate n (by omega) P false a).1 = false := by
                intro a; simp [rotate, lower]
              have ho : ∀ q, occupiedAt (rotate n (by omega) P false) false q := by
                intro q
                obtain ⟨r, rfl⟩ := next_exists n (by omega) q
                exact (occupied_rotate_lower_next n (by omega) P r).mpr (occupied r)
              have ha : (rotate n (by omega) P false (site1 n hn)).2 =
                  next n (by omega) (rotate n (by omega) P false
                    (site0 n (by omega))).2 := by simp [rotate, lower, adjacent]
              refine ⟨.full hl ho ha, ?_, by simp [SingleVacancyRep.slidesRemaining,
                SingleVacancyRep.slidePayment], rfl⟩
              have hb := vacancyReturnDebt_paid_rotate n (by omega) (P (site1 n hn)).2
              dsimp [SingleVacancyRep.debt, SingleVacancyRep.rotationPayment, rotate]
              simp only [lower, if_true]
              omega
          | true =>
              have heq : rotate n (by omega) P true = P := by
                funext a; simp [rotate, lower]
              rw [heq]
              exact ⟨.full lower occupied adjacent,
                by simp [SingleVacancyRep.rotationPayment], by simp
                  [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment], rfl⟩
      | d layer =>
          have he : Q = collapse n hn P layer := by
            simpa only [step_d, Option.some.injEq] using hs.symm
          subst Q
          cases layer with
          | false =>
              exact False.elim
                (lower_fusion_not_injective n hn P (occupied _) (occupied _) hinj)
          | true =>
              have heq : collapse n hn P true = P := by
                funext a
                have hne : P a ≠ (true, site1 n hn) := by
                  intro h; have hh := congrArg Prod.fst h; simp [lower] at hh
                simp [collapse, hne]
              rw [heq]
              exact ⟨.full lower occupied adjacent,
                by simp [SingleVacancyRep.rotationPayment], by simp
                  [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment], rfl⟩
      | v =>
          obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
          obtain ⟨a, ha⟩ := hg.1
          change P a = (false, site0 n (by omega)) at ha
          have ha1 : a = site1 n hn := by
            by_cases he : a = site1 n hn
            · exact he
            · have hk := hkeep a he
              simp [liftPacket, ha] at hk
          subst a
          have hu : (liftPacket n (by omega) P (site1 n hn)).1 = true := by
            simp [liftPacket, ha]
          have hm : ∀ q, occupiedAt (liftPacket n (by omega) P) false q ↔
              q ≠ site0 n (by omega) := by
            intro q; simp [lift_lower_packet, occupied]
          have hanchor : (P (site0 n (by omega))).2.val = n - 1 := by
            have h : next n (by omega) (P (site0 n (by omega))).2 =
                site0 n (by omega) := adjacent.symm.trans (congrArg Prod.snd ha)
            have hv := congrArg Fin.val h
            unfold next at hv
            split at hv
            · have hb : (P (site0 n (by omega))).2.val + 1 = 0 := hv
              omega
            · omega
          have hstay : P (site0 n (by omega)) ≠ (false, site0 n (by omega)) := by
            intro h; have hh := congrArg (fun l => l.2.val) h
            change (P (site0 n (by omega))).2.val = 0 at hh
            omega
          have hloc : liftPacket n (by omega) P (site0 n (by omega)) =
              P (site0 n (by omega)) := by simp [liftPacket, hstay]
          have hgap : vacancyAnchorGap n (site0 n (by omega))
              (liftPacket n (by omega) P (site0 n (by omega))).2 = n - 1 := by
            rw [hloc]
            unfold vacancyAnchorGap
            change (if 0 ≤ (P (site0 n (by omega))).2.val then
              (P (site0 n (by omega))).2.val - 0 else
              n + (P (site0 n (by omega))).2.val - 0) = n - 1
            rw [if_pos (Nat.zero_le _)]
            change (P (site0 n (by omega))).2.val - 0 = n - 1
            omega
          have hd : vacancyReturnDebt n (P (site1 n hn)).2 = 0 := by
            rw [ha]; rfl
          refine ⟨.deleted (site0 n (by omega)) hm hu hkeep, ?_, ?_, rfl⟩
          · simp only [SingleVacancyRep.debt, hd, hgap]
            rw [show n - 1 - 1 = n - 2 by omega]
            simp [SingleVacancyRep.rotationPayment, vacancyReturnDebt, site0]
          · simp [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment,
              hgap, show n - 1 - 1 = n - 2 by omega]
  | deleted hole missing upper lower =>
      cases letter with
      | p layer =>
          have he : Q = rotate n (by omega) P layer := by
            simpa only [step_p, Option.some.injEq] using hs.symm
          subst Q
          cases layer with
          | false =>
              have hm : ∀ q, occupiedAt (rotate n (by omega) P false) false q ↔
                  q ≠ next n (by omega) hole := by
                intro q
                obtain ⟨r, rfl⟩ := next_exists n (by omega) q
                rw [occupied_rotate_lower_next, missing]
                exact not_congr ⟨fun h => congrArg (next n (by omega)) h,
                  fun h => next_injective n (by omega) h⟩
              refine ⟨.deleted (next n (by omega) hole) hm
                (by simp [rotate, upper]) hkeep, ?_, ?_, rfl⟩
              · have hb := vacancyReturnDebt_paid_rotate n (by omega) hole
                have hl := lower (site0 n (by omega)) h01
                simp only [SingleVacancyRep.debt, SingleVacancyRep.rotationPayment,
                  rotate, hl, if_true]
                rw [vacancyAnchorGap_rotate]
                omega
              · simp only [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment]
                simp [rotate, lower (site0 n (by omega)) h01, vacancyAnchorGap_rotate]
          | true =>
              have hm : ∀ q, occupiedAt (rotate n (by omega) P true) false q ↔
                  q ≠ hole := by intro q; rw [upper_rotate_lower_packet, missing]
              have hu : (rotate n (by omega) P true (site1 n hn)).1 = true := by
                simp [rotate, upper]
              refine ⟨.deleted hole hm hu hkeep, ?_, ?_, rfl⟩
              · simp [SingleVacancyRep.debt, SingleVacancyRep.rotationPayment, rotate,
                  lower (site0 n (by omega)) h01]
              · simp [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment,
                  rotate, lower (site0 n (by omega)) h01]
      | d layer =>
          have he : Q = collapse n hn P layer := by
            simpa only [step_d, Option.some.injEq] using hs.symm
          subst Q
          cases layer with
          | true =>
              have hm : ∀ q, occupiedAt (collapse n hn P true) false q ↔
                  q ≠ hole := by intro q; rw [upper_collapse_lower_packet, missing]
              have hu : (collapse n hn P true (site1 n hn)).1 = true := by
                unfold collapse; split <;> simp_all
              have hl := lower (site0 n (by omega)) h01
              have hne : P (site0 n (by omega)) ≠ (true, site1 n hn) := by
                intro h; have hh := congrArg Prod.fst h; simp [hl] at hh
              refine ⟨.deleted hole hm hu hkeep, ?_, ?_, rfl⟩
              · simp [SingleVacancyRep.debt, SingleVacancyRep.rotationPayment, collapse, hne]
              · simp [SingleVacancyRep.slidesRemaining, SingleVacancyRep.slidePayment,
                  collapse, hne]
          | false =>
              by_cases hz : hole = site0 n (by omega)
              · subst hole
                have hm : ∀ q, occupiedAt (collapse n hn P false) false q ↔
                    q ≠ site1 n hn := by
                  intro q
                  rw [collapse_lower_packet]
                  simp only [missing]
                  have h10 := Ne.symm h01
                  by_cases hq0 : q = site0 n (by omega) <;>
                    by_cases hq1 : q = site1 n hn <;> simp_all
                have hu : (collapse n hn P false (site1 n hn)).1 = true := by
                  simp [collapse, show P (site1 n hn) ≠
                    (false, site1 n hn) by
                      intro h; have hh := congrArg Prod.fst h; simp [upper] at hh,
                    upper]
                have hslides :
                    (SingleVacancyRep.deleted (site0 n (by omega)) missing upper lower).slidesRemaining ≤
                      (SingleVacancyRep.deleted (site0 n (by omega)) missing upper lower).slidePayment
                        (.d false) +
                      (SingleVacancyRep.deleted (site1 n hn) hm hu hkeep).slidesRemaining := by
                  change vacancyAnchorGap n (site0 n (by omega))
                      (P (site0 n (by omega))).2 - 1 ≤
                    1 + (vacancyAnchorGap n (site1 n hn)
                      (collapse n hn P false (site0 n (by omega))).2 - 1)
                  have hl := lower (site0 n (by omega)) h01
                  have hn0 : (P (site0 n (by omega))).2.val ≠ 0 := by
                    intro he
                    exact (missing _).mp ⟨_, Prod.ext hl (Fin.ext he)⟩ rfl
                  by_cases ha1 : P (site0 n (by omega)) = (false, site1 n hn)
                  · have he : vacancyAnchorGap n (site0 n (by omega))
                        (P (site0 n (by omega))).2 = 1 := by
                      rw [ha1]
                      simp [vacancyAnchorGap, site0, site1]
                    rw [he]
                    exact Nat.zero_le _
                  · have hn1 : (P (site0 n (by omega))).2.val ≠ 1 := by
                      intro he; exact ha1 (Prod.ext hl (Fin.ext he))
                    have hloc : collapse n hn P false (site0 n (by omega)) =
                        P (site0 n (by omega)) := by simp [collapse, ha1]
                    rw [hloc]
                    change (P (site0 n (by omega))).2.val - 1 ≤
                      1 + ((if 1 ≤ (P (site0 n (by omega))).2.val then
                        (P (site0 n (by omega))).2.val - 1 else
                        n + (P (site0 n (by omega))).2.val - 1) - 1)
                    rw [if_pos (show 1 ≤ (P (site0 n (by omega))).2.val by omega)]
                    omega
                refine ⟨.deleted (site1 n hn) hm hu hkeep, ?_, hslides, rfl⟩
                have hl := lower (site0 n (by omega)) h01
                have hnot0 : (P (site0 n (by omega))).2.val ≠ 0 := by
                  intro hval
                  have hloc : P (site0 n (by omega)) =
                      (false, site0 n (by omega)) := Prod.ext hl (Fin.ext hval)
                  exact (missing (site0 n (by omega))).mp ⟨_, hloc⟩ rfl
                by_cases ha1 : P (site0 n (by omega)) = (false, site1 n hn)
                · have hold : vacancyAnchorGap n (site0 n (by omega))
                      (P (site0 n (by omega))).2 = 1 := by
                    rw [ha1]
                    simp [vacancyAnchorGap, site0, site1]
                  simp only [SingleVacancyRep.debt, hold, Nat.sub_self,
                    Nat.zero_mul]
                  simp [vacancyReturnDebt, site0]
                · have hnot1 : (P (site0 n (by omega))).2.val ≠ 1 := by
                    intro hval; exact ha1 (Prod.ext hl (Fin.ext hval))
                  have hgt : 1 < (P (site0 n (by omega))).2.val := by omega
                  have he : (P (site0 n (by omega))).2.val - 1 =
                      ((P (site0 n (by omega))).2.val - 2) + 1 := by omega
                  have hloc : collapse n hn P false (site0 n (by omega)) =
                      P (site0 n (by omega)) := by simp [collapse, ha1]
                  have hold : vacancyAnchorGap n (site0 n (by omega))
                      (P (site0 n (by omega))).2 =
                      (P (site0 n (by omega))).2.val := by
                    unfold vacancyAnchorGap
                    change (if 0 ≤ (P (site0 n (by omega))).2.val then
                      (P (site0 n (by omega))).2.val - 0 else
                      n + (P (site0 n (by omega))).2.val - 0) = _
                    rw [if_pos (Nat.zero_le _)]
                    exact Nat.sub_zero _
                  have hnew : vacancyAnchorGap n (site1 n hn)
                      (collapse n hn P false (site0 n (by omega))).2 =
                      (P (site0 n (by omega))).2.val - 1 := by
                    rw [hloc]
                    unfold vacancyAnchorGap
                    change (if 1 ≤ (P (site0 n (by omega))).2.val then
                      (P (site0 n (by omega))).2.val - 1 else
                      n + (P (site0 n (by omega))).2.val - 1) = _
                    rw [if_pos (show 1 ≤ (P (site0 n (by omega))).2.val by omega)]
                  simp only [SingleVacancyRep.debt, hold, hnew]
                  have hsub : (P (site0 n (by omega))).2.val - 1 - 1 =
                      (P (site0 n (by omega))).2.val - 2 := by omega
                  rw [hsub]
                  have hmulteq : ((P (site0 n (by omega))).2.val - 1) * (n - 1) =
                      ((P (site0 n (by omega))).2.val - 2) * (n - 1) + (n - 1) := by
                    rw [he, Nat.add_mul, Nat.one_mul]
                  have hret0 : vacancyReturnDebt n (site0 n (by omega)) = 0 := rfl
                  have hret1 : vacancyReturnDebt n (site1 n hn) = n - 1 := rfl
                  simp only [hret0, hret1, show
                    (SingleVacancyRep.deleted (site0 n (by omega)) missing upper lower).rotationPayment
                      (.d false) = 0
                    from rfl, Nat.add_zero, Nat.zero_add]
                  exact Nat.le_of_eq hmulteq
              · by_cases ho : hole = site1 n hn
                · have heq : collapse n hn P false = P := by
                    funext a
                    have hne : P a ≠ (false, site1 n hn) := by
                      intro h; exact (missing (site1 n hn)).mp ⟨a, h⟩ ho.symm
                    simp [collapse, hne]
                  rw [heq]
                  exact ⟨.deleted hole missing upper lower,
                    by simp [SingleVacancyRep.rotationPayment],
                    by simp [SingleVacancyRep.slidesRemaining,
                      SingleVacancyRep.slidePayment, show hole.val ≠ 0 from
                        fun he => hz (Fin.ext he)], rfl⟩
                · exact False.elim (lower_fusion_not_injective n hn P
                    ((missing _).mpr (Ne.symm hz))
                    ((missing _).mpr (Ne.symm ho)) hinj)
      | v =>
          obtain ⟨hg, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hs
          obtain ⟨a, ha⟩ := hg.1
          change P a = (false, site0 n (by omega)) at ha
          have hne : a ≠ site1 n hn := by
            intro he; subst a; have hh := congrArg Prod.fst ha; simp [upper] at hh
          have hk := hkeep a hne
          simp [liftPacket, ha] at hk

/-- The earlier rotation-only interface remains available separately. -/
theorem singleVacancyRep_step (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter)
    (rep : SingleVacancyRep n hn P)
    (hs : step n hn P letter = some Q)
    (hinj : Function.Injective Q)
    (hkeep : ∀ a, a ≠ site1 n hn → (Q a).1 = false) :
    ∃ nextRep : SingleVacancyRep n hn Q,
      rep.debt ≤ lowerRotationCharge letter + nextRep.debt := by
  obtain ⟨nextRep, hb, _, _⟩ :=
    singleVacancyRep_step_payments n hn P Q letter rep hs hinj hkeep
  exact ⟨nextRep, Nat.le_trans hb (Nat.add_le_add_right
    (rep.rotationPayment_le letter) _)⟩

theorem singleVacancyRep_run (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (word : List Letter)
    (rep : SingleVacancyRep n hn P)
    (hrun : run n hn P word = some Q)
    (hinj : Function.Injective Q)
    (hkeep : ∀ a, a ≠ site1 n hn → (Q a).1 = false) :
    ∃ finalRep : SingleVacancyRep n hn Q,
      rep.debt ≤ lowerRotationCount word + finalRep.debt := by
  induction word generalizing P with
  | nil =>
      have he : P = Q := by simpa only [run, Option.some.injEq] using hrun
      subst Q
      exact ⟨rep, by simp [lowerRotationCount]⟩
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [run, hs] at hrun
      | some R =>
          have ht : run n hn R rest = some Q := by simpa [run, hs] using hrun
          have hiR := run_injective_of_terminal n hn R Q rest ht hinj
          have hkR : ∀ a, a ≠ site1 n hn → (R a).1 = false := by
            intro a ha
            exact run_lower_of_terminal_lower n hn R Q rest a ht (hkeep a ha)
          obtain ⟨nextRep, hstep⟩ := singleVacancyRep_step n hn P R letter rep hs hiR hkR
          obtain ⟨finalRep, htail⟩ := ih R nextRep ht
          refine ⟨finalRep, ?_⟩
          have hc : lowerRotationCount (letter :: rest) =
              lowerRotationCharge letter + lowerRotationCount rest := by
            simp [lowerRotationCount, lowerRotationCharge, List.count_cons,
              Nat.add_comm]
          rw [hc]
          omega

/-- Terminal allocation and phase requirements.  No history or preferred
intermediate placement is part of this predicate. -/
structure SingleVacancyTerminal (n : Nat) (hn : 1 < n) (Q : Placement n) : Prop where
  injective : Function.Injective Q
  upper : (Q (site1 n hn)).1 = true
  lower : ∀ a, a ≠ site1 n hn → (Q a).1 = false
  anchor : Q (site0 n (by omega)) = (false, site1 n hn)
  empty : ¬ occupiedAt Q false (site0 n (by omega))

theorem singleVacancyTerminal_debt_zero (n : Nat) (hn : 1 < n)
    (Q : Placement n) (terminal : SingleVacancyTerminal n hn Q)
    (rep : SingleVacancyRep n hn Q) : rep.debt = 0 := by
  cases rep with
  | full lower _ _ =>
      have hl := lower (site1 n hn)
      simp [terminal.upper] at hl
  | deleted hole missing _ _ =>
      have hh : hole = site0 n (by omega) := by
        by_cases he : hole = site0 n (by omega)
        · exact he
        · exact False.elim (terminal.empty ((missing _).mpr (Ne.symm he)))
      subst hole
      simp only [SingleVacancyRep.debt]
      rw [terminal.anchor]
      simp [vacancyAnchorGap, vacancyReturnDebt, site0, site1]

/-- A quadratic rotation lower bound forced by a literal endpoint.  It does
not give a lower bound on the diameter observed only through atom partitions. -/
theorem singleVacancyTerminal_rotation_lower_bound (n : Nat) (hn : 3 ≤ n)
    (Q : Placement n) (word : List Letter)
    (hrun : run n (by omega) (seed n) word = some Q)
    (terminal : SingleVacancyTerminal n (by omega) Q) :
    (n - 1) * (n - 1) ≤ lowerRotationCount word := by
  obtain ⟨finalRep, hb⟩ := singleVacancyRep_run n (by omega) (seed n) Q word
    (singleton_singleVacancyRep n (by omega)) hrun terminal.injective terminal.lower
  rw [singleVacancyTerminal_debt_zero n (by omega) Q terminal finalRep,
    Nat.add_zero] at hb
  have hi : (singleton_singleVacancyRep n (by omega)).debt =
      (n - 1) * (n - 1) := by
    change (n - 2) * (n - 1) + vacancyReturnDebt n (site1 n (by omega)) = _
    have hd : vacancyReturnDebt n (site1 n (by omega)) = n - 1 := rfl
    rw [hd]
    calc
      _ = (n - 2 + 1) * (n - 1) := by rw [Nat.add_mul, Nat.one_mul]
      _ = _ := by congr 1; omega
  rwa [hi] at hb

/-- Atom 1 above at 0; atom 0 below at 1; all other atoms below at their
original sites.  The only lower vacancy is site 0. -/
def singleVacancyEndpoint (n : Nat) (hn : 1 < n) : Placement n := fun a =>
  if a = site1 n hn then (true, site0 n (by omega))
  else if a = site0 n (by omega) then (false, site1 n hn)
  else (false, a)

theorem singleVacancyEndpoint_terminal (n : Nat) (hn : 1 < n) :
    SingleVacancyTerminal n hn (singleVacancyEndpoint n hn) := by
  have h01 : site0 n (by omega) ≠ site1 n hn := by
    simp [site0, site1, Fin.mk.injEq]
  constructor
  · intro a b hab
    unfold singleVacancyEndpoint at hab
    by_cases ha1 : a = site1 n hn <;> by_cases hb1 : b = site1 n hn <;>
      by_cases ha0 : a = site0 n (by omega) <;>
      by_cases hb0 : b = site0 n (by omega)
    all_goals simp_all
  · simp [singleVacancyEndpoint]
  · intro a ha
    unfold singleVacancyEndpoint
    rw [if_neg ha]
    split <;> rfl
  · simp [singleVacancyEndpoint, h01]
  · rintro ⟨a, ha⟩
    unfold packet singleVacancyEndpoint at ha
    by_cases ha1 : a = site1 n hn <;> by_cases ha0 : a = site0 n (by omega)
    all_goals simp_all

theorem singleVacancyEndpoint_rotation_lower_bound (n : Nat) (hn : 3 ≤ n)
    (word : List Letter)
    (hrun : run n (by omega) (seed n) word =
      some (singleVacancyEndpoint n (by omega))) :
    (n - 1) * (n - 1) ≤ lowerRotationCount word :=
  singleVacancyTerminal_rotation_lower_bound n hn _ word hrun
    (singleVacancyEndpoint_terminal n (by omega))

end RSR2.Parametric
