using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Diagnostics;
using System.Diagnostics.Contracts;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.Boogie;

namespace boomble
{
      public class CommandLineOptionsBoomble : CommandLineOptionEngine{
          public int N;
          public bool NoMutation;

          public CommandLineOptionsBoomble() : base("Boomble", "scrumbler for Boogie")
          {
              N = 10;
              NoMutation = false;
          }
          
          public override string/*!*/ Version {
              get {
                  Contract.Ensures(Contract.Result<string>() != null);
                  return ToolName + ": " + DescriptiveToolName; // + VersionSuffix;
              }
          }
          
          private static CommandLineOptionsBoomble clo_boomble;
          
          public static CommandLineOptionsBoomble/*!*/ Clo_Boomble
          {
              get { return clo_boomble; }
          }

          public static void Install(CommandLineOptionsBoomble options) {
              Contract.Requires(options != null);
              clo_boomble = options;
          }
          
          protected override bool ParseOption(string name, CommandLineOptionEngine.CommandLineParseState ps)
          {
              var args = ps.args;  // convenient synonym
              switch (name)
              {
                  case "n":
                      if (ps.ConfirmArgumentCount(1))
                      {
                          N=Int32.Parse(cce.NonNull(args[ps.i]));
                      }

                      return true;
                  
                  case "noMutation":
                      if (ps.ConfirmArgumentCount(0))
                      {
                          NoMutation = true;
                      }

                      return true;
              }

              return base.ParseOption(name, ps);
          }
          
          public new String[] Parse([Captured] string[]/*!*/ args) {
              Contract.Requires(cce.NonNullElements(args));
              List<String> ret_list= new List<String>();
              // save the command line options for the log files
              args = cce.NonNull((string[])args.Clone());  // the operations performed may mutate the array, so make a copy
              var ps = new CommandLineParseState(args, ToolName);

              while (ps.i < args.Length) {
                  cce.LoopInvariant(ps.args == args);
                  string arg = args[ps.i];
                  Contract.Assert(arg != null);
                  ps.s = arg.Trim();

                  bool isOption = ps.s.StartsWith("-") || ps.s.StartsWith("/");
                  int colonIndex = ps.s.IndexOf(':');
                  if (0 <= colonIndex && isOption) {
                      ps.hasColonArgument = true;
                      args[ps.i] = ps.s.Substring(colonIndex + 1);
                      ps.s = ps.s.Substring(0, colonIndex);
                  } else {
                      ps.i++;
                      ps.hasColonArgument = false;
                  }
                  ps.nextIndex = ps.i;

                  if (isOption)
                  {
                      if (!ParseOption(ps.s.Substring(1), ps))
                      {
                          ret_list.Add(arg);
                      }
                  }
                  else
                  {
                      ret_list.Add(arg);
                  }

                  ps.i = ps.nextIndex;
              }

              if (HelpRequested) {
                  Usage();
              } else if (AttrHelpRequested) {
                  AttributeUsage();
              } else if (ps.EncounteredErrors) {
                  Console.WriteLine("Use /help for available options");
              }

              if (ps.EncounteredErrors) {
                  Console.WriteLine("Error while parsing boomble options!");
                  return new string[0];
              } else {
                  this.ApplyDefaultOptions();
              }
              return ret_list.ToArray();
          }
      }
}