import PaperXL.C1QuadraticRGT
import Lean.Data.Json

/-! Fixed consumer reads for the versioned finite runtime comparison.
The JSON representation below is an adapter, not a verified Python parser. -/

namespace PaperXL.ConcreteConsumer

open Lean RGTBoundedHistory

inductive Kind | origin | guard | parity | packet
  deriving DecidableEq, Repr

def environment (n : Nat) (hn : 3 ≤ n) : CircularEnvironment n n where
  hn := by omega
  hm_lower := by omega
  hm_le := le_refl _
  port0 := ⟨0, by omega⟩
  port1 := ⟨1, by omega⟩
  defect q := if q.val = 1 then ⟨0, by omega⟩ else q
  seed := id
  seed_injective := Function.injective_id
  ports_ne := by intro h; have := congrArg Fin.val h; simp at this
  ports_collide := by simp
  defect_fiber := by
    intro x y h
    by_cases hx : x.val = 1
    · by_cases hy : y.val = 1
      · exact Or.inl (Fin.ext (hx.trans hy.symm))
      · simp [hx, hy] at h
        exact Or.inr (Or.inr ⟨Fin.ext hx, h.symm⟩)
    · by_cases hy : y.val = 1
      · simp [hx, hy] at h
        exact Or.inr (Or.inl ⟨h, Fin.ext hy⟩)
      · exact Or.inl (by simpa [hx, hy] using h)

theorem environment_compatible (n : Nat) (hn : 3 ≤ n) :
    C1Compatible (environment n hn) where
  port0_val := rfl
  port1_val := rfl
  defect_eq := by
    funext q
    by_cases hq : q.val = 1 <;> simp [environment, c1Defect, Fin.ext_iff, hq]

def selected (k : Kind) (n : Nat) : List Nat :=
  match k with
  | .origin | .packet => List.range n
  | .guard | .parity => [0, 1]

def block {m : Nat} (e : EventCode m) (side : Fin 3) : List Nat :=
  (List.finRange m).filterMap fun i => if e i = side then some i.val else none

def contains (small big : List Nat) : Bool := small.all (fun i => big.contains i)

def fresh {m : Nat} (e : EventCode m) : List Nat :=
  (List.finRange m).filterMap fun i => if e i ≠ 2 then some i.val else none

def selectedHistory {m : Nat} (f : List Nat) :
    List (EventCode m) → Option (EventCode m × List (EventCode m))
  | [] => none
  | e :: es =>
      if fresh e = f then
        some (e, es.filter fun next => contains f (block next 0) || contains f (block next 1))
      else selectedHistory f es

def entries {n m : Nat} (s : CircularLogState n m) : List (Nat × List Nat) :=
  (List.range n).filterMap fun q =>
    let atoms := (List.finRange m).filterMap fun i => if (s.site i).val = q then some i.val else none
    if atoms.isEmpty then none else some (q, atoms)

def carrier {n m : Nat} (f : List Nat) (s : CircularLogState n m) : Option (Nat × List Nat) :=
  (entries s).find? (fun entry => contains f entry.2)

inductive Value where
  | null
  | nat (value : Nat)
  | bool (value : Bool)
  | text (value : String)
  | nil
  | cons (head tail : Value)
  | field (name : String) (value rest : Value)
  | array (items : Value)
  | object (fields : Value)
  deriving DecidableEq

def Value.items : Value → List Value
  | .cons x xs => x :: xs.items
  | _ => []

def Value.fields : Value → List (String × Value)
  | .field name value rest => (name, value) :: rest.fields
  | _ => []

def Value.arr (xs : List Value) : Value := .array (xs.foldr .cons .nil)
def Value.obj (xs : List (String × Value)) : Value :=
  .object (xs.foldr (fun (name, value) rest => .field name value rest) .nil)

partial def Value.json : Value → Json
  | .null => .null
  | .nat n => toJson n
  | .bool b => toJson b
  | .text s => toJson s
  | .array xs => Json.arr (xs.items.map Value.json).toArray
  | .object xs => Json.mkObj (xs.fields.map fun (name, value) => (name, value.json))
  | _ => .null

def array (xs : List Value) : Value := Value.arr xs
def naturals (xs : List Nat) : Value := array (xs.map Value.nat)
def entryJson (entry : Nat × List Nat) : Value := array [.nat entry.1, naturals entry.2]
def partitionJson {n m : Nat} (s : CircularLogState n m) : Value := array ((entries s).map entryJson)
def carrierJson {n m : Nat} (f : List Nat) (s : CircularLogState n m) : Value :=
  match carrier f s with
  | none => .null
  | some item => Value.obj [("some", entryJson item)]

def eventJson {m : Nat} (e : EventCode m) : Value := Value.obj [
  ("label", .text "d"), ("parents", array [entryJson (0, block e 0), entryJson (1, block e 1)]),
  ("target", .nat 0)]

def absorptionJson {m : Nat} (f : List Nat) (e : EventCode m) : Value :=
  let left := contains f (block e 0)
  Value.obj [("label", .text "d"), ("carrier_at", .nat (if left then 0 else 1)),
    ("carrier", naturals (block e (if left then 0 else 1))),
    ("partner_at", .nat (if left then 1 else 0)),
    ("partner", naturals (block e (if left then 1 else 0))),
    ("target", .nat 0), ("merged", naturals (fresh e))]

def commandCount : Kind → Nat | .origin => 0 | .parity => 1 | _ => 4
def commandLetter (k : Kind) (c : Fin (commandCount k)) : RawLetter :=
  if k = .parity then .d else if c.val < 2 then .p else .d

def enabled {n m : Nat} (k : Kind) (s : CircularLogState n m)
    (c : Fin (commandCount k)) : Bool :=
  if k = .parity then true else
    match carrier (selected k m) s with
    | none => false
    | some (q, _) =>
        let action := fun pos => if commandLetter k c = .p then (pos + 1) % n
          else if pos = 1 then 0 else pos
        let count := ((entries s).filter fun item => action item.1 = action q).length
        count == (if c.val % 2 = 0 then 1 else 2)

def candidate {n m : Nat} (k : Kind) (s : CircularLogState n m) : Value :=
  let f := selected k m
  match selectedHistory f s.events with
  | none => .null
  | some (o, history) =>
      let records := array (history.map (absorptionJson f))
      match k with
      | .origin | .packet => array [partitionJson s, naturals f]
      | .guard => array [naturals f, array [eventJson o, array [records, carrierJson f s]]]
      | .parity => .nat (history.length % 2)

def report {n m : Nat} (k : Kind) (s : CircularLogState n m) : Value :=
  let f := selected k m
  match selectedHistory f s.events with
  | none => .null
  | some (o, history) =>
      match k with
      | .origin => naturals (block o 0)
      | .guard => array [eventJson o, array [array (history.map (absorptionJson f)), carrierJson f s]]
      | .parity => .nat (history.length % 2)
      | .packet => partitionJson s

def consumer {n m : Nat} (E : CircularEnvironment n m) (k : Kind) :
    C1Consumer n m (Fin (commandCount k)) Value Value where
  domain s := (∃ w, (CircularConsumerBridge.completeSystem E).eval w = s) ∧
    (selectedHistory (selected k m) s.events).isSome = true
  candidate := candidate k
  report := report k
  enabled := enabled k
  letter := commandLetter k

theorem domainReachable {n m : Nat} (E : CircularEnvironment n m) (k : Kind) :
    (consumer E k).DomainReachable (CircularConsumerBridge.completeSystem E) := by
  intro s hs
  exact hs.1

def observation {n m : Nat} (k : Kind) (s : CircularLogState n m) : Json :=
  let f := selected k m
  let causal := match selectedHistory f s.events with
    | none => Value.null
    | some (o, history) => Value.obj [("partition", partitionJson s), ("selected", naturals f),
        ("origin", eventJson o), ("absorptions", array (history.map (absorptionJson f))),
        ("carrier", carrierJson f s)]
  let result := Value.obj [("site", naturals ((List.finRange m).map fun i => (s.site i).val)),
    ("events", array (s.events.map fun e => naturals ((List.finRange m).map fun i => (e i).val))),
    ("causal", causal), ("q", candidate k s), ("report", report k s),
    ("candidate_code", .text ((candidate k s).json.compress)),
    ("report_code", .text ((report k s).json.compress)),
    ("guards", if causal = Value.null then Value.null else
      array ((List.finRange (commandCount k)).map fun c => .bool (enabled k s c)))]
  result.json

end PaperXL.ConcreteConsumer
