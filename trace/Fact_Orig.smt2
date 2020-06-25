(set-option :print-success false)
(set-info :smt-lib-version 2.6)
(set-option :smt.mbqi false)
(set-option :model.compact false)
(set-option :model.v2 true)
(set-option :pp.bv_literals false)
; done setting options


(declare-fun tickleBool (Bool) Bool)
(assert (and (tickleBool true) (tickleBool false)))
(declare-fun Fact (Int) Int)
(declare-fun Seven () Int)
(declare-fun Five () Int)
(assert (forall ((t Int) ) (!  (=> (= t 0) (= (Fact t) 1))
 :qid |FactOrig.615|
 :skolemid |0|
)))
(assert (forall ((t@@0 Int) ) (!  (=> (>= t@@0 0) (= (Fact t@@0) (* t@@0 (Fact (- t@@0 1)))))
 :qid |FactOrig.815|
 :skolemid |1|
)))
(assert (= Seven 7))
(assert (= Five 5))
(declare-fun ControlFlow (Int Int) Int)
(push 1)
(set-info :boogie-vc-id Test)
(assert (not
 (=> (= (ControlFlow 0 0) 102) (let ((anon0_correct  (=> (= (ControlFlow 0 71) (- 0 103)) (= (Fact 3) 6))))
(let ((PreconditionGeneratedEntry_correct  (=> (= (ControlFlow 0 102) 71) anon0_correct)))
PreconditionGeneratedEntry_correct)))
))
(check-sat)
(pop 1)
; Valid
