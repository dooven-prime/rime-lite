import PaperXL.ConcreteConsumer

namespace PaperXL.ConcreteConsumer

private def e3 := environment 3 (by decide)
private def e4 := environment 4 (by decide)
private def at3 (w : List RawLetter) := (CircularConsumerBridge.completeSystem e3).eval w
private def at4 (w : List RawLetter) := (CircularConsumerBridge.completeSystem e4).eval w

theorem origin_read_failure : ¬ (consumer e3 .origin).R := by
  intro hR
  have hx : (consumer e3 .origin).domain (at3 [.d, .p, .d]) :=
    ⟨⟨[.d, .p, .d], rfl⟩, by decide⟩
  have hy : (consumer e3 .origin).domain (at3 [.p, .d, .p, .d]) :=
    ⟨⟨[.p, .d, .p, .d], rfl⟩, by decide⟩
  have heq := hR _ _ ⟨hx, hy, by decide⟩
  exact (by decide : (consumer e3 .origin).report (at3 [.d, .p, .d]) ≠
    (consumer e3 .origin).report (at3 [.p, .d, .p, .d])) heq

theorem partition_guard_failure : ¬ (consumer e4 .guard).G := by
  intro hG
  have hx : (consumer e4 .guard).domain (at4 [.d]) := ⟨⟨[.d], rfl⟩, by decide⟩
  have hy : (consumer e4 .guard).domain (at4 [.d, .p, .p, .p, .d, .p]) :=
    ⟨⟨[.d, .p, .p, .p, .d, .p], rfl⟩, by decide⟩
  have heq := hG _ _ ⟨hx, hy, by decide⟩ ⟨2, by decide⟩
  exact (by decide : (consumer e4 .guard).enabled (at4 [.d]) ⟨2, by decide⟩ ≠
    (consumer e4 .guard).enabled (at4 [.d, .p, .p, .p, .d, .p]) ⟨2, by decide⟩) heq

theorem parity_successor_failure :
    ¬ (consumer e4 .parity).T (CircularLogState.rawSystem e4) := by
  intro hT
  have hx : (consumer e4 .parity).domain (at4 [.d]) := ⟨⟨[.d], rfl⟩, by decide⟩
  have hy : (consumer e4 .parity).domain (at4 [.d, .p]) := ⟨⟨[.d, .p], rfl⟩, by decide⟩
  have heq := hT _ _ ⟨hx, hy, by decide⟩ ⟨0, by decide⟩ (by decide) (by decide)
  exact (by decide : (consumer e4 .parity).candidate
      ((CircularLogState.rawSystem e4).step (at4 [.d]) .d) ≠
    (consumer e4 .parity).candidate
      ((CircularLogState.rawSystem e4).step (at4 [.d, .p]) .d)) heq

end PaperXL.ConcreteConsumer
