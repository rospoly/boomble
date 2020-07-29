# boomble
boomble is a scrambler for the boogie programming language.
Currently, the only mutation it supports is the random shuffling of declarations.

### requirements
1) boogie and z3 as global tools (open a terminal and digit `boogie` and `z3` to check)
2) python3
3) [dotnet](https://docs.microsoft.com/en-us/dotnet/core/install/)


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

# run boomble
* `bin/debug/../boomble -n:<num_of_shuffles> -noMutation File-1.bpl ... File-M.bpl`
# notes
* boomble labels all quantifiers without a qid in the input program (in progressive order: quantifier0, quantifier1, quantifier2, etc).
* -noMutation is optional, and in case you provide it, boomble creates n identical copy of the input file (with identical labels also).
* the resulting shuffles are dumped to a folder called `results` in the current directory. 
Please note that in case the folder `results` already exists, boomble does not override the folder, 
and returns an error message. 

# run the quantifier analysis
In the folder `parallel` in the home directory of boomble there are two Python3 scripts:

1) `parAnalysis` runs `boogie` and `z3` (with profiling and log enabled). The script is standalone and it has a dedicate parser with a`-help` option. Just run `python3 parAnalysis.py` to see the help message.

2) `elaborateLogs.py` runs the quantifier instantiations analysis on the logs produced by `parAnalysis`. The script is standalone and it has a dedicate parser with`-help` option. Just run `python3 elaborateLogs.py` to see the help message.
