import os
import shlex
import subprocess
import time


def elaborateResults():
    name_time={}
    for file_name in os.listdir("../log/"):
        if file_name.endswith(".log"):
            tmp=open("../log/"+file_name,"r").readlines()
            for line in tmp:
                if "time:" in line:
                    name_time[line.split("Execution time:")[0]]=line.split("Execution time:")[1]
    return name_time

def process_z3_file(file_name, log_folder):
    name_no_ext = file_name.split(".")[0]
    #f="z3 -t:1000 proof=true trace=true trace-file-name="+log_folder+name_no_ext+"_z3.log "+log_folder+file_name
    f = "z3 smt.qi.profile=true " + log_folder + file_name
    log_file=open(log_folder+name_no_ext+"_z3_profile.profile","w+")
    log_file.writelines("\n\n")
    log_file.writelines("###"+f+"\n")
    proc_run = subprocess.Popen(shlex.split(f), stdout=log_file, stderr=log_file)
    start = time.time()
    proc_run.wait()
    end = time.time()
    log_file.writelines("###Execution time: "+str(end-start))
    log_file.close()


name_time=elaborateResults()
view = [(float(value),key) for key,value in name_time.items()]
last_chunk=int(len(view)/1.0)
for key,val in sorted(view)[-last_chunk:]:
    print(val, key)

input()

for file_name in os.listdir("../log/"):
    if file_name.endswith(".smt2"):
        process_z3_file(file_name, "../log/")