from graphviz import Digraph
import ntpath

class Father:
    def __init__(self, id):
        self.id=id
        self.saturated=False

class Node:
    def __init__(self, finger_print):
        self.finger_print=finger_print
        self.label="unknown"
        self.fathers=[]
        self.enodes=[]
        self.children=[]
        self.istrue=False
        self.issat=False
        self.bindings = []
        self.line_number=-1

    def add_kid(self, kid):
        self.children.append(kid)

    def set_line_number(self, line_number):
        self.line_number=line_number

    def add_father(self, father_id):
        for father in self.fathers:
            if father.id==father_id:
                return
        self.fathers.append(Father(father_id))

    def add_enode(self, id_enode):
        if id_enode not in self.enodes:
            self.enodes.append(id_enode)

    def set_label(self, label):
        self.label=label

    def add_binding(self, binding):
        self.bindings.append(binding)

def get_new_match(line):
    if "New-Match:" in line:
        fathers = ((line.split("Father:")[1]).strip()).split()
        fp=((line.split(",")[0]).split("New-Match:")[1]).strip()
        if fp=="" or len(fathers)==0:
            print("Problem with finger_print or father!")
            exit(-1)
        node=Node(fp)
        for father in fathers:
            # if ( or ) in father means a term like (#id1 #id2). These two ids contribute indirectly
            # to the instantiations (e.g. with a rewriting). With the flag soundRelationship we are sound.
            if "(" in father or ")" in father:
                if soundRelationship:
                    father=father.replace("(","")
                    father=father.replace(")","")
                else:
                    continue
            if not father in node.fathers:
                node.add_father(father)
        return node

def get_label_node(line):
    if "###" in line:
        label = (line.split(",")[1]).strip()
        label=label.replace(":", ".")
        finger_print = ((line.split(",")[0]).split("###")[1]).strip()
        if finger_print=="" or label=="":
            print("Problem with finger_print or label!")
            exit(-1)
        return (finger_print, label)
    elif "New-Match:" in line:
        return ("-1xdummy", "dummy")
    else:
        print("Logic problem")
        exit(-1)

def get_binding(line):
    if ":" in line:
        binding=(line.split(":")[1]).strip()
        return binding

def get_enode(line):
    if "EN:" in line:
        enode=(line.split("EN:")[1]).strip()
        return enode

def build_single_instantiation(lines, index, current_node, label):
    current_node.set_label(label)
    current_node.set_line_number(index+1)
    index = index + 1
    binding = 0
    while index < len(lines) and not "###" in lines[index] and not "New-Match:" in lines[index]:
        line = lines[index]
        if str(binding) + ":" in line:
            current_node.add_binding(get_binding(line))
            binding=binding+1
        elif "EN:" in line:
            current_node.add_enode(get_enode(line))
        elif "Instance reduced to true" in line:
            current_node.istrue = True
        elif "Instance already satisfied (dummy)" in line:
            current_node.issat = True
        elif "(cache)" in line:
            pass
        else:
            print("Unknown property for a node!")
            exit(-1)
        index = index + 1
    return index, current_node, (current_node.istrue or current_node.issat)

def get_node_from_finger_print(finger_print, nodes):
    i = len(nodes) - 1
    while i >= 0:
        if nodes[i].finger_print==finger_print:
            return nodes[i]
        i=i-1
    return None

def find_father_in_list(nodes, node):
    i=len(nodes)-1
    while i>=0:
        for father in node.fathers:
            if father.id in nodes[i].enodes:
                if not father.saturated:
                    nodes[i].add_kid(node)
                    father.saturated=True
                    if onlyOneFather:
                        return
        i=i-1
    return


def build_graph_nodes(file_path):
    lines=open(file_path, "r").readlines()
    nodes=[]
    index=0
    node_index=0

    while index < len(lines):
        #print("Nodes:"+str(len(nodes)))
        while index<len(lines) and "New-Match:" in lines[index]:
            line = lines[index]
            #Collect all new-match tags.
            if "New-Match:" in line:
                new_node=get_new_match(line)
                nodes.append(new_node)
                index=index+1
        if node_index < len(nodes):
            while index < len(lines) and node_index<len(nodes):
                current_node=nodes[node_index]
                fp, label = get_label_node(lines[index])
                if fp != current_node.finger_print:
                    #print("Finger print does not match! Ok if trace is without dummies.")
                    del nodes[node_index]
                else:
                    index, current_node, is_dummy = build_single_instantiation(lines, index, current_node, label)
                    find_father_in_list(nodes, current_node)
                    node_index=node_index+1
        else:
            while index < len(lines):
                if "New-Match:" in lines[index]:
                    break
                fp, label = get_label_node(lines[index])
                father_node=get_node_from_finger_print(fp, nodes)
                if father_node==None:
                    print("(Cache Instantiation) Father node not found!")
                    exit(-1)
                current_node=Node(fp)
                nodes.append(current_node)
                father_node.add_kid(current_node)
                index, current_node, is_dummy = build_single_instantiation(lines, index, current_node, label)
                node_index=node_index+1
    return nodes

def remove_unknown(nodes):
    if removeUnknown:
        i = 0
        while (i < len(nodes)):
            if nodes[i].label == 'unknown':
                del nodes[i]
            else:
                i = i + 1
    return nodes

def truncate_tree(depth, nodes):
    if depth != -1:
        if CutBeginTrueCutLeavesFalse:
            nodes = nodes[0:depth]
        else:
            nodes = nodes[-depth:-1]
    return nodes

def build_dictionary_for_edges(nodes):
    counter_labels={}
    for ind_1, node_1 in enumerate(nodes):
        if strict:
            for kid in node_1.children:
                if (node_1.label, kid.label) in counter_labels:
                    counter_labels[(node_1.label, kid.label)] += 1
                else:
                    counter_labels[(node_1.label, kid.label)] = 1
        else:
            for kid in node_1.children:
                counter_labels[(node_1, kid)] = 1
    return counter_labels

def plot_single_trace(counter_labels, limit, trace_path):
    dot = Digraph(comment='Graph', strict=strict)

    for val in counter_labels:
        if strict:
            if counter_labels[val] > limit or counter_labels[val] < -limit: #consider both negative and positive edges
                dot.node(val[0], val[0], fillcolor="white", style='filled')
                dot.edge(val[0], val[1], label=str(counter_labels[val]))
        else:
            if val[0].istrue:
                col = "lightblue"
            elif val[0].issat:
                col = "tomato"
            else:
                col = "white"
            dot.node(val[0].label + "_" + str(val[0].line_number), val[0].label + "_" + str(val[0].line_number),
                     fillcolor=col, style='filled')
            dot.edge(val[0].label + "_" + str(val[0].line_number), val[1].label + "_" + str(val[1].line_number))

    dot.render("output/" + ntpath.basename(trace_path) + "/Depth_" + str(depth) + "_EdgeThreshold_" + str(
        limit) + "_OneFather_" + str(onlyOneFather) + "_Strict_" + str(strict), view=False, format="pdf")
    # dot.render("output/"+ntpath.basename(trace_path)+"/Depth_"+str(depth)+"_EdgeThreshold_"+str(limit)+"_OneFather_"+str(onlyOneFather)+"_Strict_"+str(strict), view=False, format="gv")

def build_dictionary_for_diff(counter_labels_original, counter_labels_comparison):
    counter_label_diff={}
    for key_original in counter_labels_original:
        comp_value=counter_labels_comparison.get(key_original,0)
        counter_label_diff[key_original]=comp_value-counter_labels_original[key_original]

    keys_orig = counter_labels_original.keys()
    keys_cmp = counter_labels_comparison.keys()
    difference = keys_cmp - keys_orig
    for key in difference:
        counter_label_diff[key] = counter_labels_comparison[key]

    return counter_label_diff

#Merge quantifiers by QID.
strict=True
#Remove instantiations that are incomplete (due to timeout)
removeUnknown=True
#Consider transitive relations between quantifeirs (true) or only direct ones (false).
soundRelationship=False
#Connect with all fathers. In case it is False, we climb up to the root to look for "all the fathers".
#In case you set to True, we consider only the closest father.
onlyOneFather=False
#In case depth is !=-1 we cut from the root, or from the leaves.
CutBeginTrueCutLeavesFalse=True
#Depth of the analysis. -1 means all nodes.

depths=[1000, 5000, 10000, 20000, -1]
#Ignore edges with countere less than:
counterLimit=[0, 5, 10, 20, 50, 100, 500]


trace_path_original="../logs_is_step_a_paxos/.z3-trace_8"
trace_path_comparisons=["../logs_is_step_a_paxos/.z3-trace_0",
                        "../logs_is_step_a_paxos/.z3-trace_1",
                        "../logs_is_step_a_paxos/.z3-trace_2",
                        "../logs_is_step_a_paxos/.z3-trace_3",
                        "../logs_is_step_a_paxos/.z3-trace_4",
                        "../logs_is_step_a_paxos/.z3-trace_5",
                        "../logs_is_step_a_paxos/.z3-trace_6",
                        "../logs_is_step_a_paxos/.z3-trace_7",
                        "../logs_is_step_a_paxos/.z3-trace_9",
                        "../logs_is_step_a_paxos/.z3-trace_10"]

native_complete_nodes_original = build_graph_nodes(trace_path_original)
native_complete_nodes_original = remove_unknown(native_complete_nodes_original)

for trace_path_comparison in trace_path_comparisons:
    print(ntpath.basename(trace_path_comparison))

    native_complete_nodes_comparison=build_graph_nodes(trace_path_comparison)

    print("Total number of nodes original:"+str(len(native_complete_nodes_original)))
    print("Total number of nodes comparison:"+str(len(native_complete_nodes_comparison)))

    print("Running...")

    native_complete_nodes_comparison=remove_unknown(native_complete_nodes_comparison)

    print("Total number of nodes original (without unknown):"+str(len(native_complete_nodes_original)))
    print("Total number of nodes comparison (without unknown):"+str(len(native_complete_nodes_comparison)))

    for depth in depths:

        complete_nodes_original = truncate_tree(depth, native_complete_nodes_original)
        complete_nodes_comparison = truncate_tree(depth, native_complete_nodes_comparison)

        print("Total number of nodes original (after truncate to depth="+str(depth)+"):" + str(len(complete_nodes_original)))
        print("Total number of nodes comparison (after truncate to depth="+str(depth)+"):" + str(len(complete_nodes_comparison)))

        counter_labels_original = build_dictionary_for_edges(complete_nodes_original)
        counter_labels_comparison = build_dictionary_for_edges(complete_nodes_comparison)

        diff_original_vs_comparison = build_dictionary_for_diff(counter_labels_original, counter_labels_comparison)

        for limit in counterLimit:

            plot_single_trace(counter_labels_original,limit,trace_path_original)
            plot_single_trace(counter_labels_comparison,limit,trace_path_comparison)
            plot_single_trace(diff_original_vs_comparison, limit, "diff_"+ntpath.basename(trace_path_original)+"_"+ntpath.basename(trace_path_comparison))