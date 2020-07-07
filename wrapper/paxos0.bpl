// Boogie program verifier version 2.6.16.0, Copyright (c) 2003-2014, Microsoft.
// Command Line Options: Paxos.bpl PaxosSeqAxioms.bpl PaxosActions.bpl PaxosAbstractions.bpl PaxosSeq.bpl

const numNodes: int;

axiom numNodes > 0;

type Round = int;

function Round(x: int) : bool;

axiom (forall x: int :: {:qid "quantifier0"} { Round(x): bool } Round(x): bool == (1 <= x));

type Node = int;

function Node(x: int) : bool;

axiom (forall x: int :: {:qid "quantifier1"} { Node(x): bool } Node(x): bool == (1 <= x && x <= numNodes));

type NodeSet = [Node]bool;

type Value;

type {:datatype} OptionValue;

function {:constructor} SomeValue(value: Value) : OptionValue;

function {:constructor} NoneValue() : OptionValue;

type {:datatype} OptionVoteInfo;

function {:constructor} NoneVoteInfo() : OptionVoteInfo;

function {:constructor} SomeVoteInfo(value: Value, ns: NodeSet) : OptionVoteInfo;

type {:datatype} AcceptorState;

function {:constructor} AcceptorState(lastJoinRound: Round, lastVoteRound: int, lastVoteValue: Value) : AcceptorState;

type {:datatype} JoinResponse;

function {:constructor} JoinResponse(from: Node, lastVoteRound: int, lastVoteValue: Value) : JoinResponse;

type {:datatype} JoinResponseChannel;

function {:constructor} JoinResponseChannel(domain: [Permission]bool, contents: [Permission]JoinResponse) : JoinResponseChannel;

type {:datatype} VoteResponse;

function {:constructor} VoteResponse(from: Node) : VoteResponse;

type {:datatype} VoteResponseChannel;

function {:constructor} VoteResponseChannel(domain: [Permission]bool, contents: [Permission]VoteResponse) : VoteResponseChannel;

type {:datatype} Permission;

function {:constructor} JoinPerm(r: Round, n: Node) : Permission;

function {:constructor} VotePerm(r: Round, n: Node) : Permission;

function {:constructor} ConcludePerm(r: Round) : Permission;

type {:pending_async} {:datatype} PA;

function {:pending_async "A_StartRound"} {:constructor} StartRound_PA(round: Round, round_lin: Round) : PA;

function {:pending_async "A_Join"} {:constructor} Join_PA(round: Round, node: Node, p: Permission) : PA;

function {:pending_async "A_Propose"} {:constructor} Propose_PA(round: Round, ps: [Permission]bool) : PA;

function {:pending_async "A_Vote"} {:constructor} Vote_PA(round: Round, node: Node, value: Value, p: Permission) : PA;

function {:pending_async "A_Conclude"} {:constructor} Conclude_PA(round: Round, value: Value, p: Permission) : PA;

function {:builtin "MapConst"} MapConstPermission(bool) : [Permission]bool;

function {:builtin "MapOr"} MapOrPermission([Permission]bool, [Permission]bool) : [Permission]bool;

function {:builtin "MapConst"} MapConstNode(bool) : NodeSet;

function {:builtin "MapOr"} MapOrNode(NodeSet, NodeSet) : NodeSet;

function {:builtin "MapAnd"} MapAndNode(NodeSet, NodeSet) : NodeSet;

function {:builtin "MapImp"} MapImpNode(NodeSet, NodeSet) : NodeSet;

function {:builtin "MapConst"} MapConstPA(int) : [PA]int;

function {:builtin "MapAdd"} MapAddPA([PA]int, [PA]int) : [PA]int;

function {:builtin "MapSub"} MapSubPA([PA]int, [PA]int) : [PA]int;

function {:builtin "MapConst"} MapConstBool(bool) : [Permission]bool;

function {:builtin "MapOr"} MapOr([Permission]bool, [Permission]bool) : [Permission]bool;

function {:builtin "MapConst"} MapConstVoteResponse(int) : [VoteResponse]int;

function {:builtin "MapAdd"} MapAddVoteResponse([VoteResponse]int, [VoteResponse]int) : [VoteResponse]int;

function {:builtin "MapSub"} MapSubVoteResponse([VoteResponse]int, [VoteResponse]int) : [VoteResponse]int;

function {:inline} NoPAs() : [PA]int
{
  MapConstPA(0)
}

function {:inline} SingletonPA(pa: PA) : [PA]int
{
  NoPAs()[pa := 1]
}

function {:inline} NoNodes() : NodeSet
{
  MapConstNode(false)
}

function {:inline} SingletonNode(node: Node) : NodeSet
{
  NoNodes()[node := true]
}

function Cardinality(q: NodeSet) : int;

axiom Cardinality(NoNodes()) == 0;

function {:inline} IsQuorum(ns: NodeSet) : bool
{
  2 * Cardinality(ns) > numNodes && (forall n: Node :: {:qid "quantifier2"} ns[n] ==> Node(n))
}

function {:inline} IsSubset(ns1: NodeSet, ns2: NodeSet) : bool
{
  MapImpNode(ns1, ns2) == MapConstNode(true)
}

function {:inline} IsDisjoint(ns1: NodeSet, ns2: NodeSet) : bool
{
  MapAndNode(ns1, ns2) == MapConstNode(false)
}

function MaxRound(r: Round, ns: NodeSet, voteInfo: [Round]OptionVoteInfo) : int;

axiom (forall r: Round, ns: NodeSet, voteInfo: [Round]OptionVoteInfo :: {:qid "quantifier3"} { MaxRound(r, ns, voteInfo) } Round(r) ==> (var ret := MaxRound(r, ns, voteInfo); 0 <= ret && ret < r && (forall r': Round :: {:qid "quantifier4"} ret < r' && r' < r && is#SomeVoteInfo(voteInfo[r']) ==> IsDisjoint(ns, ns#SomeVoteInfo(voteInfo[r']))) && (Round(ret) ==> is#SomeVoteInfo(voteInfo[ret]) && !IsDisjoint(ns, ns#SomeVoteInfo(voteInfo[ret])))));

function {:inline} Lemma_MaxRound_InitVote(voteInfo: [Round]OptionVoteInfo, r: Round, r': Round) : bool
{
  (forall ns: NodeSet, v': Value :: {:qid "quantifier5"} is#NoneVoteInfo(voteInfo[r']) ==> MaxRound(r, ns, voteInfo) == MaxRound(r, ns, voteInfo[r' := SomeVoteInfo(v', NoNodes())]))
}

function {:inline} Lemma_MaxRound_AddNodeToVote(voteInfo: [Round]OptionVoteInfo, r: Round, r': Round, n: Node) : bool
{
  (forall ns: NodeSet :: {:qid "quantifier6"} is#SomeVoteInfo(voteInfo[r']) && (!ns[n] || r <= r') ==> (var v', ns' := value#SomeVoteInfo(voteInfo[r']), ns#SomeVoteInfo(voteInfo[r']); MaxRound(r, ns, voteInfo) == MaxRound(r, ns, voteInfo[r' := SomeVoteInfo(v', ns'[n := true])])))
}

function {:inline} JoinPermissions(r: Round) : [Permission]bool
{
  (lambda p: Permission :: {:qid "quantifier7"} (if is#JoinPerm(p) && r#JoinPerm(p) == r then true else false))
}

function {:inline} ProposePermissions(r: Round) : [Permission]bool
{
  (lambda p: Permission :: {:qid "quantifier8"} (if (is#VotePerm(p) && r#VotePerm(p) == r) || (is#ConcludePerm(p) && r#ConcludePerm(p) == r) then true else false))
}

function {:inline} VotePermissions(r: Round) : [Permission]bool
{
  (lambda p: Permission :: {:qid "quantifier9"} (if is#VotePerm(p) && r#VotePerm(p) == r then true else false))
}

function {:inline} JoinPAs(r: Round) : [PA]int
{
  (lambda pa: PA :: {:qid "quantifier10"} (if is#Join_PA(pa) && round#Join_PA(pa) == r && Node(node#Join_PA(pa)) && p#Join_PA(pa) == JoinPerm(r, node#Join_PA(pa)) then 1 else 0))
}

function {:inline} VotePAs(r: Round, v: Value) : [PA]int
{
  (lambda pa: PA :: {:qid "quantifier11"} (if is#Vote_PA(pa) && round#Vote_PA(pa) == r && Node(node#Vote_PA(pa)) && value#Vote_PA(pa) == v && p#Vote_PA(pa) == VotePerm(r, node#Vote_PA(pa)) then 1 else 0))
}

var {:layer 1, 3} joinedNodes: [Round]NodeSet;

var {:layer 1, 3} voteInfo: [Round]OptionVoteInfo;

var {:layer 1, 3} pendingAsyncs: [PA]int;

var {:layer 0, 1} acceptorState: [Node]AcceptorState;

var {:layer 0, 1} joinChannel: [Round][JoinResponse]int;

var {:layer 0, 1} voteChannel: [Round][VoteResponse]int;

var {:layer 0, 3} decision: [Round]OptionValue;

var {:layer 1, 1} {:linear "perm"} permJoinChannel: JoinResponseChannel;

var {:layer 1, 1} {:linear "perm"} permVoteChannel: VoteResponseChannel;

function {:inline} Init(rs: [Round]bool, joinedNodes: [Round]NodeSet, voteInfo: [Round]OptionVoteInfo, decision: [Round]OptionValue, pendingAsyncs: [PA]int) : bool
{
  rs == (lambda r: Round :: {:qid "quantifier12"} true) && (forall r: Round :: {:qid "quantifier13"} joinedNodes[r] == NoNodes()) && (forall r: Round :: {:qid "quantifier14"} is#NoneVoteInfo(voteInfo[r])) && (forall r: Round :: {:qid "quantifier15"} is#NoneValue(decision[r])) && (forall pa: PA :: {:qid "quantifier16"} pendingAsyncs[pa] == 0)
}

function {:inline} InitLow(acceptorState: [Node]AcceptorState, joinChannel: [Round][JoinResponse]int, voteChannel: [Round][VoteResponse]int, permJoinChannel: JoinResponseChannel, permVoteChannel: VoteResponseChannel) : bool
{
  (forall n: Node :: {:qid "quantifier17"} lastJoinRound#AcceptorState(acceptorState[n]) == 0 && lastVoteRound#AcceptorState(acceptorState[n]) == 0) && (forall r: Round, jr: JoinResponse :: {:qid "quantifier18"} joinChannel[r][jr] == 0) && (forall r: Round, vr: VoteResponse :: {:qid "quantifier19"} voteChannel[r][vr] == 0) && domain#JoinResponseChannel(permJoinChannel) == MapConstPermission(false) && domain#VoteResponseChannel(permVoteChannel) == MapConstPermission(false)
}

function {:inline} {:linear "perm"} PermissionCollector(p: Permission) : [Permission]bool
{
  MapConstBool(false)[p := true]
}

function {:inline} {:linear "perm"} PermissionSetCollector(ps: [Permission]bool) : [Permission]bool
{
  ps
}

function {:inline} {:linear "perm"} RoundCollector(round: Round) : [Permission]bool
{
  (lambda p: Permission :: {:qid "quantifier20"} (if (is#JoinPerm(p) && round == r#JoinPerm(p)) || (is#VotePerm(p) && round == r#VotePerm(p)) || (is#ConcludePerm(p) && round == r#ConcludePerm(p)) then true else false))
}

function {:inline} {:linear "perm"} RoundSetCollector(rounds: [Round]bool) : [Permission]bool
{
  (lambda p: Permission :: {:qid "quantifier21"} (if (is#JoinPerm(p) && rounds[r#JoinPerm(p)]) || (is#VotePerm(p) && rounds[r#VotePerm(p)]) || (is#ConcludePerm(p) && rounds[r#ConcludePerm(p)]) then true else false))
}

function {:inline} {:linear "perm"} JoinResponseChannelCollector(permJoinChannel: JoinResponseChannel) : [Permission]bool
{
  domain#JoinResponseChannel(permJoinChannel)
}

function {:inline} {:linear "perm"} VoteResponseChannelCollector(permVoteChannel: VoteResponseChannel) : [Permission]bool
{
  domain#VoteResponseChannel(permVoteChannel)
}

function triggerRound(r: Round) : bool;

axiom (forall r: Round :: {:qid "quantifier22"} { triggerRound(r): bool } triggerRound(r): bool == true);

function triggerNode(n: Node) : bool;

axiom (forall n: Node :: {:qid "quantifier23"} { triggerNode(n): bool } triggerNode(n): bool == true);



















































function {:inline} {:lemma} {:commutativity "A_Propose", "A_Propose'"} CommutativityLemma_A_Propose_A_Propose'(voteInfo: [Round]OptionVoteInfo, first_r: Round, second_r: Round) : bool
{
  Lemma_MaxRound_InitVote(voteInfo, first_r, second_r) && Lemma_MaxRound_InitVote(voteInfo, second_r, first_r)
}

function {:inline} {:lemma} {:commutativity "A_Vote", "A_Propose'"} CommutativityLemma_A_Vote_A_Propose'(voteInfo: [Round]OptionVoteInfo, first_r: Round, second_r: Round, first_n: Node) : bool
{
  Lemma_MaxRound_AddNodeToVote(voteInfo, second_r, first_r, first_n)
}

function {:inline} {:lemma} {:commutativity "A_Propose", "A_Vote'"} CommutativityLemma_A_Propose_A_Vote'(voteInfo: [Round]OptionVoteInfo, first_r: Round, second_r: Round, second_n: Node) : bool
{
  Lemma_MaxRound_AddNodeToVote(voteInfo, first_r, second_r, second_n)
}

axiom (forall ns1: NodeSet, ns2: NodeSet :: {:qid "quantifier24"} { IsQuorum(ns1), IsQuorum(ns2) } IsQuorum(ns1) && IsQuorum(ns2) ==> (exists n: Node :: {:qid "quantifier25"} Node(n) && ns1[n] && ns2[n]));

procedure {:atomic} {:layer 2} A_StartRound(r: Round, {:linear_in "perm"} r_lin: Round) returns ({:pending_async "A_Join", "A_Propose"} PAs: [PA]int);
  modifies pendingAsyncs;



implementation {:atomic} {:layer 2} A_StartRound(r: Round, r_lin: Round) returns (PAs: [PA]int)
{
    assert r == r_lin;
    assert Round(r);
    assert pendingAsyncs[StartRound_PA(r, r_lin)] > 0;
    PAs := MapAddPA(JoinPAs(r), SingletonPA(Propose_PA(r, ProposePermissions(r))));
    pendingAsyncs := MapAddPA(pendingAsyncs, PAs);
    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(StartRound_PA(r, r_lin)));
}



procedure {:atomic} {:layer 2} A_Propose(r: Round, {:linear_in "perm"} ps: [Permission]bool) returns ({:pending_async "A_Vote", "A_Conclude"} PAs: [PA]int);
  modifies voteInfo, pendingAsyncs;



implementation {:atomic} {:layer 2} A_Propose(r: Round, ps: [Permission]bool) returns (PAs: [PA]int)
{
  var maxRound: int;
  var maxValue: Value;
  var ns: NodeSet;

    assert Round(r);
    assert pendingAsyncs[Propose_PA(r, ps)] > 0;
    assert ps == ProposePermissions(r);
    assert is#NoneVoteInfo(voteInfo[r]);
    if (*)
    {
        assume IsSubset(ns, joinedNodes[r]) && IsQuorum(ns);
        maxRound := MaxRound(r, ns, voteInfo);
        if (maxRound != 0)
        {
            maxValue := value#SomeVoteInfo(voteInfo[maxRound]);
        }

        voteInfo[r] := SomeVoteInfo(maxValue, NoNodes());
        PAs := MapAddPA(VotePAs(r, maxValue), SingletonPA(Conclude_PA(r, maxValue, ConcludePerm(r))));
    }
    else
    {
        PAs := NoPAs();
    }

    pendingAsyncs := MapAddPA(pendingAsyncs, PAs);
    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Propose_PA(r, ps)));
}



procedure {:atomic} {:layer 2} A_Conclude(r: Round, v: Value, {:linear_in "perm"} p: Permission);
  modifies decision, pendingAsyncs;



implementation {:atomic} {:layer 2} A_Conclude(r: Round, v: Value, p: Permission)
{
  var q: NodeSet;

    assert Round(r);
    assert pendingAsyncs[Conclude_PA(r, v, p)] > 0;
    assert p == ConcludePerm(r);
    assert is#SomeVoteInfo(voteInfo[r]);
    assert value#SomeVoteInfo(voteInfo[r]) == v;
    if (*)
    {
        assume IsSubset(q, ns#SomeVoteInfo(voteInfo[r])) && IsQuorum(q);
        decision[r] := SomeValue(v);
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Conclude_PA(r, v, p)));
}



procedure {:atomic} {:layer 2} A_Join(r: Round, n: Node, {:linear_in "perm"} p: Permission);
  modifies joinedNodes, pendingAsyncs;



implementation {:atomic} {:layer 2} A_Join(r: Round, n: Node, p: Permission)
{
    assert Round(r);
    assert pendingAsyncs[Join_PA(r, n, p)] > 0;
    assert p == JoinPerm(r, n);
    if (*)
    {
        assume (forall r': Round :: {:qid "quantifier26"} Round(r') && joinedNodes[r'][n] ==> r' < r);
        joinedNodes[r][n] := true;
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Join_PA(r, n, p)));
}



procedure {:atomic} {:layer 2} A_Vote(r: Round, n: Node, v: Value, {:linear_in "perm"} p: Permission);
  modifies joinedNodes, voteInfo, pendingAsyncs;



implementation {:atomic} {:layer 2} A_Vote(r: Round, n: Node, v: Value, p: Permission)
{
    assert Round(r);
    assert p == VotePerm(r, n);
    assert pendingAsyncs[Vote_PA(r, n, v, p)] > 0;
    assert is#SomeVoteInfo(voteInfo[r]);
    assert value#SomeVoteInfo(voteInfo[r]) == v;
    assert !ns#SomeVoteInfo(voteInfo[r])[n];
    if (*)
    {
        assume (forall r': Round :: {:qid "quantifier27"} Round(r') && joinedNodes[r'][n] ==> r' <= r);
        voteInfo[r] := SomeVoteInfo(v, ns#SomeVoteInfo(voteInfo[r])[n := true]);
        joinedNodes[r][n] := true;
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Vote_PA(r, n, v, p)));
}



procedure {:IS_abstraction} {:layer 2} A_StartRound'(r: Round, {:linear_in "perm"} r_lin: Round) returns ({:pending_async "A_Join", "A_Propose"} PAs: [PA]int);
  modifies pendingAsyncs;



implementation {:IS_abstraction} {:layer 2} A_StartRound'(r: Round, r_lin: Round) returns (PAs: [PA]int)
{
    assert r == r_lin;
    assert Round(r);
    assert pendingAsyncs[StartRound_PA(r, r_lin)] > 0;
    assert RoundCollector(r)[ConcludePerm(r)];
    assert triggerRound(r - 1);
    assert triggerNode(0);
    PAs := MapAddPA(JoinPAs(r), SingletonPA(Propose_PA(r, ProposePermissions(r))));
    pendingAsyncs := MapAddPA(pendingAsyncs, PAs);
    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(StartRound_PA(r, r_lin)));
}



procedure {:IS_abstraction} {:layer 2} A_Propose'(r: Round, {:linear_in "perm"} ps: [Permission]bool) returns ({:pending_async "A_Vote", "A_Conclude"} PAs: [PA]int);
  modifies voteInfo, pendingAsyncs;



implementation {:IS_abstraction} {:layer 2} A_Propose'(r: Round, ps: [Permission]bool) returns (PAs: [PA]int)
{
  var maxRound: int;
  var maxValue: Value;
  var ns: NodeSet;

    assert Round(r);
    assert pendingAsyncs[Propose_PA(r, ps)] > 0;
    assert ps == ProposePermissions(r);
    assert is#NoneVoteInfo(voteInfo[r]);
    assert (forall r': Round :: {:qid "quantifier28"} r' <= r ==> pendingAsyncs[StartRound_PA(r', r')] == 0);
    assert (forall r': Round, n': Node, p': Permission :: {:qid "quantifier29"} r' <= r ==> pendingAsyncs[Join_PA(r', n', p')] == 0);
    assert PermissionSetCollector(ps)[ConcludePerm(r)];
    assert triggerRound(r);
    assert triggerRound(r - 1);
    assert triggerNode(0);
    if (*)
    {
        assume IsSubset(ns, joinedNodes[r]) && IsQuorum(ns);
        maxRound := MaxRound(r, ns, voteInfo);
        if (maxRound != 0)
        {
            maxValue := value#SomeVoteInfo(voteInfo[maxRound]);
        }

        voteInfo[r] := SomeVoteInfo(maxValue, NoNodes());
        PAs := MapAddPA(VotePAs(r, maxValue), SingletonPA(Conclude_PA(r, maxValue, ConcludePerm(r))));
    }
    else
    {
        PAs := NoPAs();
    }

    pendingAsyncs := MapAddPA(pendingAsyncs, PAs);
    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Propose_PA(r, ps)));
}



procedure {:IS_abstraction} {:layer 2} A_Conclude'(r: Round, v: Value, {:linear_in "perm"} p: Permission);
  modifies decision, pendingAsyncs;



implementation {:IS_abstraction} {:layer 2} A_Conclude'(r: Round, v: Value, p: Permission)
{
  var q: NodeSet;

    assert Round(r);
    assert pendingAsyncs[Conclude_PA(r, v, p)] > 0;
    assert p == ConcludePerm(r);
    assert is#SomeVoteInfo(voteInfo[r]);
    assert value#SomeVoteInfo(voteInfo[r]) == v;
    assert (forall n': Node, v': Value, p': Permission :: {:qid "quantifier30"} pendingAsyncs[Vote_PA(r, n', v', p')] == 0);
    assert triggerRound(r);
    if (*)
    {
        assume IsSubset(q, ns#SomeVoteInfo(voteInfo[r])) && IsQuorum(q);
        decision[r] := SomeValue(v);
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Conclude_PA(r, v, p)));
}



procedure {:IS_abstraction} {:layer 2} A_Join'(r: Round, n: Node, {:linear_in "perm"} p: Permission);
  modifies joinedNodes, pendingAsyncs;



implementation {:IS_abstraction} {:layer 2} A_Join'(r: Round, n: Node, p: Permission)
{
    assert Round(r);
    assert pendingAsyncs[Join_PA(r, n, p)] > 0;
    assert p == JoinPerm(r, n);
    assert (forall r': Round :: {:qid "quantifier31"} r' <= r ==> pendingAsyncs[StartRound_PA(r', r')] == 0);
    assert (forall r': Round, n': Node, p': Permission :: {:qid "quantifier32"} r' < r ==> pendingAsyncs[Join_PA(r', n', p')] == 0);
    assert (forall r': Round, p': [Permission]bool :: {:qid "quantifier33"} r' < r ==> pendingAsyncs[Propose_PA(r', p')] == 0);
    assert (forall r': Round, n': Node, v': Value, p': Permission :: {:qid "quantifier34"} r' < r ==> pendingAsyncs[Vote_PA(r', n', v', p')] == 0);
    assert triggerRound(r - 1);
    assert triggerNode(n);
    if (*)
    {
        assume (forall r': Round :: {:qid "quantifier35"} Round(r') && joinedNodes[r'][n] ==> r' < r);
        joinedNodes[r][n] := true;
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Join_PA(r, n, p)));
}



procedure {:IS_abstraction} {:layer 2} A_Vote'(r: Round, n: Node, v: Value, {:linear_in "perm"} p: Permission);
  modifies joinedNodes, voteInfo, pendingAsyncs;



implementation {:IS_abstraction} {:layer 2} A_Vote'(r: Round, n: Node, v: Value, p: Permission)
{
    assert Round(r);
    assert p == VotePerm(r, n);
    assert pendingAsyncs[Vote_PA(r, n, v, p)] > 0;
    assert is#SomeVoteInfo(voteInfo[r]);
    assert value#SomeVoteInfo(voteInfo[r]) == v;
    assert !ns#SomeVoteInfo(voteInfo[r])[n];
    assert (forall r': Round :: {:qid "quantifier36"} r' <= r ==> pendingAsyncs[StartRound_PA(r', r')] == 0);
    assert (forall r': Round, n': Node, p': Permission :: {:qid "quantifier37"} r' <= r ==> pendingAsyncs[Join_PA(r', n', p')] == 0);
    assert (forall r': Round, p': [Permission]bool :: {:qid "quantifier38"} r' <= r ==> pendingAsyncs[Propose_PA(r', p')] == 0);
    assert (forall r': Round, n': Node, v': Value, p': Permission :: {:qid "quantifier39"} r' < r ==> pendingAsyncs[Vote_PA(r', n', v', p')] == 0);
    assert triggerRound(r - 1);
    assert triggerNode(n);
    if (*)
    {
        assume (forall r': Round :: {:qid "quantifier40"} Round(r') && joinedNodes[r'][n] ==> r' <= r);
        voteInfo[r] := SomeVoteInfo(v, ns#SomeVoteInfo(voteInfo[r])[n := true]);
        joinedNodes[r][n] := true;
    }

    pendingAsyncs := MapSubPA(pendingAsyncs, SingletonPA(Vote_PA(r, n, v, p)));
}



procedure {:atomic} {:layer 3} A_Paxos'({:linear_in "perm"} rs: [Round]bool);
  modifies joinedNodes, voteInfo, decision, pendingAsyncs;



implementation {:atomic} {:layer 3} A_Paxos'(rs: [Round]bool)
{
    assert Init(rs, joinedNodes, voteInfo, decision, pendingAsyncs);
    havoc joinedNodes, voteInfo, decision, pendingAsyncs;
    assume (forall r1: Round, r2: Round :: {:qid "quantifier41"} is#SomeValue(decision[r1]) && is#SomeValue(decision[r2]) ==> decision[r1] == decision[r2]);
}



procedure {:atomic} {:layer 2} {:IS "A_Paxos'", "INV"} {:elim "A_StartRound", "A_StartRound'"} {:elim "A_Propose", "A_Propose'"} {:elim "A_Conclude", "A_Conclude'"} {:elim "A_Join", "A_Join'"} {:elim "A_Vote", "A_Vote'"} A_Paxos({:linear_in "perm"} rs: [Round]bool) returns ({:pending_async "A_StartRound"} PAs: [PA]int);
  modifies pendingAsyncs;



implementation {:atomic} {:layer 2} {:IS "A_Paxos'", "INV"} {:elim "A_StartRound", "A_StartRound'"} {:elim "A_Propose", "A_Propose'"} {:elim "A_Conclude", "A_Conclude'"} {:elim "A_Join", "A_Join'"} {:elim "A_Vote", "A_Vote'"} A_Paxos(rs: [Round]bool) returns (PAs: [PA]int)
{
  var numRounds: int;

    assert Init(rs, joinedNodes, voteInfo, decision, pendingAsyncs);
    assert triggerRound(0);
    assume 0 <= numRounds;
    assume triggerRound(numRounds);
    PAs := (lambda pa: PA :: {:qid "quantifier42"} (if is#StartRound_PA(pa) && round#StartRound_PA(pa) == round_lin#StartRound_PA(pa) && Round(round#StartRound_PA(pa)) && round#StartRound_PA(pa) <= numRounds then 1 else 0));
    pendingAsyncs := PAs;
}



function {:inline} FirstCasePAs(k: int, numRounds: int) : [PA]int
{
  (lambda pa: PA :: {:qid "quantifier43"} (if is#StartRound_PA(pa) && round#StartRound_PA(pa) == round_lin#StartRound_PA(pa) && k < round#StartRound_PA(pa) && round#StartRound_PA(pa) <= numRounds then 1 else 0))
}

function {:inline} SecondCasePAs(k: int, m: Node, numRounds: int) : [PA]int
{
  (lambda pa: PA :: {:qid "quantifier44"} (if (is#StartRound_PA(pa) && round#StartRound_PA(pa) == round_lin#StartRound_PA(pa) && k + 1 < round#StartRound_PA(pa) && round#StartRound_PA(pa) <= numRounds) || pa == Propose_PA(k + 1, ProposePermissions(k + 1)) || (is#Join_PA(pa) && round#Join_PA(pa) == k + 1 && m < node#Join_PA(pa) && node#Join_PA(pa) <= numNodes && p#Join_PA(pa) == JoinPerm(k + 1, node#Join_PA(pa))) then 1 else 0))
}

function {:inline} SecondCaseChoice(k: int, m: Node) : PA
{
  (if m == numNodes then Propose_PA(k + 1, ProposePermissions(k + 1)) else Join_PA(k + 1, m + 1, JoinPerm(k + 1, m + 1)))
}

function {:inline} ThirdCasePAs(k: int, m: Node, v: Value, numRounds: int) : [PA]int
{
  (lambda pa: PA :: {:qid "quantifier45"} (if (is#StartRound_PA(pa) && round#StartRound_PA(pa) == round_lin#StartRound_PA(pa) && k + 1 < round#StartRound_PA(pa) && round#StartRound_PA(pa) <= numRounds) || pa == Conclude_PA(k + 1, v, ConcludePerm(k + 1)) || (is#Vote_PA(pa) && round#Vote_PA(pa) == k + 1 && m < node#Vote_PA(pa) && node#Vote_PA(pa) <= numNodes && value#Vote_PA(pa) == v && p#Vote_PA(pa) == VotePerm(k + 1, node#Vote_PA(pa))) then 1 else 0))
}

function {:inline} ThirdCaseChoice(k: int, m: Node, v: Value) : PA
{
  (if m == numNodes then Conclude_PA(k + 1, v, ConcludePerm(k + 1)) else Vote_PA(k + 1, m + 1, v, VotePerm(k + 1, m + 1)))
}

procedure {:IS_invariant} {:layer 2} INV({:linear_in "perm"} rs: [Round]bool) returns ({:pending_async "A_StartRound", "A_Propose", "A_Conclude", "A_Join", "A_Vote"} PAs: [PA]int, {:choice} choice: PA);
  modifies joinedNodes, voteInfo, decision, pendingAsyncs;



implementation {:IS_invariant} {:layer 2} INV(rs: [Round]bool) returns (PAs: [PA]int, choice: PA)
{
    assert Init(rs, joinedNodes, voteInfo, decision, pendingAsyncs);
    havoc joinedNodes, voteInfo, decision;
    assume (exists k: int, numRounds: int :: {:qid "quantifier46"} { triggerRound(k), triggerRound(numRounds) } 0 <= k && k <= numRounds && triggerRound(numRounds) && (if k == numRounds then PAs == NoPAs() else (PAs == FirstCasePAs(k, numRounds) && choice == StartRound_PA(k + 1, k + 1) && (forall r: Round :: {:qid "quantifier47"} r < 1 || r > k ==> joinedNodes[r] == NoNodes()) && (forall r: Round :: {:qid "quantifier48"} r < 1 || r > k ==> is#NoneVoteInfo(voteInfo[r])) && (forall r: Round :: {:qid "quantifier49"} r < 1 || r > k ==> is#NoneValue(decision[r]))) || ((forall r: Round :: {:qid "quantifier50"} r < 1 || r > k + 1 ==> joinedNodes[r] == NoNodes()) && (forall r: Round :: {:qid "quantifier51"} r < 1 || r > k ==> is#NoneVoteInfo(voteInfo[r])) && (forall r: Round :: {:qid "quantifier52"} r < 1 || r > k ==> is#NoneValue(decision[r])) && (exists m: Node :: {:qid "quantifier53"} { triggerNode(m) } 0 <= m && m <= numNodes && (forall n: Node :: {:qid "quantifier54"} n < 1 || n > m ==> !joinedNodes[k + 1][n]) && PAs == SecondCasePAs(k, m, numRounds) && choice == SecondCaseChoice(k, m))) || (is#SomeVoteInfo(voteInfo[k + 1]) && (forall r: Round :: {:qid "quantifier55"} r < 1 || r > k + 1 ==> joinedNodes[r] == NoNodes()) && (forall r: Round :: {:qid "quantifier56"} r < 1 || r > k + 1 ==> is#NoneVoteInfo(voteInfo[r])) && (forall r: Round :: {:qid "quantifier57"} r < 1 || r > k ==> is#NoneValue(decision[r])) && (exists m: Node :: {:qid "quantifier58"} { triggerNode(m) } 0 <= m && m <= numNodes && (forall n: Node :: {:qid "quantifier59"} n < 1 || n > m ==> !ns#SomeVoteInfo(voteInfo[k + 1])[n]) && PAs == ThirdCasePAs(k, m, value#SomeVoteInfo(voteInfo[k + 1]), numRounds) && choice == ThirdCaseChoice(k, m, value#SomeVoteInfo(voteInfo[k + 1]))))));
    assume (forall r: Round :: {:qid "quantifier60"} is#SomeValue(decision[r]) ==> is#SomeVoteInfo(voteInfo[r]) && value#SomeVoteInfo(voteInfo[r]) == value#SomeValue(decision[r]) && (exists q: NodeSet :: {:qid "quantifier61"} { IsSubset(q, ns#SomeVoteInfo(voteInfo[r])), IsQuorum(q) } IsSubset(q, ns#SomeVoteInfo(voteInfo[r])) && IsQuorum(q)));
    assume (forall r1: Round, r2: Round :: {:qid "quantifier62"} is#SomeValue(decision[r1]) && r1 <= r2 && is#SomeVoteInfo(voteInfo[r2]) ==> value#SomeVoteInfo(voteInfo[r2]) == value#SomeValue(decision[r1]));
    assume (forall r1: Round, r2: Round :: {:qid "quantifier63"} is#SomeValue(decision[r1]) && is#SomeValue(decision[r2]) ==> decision[r1] == decision[r2]);
    pendingAsyncs := PAs;
}


