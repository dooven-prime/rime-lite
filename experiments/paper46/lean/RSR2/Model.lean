namespace RSR2

abbrev Packet := Nat

inductive Action where
  | p0 | p1 | d0 | d1 | v
  deriving DecidableEq, Repr

inductive Event where
  | vertical (packet : Packet)
  | fusion (layerOne : Bool) (left right child : Packet)
  deriving DecidableEq, Repr

structure Layer where
  s0 : Packet
  s1 : Packet
  s2 : Packet
  s3 : Packet
  deriving DecidableEq, Repr

structure RawState where
  l0 : Layer
  l1 : Layer
  events : List Event
  deriving DecidableEq, Repr

def Layer.rotate (x : Layer) : Layer :=
  ⟨x.s3, x.s0, x.s1, x.s2⟩

def Layer.collapse (x : Layer) (isLayerOne : Bool) : Layer × Option Event :=
  if x.s0 != 0 then
    if x.s1 != 0 then
      (⟨x.s0 ||| x.s1, 0, x.s2, x.s3⟩,
        some (.fusion isLayerOne x.s0 x.s1 (x.s0 ||| x.s1)))
    else
      (x, none)
  else if x.s1 != 0 then
    (⟨x.s1, 0, x.s2, x.s3⟩, none)
  else
    (x, none)

def packetOr (x : Layer) : Nat := x.s0 ||| x.s1 ||| x.s2 ||| x.s3

def boundedB (x : Layer) : Prop :=
  x.s0 ≤ 15 ∧ x.s1 ≤ 15 ∧ x.s2 ≤ 15 ∧ x.s3 ≤ 15

def disjointWithB (a b : Layer) : Prop :=
  (a.s0 &&& b.s0) = 0 ∧ (a.s0 &&& b.s1) = 0 ∧
  (a.s0 &&& b.s2) = 0 ∧ (a.s0 &&& b.s3) = 0 ∧
  (a.s1 &&& b.s0) = 0 ∧ (a.s1 &&& b.s1) = 0 ∧
  (a.s1 &&& b.s2) = 0 ∧ (a.s1 &&& b.s3) = 0 ∧
  (a.s2 &&& b.s0) = 0 ∧ (a.s2 &&& b.s1) = 0 ∧
  (a.s2 &&& b.s2) = 0 ∧ (a.s2 &&& b.s3) = 0 ∧
  (a.s3 &&& b.s0) = 0 ∧ (a.s3 &&& b.s1) = 0 ∧
  (a.s3 &&& b.s2) = 0 ∧ (a.s3 &&& b.s3) = 0

def validRaw (s : RawState) : Prop :=
  boundedB s.l0 ∧ boundedB s.l1 ∧ disjointWithB s.l0 s.l1 ∧
  (packetOr s.l0 ||| packetOr s.l1) = 15

instance validRawDecidable (s : RawState) : Decidable (validRaw s) := by
  unfold validRaw boundedB disjointWithB packetOr
  infer_instance

def addEvent (s : RawState) (e : Option Event) : List Event :=
  match e with
  | none => s.events
  | some event => s.events ++ [event]

def stepRaw (s : RawState) : Action → Option RawState
  | .p0 => some { s with l0 := s.l0.rotate }
  | .p1 => some { s with l1 := s.l1.rotate }
  | .d0 =>
      let result := s.l0.collapse false
      some { s with l0 := result.1, events := addEvent s result.2 }
  | .d1 =>
      let result := s.l1.collapse true
      some { s with l1 := result.1, events := addEvent s result.2 }
  | .v =>
      if s.l0.s0 != 0 && s.l1.s0 = 0 then
        some { s with
          l0 := ⟨0, s.l0.s1, s.l0.s2, s.l0.s3⟩
          l1 := ⟨s.l0.s0, s.l1.s1, s.l1.s2, s.l1.s3⟩
          events := s.events ++ [.vertical s.l0.s0] }
      else
        none

def replayRaw (s : RawState) : List Action → Option RawState
  | [] => some s
  | action :: rest => (stepRaw s action).bind (fun s' => replayRaw s' rest)

def seedRaw : RawState :=
  { l0 := ⟨1, 2, 4, 8⟩
    l1 := ⟨0, 0, 0, 0⟩
    events := [] }

def State := { s : RawState // validRaw s }

def seed : State := ⟨seedRaw, by decide⟩

def step (s : State) (action : Action) : Option State :=
  (stepRaw s.1 action).bind (fun t =>
    if h : validRaw t then some ⟨t, h⟩ else none)

def replay (s : State) : List Action → Option State
  | [] => some s
  | action :: rest => (step s action).bind (fun s' => replay s' rest)

def occupied (x : Layer) : Nat :=
  (if x.s0 != 0 then 1 else 0) +
  (if x.s1 != 0 then 1 else 0) +
  (if x.s2 != 0 then 1 else 0) +
  (if x.s3 != 0 then 1 else 0)

def layerRank (s : RawState) (layerOne : Bool) : Nat :=
  if layerOne then occupied s.l1 else occupied s.l0

def rawRank (s : RawState) : Nat := occupied s.l0 + occupied s.l1

theorem collapse_fusion_rank (x : Layer) (isLayerOne : Bool)
    (h0 : x.s0 ≠ 0) (h1 : x.s1 ≠ 0) :
    (x.collapse isLayerOne).1.s0 = x.s0 ||| x.s1 ∧
    (x.collapse isLayerOne).1.s1 = 0 := by
  simp [Layer.collapse, h0, h1]

theorem layer_zero_fusion_reduces_rank (s t : RawState) (h : stepRaw s .d0 = some t)
    (h0 : s.l0.s0 ≠ 0) (h1 : s.l0.s1 ≠ 0) :
    rawRank t = rawRank s - 1 := by
  have hor : s.l0.s0 ||| s.l0.s1 ≠ 0 := by
    simp [Nat.or_eq_zero_iff, h0, h1]
  simp [stepRaw, Layer.collapse, h0, h1] at h
  cases h
  simp [rawRank, occupied, hor, h0, h1]
  omega

theorem layer_one_fusion_reduces_rank (s t : RawState) (h : stepRaw s .d1 = some t)
    (h0 : s.l1.s0 ≠ 0) (h1 : s.l1.s1 ≠ 0) :
    rawRank t = rawRank s - 1 := by
  have hor : s.l1.s0 ||| s.l1.s1 ≠ 0 := by
    simp [Nat.or_eq_zero_iff, h0, h1]
  simp [stepRaw, Layer.collapse, h0, h1] at h
  cases h
  simp [rawRank, occupied, hor, h0, h1]
  omega

theorem vertical_step_preserves_atom_mask (s t : RawState)
    (h : stepRaw s .v = some t) :
    packetOr t.l0 ||| packetOr t.l1 = packetOr s.l0 ||| packetOr s.l1 := by
  by_cases hc : s.l0.s0 != 0 && s.l1.s0 = 0
  · simp [stepRaw, hc] at h
    cases h
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
    rcases hc with ⟨_, hzero⟩
    simp only [packetOr, hzero]
    ac_rfl
  · simp [stepRaw, hc] at h

end RSR2
