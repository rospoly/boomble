# boomble
*boomble* is a suite of tools you can use to debug the execution of a set of Boogie programs.  
*boomble* consists of:  

1) `boomble` a C# tool we use to:  
  1.1) label quantifiers in a boogie program using the `QID`.  
  1.2) shuffle the declarations in a boogie program.  
2) a set of Python scripts (folder parallel) to run Boogie and Z3 in parallel on a set of boogie program (typically coming from point 1).  
3) a set of Python scripts (folder trace) to debug the execution of Z3. You need to compile Z3 in debugging mode.  

### requirements
1) boogie and z3 executables  
2) python3
3) [dotnet](https://docs.microsoft.com/en-us/dotnet/core/install/)
4) (used only for the trace) Z3 compiled in debugging mode.  

### compile
1) clone the repo
2) `cd boomble`
3) `git submodule update --init --recursive`
4) `cd boogie`
5) `git checkout master`
6) compile boogie with `dotnet build Source/Boogie-NetCore.sln` 
(remember to set the environment variable MSBUILDSINGLELOADCONTEXT=1 see https://github.com/boogie-org/boogie)
7) from the home of boomble run `dotnet build boomble.sln` (or if you have Visual-Studio/Rider just open the project)
8) now you can find the executable(s) in `bin/debug`

Note: in case you dont find the exe `boomble`, you can run the following from the home directory of boomble  
`dotnet publish boomble.sln --self-contained true --runtime <your_os> /p:PackAsTool=false`,  
and you substitute `<your_os>` with `osx-x64` or `win-x64` or `linux-x64`.  
Now you should find the executable in `bin/debug`.

# run boomble
* `bin/debug/../boomble -n:<num_of_shuffles> -noMutation File-1.bpl ... File-M.bpl`

# notes
* boomble labels all quantifiers (without a qid) in the input program (in progressive order: quantifier0, quantifier1, quantifier2, etc).
* -noMutation is optional, and in case you provide it, boomble creates n identical copy of the input file (with identical labels also).
* the resulting shuffles are dumped to a folder called `results` in the working directory. 
Please note that in case the folder `results` already exists, boomble does not override the folder, and returns an error message. 

# run Boogie and Z3

In the folder `parallel` there are two Python3 scripts:

1) `parAnalysis.py` runs `boogie` and `z3` (with profiling and log enabled). The script is standalone and it has a dedicate parser with a`-help` option. Just run `python3 parAnalysis.py` to see the help message.

2) `elaborateLogs.py` runs the quantifier instantiations analysis on the logs produced by `parAnalysis`. The script is standalone and it has a dedicate parser with`-help` option. Just run `python3 elaborateLogs.py` to see the help message.

# run Z3 with profiling and create the casuality graph

Note: in this section we assume you have the following custom Z3 implementation (link).

In the folder `trace` there are two Python3 scripts:

1) `casuality_graph.py` creates a casuality graph between quantifier instantiations.  
The script needs a debugging trace from Z3 (instruction for the debugging trace [here](https://github.com/rospoly/z3/blob/prototype/README.md)).  
The debugging trace is available only when Z3 is compiled with the option DZ3_ENABLE_TRACING_FOR_NON_DEBUG set to true. Note, this is not the case for the standard release executable of Z3.  
You need to compile [Z3 master](https://github.com/Z3Prover/z3) with  
`cmake -DCMAKE_BUILD_TYPE=Release -DZ3_ENABLE_TRACING_FOR_NON_DEBUG=TRUE`.
See [link](https://github.com/Z3Prover/z3/blob/master/README-CMake.md) for more details.

2) `causality_graph_comparison.py` compares two or more traces, it creates a diff graph for each pair of traces.
