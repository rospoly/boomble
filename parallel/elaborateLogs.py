import os
import shlex
import subprocess
import time
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 30})

def elaborateResults():
    name_time={}
    for file_name in os.listdir("../log/"):
        if file_name.endswith(".log"):
            tmp=open("../log/"+file_name,"r").readlines()
            for line in tmp:
                if "time:" in line:
                    clean_file_name=(line.split("Execution time:")[0]).split("/")[-1].replace("#","")
                    name_time[clean_file_name]=line.split("Execution time:")[1]
    return name_time

def get_number_instances_line_qdiff(line):
    inst=(line.split("(")[1]).split("inst")[0]
    return int(inst)

def compare_z3_profiles(log_folder, orig_profile, compare_profile):
    #name_no_ext = file_name.split(".")[0]
    f = "qprofdiff " + log_folder + orig_profile + " " + log_folder + compare_profile
    proc_run = subprocess.Popen(shlex.split(f), stdout=subprocess.PIPE)
    output,errors=proc_run.communicate()
    plus=0
    equal=0
    minus=0
    more=0
    less=0
    #Note. Everything refer to the compare profile: + means compare profile has more inst. than orig.
    # > means compare_profile has something new wrt to orig.
    # < means compare_profile does not have something that is in orig.
    output=output.decode('unicode_escape')
    for line in output.split("\n"):
        if line.startswith("+"):
            plus = plus + get_number_instances_line_qdiff(line)
        elif line.startswith("="):
            equal = equal + get_number_instances_line_qdiff(line)
        elif line.startswith("-"):
            minus = minus + get_number_instances_line_qdiff(line)
        elif line.startswith(">"):
            more = more + get_number_instances_line_qdiff(line)
        elif line.startswith("<"):
            less = less + get_number_instances_line_qdiff(line)
    return plus,equal,minus,more,less


name_time=elaborateResults()
view = [(float(value),key) for key,value in name_time.items()]
last_chunk=int(len(view)/1.0)
x_val=[]
y_val=[]

plt.figure()
for key,val in sorted(view)[-last_chunk:]:
    x_val.append(val)
    y_val.append(key)
    print(val, key)

plt.bar(x_val, y_val, align='center', color='blue', linewidth=10)
problems=len(x_val)
plt.xticks([0, int(problems/4),int(problems/2), int((problems*3)/4), int(problems)], ["0", str(int(problems/4)), str(int(problems/2)), str(int((problems*3)/4)),str(int(problems))])
plt.title("Execution Times")
plt.ylabel('Time (sec)')
plt.xlabel('programs')

plt.figure()
original_file="tmp19_z3_profile.profile"
original_index=-1
pos_values=[]
neg_values=[]
more_values=[]
less_values=[]
equal_values=[]

for ind, file_name in enumerate(x_val):
    if file_name==original_file.split("_")[0]+".bpl":
        original_index=ind
    file_name=file_name.split(".")[0]+"_z3_profile.profile"
    plus,equal,minus,more,less=compare_z3_profiles("../log/", original_file, file_name)
    pos_values.append(plus)
    neg_values.append(minus)
    more_values.append(more)
    less_values.append(less)
    equal_values.append(equal)

x_enumerate=range(0,len(x_val))
plt.bar(x_enumerate, pos_values, align='center', color='blue')
plt.bar(x_enumerate, neg_values, align='center', color='red')

for ind, value in enumerate(more_values):
    if value != 0:
        plt.scatter(ind, y=pos_values[ind], color='blue', s=40)

for ind, value in enumerate(less_values):
    if value != 0:
        plt.scatter(ind, y=neg_values[ind], color='red', s=40)

plt.plot([original_index, original_index], [min(neg_values), max(pos_values)], color="black", linestyle='dashed')
#plt.bar(x_val, more_values, align='center', color='black')
#plt.bar(x_val, less_values, align='center', color='black')
#plt.bar(x_val, equal_values, align='center', color='blue')
plt.xticks([])
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.ylabel('num of quant. instantiations')
plt.xlabel('programs')
plt.title(original_file.split(".")[0])
plt.show()