﻿using System;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Boogie;

namespace Microsoft.Boogie
{
    public class CivlUtil
    {
        public static void AddInlineAttribute(Declaration decl)
        {
            decl.AddAttribute("inline", Expr.Literal(1));
        }

        public static void ResolveAndTypecheck(Absy absy)
        {
            absy.Resolve(new ResolutionContext(null));
            absy.Typecheck(new TypecheckingContext(null));
        }

        public static void ResolveAndTypecheck(IEnumerable<Absy> absys)
        {
            foreach (var absy in absys)
                ResolveAndTypecheck(absy);
        }
    }

    // Handy syntactic suggar missing in Expr
    public static class ExprHelper
    {
        public static NAryExpr FunctionCall(Function f, params Expr[] args)
        {
            return new NAryExpr(Token.NoToken, new FunctionCall(f), args);
        }

        public static NAryExpr IfThenElse(Expr ifExpr, Expr thenExpr, Expr elseExpr)
        {
            return new NAryExpr(Token.NoToken, new IfThenElse(Token.NoToken),
                new Expr[] { ifExpr, thenExpr, elseExpr });
        }

        public static OldExpr Old(Expr expr)
        {
            return new OldExpr(Token.NoToken, expr);
        }

        public static void FlattenAnd(Expr x, List<Expr> xs)
        {
            if (x is NAryExpr naryExpr && naryExpr.Fun.FunctionName == "&&")
            {
                FlattenAnd(naryExpr.Args[0], xs);
                FlattenAnd(naryExpr.Args[1], xs);
            }
            else { xs.Add(x); }
        }
    }

    public static class CmdHelper
    {
        public static ReturnCmd ReturnCmd => new ReturnCmd(Token.NoToken);

        public static CallCmd CallCmd(Procedure callee, List<Expr> ins, List<IdentifierExpr> outs)
        {
            return new CallCmd(Token.NoToken, callee.Name, ins, outs)
            { Proc = callee };
        }

        public static AssumeCmd AssumeCmd(Expr expr)
        {
            return new AssumeCmd(Token.NoToken, expr);
        }

        public static AssignCmd AssignCmd(Variable v, Expr x)
        {
            var lhs = new SimpleAssignLhs(Token.NoToken, Expr.Ident(v));
            return new AssignCmd(Token.NoToken, new List<AssignLhs> { lhs }, new List<Expr> { x });
        }
    }

    public static class VarHelper
    {
        public static LocalVariable LocalVariable(string name, Type type)
        {
            return new LocalVariable(Token.NoToken, new TypedIdent(Token.NoToken, name, type));
        }

        public static BoundVariable BoundVariable(string name, Type type)
        {
            return new BoundVariable(Token.NoToken, new TypedIdent(Token.NoToken, name, type));
        }

        public static Formal Formal(string name, Type type, bool incoming)
        {
            return new Formal(Token.NoToken, new TypedIdent(Token.NoToken, name, type), incoming);
        }
    }

    public static class SubstitutionHelper
    {
        public static Substitution FromVariableMap(Dictionary<Variable, Variable> map)
        {
            return Substituter.SubstitutionFromHashtable(map.ToDictionary(kv => kv.Key, kv => (Expr)Expr.Ident(kv.Value)));
        }

        public static Expr Apply(Dictionary<Variable, Expr> map, Expr expr)
        {
            return Substituter.Apply(Substituter.SubstitutionFromHashtable(map), expr);
        }

        public static Expr Apply(Dictionary<Variable, Variable> map, Expr expr)
        {
            return Substituter.Apply(FromVariableMap(map), expr);
        }

        public static Cmd Apply(Dictionary<Variable, Expr> map, Cmd cmd)
        {
            return Substituter.Apply(Substituter.SubstitutionFromHashtable(map), cmd);
        }

        public static Cmd Apply(Dictionary<Variable, Variable> map, Cmd cmd)
        {
            return Substituter.Apply(FromVariableMap(map), cmd);
        }

        public static IEnumerable<Expr> Apply(Substitution subst, IEnumerable<Expr> exprs)
        {
            return exprs.Select(x => Substituter.Apply(subst, x));
        }

        public static IEnumerable<Expr> Apply(Dictionary<Variable, Expr> map, IEnumerable<Expr> exprs)
        {
            var subst = Substituter.SubstitutionFromHashtable(map);
            return Apply(subst, exprs);
        }

        public static IEnumerable<Expr> Apply(Dictionary<Variable, Variable> map, IEnumerable<Expr> exprs)
        {
            var subst = FromVariableMap(map);
            return Apply(subst, exprs);
        }

        public static IEnumerable<Cmd> Apply(Substitution subst, IEnumerable<Cmd> cmds)
        {
            return cmds.Select(x => Substituter.Apply(subst, x));
        }

        public static IEnumerable<Cmd> Apply(Dictionary<Variable, Expr> map, IEnumerable<Cmd> cmds)
        {
            var subst = Substituter.SubstitutionFromHashtable(map);
            return Apply(subst, cmds);
        }

        public static IEnumerable<Cmd> Apply(Dictionary<Variable, Variable> map, IEnumerable<Cmd> cmds)
        {
            var subst = FromVariableMap(map);
            return Apply(subst, cmds);
        }
    }

    public static class LinqExtensions
    {
        public static IEnumerable<IEnumerable<T>> CartesianProduct<T>(this IEnumerable<IEnumerable<T>> sequences)
        {
            IEnumerable<IEnumerable<T>> emptyProduct = new[] { Enumerable.Empty<T>() };
            return sequences.Aggregate(
                emptyProduct,
                (accumulator, sequence) =>
                from acc in accumulator
                from item in sequence
                select acc.Concat(new[] { item }));
        }

        public static Dictionary<TKey, TValue> ToDictionary<TKey, TValue>(this IEnumerable<TKey> keys, Func<TKey, TValue> f)
        {
            return keys.ToDictionary(k => k, k => f(k));
        }
    }
}
