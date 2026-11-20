import RSR2History.EventResourceLedger
import RSR2History.ObservationForgettingCosts

/-!
Each layer's site 1 supplies an occupied source for an effective fusion.
A defect clears that source and a transfer acts only at site 0. Summing
the refill budget in the original guarded execution bounds partition cost.
-/
namespace RSR2History
open RSR2.Parametric

/-- One credit for each layer whose fusion source is occupied. -/
noncomputable def fusionSourceCredit (n : Nat) (hn : 1 < n)
    (P : Placement n) : Nat := by
  classical
  exact (if occupiedAt P false (site1 n hn) then 1 else 0) +
    (if occupiedAt P true (site1 n hn) then 1 else 0)

private theorem site0_ne_site1 (n : Nat) (hn : 1 < n) :
    site0 n (by omega) ≠ site1 n hn := by
  intro h
  have he := congrArg Fin.val h
  simp [site0, site1] at he

private theorem occupied_source_rotate_other (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer other : Layer) (hne : other ≠ layer) :
    occupiedAt (rotate n (by omega) P layer) other (site1 n hn) ↔
      occupiedAt P other (site1 n hn) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet rotate at ha
    split at ha
    · exact False.elim (hne (congrArg Prod.fst ha).symm)
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (other, site1 n hn) at ha
    exact ⟨a, by simp [packet, rotate, ha, hne]⟩

private theorem occupied_source_collapse_other (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer other : Layer) (hne : other ≠ layer) :
    occupiedAt (collapse n hn P layer) other (site1 n hn) ↔
      occupiedAt P other (site1 n hn) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet collapse at ha
    split at ha
    · exact False.elim (hne (congrArg Prod.fst ha).symm)
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (other, site1 n hn) at ha
    exact ⟨a, by simp [packet, collapse, ha, hne]⟩

private theorem collapse_source_empty (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) :
    ¬ occupiedAt (collapse n hn P layer) layer (site1 n hn) := by
  rintro ⟨a, ha⟩
  unfold packet collapse at ha
  split at ha
  · exact site0_ne_site1 n hn (congrArg Prod.snd ha)
  · contradiction

private theorem occupied_source_lift (n : Nat) (hn : 1 < n)
    (P : Placement n) (layer : Layer) :
    occupiedAt (liftPacket n (by omega) P) layer (site1 n hn) ↔
      occupiedAt P layer (site1 n hn) := by
  constructor
  · rintro ⟨a, ha⟩
    unfold packet liftPacket at ha
    split at ha
    · exact False.elim (site0_ne_site1 n hn (congrArg Prod.snd ha))
    · exact ⟨a, ha⟩
  · rintro ⟨a, ha⟩
    change P a = (layer, site1 n hn) at ha
    have hne : P a ≠ (false, site0 n (by omega)) := by
      intro he
      exact site0_ne_site1 n hn (congrArg Prod.snd (he.symm.trans ha))
    exact ⟨a, by simp only [packet, liftPacket, if_neg hne]; exact ha⟩

private def fusionSourceRotationCharge : Letter → Nat
  | .p _ => 1
  | _ => 0

private theorem step_fusionSource_bound (n : Nat) (hn : 1 < n)
    (P Q : Placement n) (letter : Letter) (hstep : step n hn P letter = some Q) :
    fusionSourceCredit n hn Q + logFusionCount (emittedEvents n hn P letter) ≤
      fusionSourceCredit n hn P + fusionSourceRotationCharge letter := by
  classical
  cases letter with
  | p layer =>
      have hQ : rotate n (by omega) P layer = Q := by
        simpa only [step_p, Option.some.injEq] using hstep
      subst Q
      cases layer
      all_goals
        simp only [fusionSourceCredit, emittedEvents, logFusionCount,
          List.map_nil, List.sum_nil, Nat.add_zero, fusionSourceRotationCharge]
      · rw [if_congr (occupied_source_rotate_other n hn P false true (by decide))
          rfl rfl]
        split <;> split <;> omega
      · rw [if_congr (occupied_source_rotate_other n hn P true false (by decide))
          rfl rfl]
        split <;> split <;> omega
  | d layer =>
      have hQ : collapse n hn P layer = Q := by
        simpa only [step_d, Option.some.injEq] using hstep
      subst Q
      have hempty := collapse_source_empty n hn P layer
      by_cases hsrc : occupiedAt P layer (site1 n hn) <;>
        by_cases htarget : occupiedAt P layer (site0 n (by omega)) <;>
        cases layer <;>
        simp [fusionSourceCredit, collapse_source_empty, occupied_source_collapse_other,
          emittedEvents, logFusionCount, fusionSourceRotationCharge, hsrc, htarget]
  | v =>
      obtain ⟨_, rfl⟩ := (step_v_eq_some_iff n hn P Q).mp hstep
      simp [fusionSourceCredit, occupied_source_lift, emittedEvents,
        logFusionCount, fusionSourceRotationCharge]

private theorem emitted_fusion_and_rotation_le_one (n : Nat) (hn : 1 < n)
    (P : Placement n) (letter : Letter) :
    logFusionCount (emittedEvents n hn P letter) +
      fusionSourceRotationCharge letter ≤ 1 := by
  classical
  cases letter with
  | p _ | v => simp [emittedEvents, logFusionCount, fusionSourceRotationCharge]
  | d layer =>
      by_cases hf : occupiedAt P layer (site0 n (by omega)) ∧
        occupiedAt P layer (site1 n hn) <;>
          simp [emittedEvents, hf, logFusionCount, fusionSourceRotationCharge]

/-- Each fusion uses one raw letter and one site-1 credit. The only steps
that can create credits are rotations, which use separate raw letters. -/
theorem runLogged_fusionSource_length_bound (n : Nat) (hn : 1 < n)
    (word : List Letter) {P Q : Placement n} {H : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, H)) :
    2 * logFusionCount H + fusionSourceCredit n hn Q ≤
      word.length + fusionSourceCredit n hn P := by
  induction word generalizing P H with
  | nil =>
      have he : P = Q ∧ H = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.1, he.2, logFusionCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases hr : runLogged n hn R rest with
          | none => simp [runLogged, hs, hr] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = H := by
                simpa [runLogged, hs, hr] using hexec
              have ht := ih (by simpa [he.1] using hr :
                runLogged n hn R rest = some (Q, later))
              have hf := step_fusionSource_bound n hn P R letter hs
              have hletter := emitted_fusion_and_rotation_le_one n hn P letter
              rw [← he.2, logFusionCount_append, List.length_cons]
              omega

@[simp] theorem fusionSourceCredit_seed (n : Nat) (hn : 1 < n) :
    fusionSourceCredit n hn (seed n) = 1 := by
  classical
  have h0 : occupiedAt (seed n) false (site1 n hn) := ⟨site1 n hn, rfl⟩
  have h1 : ¬ occupiedAt (seed n) true (site1 n hn) := by
    rintro ⟨a, ha⟩
    exact Bool.noConfusion (congrArg Prod.fst ha)
  simp [fusionSourceCredit, h0, h1]

/-- From the singleton seed, rank loss requires an effective fusion for
each removed packet and one refill per fusion beyond the initial credit. -/
theorem singleton_run_length_lower_bound_of_packet_rank (n : Nat) (hn : 1 < n)
    (word : List Letter) {Q : Placement n}
    (hrun : run n hn (seed n) word = some Q) :
    2 * (n - totalPacketCount Q) - 1 ≤ word.length := by
  obtain ⟨H, hlog⟩ := runLogged_exists_of_run n hn hrun
  have hcount := (runLogged_resource_balance n hn word hlog).1
  have hcost := runLogged_fusionSource_length_bound n hn word hlog
  rw [seed_totalPacketCount] at hcount
  rw [fusionSourceCredit_seed] at hcost
  omega

/-- The observer counts one block per occupied packet location. -/
theorem unorderedPacketBlocks_card_eq_totalPacketCount (n : Nat) (Q : Placement n) :
    (unorderedPacketBlocks n Q).card = totalPacketCount Q := by
  classical
  let live := Finset.univ.image Q
  have hrank : totalPacketCount Q = live.card := by
    rw [← Finset.length_toList]
    apply totalPacketCount_eq_representatives_length Q live.toList live.nodup_toList
    intro loc
    simp [live]
  have hblocks : unorderedPacketBlocks n Q =
      live.image (fun loc => packetAt Q loc.1 loc.2) := by
    rw [show live = Finset.univ.image Q from rfl, Finset.image_image]
    rfl
  rw [hblocks, hrank]
  apply Finset.card_image_of_injOn
  intro loc hloc loc' _ he
  obtain ⟨a, _, ha⟩ := Finset.mem_image.mp hloc
  have hamem : a ∈ packetAt Q loc.1 loc.2 :=
    (mem_packetAt Q loc.1 loc.2 a).mpr ha
  change packetAt Q loc.1 loc.2 = packetAt Q loc'.1 loc'.2 at he
  rw [he] at hamem
  exact ha.symm.trans ((mem_packetAt Q loc'.1 loc'.2 a).mp hamem)

/-- Rank loss gives a lower bound for the minimum over all realizations of
the same unordered partition. At rank `n` the bound is zero. -/
theorem partitionDistance_lower_bound_of_card (n : Nat) (hn : 1 < n)
    (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word) :
    2 * (n - π.card) - 1 ≤ partitionDistance n hn π attain := by
  obtain ⟨word, ⟨Q, hrun, hblocks⟩, hlen⟩ :=
    partitionDistance_attained n hn π attain
  have h := singleton_run_length_lower_bound_of_packet_rank n hn word hrun
  rwa [← unorderedPacketBlocks_card_eq_totalPacketCount n Q, hblocks, hlen] at h

/-- A loss of `k-1` packet blocks costs at least `2*k-3`, uniformly over
the atoms in those blocks and all allowed layers, phases and histories. -/
theorem partitionDistance_lower_bound_of_rank_drop
    (n : Nat) (hn : 1 < n) (π : Finset (Finset (Fin n)))
    (attain : ∃ word, RealizesUnorderedPartition n hn π word)
    (k : Nat) (hk : k ≤ n) (hcard : π.card = n - k + 1) :
    2 * k - 3 ≤ partitionDistance n hn π attain := by
  have h := partitionDistance_lower_bound_of_card n hn π attain
  rw [hcard] at h
  omega

end RSR2History
