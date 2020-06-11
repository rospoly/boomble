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

def get_exe_time_from_z3_profiling(log_folder, file_name):
    tmp = open(log_folder + file_name, "r").readlines()
    exe_time=-1
    for line in tmp:
        if "###Execution time:" in line:
            exe_time = line.split("Execution time:")[1]
    return float(exe_time)

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


def get_last_percent_of_shuffles(percentage):
    name_time=elaborateResults()
    view = [(float(value),key) for key,value in name_time.items()]
    last_chunk=int(len(view)/percentage)
    x_val=[]
    y_val=[]

    for key,val in sorted(view)[-last_chunk:]:
        x_val.append(val)
        y_val.append(key)
    return x_val, y_val

def get_plot_exe_time_boogie():
    plt.figure()
    plt.plot(x_val, y_val, '-o', color='blue', label="boogie")
    problems=len(x_val)
    plt.xticks([0, int(problems/4),int(problems/2), int((problems*3)/4), int(problems)], ["0", str(int(problems/4)), str(int(problems/2)), str(int((problems*3)/4)),str(int(problems))])
    plt.title("exe time (boogie)")
    plt.legend()
    plt.ylabel('Time (sec)')
    plt.xlabel('programs')

def get_plot_exe_time_z3_vs_boogie():
    plt.figure()
    plt.title("Exe time boogie vs z3 (with profile)")
    name_time=elaborateResults()
    view = [(float(value),key) for key,value in name_time.items()]
    last_chunk=int(len(view)/1.0)
    filename_val=[]
    boogie_val=[]
    z3_val=[]

    for key,val in sorted(view)[-last_chunk:]:
        z3_key=get_exe_time_from_z3_profiling("../log/", val.split(".")[0]+"_z3_profile.profile")
        if z3_key != -1:
            filename_val.append(val)
            boogie_val.append(float(key))
            z3_val.append(float(z3_key))

    plt.plot(range(0, len(filename_val)), boogie_val, '-o', color="blue", label="boogie")
    plt.plot(range(0, len(filename_val)), z3_val, '-o', color="red", label="z3")
    plt.ylabel('Time (sec)')
    plt.xlabel('programs')
    len_comparison=len(boogie_val)
    plt.xticks([0, int(len_comparison/4),int(len_comparison/2), int((len_comparison*3)/4), int(len_comparison)], ["0", str(int(len_comparison/4)), str(int(len_comparison/2)), str(int((len_comparison*3)/4)),str(int(len_comparison))])
    plt.legend()

def global_quantifiers_instantiation_analysis(x_val, y_val):
    plt.figure()
    original_file="tmp0_z3_profile.profile"
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
    plt.bar(x_enumerate, pos_values, align='center', color='blue', label="more instantiations")
    plt.bar(x_enumerate, neg_values, align='center', color='red', label="less instantiations")

    p=False
    for ind, value in enumerate(more_values):
        if value != 0:
            if not p:
                p=True
                plt.scatter(ind, y=pos_values[ind], color='blue', s=40, label="new quantifiers")
            else:
                plt.scatter(ind, y=pos_values[ind], color='blue', s=40)

    p=False
    for ind, value in enumerate(less_values):
        if value != 0:
            if not p:
                p=True
                plt.scatter(ind, y=neg_values[ind], color='red', s=40, label="missing quantifiers")
            else:
                plt.scatter(ind, y=neg_values[ind], color='red', s=40)

    plt.plot([original_index, original_index], [min(neg_values), max(pos_values)], color="black", linewidth=3, linestyle='dashed', label="mutation 0")
    plt.xticks([])
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    plt.ylabel('abs num. of quant. instantiations')
    plt.xlabel('programs (sort by exe time)')
    plt.ylim([-2.5*10**5, 10**6])
    plt.title(original_file.split(".")[0])
    plt.legend()

x_val, y_val = get_last_percent_of_shuffles(1.0)
get_plot_exe_time_boogie()
get_plot_exe_time_z3_vs_boogie()
global_quantifiers_instantiation_analysis(x_val,y_val)
plt.show()