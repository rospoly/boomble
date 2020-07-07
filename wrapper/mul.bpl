// Boogie program verifier version 2.6.15.0, Copyright (c) 2003-2014, Microsoft.
// Command Line Options: -print:tmp.bpl -printDesugared ./Fact.bpl

function mul(x: int, y:int) : int;

axiom (forall x,y:int :: x== 0 ==> mul(x,y) == 0); // (x==0 and not(mul(x,y)==0)) same as (not(x==0) or mul(x,y)==0)

axiom (forall x,y:int :: y == 0 ==> mul(x,y) == 0); //(y==0 and not(mul(x,y)==0))  same as (not(y==0) or mul(x,y)==0)

axiom (forall t,v: int :: (t>0 && v>0) ==> mul(t,v) == v + mul(t-1,v));

procedure Test();

implementation Test()
{
    assert mul(12,4) == 48;
}
