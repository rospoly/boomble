# boomble
boomble is a scrambler for the boogie programming language.
Currently, the only mutation it supports is the random shuffling of declarations.

### requirements
1) boogie and z3 as global tools (open a terminal and digit `boogie` and `z3` to check)
2) python3


### compile
1) clone the repo
2) `cd boomble/boogie`
3) `git init submodule`
4) `git submodule update`
5) `git checkout master`
6) compile boogie with `dotnet build Source/Boogie-NetCore.sln` 
(remember to set the environment variable MSBUILDSINGLELOADCONTEXT=1 see https://github.com/boogie-org/boogie)
7) from the home of boomble run `dotnet build boomble.sln` (or if you have Visual-Studio/Rider just open the project)
8) now you can find the executable(s) in `bin/debug`

# run boomble
1) `boomble -n:<num_of_shuffles> File-1.bpl ... File-M.bpl`
2) the resulting shuffles are dumped to a folder called `results` in the current directory. 
Please note that in case the folder `results` already exists, boomble does not override the folder, 
and returns an error message. 

# run the quantifier analysis
In the folder `parallel` in the home directory of boomble there are two Python3 scripts:

1) `parAnalysis` runs `boogie` and `z3` (with profiling and log enabled). The script is standalone and it has a dedicate parser with usefull message and `-help` option. Just run `python3 parAnalysis.py`.

2) `elaborateLogs.py` runs the quantifier instantiations analysis on the logs produced by `parAnalysis`. (TODO: parser with help message)