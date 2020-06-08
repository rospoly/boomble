import shutil
from multiprocessing.pool import ThreadPool, Pool
import os
import subprocess
import shlex
import time

def process_file(file_folder, file_name, log_folder):
	print(file_name)
	name_no_ext=file_name.split(".")[0]
	f="boogie -trace -proverLog:"+log_folder+name_no_ext+".smt2 -traceTimes -useArrayTheory "+file_folder+file_name
	log_file=open(log_folder+name_no_ext+"_boogie.log","w+")
	log_file.writelines(f)
	proc_run = subprocess.Popen(shlex.split(f), stdout=log_file, stderr=log_file)
	start = time.time()
	proc_run.wait()
	end = time.time()
	log_file.writelines("Execution time: "+str(end-start))
	log_file.close()

pool = Pool(processes=6, maxtasksperchild=3)

log = "../log/"
if os.path.exists(log):
	folder = os.listdir(log)
	if len(folder) > 0:
		print("The log folder is not empty")
		exit(-1)

os.makedirs(log)

file_set = os.listdir("../results/").sort(key=lambda f: int(filter(str.isdigit, f)))
for file_name in file_set:
	if file_name.endswith(".bpl"):
		pool.apply_async(process_file, ["../results/", file_name, log])

pool.close()
pool.join()
