using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.IO;
using System.Linq;
using System.Linq.Expressions;
using System.Net.Http.Headers;
using System.Text;
using Microsoft.Boogie;
using Microsoft.Boogie.VCExprAST;

namespace boomble
{
  class Test
  {
    static int Main(string[] args)
    {
      Console.WriteLine("Hello World!");

      Contract.Requires(cce.NonNullElements(args));

      ExecutionEngine.printer = new ConsolePrinter();

      CommandLineOptions.Install(new CommandLineOptions());

      CommandLineOptions.Clo.RunningBoogieFromCommandLine = true;
      if (!CommandLineOptions.Clo.Parse(args))
      {
        goto END;
      }

      if (CommandLineOptions.Clo.Files.Count == 0)
      {
        ExecutionEngine.printer.ErrorWriteLine(Console.Out, "*** Error: No input files were specified.");
        goto END;
      }

      if (CommandLineOptions.Clo.XmlSink != null)
      {
        string errMsg = CommandLineOptions.Clo.XmlSink.Open();
        if (errMsg != null)
        {
          ExecutionEngine.printer.ErrorWriteLine(Console.Out, "*** Error: " + errMsg);
          goto END;
        }
      }

      if (!CommandLineOptions.Clo.DontShowLogo)
      {
        Console.WriteLine(CommandLineOptions.Clo.Version);
      }

      if (CommandLineOptions.Clo.ShowEnv == CommandLineOptions.ShowEnvironment.Always)
      {
        Console.WriteLine("---Command arguments");
        foreach (string arg in args)
        {
          Contract.Assert(arg != null);
          Console.WriteLine(arg);
        }

        Console.WriteLine("--------------------");
      }

      Helpers.ExtraTraceInformation("Becoming sentient");

      List<string> fileList = new List<string>();
      foreach (string file in CommandLineOptions.Clo.Files)
      {
        string extension = Path.GetExtension(file);
        if (extension != null)
        {
          extension = extension.ToLower();
        }

        if (extension == ".txt")
        {
          StreamReader stream = new StreamReader(file);
          string s = stream.ReadToEnd();
          fileList.AddRange(s.Split(new char[3] {' ', '\n', '\r'}, StringSplitOptions.RemoveEmptyEntries));
        }
        else
        {
          fileList.Add(file);
        }
      }

      foreach (string file in fileList)
      {
        Contract.Assert(file != null);
        string extension = Path.GetExtension(file);
        if (extension != null)
        {
          extension = extension.ToLower();
        }

        if (extension != ".bpl")
        {
          ExecutionEngine.printer.ErrorWriteLine(Console.Out,
            "*** Error: '{0}': Filename extension '{1}' is not supported. Input files must be BoogiePL programs (.bpl).",
            file,
            extension == null ? "" : extension);
          goto END;
        }
      }

      Program program = ExecutionEngine.ParseBoogieProgram(fileList, false);
      var tuple = Shuffler.Get_N_Permutations_of_Program(program, 1000);
      var list_of_program = tuple.Item1.ToList();
      var list_of_order = tuple.Item2.ToList();

      var outputpath = Environment.CurrentDirectory + "/results/";

      if (Directory.Exists(outputpath))
      {
        Directory.Delete(outputpath, true);
      }

      Directory.CreateDirectory(outputpath);
      
      for (int i = 0; i < list_of_program.Count; i++)
      {
        var file_name = "tmp" + i + ".bpl";
        ExecutionEngine.PrintBplFile(outputpath + file_name, list_of_program[i], false);
      }
      
      return 0;

      END:
      if (CommandLineOptions.Clo.XmlSink != null)
      {
        CommandLineOptions.Clo.XmlSink.Close();
      }

      if (CommandLineOptions.Clo.Wait)
      {
        Console.WriteLine("Press Enter to exit.");
        Console.ReadLine();
      }

      return 1;
    }
  }

  public static class ProgramClonerPlus
  {
    public static Absy Clone_Empty_declarations(this Program p)
    {
      var cloned = (Program) p.Clone();
      cloned.ClearTopLevelDeclarations();
      return cloned;
    }
  }

  public class Shuffler
  {
    public static (IEnumerable<Program>, List<List<int>>) Get_N_Permutations_of_Program(Program program, int n)
    {

      var permutations_list = new List<Program>();
      permutations_list.Add(program);
      var list_of_decl = program.TopLevelDeclarations;
      Assign_Label_To_Set_Of_Declarations(list_of_decl.ToList());
      var list_of_numbers = Enumerable.Range(0, list_of_decl.Count()).ToList();
      var list_of_permutation = new List<List<int>>();
      list_of_permutation.Add(list_of_numbers);
      //GetPermutations(list_of_numbers, 0, list_of_numbers.Count - 1);
      int n_permutations = n;

      for (int i = 0; i < n_permutations; i++)
      {
        Program new_program = (Program) program.Clone_Empty_declarations();
        List<int> perm = GetOneRandomPermutation(list_of_numbers);
        list_of_permutation.Add(perm);
        List<Declaration> tmp = GetDeclarationsGivenPermutation(list_of_decl.ToList(), perm);
        new_program.AddTopLevelDeclarations(tmp);
        permutations_list.Add(new_program);
      }

      return (permutations_list, list_of_permutation);
    }

    public static List<Declaration> GetDeclarationsGivenPermutation(List<Declaration> decl, List<int> permutation)
    {
      List<Declaration> ret = new List<Declaration>();
      for (int i = 0; i < permutation.Count(); i++)
      {
        ret.Add(decl[permutation[i]]);
      }
      return ret;
    }

    public static List<int> GetOneRandomPermutation(List<int> input_list)
    {
      Random random = new Random();
      var list = new List<int>(input_list);
      int n = list.Count();
      while (n > 1)
      {
        n--;
        int i = random.Next(n + 1);
        (list[i], list[n]) = (list[n], list[i]);
      }

      return list;
    }

    private static void GetPermutations(List<int> list, int current_depth, int max_depth)
    {
      if (current_depth == max_depth)
      {
        list.ForEach(Console.Write);
        Console.WriteLine();
      }
      else
        for (int i = current_depth; i <= max_depth; i++)
        {
          (list[current_depth], list[i]) = (list[i], list[current_depth]);
          GetPermutations(list, current_depth + 1, max_depth);
          (list[current_depth], list[i]) = (list[i], list[current_depth]);
        }
    }

    public static void Assign_Label_To_Set_Of_Declarations(List<Declaration> ld)
    {
      for (int i = 0; i < ld.Count; i++)
      {
        var declaration = ld[i];
        Assign_Label_To_Declaration(ref declaration);
      }
    }

    public static void Assign_Label_To_Expression(ref Expr expr)
    {
      var ForAllExpr = expr as ForallExpr;
      var ExistsExpr = expr as ExistsExpr;
      var NAryExpr = expr as NAryExpr;
      var LetExpr = expr as LetExpr;
      var LambdaExpr = expr as LambdaExpr;
      
      if (ForAllExpr != null)
      {
        ((ForallExpr) expr).Attributes=Elaborate_Qid(((ForallExpr) expr).Attributes);
        var body = ((ForallExpr) expr).Body;
        Assign_Label_To_Expression(ref body);
      }
      else if (ExistsExpr!=null)
      {
        ((ExistsExpr) expr).Attributes=Elaborate_Qid(((ExistsExpr) expr).Attributes);
        var body = ((ExistsExpr) expr).Body;
        Assign_Label_To_Expression(ref body);
      }
      else if (LambdaExpr!=null)
      {
        ((LambdaExpr) expr).Attributes=Elaborate_Qid(((LambdaExpr) expr).Attributes);
        var body = ((LambdaExpr) expr).Body;
        Assign_Label_To_Expression(ref body);
      }
      else if (LetExpr!=null)
      {
        var body = ((LetExpr) expr).Body;
        Assign_Label_To_Expression(ref body);
      }
      else if (NAryExpr != null)
      {
        List<Expr> tmp = NAryExpr.Args.ToList();
        for (int i = 0; i < tmp.Count; i++)
        {
          var tmp_expr = tmp[i];
          Assign_Label_To_Expression(ref tmp_expr);
        }
      }
    }

    public static void Assign_Label_To_Set_Of_Expressions(ref List<Expr> expr)
    {
      for (int i = 0; i < expr.Count; i++)
      {
        var tmp = expr[i];
        Assign_Label_To_Expression(ref tmp);
      }
    }

    public static void Assign_Label_To_Declaration(ref Declaration decl)
    {

      Contract.Assert(decl != null);

      var axiomDecl = decl as Axiom;
      var procedureDecl = decl as Procedure;
      var functionDecl = decl as Function;
      var implemDecl = decl as Implementation;
      
      if (axiomDecl != null)
      {
        var expr = axiomDecl.Expr;
        Assign_Label_To_Expression(ref expr);
      }
      else if (procedureDecl != null)
      {
        var requires = procedureDecl.Requires;
        var ensures = procedureDecl.Ensures;
        var list_ens_req = new List<Absy>();
        list_ens_req.AddRange(requires);
        list_ens_req.AddRange(ensures);
        Get_Names_For_Procedure(list_ens_req);
      }
      else if (functionDecl != null)
      {
        var body_expressions=(functionDecl.Body);
        if (body_expressions != null)
        {
          Assign_Label_To_Expression(ref body_expressions);
        }
      }
      else if (implemDecl != null)
      {
        for (int i = 0; i < implemDecl.Blocks.Count; i++)
        {
          for (int j = 0; j < implemDecl.Blocks.ToList()[i].Cmds.Count; j++)
          {
            Cmd c = implemDecl.Blocks.ToList()[i].Cmds.ToList()[j];
            AssertCmd artc = c as AssertCmd;
            AssumeCmd amec = c as AssumeCmd;
            AssignCmd assc = c as AssignCmd;
            Expr tmp = null;
            if (artc != null)
            {
              tmp = artc.Expr;
            }
            else if (amec != null)
            {
              tmp = amec.Expr;
            }
            else if (assc != null)
            {
              var list_temp = assc.Rhss.ToList();
              Assign_Label_To_Set_Of_Expressions(ref list_temp);
            }
            Assign_Label_To_Expression(ref tmp);
          }
        }
      }
    }

    public static QKeyValue Elaborate_Qid(QKeyValue qkv)
    {
      QKeyValue tmp = qkv;
      if (tmp == null)
      {
        var fal = new List<Object>(1);
        tmp = new QKeyValue(new Token(), "qid", fal, null);
        tmp.AddParam(Identifier.getValue());
      }
      else
      {
        if (QKeyValue.FindStringAttribute(tmp, "qid") == null)
        {
          var fal = new List<Object>(1);
          var qkey = new QKeyValue(new Token(), "qid", fal, null);
          qkey.AddParam(Identifier.getValue());
          tmp.AddLast(qkey);
        }
      }
      return tmp;
    }

    public static void Get_Names_For_Procedure(List<Absy> t)
    {
      for (int i = 0; i < t.Count; i++)
      {
        var req_ensure = t[i] as Ensures;
        var req_require = t[i] as Requires;
        Expr res = null;
        if (req_ensure != null)
          res = req_ensure.Condition;
        else if (req_require != null)
          res = req_require.Condition;
        Assign_Label_To_Expression(ref res);
      }
    }
  }

  public static class Identifier
  {
    private static string value = "quantifier";
    private static int id = 0;
    public static string getValue()
    {
      var tmp = value + id;
      id++;
      return tmp;
    } 
  }
}
