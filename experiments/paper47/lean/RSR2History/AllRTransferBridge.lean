import RSR2History.AllRLowerProjection

/-!
The complete log forces one transfer, after all lower fusions. The prefix
and its guarded state come from the same raw execution. Erasing only upper
letters and appending the physical phase tail yields the single-ring all-R
target, without a competitor normal-form or routing-cost assumption.
-/
namespace RSR2History.AllRTransfer

open RSR2.Parametric

theorem runLogged_transfer_count (n : Nat) (hn : 1 < n)
    {word : List Letter} {P Q : Placement n} {events : List (EffectiveEvent n)}
    (hexec : runLogged n hn P word = some (Q, events)) :
    logTransferCount events = word.count .v := by
  induction word generalizing P events with
  | nil =>
      have he : P = Q ∧ events = [] := by simpa [runLogged, eq_comm] using hexec
      simp [he.2, logTransferCount]
  | cons letter rest ih =>
      cases hs : step n hn P letter with
      | none => simp [runLogged, hs] at hexec
      | some R =>
          cases ht : runLogged n hn R rest with
          | none => simp [runLogged, hs, ht] at hexec
          | some result =>
              obtain ⟨S, later⟩ := result
              have he : S = Q ∧ emittedEvents n hn P letter ++ later = events := by
                simpa [runLogged, hs, ht] using hexec
              have hi := ih (by simpa [he.1] using ht)
              rw [← he.2, logTransferCount_append, hi]
              cases letter with
              | p layer => simp [emittedEvents, logTransferCount]
              | d layer => simp only [emittedEvents]; split <;> simp [logTransferCount]
              | v => simp [emittedEvents, logTransferCount, Nat.add_comm]

theorem noTransfers_iff (events : List (EffectiveEvent n)) :
    logTransferCount events = 0 ↔ ∀ packet, .transfer packet ∉ events := by
  induction events with
  | nil => simp [logTransferCount]
  | cons event rest ih =>
      cases event with
      | fusion layer A B C => simpa [logTransferCount] using ih
      | transfer A =>
          constructor
          · intro h
            simp [logTransferCount] at h
          · intro h
            exact (h A (by simp)).elim

private theorem first_vertical {word : List Letter} (hv : .v ∈ word) :
    ∃ pre post, word = pre ++ .v :: post ∧ .v ∉ pre := by
  induction word with
  | nil => simp at hv
  | cons letter rest ih =>
      by_cases he : letter = .v
      · exact ⟨[], rest, by simp [he], by simp⟩
      · have hr : .v ∈ rest := by simpa [Ne.symm he] using hv
        obtain ⟨pre, post, hw, hn⟩ := ih hr
        exact ⟨letter :: pre, post, by simp [hw], by simp [Ne.symm he, hn]⟩

private theorem split_before_transfer {n : Nat}
    {priorLog expected tail : List (EffectiveEvent n)} {packet full : Finset (Fin n)}
    (hp : ∀ A, .transfer A ∉ priorLog) (he : ∀ A, .transfer A ∉ expected)
    (h : priorLog ++ .transfer packet :: tail = expected ++ [.transfer full]) :
    priorLog = expected ∧ packet = full ∧ tail = [] := by
  induction expected generalizing priorLog with
  | nil =>
      cases priorLog with
      | nil => simpa using h
      | cons event rest =>
          have hx : event = .transfer full := (List.cons.inj h).1
          exact (hp full (by simp [hx])).elim
  | cons event rest ih =>
      cases priorLog with
      | nil =>
          have hx : .transfer packet = event := (List.cons.inj h).1
          exact (he packet (by simp [← hx])).elim
      | cons actual prior =>
          obtain ⟨hx, ht⟩ := List.cons.inj h
          obtain ⟨hpre, hpacket, htail⟩ := ih
            (fun A hA => hp A (by simp [hA])) (fun A hA => he A (by simp [hA])) ht
          exact ⟨by simp [hx, hpre], hpacket, htail⟩

def lowerTransferHistory {n : Nat} [NeZero n]
    (records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))) :
    List (EffectiveEvent n) := records.map lowerEvent ++ [.transfer Finset.univ]

@[simp] theorem lowerEvent_transfer_count {n : Nat} [NeZero n]
    (records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))) :
    logTransferCount (records.map lowerEvent) = 0 := by
  induction records with
  | nil => rfl
  | cons record rest ih => simpa [logTransferCount, lowerEvent] using ih

@[simp] theorem lowerTransferHistory_count {n : Nat} [NeZero n]
    (records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))) :
    logTransferCount (lowerTransferHistory records) = 1 := by
  rw [lowerTransferHistory, logTransferCount_append, lowerEvent_transfer_count]
  rfl

/-- The actual unique-transfer cut, including its guarded prefix and tail. -/
structure UniqueTransferPrefix {n : Nat} [NeZero n] (hn : 1 < n)
    (word : List Letter) (Q : Placement n)
    (records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))) where
  pre : List Letter
  post : List Letter
  before : Placement n
  after : Placement n
  word_eq : word = pre ++ .v :: post
  pre_no_transfer : .v ∉ pre
  post_no_transfer : .v ∉ post
  prefix_run : runLogged n hn (seed n) pre = some (before, records.map lowerEvent)
  transfer_step : step n hn before .v = some after
  source_full : packetAt before false (site0 n (by omega)) = Finset.univ
  tail_run : runLogged n hn after post = some (Q, [])

theorem uniqueTransferPrefix_of_runLogged {n : Nat} [NeZero n] (hn : 1 < n)
    {word : List Letter} {Q : Placement n}
    {records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))}
    (hexec : runLogged n hn (seed n) word = some (Q, lowerTransferHistory records)) :
    Nonempty (UniqueTransferPrefix hn word Q records) := by
  have hc : word.count .v = 1 := by
    simpa using (runLogged_transfer_count n hn hexec).symm
  have hv : .v ∈ word := by
    by_contra h
    have hz : word.count .v = 0 := List.count_eq_zero.mpr h
    omega
  obtain ⟨pre, post, hw, hnpre⟩ := first_vertical hv
  have hnpost : .v ∉ post := by
    have hz : pre.count .v = 0 := List.count_eq_zero.mpr hnpre
    rw [hw, List.count_append] at hc
    have hp : post.count .v = 0 := by simpa [hz] using hc
    exact List.count_eq_zero.mp hp
  cases hp : runLogged n hn (seed n) pre with
  | none => simp [hw, runLogged_append, hp] at hexec
  | some result =>
      obtain ⟨before, earlier⟩ := result
      cases hs : step n hn before .v with
      | none => simp [hw, runLogged_append, hp, runLogged, hs] at hexec
      | some after =>
          cases ht : runLogged n hn after post with
          | none => simp [hw, runLogged_append, hp, runLogged, hs, ht] at hexec
          | some result =>
              obtain ⟨last, later⟩ := result
              have he : last = Q ∧ earlier ++
                  .transfer (packetAt before false (site0 n (by omega))) :: later =
                    records.map lowerEvent ++ [.transfer Finset.univ] := by
                simpa [hw, runLogged_append, hp, runLogged, hs, ht, emittedEvents,
                  lowerTransferHistory] using hexec
              have hprezero : logTransferCount earlier = 0 := by
                rw [runLogged_transfer_count n hn hp, List.count_eq_zero.mpr hnpre]
              obtain ⟨hpre, hpacket, htail⟩ := split_before_transfer
                ((noTransfers_iff earlier).mp hprezero)
                ((noTransfers_iff _).mp (lowerEvent_transfer_count records)) he.2
              exact ⟨{
                pre := pre
                post := post
                before := before
                after := after
                word_eq := hw
                pre_no_transfer := hnpre
                post_no_transfer := hnpost
                prefix_run := by simpa [hpre] using hp
                transfer_step := hs
                source_full := hpacket
                tail_run := by simpa [he.1, htail] using ht }⟩

def allRHistory (n : Nat) [NeZero n] : List (EffectiveEvent n) :=
  lowerTransferHistory (FusionLogAllR.allRLog n)

/-- The erased prefix is a literal single-ring realization at site zero,
including the entire ordered log and not just the selected chain. -/
theorem UniqueTransferPrefix.lower_allR {n : Nat} [NeZero n] {hn : 1 < n}
    {word : List Letter} {Q : Placement n}
    (cut : UniqueTransferPrefix hn word Q (FusionLogAllR.allRLog n)) :
    FusionLogAllR.completeFusionLog (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n) (lowerWord cut.pre) =
        FusionLogAllR.allRLog n ∧
      (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n) (lowerWord cut.pre)).placed =
        (fun q => if q = 0 then some Finset.univ else none) := by
  obtain ⟨hview, hlog, _⟩ := lowerWord_simulation hn (FusionLogAllR.allRSelectedPair n)
    (allLower_seed n) cut.pre_no_transfer cut.prefix_run
    (RegisteredAbsorptionChains.singletonExecution n) lowerView_seed.symm
  exact ⟨by simpa using hlog, hview.trans (lowerView_full_zero hn cut.source_full)⟩

/-- The only added letters are the actual `n-1` rotations needed to match
the frozen all-R literal target. No physical step of the erased prefix is assumed. -/
theorem UniqueTransferPrefix.to_allR {n : Nat} [NeZero n] {hn : 1 < n}
    {word : List Letter} {Q : Placement n}
    (cut : UniqueTransferPrefix hn word Q (FusionLogAllR.allRLog n)) :
    FusionLogAllR.RealizesAllR (n := n)
      (lowerWord cut.pre ++ RegisteredAbsorptionChains.pWord (n - 1)) := by
  obtain ⟨hlog, hview⟩ := cut.lower_allR
  constructor
  · rw [FusionLogAllR.completeFusionLog_append, hlog]
    have ht := (FusionLogAllR.completeFusionLog_eq_nil_iff_fusionFree
      (FusionLogAllR.allRSelectedPair n)
      (RegisteredAbsorptionChains.run (FusionLogAllR.allRSelectedPair n)
        (RegisteredAbsorptionChains.singletonExecution n) (lowerWord cut.pre))
      (RegisteredAbsorptionChains.pWord (n - 1))).mpr
        (RegisteredAbsorptionChains.fusionFree_pWord _ _ _)
    simp [ht]
  · rw [RegisteredAbsorptionChains.run_append, RegisteredAbsorptionChains.run_pWord]
    funext q
    simp [RegisteredAbsorptionChains.rotate, hview, FusionLogAllR.allREndpoint, sub_eq_zero]

theorem UniqueTransferPrefix.projected_length_le {n : Nat} [NeZero n] {hn : 1 < n}
    {word : List Letter} {Q : Placement n}
    {records : List (RegisteredAbsorptionChains.FusionRecord (ZMod n))}
    (cut : UniqueTransferPrefix hn word Q records) :
    (lowerWord cut.pre).length + 1 ≤ word.length := by
  have h := lowerWord_length_le cut.pre
  have he := congrArg List.length cut.word_eq
  simp only [List.length_append, List.length_cons] at he
  omega

/-- Public bridge: every raw realization of this log yields its own actual
unique-transfer cut and an all-R word obtained by erasing upper letters. -/
theorem unique_transfer_prefix_to_allR {n : Nat} [NeZero n] (hn : 1 < n)
    {word : List Letter} {Q : Placement n}
    (hexec : runLogged n hn (seed n) word = some (Q, allRHistory n)) :
    ∃ cut : UniqueTransferPrefix hn word Q (FusionLogAllR.allRLog n),
      FusionLogAllR.RealizesAllR (n := n)
        (lowerWord cut.pre ++ RegisteredAbsorptionChains.pWord (n - 1)) ∧
      (lowerWord cut.pre).length + 1 ≤ word.length := by
  obtain ⟨cut⟩ := uniqueTransferPrefix_of_runLogged hn hexec
  exact ⟨cut, cut.to_allR, cut.projected_length_le⟩

/-- A consequence for every competing guarded raw word, independent of its
upper silent letters, intermediate placement choices or final silent tail. -/
theorem allRHistory_word_length_lower_bound {n : Nat} [NeZero n] (hn : 3 ≤ n)
    {word : List Letter} {Q : Placement n}
    (hexec : runLogged n (by omega) (seed n) word = some (Q, allRHistory n)) :
    (3 * n * (n - 1)) / 2 - n + 1 ≤ word.length := by
  obtain ⟨cut, hallR, hlen⟩ := unique_transfer_prefix_to_allR (by omega) hexec
  have h := hallR.word_length_lower_bound hn
  simp only [List.length_append, FusionLogCompression.pWord_length] at h
  omega

end RSR2History.AllRTransfer
