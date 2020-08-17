import argparse
import os
import shlex
import subprocess
import sys
from multiprocessing.pool import Pool
import ntpath

class MyParser(argparse.ArgumentParser):
   def error(self, message):
      sys.stderr.write('ERROR: %s\n' % message)
      self.print_help()
      sys.exit(1)

parser = MyParser(description='Run our custom trace of Z3 on a set of .smt2 files. ')
parser.add_argument('z3', type=str, metavar='<path_to_z3>',
                    help='the path to Z3 exe')
parser.add_argument('files', type=str, metavar='<path_to_programs>',
                    help='the path to the folder with the .smt2 programs to analyze')
parser.add_argument('-timeout', type=str, metavar='<timeout>',
                    help='timeout in seconds (default=30s)', default=30)
parser.add_argument('-opt', nargs='*', metavar='<option_for_the_trace>',
					help='Options for the trace: instance, bindings, dummy, causality, triggers', default="")
args = parser.parse_args()

file_set = sorted(os.listdir(args.files))
time_out=args.timeout
z3=args.z3
opt=args.opt

for index_file_name, file_name in enumerate(file_set):
    if file_name.endswith(".smt2"):
        shuffle_name=ntpath.basename(file_name)
        print("Start with "+str(shuffle_name))
        f = (z3 +" -T:" + time_out + " " if int(time_out) != -1 else "")
        for val in opt:
            f= f+ "-tr:"+val+" "
        f=f+args.files+file_name
        proc_run = subprocess.Popen(shlex.split(f))
        proc_run.wait()
        os.rename(args.files+".z3-trace", args.files+".z3-trace"+"-"+shuffle_name.split(".")[0])
        print("Done with "+str(shuffle_name))