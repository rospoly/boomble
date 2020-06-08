// Boogie program verifier version 2.6.15.0, Copyright (c) 2003-2014, Microsoft.
// Command Line Options: -contractInfer -printAssignment -abstractHoudini:IA[ConstantProp] -print:tmp.bpl fail1.bpl

function {:existential true} b1(x: bool) : bool;

var myVar: int;

procedure foo(i: int);
  modifies myVar;
  ensures b1(myVar > 0);



implementation foo(i: int)
{
    if (i > 0)
    {
        myVar := 5;
    }
    else
    {
        myVar := 0;
    }

    assert false;
}


