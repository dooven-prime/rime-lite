import PaperXL.ConcreteConsumer

open Lean PaperXL PaperXL.ConcreteConsumer

def decodeWord (text : String) : Except String (List RawLetter) :=
  text.toList.mapM fun c => match c with
    | 'p' => pure .p
    | 'd' => pure .d
    | _ => throw "word must contain only p and d"

def replayInput (input : Json) : Except String Json := do
  let kind ← (← input.getObjVal? "case").getStr?
  let word ← decodeWord (← (← input.getObjVal? "word").getStr?)
  let result ← match kind with
    | "R" => pure (observation .origin (RawSystem.run (CircularLogState.rawSystem (environment 3 (by decide))) word))
    | "P" => pure (observation .packet (RawSystem.run (CircularLogState.rawSystem (environment 3 (by decide))) word))
    | "G" => pure (observation .guard (RawSystem.run (CircularLogState.rawSystem (environment 4 (by decide))) word))
    | "T" => pure (observation .parity (RawSystem.run (CircularLogState.rawSystem (environment 4 (by decide))) word))
    | _ => throw "unknown fixed consumer case"
  pure result

def main : IO Unit := do
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    match Json.parse line >>= replayInput with
    | .error message => throw (IO.userError message)
    | .ok result => stdout.putStrLn result.compress
