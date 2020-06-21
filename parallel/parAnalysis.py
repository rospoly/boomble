import multiprocessing
import shutil
import sys
from multiprocessing.pool import ThreadPool, Pool
import os
import random
import subprocess
import shlex
import time
import argparse

class MyParser(argparse.ArgumentParser):
   def error(self, message):
      sys.stderr.write('ERROR: %s\n' % message)
      self.print_help()
      sys.exit(1)


def process_file(time_out_vc, random_seed, file_folder, file_name, log_folder):
	print("Currently analyzing: "+str(file_name))
	name_no_ext=file_name.split(".")[0]
	f=("boogie "+
	   ("-p:O:timeout="+time_out_vc+" " if int(timeout)!=-1 else "")+
	   	"-p:O:sat.random_seed="+random_seed+" "
		"-p:O:nlsat.seed="+random_seed+" "
		"-p:O:fp.spacer.random_seed="+random_seed+" "
		"-p:O:smt.random_seed="+random_seed+" "
		"-p:O:sls.random_seed="+random_seed+" "
		"-trace "
		"-proverLog:"+log_folder+name_no_ext+".smt2 "
		"-traceTimes "
		"-useArrayTheory "+file_folder+file_name)

	log_file=open(log_folder+name_no_ext+"_boogie.log","w+")
	log_file.writelines(f)
	proc_run = subprocess.Popen(shlex.split(f), stdout=log_file, stderr=log_file)
	start = time.time()
	proc_run.wait()
	end = time.time()
	log_file.writelines("###Execution time: "+str(end-start))
	log_file.close()
	###########################################
	f = ("z3 "
		 "-v:10 "
		 "-st "+
		 ("-t:"+time_out_vc+" " if int(timeout)!=-1 else "")+
		 "smt.qi.profile=true "
		 "fp.spacer.iuc.debug_proof=true "
		 "fp.datalog.output_profile=true "
		 "smt.mbqi.trace=true "
		 "sat.local_search_dbg_flips=true "
		 "sat.random_seed=" + random_seed + " "
		 "nlsat.seed=" + random_seed + " "
		 "fp.spacer.random_seed=" + random_seed + " "
		 "smt.random_seed=" + random_seed + " "
		 "sls.random_seed=" + random_seed + " "
		 + log_folder + name_no_ext + ".smt2")

	log_file = open(log_folder + name_no_ext + "_z3_profile.profile", "w+")
	log_file.writelines("\n\n")
	log_file.writelines("###" + f + "\n")
	proc_run = subprocess.Popen(shlex.split(f), stdout=log_file, stderr=log_file)
	start = time.time()
	proc_run.wait()
	end = time.time()
	log_file.writelines("###Execution time: " + str(end - start))
	log_file.close()
	print("Done with : " + str(file_name))
	############################################

parser = MyParser(description='Run Boogie and Z3 on a set of programs. '
							  'By default, the analysis is done in parallel using all the available cores.')
parser.add_argument('res', type=str, metavar='<path_to_programs>',
                    help='the path to the folder with the boogie programs to analyze')
parser.add_argument('log', type=str, metavar='<path_for_logs>',
                    help='the path where to dump the log files (the folder has to be empty)')
parser.add_argument('-seed', type=int, metavar='<seed_value>',
                    help='the seed to use in z3. '
						 'In case you provide -1, we run z3 with a different seed for each program (default 0)', default=0)
parser.add_argument('-cores', type=int, metavar='<num_of_cores>',
                    help='the number of cores to use (default all)', default=multiprocessing.cpu_count())
parser.add_argument('-timeout', type=int, metavar='<timeout_per_single_vc>',
                    help='(soft) timeout in milliseconds, it kills the current VC. '
						 'In case you provide -1, we run z3 with no timeout  (default 60000)', default=60000)

args = parser.parse_args()

log = args.log
results = args.res
random_seed = args.seed
timeout = str(args.timeout)
num_cores = min(int(args.cores),multiprocessing.cpu_count())

if os.path.exists(log):
	folder = os.listdir(log)
	if len(folder) > 0:
		print("The log folder is not empty")
		exit(-1)
os.makedirs(log, exist_ok=True)

file_set = sorted(os.listdir(results))

pool = Pool(processes=num_cores, maxtasksperchild=2)
for file_name in file_set:
	if file_name.endswith(".bpl"):
		if random_seed==-1:
			tmp_seed=str(random.randint(0, len(file_set)))
			pool.apply_async(process_file, [timeout, tmp_seed, results, file_name, log])
		else:
			pool.apply_async(process_file, [timeout, random_seed, results, file_name, log])

pool.close()
pool.join()
