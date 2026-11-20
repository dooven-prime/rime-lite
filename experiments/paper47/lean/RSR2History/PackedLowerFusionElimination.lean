import RSR2History.PackedLowerMinimum
import RSR2History.PackedLowerShadow
import RSR2History.PackedLowerPrefixOrder
import RSR2History.PackedLowerFusionMacro

/-! First-fusion refinement and its cost-preserving path interfaces. -/
namespace RSR2History
open RSR2.Parametric

def singletonLowerLog (z : List (Fin n)) : List (EffectiveEvent n) :=
  z.map (fun a => .transfer {a})

@[simp] theorem singletonLowerLog_append (u v : List (Fin n)) :
    singletonLowerLog (u++v) = singletonLowerLog u ++ singletonLowerLog v := by
  simp [singletonLowerLog]

@[simp] theorem singletonLowerLog_fusionCount (z : List (Fin n)) :
    logFusionCount (singletonLowerLog z) = 0 := by
  induction z with
  | nil => rfl
  | cons a z ih => simpa [singletonLowerLog, logFusionCount] using ih

theorem lowerPacket_eq_singleton_of_valid {c : LowerConfiguration n}
    (valid : c.Valid) {q : Fin n} {a : Fin n} (ha : c a = some q) :
    lowerPacket c q = {a} := by
  ext b
  simp only [lowerPacket, Finset.mem_filter, Finset.mem_univ, true_and,
    Finset.mem_singleton]
  exact ⟨fun hb => valid b a q hb ha, fun h => h ▸ ha⟩

theorem lowerErasePacket_singleton (c : LowerConfiguration n) (a : Fin n) :
    lowerErasePacket c {a} = lowerDelete c a := by
  funext b
  simp [lowerErasePacket, lowerDelete]

/-- Pure singleton paths embed into the packed contract with unchanged
cost, recording each actual singleton deletion as a whole-packet event. -/
theorem LowerExtractionPath.toPacked {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) :
    PackedLowerPath n hn c (singletonLowerLog z) d cost := by
  induction path with
  | refl c => exact .prepare (.refl c)
  | rotate c => exact .prepare (.rotate c)
  | slide c empty occupied => exact .prepare (.slide c empty occupied)
  | delete c a atPort singleton =>
      have hp : lowerPacket c (site0 n (by omega)) = {a} := by
        ext b
        simp only [lowerPacket, Finset.mem_filter, Finset.mem_univ, true_and,
          Finset.mem_singleton]
        exact ⟨singleton b, fun h => h ▸ atPort⟩
      have he := PackedLowerEvent.extract (hn := hn) c (show (lowerPacket c (site0 n (by omega))).Nonempty by
        rw [hp]; simp)
      simpa [hp, lowerErasePacket_singleton, singletonLowerLog] using
        (PackedLowerPath.event he)
  | trans first second ih₁ ih₂ =>
      simpa only [singletonLowerLog_append] using ih₁.trans ih₂

/-- With no effective fusion, the packed model is precisely singleton
extraction whenever the initial configuration is injective. -/
theorem PackedLowerPath.noFusion_singleton {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost) (valid : c.Valid)
    (hzero : logFusionCount H = 0) :
    ∃ z, H = singletonLowerLog z ∧ LowerExtractionPath n hn c z d cost := by
  induction path with
  | prepare path => exact ⟨[], rfl, path⟩
  | @event c d e cost step =>
      cases step with
      | fusion left right => simp [logFusionCount] at hzero
      | extract nonempty =>
          obtain ⟨a, ha⟩ := nonempty
          have hat : c a = some (site0 n (by omega)) := by simpa [lowerPacket] using ha
          have hp := lowerPacket_eq_singleton_of_valid valid hat
          refine ⟨[a], by simp [singletonLowerLog, hp], ?_⟩
          rw [hp, lowerErasePacket_singleton]
          exact .delete c a hat (fun b hb => valid b a _ hb hat)
  | trans first second ih₁ ih₂ =>
      simp only [logFusionCount_append] at hzero
      obtain ⟨u, hu, pu⟩ := ih₁ valid (by omega)
      obtain ⟨v, hv, pv⟩ := ih₂ (pu.valid valid) (by omega)
      exact ⟨u++v, by simp [hu, hv], pu.trans pv⟩

theorem LowerExtractionPath.deleted_was_live {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) :
    ∀ a ∈ z, c a ≠ none := by
  induction path with
  | refl => simp
  | rotate => simp
  | slide => simp
  | delete c a atPort singleton =>
      intro b hb
      have hb : b = a := by simpa using hb
      subst b
      simp [atPort]
  | trans first second ih₁ ih₂ =>
      intro a ha
      rcases List.mem_append.mp ha with ha | ha
      · exact ih₁ a ha
      · exact ((first.support a).mp (ih₂ a ha)).1

theorem LowerExtractionPath.deleted_nodup {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn c z d cost) : z.Nodup := by
  induction path with
  | refl => simp
  | rotate => simp
  | slide => simp
  | delete => simp
  | trans first second ih₁ ih₂ =>
      apply List.nodup_append.mpr
      refine ⟨ih₁, ih₂, ?_⟩
      intro a ha b hb hab
      subst b
      have hlive := second.deleted_was_live a hb
      exact ((first.support a).mp hlive).2 ha

/-- Ending empty from the full seed makes the singleton deletion order a
full permutation, independently of any supplied order certificate. -/
theorem LowerExtractionPath.full_order {n : Nat} {hn : 1 < n}
    {z : List (Fin n)} {cost : Nat}
    (path : LowerExtractionPath n hn (lowerExtractionSeed n) z
      (lowerExtractionEmpty n) cost) : z.length = n ∧ z.Nodup := by
  classical
  have hnd := path.deleted_nodup
  have hcover : ∀ a, a ∈ z := by
    intro a
    have hs := path.support a
    simp only [lowerExtractionEmpty, ne_eq, not_true_eq_false, lowerExtractionSeed,
      Option.some_ne_none, not_false_eq_true, true_and, false_iff, not_not] at hs
    exact hs
  have hset : z.toFinset = Finset.univ := by ext a; simp [hcover a]
  have hc := congrArg Finset.card hset
  rw [List.toFinset_card_of_nodup hnd] at hc
  exact ⟨by simpa using hc, hnd⟩


theorem PackedLowerEvent.transfer_spec {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {B : Finset (Fin n)} {cost : Nat}
    (step : PackedLowerEvent n hn c (.transfer B) d cost) :
    lowerPacket c (site0 n (by omega)) = B ∧ B.Nonempty ∧
      d = lowerErasePacket c B ∧ cost = 0 := by
  cases step with
  | extract nonempty => exact ⟨rfl,nonempty,rfl,rfl⟩

/-- Split a prescribed singleton transfer prefix, retaining its exact pure
lower path and the remainder of the original packed event list. -/
theorem PackedLowerPath.split_singleton_prefix {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {z : List (Fin n)}
    {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c (singletonLowerLog z ++ H) d cost) :
    ∃ mid prep rest, LowerExtractionPath n hn c z mid prep ∧
      PackedLowerPath n hn mid H d rest ∧ cost = prep+rest := by
  induction z generalizing c cost with
  | nil => exact ⟨c,0,cost,.refl c,by simpa [singletonLowerLog] using path,by omega⟩
  | cons a z ih =>
      obtain ⟨mid,next,prep,charge,rest,before,step,after,hcost⟩ :=
        path.split_first_event (.transfer {a}) (singletonLowerLog z ++ H)
          (by simp [singletonLowerLog])
      obtain ⟨hp,_,hd,hcharge⟩ := step.transfer_spec
      have hat : mid a = some (site0 n (by omega)) := by
        have : a ∈ lowerPacket mid (site0 n (by omega)) := by rw [hp]; simp
        simpa [lowerPacket] using this
      have hsingle : ∀ b, mid b = some (site0 n (by omega)) → b = a := by
        intro b hb
        have : b ∈ lowerPacket mid (site0 n (by omega)) := by simpa [lowerPacket] using hb
        simpa [hp] using this
      rw [hd,lowerErasePacket_singleton] at after
      obtain ⟨last,p,q,first,tail,htotal⟩ := ih after
      refine ⟨last,prep+p,q,?_,tail,by omega⟩
      have path' := (before.trans (.delete mid a hat hsingle)).trans first
      simpa only [List.nil_append, List.singleton_append, Nat.add_zero] using path'

/-- Before the first packed fusion all live packets are singleton. This
statement extracts the actual pure prefix, not a chosen replacement layout. -/
theorem PackedLowerPath.first_fusion_singletons {n : Nat} {hn : 1 < n}
    {c d : LowerConfiguration n} {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn c H d cost) (valid : c.Valid)
    (positive : 0 < logFusionCount H) :
    ∃ z mid a b tail prep rest,
      H = singletonLowerLog z ++ .fusion false {a} {b} ({a} ∪ {b}) :: tail ∧
      LowerExtractionPath n hn c z mid prep ∧
      mid a = some (site0 n (by omega)) ∧ mid b = some (site1 n hn) ∧ a ≠ b ∧
      PackedLowerPath n hn (lowerSlide n hn mid) tail d rest := by
  induction H generalizing c cost with
  | nil => simp [logFusionCount] at positive
  | cons e H ih =>
      obtain ⟨mid,next,prep,charge,rest,before,step,after,hcost⟩ :=
        path.split_first_event e H rfl
      have vm := before.valid valid
      cases step with
      | fusion left right =>
          obtain ⟨a,ha⟩ := left
          obtain ⟨b,hb⟩ := right
          have ha : mid a = some (site0 n (by omega)) := by simpa [lowerPacket] using ha
          have hb : mid b = some (site1 n hn) := by simpa [lowerPacket] using hb
          have hpa := lowerPacket_eq_singleton_of_valid vm ha
          have hpb := lowerPacket_eq_singleton_of_valid vm hb
          have hab : a ≠ b := by
            intro he
            subst b
            have := ha.symm.trans hb
            simp [site0,site1,Fin.ext_iff] at this
          exact ⟨[],mid,a,b,H,prep,rest,by simp [singletonLowerLog,hpa,hpb],
            before,ha,hb,hab,after⟩
      | extract nonempty =>
          obtain ⟨a,ha⟩ := nonempty
          have ha : mid a = some (site0 n (by omega)) := by simpa [lowerPacket] using ha
          have hp := lowerPacket_eq_singleton_of_valid vm ha
          have del : LowerExtractionPath n hn mid [a] (lowerDelete mid a) 0 :=
            .delete mid a ha (fun b hb => vm b a _ hb ha)
          simp only [hp,lowerErasePacket_singleton] at after
          obtain ⟨z,last,b,e,tail,p,q,hlog,first,hb,he,hbe,remaining⟩ :=
            ih after (del.valid vm) (by simpa [logFusionCount] using positive)
          refine ⟨a::z,last,b,e,tail,prep+p,q,?_,?_,hb,he,hbe,remaining⟩
          · simpa [singletonLowerLog,hp] using congrArg (fun L =>
              EffectiveEvent.transfer ({a} : Finset (Fin n)) :: L) hlog
          · simpa only [List.nil_append,List.singleton_append,Nat.add_zero] using
              (before.trans del).trans first

/-- Refine the first fusion by extracting its right singleton and erasing it
from every later packet field. This changes only the auxiliary comparison
log; the original log is recovered by the lifting theorem below. -/
def firstFusionRefinedLog (z : List (Fin n)) (b : Fin n)
    (tail : List (EffectiveEvent n)) : List (EffectiveEvent n) :=
  singletonLowerLog z ++ .transfer {b} :: tail.map (eraseLowerEvent b)

private theorem firstFusion_cohabiting {n : Nat} {hn : 1 < n}
    {c : LowerConfiguration n} {a b : Fin n}
    (ha : c a = some (site0 n (by omega))) (hb : c b = some (site1 n hn)) :
    lowerSlide n hn c a = lowerSlide n hn c b := by
  have hsites : (site0 n (by omega) : Fin n) ≠ site1 n hn := by
    simp [site0,site1,Fin.ext_iff]
  simp [lowerSlide,ha,hb,hsites]

/-- The refined log is feasible before its minimum is ever used. -/
theorem firstFusionRefinedLog_feasible {n : Nat} {hn : 1 < n}
    {z : List (Fin n)} {c : LowerConfiguration n} {a b : Fin n}
    {tail : List (EffectiveEvent n)} {prep rest : Nat}
    (initialPath : LowerExtractionPath n hn (lowerExtractionSeed n) z c prep)
    (ha : c a = some (site0 n (by omega))) (hb : c b = some (site1 n hn))
    (hab : a ≠ b)
    (after : PackedLowerPath n hn (lowerSlide n hn c) tail (lowerExtractionEmpty n) rest) :
    ∃ cost, PackedLowerPath n hn (lowerExtractionSeed n) (firstFusionRefinedLog z b tail)
      (lowerExtractionEmpty n) cost := by
  have : NeZero n := ⟨by omega⟩
  have valid := initialPath.valid (lowerExtractionSeed_valid n)
  have refined := packedLower_refine_first_fusion_path hn c b valid hb
  have erased := after.erase_cohabiting a b hab (firstFusion_cohabiting ha hb)
  rw [lowerDelete_lowerSlide_of_right_singleton hn c b valid hb, lowerDelete_empty] at erased
  exact ⟨prep+n+rest,by simpa [firstFusionRefinedLog,List.append_assoc] using
    (initialPath.toPacked.trans refined).trans erased⟩

/-- Any implementation of the feasible refined log lifts to the exact
original lower log, at additive cost at most `2*n-1`. Its literal tail and
ordered event fields are recovered by shadow simulation. -/
theorem firstFusionRefinedLog_lift {n : Nat} {hn : 1 < n}
    {z : List (Fin n)} {c : LowerConfiguration n} {a b : Fin n}
    {tail : List (EffectiveEvent n)} {prep rest refinedCost : Nat}
    (initialPath : LowerExtractionPath n hn (lowerExtractionSeed n) z c prep)
    (ha : c a = some (site0 n (by omega))) (hb : c b = some (site1 n hn))
    (hab : a ≠ b)
    (after : PackedLowerPath n hn (lowerSlide n hn c) tail (lowerExtractionEmpty n) rest)
    (refined : PackedLowerPath n hn (lowerExtractionSeed n) (firstFusionRefinedLog z b tail)
      (lowerExtractionEmpty n) refinedCost) :
    ∃ cost, PackedLowerPath n hn (lowerExtractionSeed n)
      (singletonLowerLog z ++ .fusion false {a} {b} ({a} ∪ {b}) :: tail)
      (lowerExtractionEmpty n) cost ∧ cost ≤ refinedCost+(2*n-1) := by
  have : NeZero n := ⟨by omega⟩
  obtain ⟨mid,p,q,before,remaining,hcost⟩ := refined.split_singleton_prefix
  obtain ⟨ready,next,turns,charge,last,silent,step,endPath,hremaining⟩ :=
    remaining.split_first_event (.transfer {b}) (tail.map (eraseLowerEvent b)) rfl
  obtain ⟨hpacket,_,hnext,hcharge⟩ := step.transfer_spec
  have hbready : ready b = some (site0 n (by omega)) := by
    have : b ∈ lowerPacket ready (site0 n (by omega)) := by rw [hpacket]; simp
    simpa [lowerPacket] using this
  have beforeReady : LowerExtractionPath n hn (lowerExtractionSeed n) z ready (p+turns) := by
    simpa only [List.append_nil] using before.trans silent
  have valid := beforeReady.valid (lowerExtractionSeed_valid n)
  obtain ⟨site,hasite,hnzero,holes⟩ := initialPath.same_prefix_fusion_gap beforeReady ha hb hbready
  have hpA := lowerPacket_eq_singleton_of_valid valid hasite
  have hpB := lowerPacket_eq_singleton_of_valid valid hbready
  have hsite : site.val ≠ 0 := by
    intro he
    exact hnzero (Fin.ext (by simpa [site0] using he))
  have holePackets : ∀ r : Fin n, site.val < r.val → lowerPacket ready r = ∅ := by
    intro r hr
    ext x
    simp [lowerPacket,holes r hr x]
  obtain ⟨macroCost,macroPath,macroBound⟩ := packedLowerFusionMacro_path hn ready site hsite
    (hpA.symm ▸ Finset.singleton_nonempty a) (hpB.symm ▸ Finset.singleton_nonempty b) holePackets
  have htarget : lowerRelocatePort n hn ready site = lowerShadow a b (lowerDelete ready b) := by
    funext x
    by_cases hx : x = b
    · subst x
      simp [lowerRelocatePort,lowerShadow,lowerDelete,hab,hbready,hasite]
    · have hxport : ready x ≠ some (site0 n (by omega)) := by
        intro hx0
        exact hx (valid x b _ hx0 hbready)
      simp [lowerRelocatePort,lowerShadow,lowerDelete,hx,hxport]
  rw [hpA,hpB,htarget] at macroPath
  rw [hnext,lowerErasePacket_singleton] at endPath
  have shadowTail := endPath.shadow a b hab (by simp)
  have recovered := after.shadow_erase_log a b hab (firstFusion_cohabiting ha hb)
  rw [recovered,lowerShadow_empty] at shadowTail
  refine ⟨p+turns+macroCost+last,?_,by omega⟩
  simpa [List.append_assoc,Nat.add_assoc] using
    (beforeReady.toPacked.trans macroPath).trans shadowTail

/-- Every positive-fusion feasible log has a feasible refinement with one
fewer fusion, and its minimum rises by at most the single local macro cost. -/
theorem packedLowerCost_first_fusion_elimination {n : Nat} {hn : 1 < n}
    {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn (lowerExtractionSeed n) H (lowerExtractionEmpty n) cost)
    (positive : 0 < logFusionCount H) :
    ∃ H', (∃ c', PackedLowerPath n hn (lowerExtractionSeed n) H' (lowerExtractionEmpty n) c') ∧
      logFusionCount H = logFusionCount H'+1 ∧
      packedLowerCost n hn H ≤ packedLowerCost n hn H'+(2*n-1) := by
  obtain ⟨z,c,a,b,tail,prep,rest,hlog,initialPath,ha,hb,hab,after⟩ :=
    path.first_fusion_singletons (lowerExtractionSeed_valid n) positive
  let H' := firstFusionRefinedLog z b tail
  have feasible := firstFusionRefinedLog_feasible initialPath ha hb hab after
  refine ⟨H',feasible,?_,?_⟩
  · have hcons : logFusionCount (.fusion false {a} {b} ({a} ∪ {b}) :: tail) =
        1+logFusionCount tail := rfl
    have htrans : logFusionCount (.transfer {b} :: tail.map (eraseLowerEvent b)) =
        logFusionCount (tail.map (eraseLowerEvent b)) := by simp [logFusionCount]
    rw [hlog]
    simp only [H',firstFusionRefinedLog,logFusionCount_append,
      singletonLowerLog_fusionCount,hcons,htrans,logFusionCount_map_eraseLowerEvent]
    omega
  · obtain ⟨newCost,newPath,bound⟩ := firstFusionRefinedLog_lift initialPath ha hb hab after
      (packedLowerCost_attained feasible)
    rw [← hlog] at newPath
    exact (packedLowerCost_le newPath).trans bound

/-- Iterated elimination retains an actual full extraction permutation,
rather than using `K_n` as an unexplained cost for packed extraction. -/
theorem packedLowerCost_le_extraction_add_fusions {n : Nat} {hn : 1 < n}
    {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn (lowerExtractionSeed n) H (lowerExtractionEmpty n) cost) :
    ∃ z : List (Fin n), z.length = n ∧ z.Nodup ∧
      packedLowerCost n hn H ≤ lowerExtractionCost n hn z+(2*n-1)*logFusionCount H := by
  generalize hcount : logFusionCount H = r
  induction r using Nat.strong_induction_on generalizing H cost with
  | h r ih =>
      by_cases hzero : r = 0
      · obtain ⟨z,hlog,pure⟩ := path.noFusion_singleton
          (lowerExtractionSeed_valid n) (by omega)
        obtain ⟨hlen,hnd⟩ := pure.full_order
        have best := lowerExtractionCost_attained_of_permutation (hn := hn) hlen hnd
        refine ⟨z,hlen,hnd,?_⟩
        have hp : packedLowerCost n hn H ≤ lowerExtractionCost n hn z := by
          rw [hlog]
          exact packedLowerCost_le best.toPacked
        simpa [hcount,hzero] using hp
      · obtain ⟨H',⟨c',refined⟩,hcounts,hbound⟩ :=
          packedLowerCost_first_fusion_elimination path (by omega)
        obtain ⟨z,hlen,hnd,hrec⟩ := ih (logFusionCount H') (by omega) refined rfl
        refine ⟨z,hlen,hnd,?_⟩
        calc
          packedLowerCost n hn H ≤ packedLowerCost n hn H'+(2*n-1) := hbound
          _ ≤ lowerExtractionCost n hn z+(2*n-1)*logFusionCount H'+(2*n-1) := by omega
          _ = lowerExtractionCost n hn z+(2*n-1)*logFusionCount H := by
            rw [hcounts,Nat.mul_add,Nat.mul_one]
            omega
          _ = lowerExtractionCost n hn z+(2*n-1)*r := by rw [hcount]

/-- Uniform lower fusion elimination. No original silent cost and no upper
fusion-tree classification is used in this bound. -/
theorem packedLowerCost_le_max_add_fusions {n : Nat} {hn : 1 < n}
    {H : List (EffectiveEvent n)} {cost : Nat}
    (path : PackedLowerPath n hn (lowerExtractionSeed n) H (lowerExtractionEmpty n) cost) :
    packedLowerCost n hn H ≤ maxLowerExtractionCost n hn+(2*n-1)*logFusionCount H := by
  obtain ⟨z, hlen, hnd, hcost⟩ := packedLowerCost_le_extraction_add_fusions path
  exact hcost.trans (Nat.add_le_add_right (lowerExtractionCost_le_max (hn := hn) hlen hnd) _)

end RSR2History
