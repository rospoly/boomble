import os
import shlex
import subprocess
import time
import numpy as np
import random
from matplotlib.pyplot import cm
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 20})

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

def get_partial_distribution_given_vector(list, percentage):
    if percentage>1.0:
        print("Illegal probability measure")
        exit(-1)
    vector=np.array(list)
    summation=sum(vector)
    vector=vector/summation
    cum_vector=np.cumsum(vector)
    i=0
    while i<len(cum_vector) and cum_vector[i]<percentage:
        i=i+1
    i=min(i, len(cum_vector)-1)
    return i

def get_chunk_of_shuffles_given_percentage(percentage, reverse):
    name_time=elaborateResults()
    view = [(float(value),key) for key,value in name_time.items()]
    x_val=[]
    y_val=[]
    tmp=sorted(view, reverse=reverse)
    for key,val in tmp:
        x_val.append(val)
        y_val.append(key)
    i=get_partial_distribution_given_vector(y_val,percentage)+1
    return x_val[0:i], y_val[0:i]

def get_plot_exe_time_boogie(x_val, y_val):
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


def get_set_of_worst_vcs(log_folder, percentagePrograms, percentageVCs):
    x_val, y_val = get_chunk_of_shuffles_given_percentage(percentagePrograms, reverse=True)
    ret={}
    for file_name in x_val:
        name_of_vcs, exe_times, orig_indxs = get_vcs_in_exe_time_order(log_folder, file_name.split(".")[0] + "_boogie.log")
        i = get_partial_distribution_given_vector(exe_times, percentageVCs) + 1
        #i=len(exe_times)
        for val in range(0,i):
            if file_name.split(".")[0] in ret:
                ret[file_name.split(".")[0]].append((name_of_vcs[val],exe_times[val], orig_indxs[val]))
            else:
                ret[file_name.split(".")[0]]=[]
                ret[file_name.split(".")[0]].append((name_of_vcs[val],exe_times[val], orig_indxs[val]))
    return ret

def get_vcs_in_exe_time_order(log_folder, file_name):
    file=open(log_folder+file_name, "r").read()
    conditions=file.split("\n\n")
    name_of_vcs= []
    exe_times  = []
    orig_index = []
    for ind, cond in enumerate(conditions):
        name_of_vc="N/A"
        init_time=None
        end_time = None
        for line in cond.splitlines():
            if "Verifying" in line:
                name_of_vc=(line.split("Verifying")[1]).split("...")[0]
            elif "Starting implementation verification" in line:
                init_time=float((line.split("[")[1]).split("s")[0])
            elif "Finished implementation verification" in line:
                end_time=float((line.split("[")[1]).split("s")[0])
        if name_of_vc is not None and init_time is not None and end_time is not None:
            name_of_vcs.append(name_of_vc)
            exe_times.append(end_time-init_time)
            orig_index.append(ind)
    sorted_zip=sorted(zip(name_of_vcs, exe_times, orig_index), key=lambda pair: pair[1], reverse=True)
    name_of_vcs = [x for x,y,z in sorted_zip]
    exe_times = [y for x,y,z in sorted_zip]
    orig_indexs = [z for x,y,z in sorted_zip]
    return name_of_vcs,exe_times, orig_indexs

def check_profiling_completes(logfolder,filename):
    prof_file=open(logfolder+filename, "r").readlines()
    if "###Execution time:" in prof_file[::-1][0]:
        return True
    return False

def global_quantifiers_instantiation_analysis(percentage, original_file):
    if not check_profiling_completes("../log/", original_file + "_z3_profile.profile"):
        print("File picked for comparison did not complete profiling")
        exit(-1)
    x_val, y_val = get_chunk_of_shuffles_given_percentage(percentage, reverse=False)
    plt.figure(figsize=(17, 10))
    #original_file="tmp19"
    original_index=-1
    pos_values=[]
    neg_values=[]
    more_values=[]
    less_values=[]
    equal_values=[]
    program_names = []
    for ind, file_name in enumerate(x_val):
        file_name = file_name.split(".")[0] + "_z3_profile.profile"
        if check_profiling_completes("../log/",file_name):
            if file_name==original_file.split("_")[0]+".bpl":
                original_index=ind
            plus,equal,minus,more,less=compare_z3_profiles("../log/", original_file+"_z3_profile.profile", file_name)
            pos_values.append(plus)
            neg_values.append(minus)
            more_values.append(more)
            less_values.append(less)
            equal_values.append(equal)
            program_names.append(file_name)

    x_enumerate=range(0,len(program_names))
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

def extract_quantifiers_given_index_in_profile(logfolder, filename, index):
    profile = open(logfolder+filename+"_z3_profile.profile", "r").read()
    pattern="#####"
    vcs_sections=profile.replace("unsat", pattern).replace("sat", pattern).split(pattern)
    if index < len(vcs_sections):
        return vcs_sections[index]
    else:
        return ""

def dump_partial_quantifiers_to_file(logfolder, filename, index, partial_quantifiers):
    profile = open(logfolder + filename + "_z3_profile_"+str(index)+".syntprofile" , "w+")
    profile.write(partial_quantifiers)
    profile.close()
    return (filename + "_z3_profile_"+str(index)+".syntprofile")

def specific_quantifiers_instantiation_analysis(log_folder, original_file, percentagePrograms, percentageVCs):
    if not check_profiling_completes("../log/", original_file + "_z3_profile.profile"):
        print("File picked for comparison did not complete profiling")
        exit(-1)
    worst_dict_file_vcs_indexs = get_set_of_worst_vcs("../log/", percentagePrograms, 1)
    ordered_filenames, ordered_exe_time = get_chunk_of_shuffles_given_percentage(1, reverse=False)
    plot_index=ordered_filenames.index(original_file+".bpl")
    vcs_counter={}
    plt.figure(figsize=(17, 10))
    for file_name in worst_dict_file_vcs_indexs:
        name_of_vcs, exe_times, orig_indxs = get_vcs_in_exe_time_order(log_folder, file_name.split(".")[0] + "_boogie.log")
        ind_range = get_partial_distribution_given_vector(exe_times, percentageVCs) + 1
        for i in range(0, ind_range):
            tmp_name=worst_dict_file_vcs_indexs[file_name][i][0]
            if tmp_name in vcs_counter:
                vcs_counter[tmp_name]=vcs_counter[tmp_name]+1
            else:
                vcs_counter[tmp_name]=1
    most_common_vcs=sorted(vcs_counter.items(), key=lambda x: x[1], reverse=True)
    all_dict_file_vcs_indexs = get_set_of_worst_vcs("../log/", 1, 1)
    color = iter(cm.rainbow(np.linspace(0, 1, len(most_common_vcs))))
    for index_common_vc,(vc_common,cntr) in enumerate(most_common_vcs):
        program_names = []
        pos_values = []
        neg_values = []
        more_values = []
        less_values = []
        equal_values = []
        original_index = -1.5
        for orig_vs, orig_time, orig_index in all_dict_file_vcs_indexs[original_file]:
            if orig_vs == vc_common:
                original_index = orig_index
                continue
        for ord_filename in ordered_filenames:
            file=ord_filename.split(".")[0]
            if check_profiling_completes("../log/", file+"_z3_profile.profile"):
                program_names.append(file)
                for vc_all, time, index in all_dict_file_vcs_indexs[file]:
                    if vc_common==vc_all:
                        # open the file and get quantifiers.
                        partial_profile_compare=extract_quantifiers_given_index_in_profile(log_folder, file, index)
                        partial_profile_orig=extract_quantifiers_given_index_in_profile(log_folder, original_file, original_index)
                        # dump the result to file
                        cmp_partial_file =dump_partial_quantifiers_to_file(log_folder, file, index, partial_profile_compare)
                        orig_partial_file=dump_partial_quantifiers_to_file(log_folder, original_file, original_index, partial_profile_orig)
                        #compare the partial files
                        plus,equal,minus,more,less=compare_z3_profiles(log_folder, orig_partial_file, cmp_partial_file)

                        pos_values.append(plus)
                        neg_values.append(minus)
                        more_values.append(more)
                        less_values.append(less)
                        equal_values.append(equal)
                        continue

        x_enumerate = range(0, len(program_names))

        plt.plot([plot_index, plot_index], [min(neg_values), max(pos_values)], color="black", linewidth=3, linestyle='dashed', label="mutation 0" if index_common_vc==0 else "")
        current_color=next(color)
        plt.bar(x_enumerate, pos_values, align='center', color = current_color, width=1.0, label=vc_common, linewidth=3)
        plt.bar(x_enumerate, neg_values, align='center', color = current_color, width=1.0, label="", linewidth=3)

        #p=False
        #for ind, value in enumerate(more_values):
        #    if value != 0:
        #        if not p:
        #            p=True
        #            plt.scatter(ind, y=pos_values[ind], color='blue', s=40, label="new quantifiers")
        #        else:
        #            plt.scatter(ind, y=pos_values[ind], color='blue', s=40)

        #p=False
        #for ind, value in enumerate(less_values):
        #    if value != 0:
        #        if not p:
        #            p=True
        #            plt.scatter(ind, y=neg_values[ind], color='red', s=40, label="missing quantifiers")
        #        else:
        #            plt.scatter(ind, y=neg_values[ind], color='red', s=40)

        plt.xticks([])
        #plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        plt.ylabel('abs num. of quant. instantiations')
        plt.xlabel('programs (sort by exe time)')
        #plt.ylim([-2.5*10**5, 10**6])
        plt.title("Analysis of worst VCs")
    plt.legend()


#get_plot_exe_time_boogie()
#get_plot_exe_time_z3_vs_boogie()
#global_quantifiers_instantiation_analysis(1.0, "tmp19")
specific_quantifiers_instantiation_analysis("../log/", "tmp19", 0.6, 0.5)
plt.show()