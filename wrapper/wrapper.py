import sys
import subprocess
import shlex

def main(args):
    log_file = open("tmp.log", "a+")
    f = "z3 "
    for elem in args[1:]:
        f = f + elem + " "

    log_file.write(f)
    log_file.flush()
    proc_run = subprocess.Popen(shlex.split(f))
    out,err=proc_run.communicate()
    log_file.write("Done")
    log_file.close()

if __name__ == '__main__':
    main(sys.argv)