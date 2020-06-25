// Boogie program verifier version 2.6.15.0, Copyright (c) 2003-2014, Microsoft.
// Command Line Options: -print:tmp.bpl -printDesugared ./Fact.bpl

function Fact(x: int) : int;

axiom (forall t: int :: t == 0 ==> Fact(t) == 1);

axiom (forall t: int :: t >= 0 ==> Fact(t) == t * Fact(t - 1));

const Seven: int;

axiom Seven == 7;

procedure Test();



implementation Test()
{
    assert Fact(3) == 6;
}



const Five: int;

axiom Five == 5;
