import os
from graphviz import Digraph
import ntpath

global_fathers_dict={}

#We saturate the father the first time the node match a father.
class Father:
    def __init__(self, id):
        self.id = id
        self.saturated = False

class Node:
    def __init__(self, finger_print):
        self.finger_print = finger_print
        self.label = "unknown"
        self.fathers = []
        self.trigger = "unknown"
        self.enodes = []
        self.children = []
        self.istrue = False
        self.issat = False
        self.bindings = []
        self.line_number = -1

    def set_trigger(self, trigger):
        self.trigger = trigger

    def add_kid(self, kid):
        if kid not in self.children:
            self.children.append(kid)

    def set_line_number(self, line_number):
        self.line_number = line_number

    def add_father(self, father_id):
        for father in self.fathers:
            if father_id==father.id:
                return
        self.fathers.append(Father(father_id))

    def add_enode(self, id_enode):
        self.add_enode(id_enode)

    def add_enode(self, id_enode):
        if id_enode not in self.enodes:
            self.enodes.append(id_enode)

    def set_label(self, label):
        self.label = label

    def add_binding(self, binding):
        self.bindings.append(binding)

    def get_bindings_as_string(self):
        ret="("
        inside=False
        for bind in self.bindings:
            inside=True
            ret=ret+str(bind)+", "
        if inside:
            ret=ret[:-2]
        ret=ret+")"
        return ret


def get_new_match(lines, index):
    line=lines[index]
    if "New-Match:" in line:
        fp = get_fingerprint(lines,index)
        trigger, index = get_trigger(lines, index)
        fathers = get_fathers(lines, index)

        if fp == "" or len(fathers) == 0:
            print("Problem with finger_print or father!")
            exit(-1)

        node = Node(fp)
        node.set_trigger(trigger)
        for father_dirty in fathers:
            father = father_dirty.strip()
            # if ( or ) in father means a term like (#id1 #id2). These two ids contribute indirectly
            # to the instantiations (e.g. with a rewriting). With the flag soundRelationship we are sound.
            if "(" in father or ")" in father:
                if soundRelationship:
                    father = father.replace("(", "")
                    father = father.replace(")", "")
                else:
                    continue
            node.add_father(father)
        return node, index


def get_label_node(line):
    if "###" in line:
        label = (line.split(",")[1]).strip()
        label = label.replace(":", ".")
        finger_print = ((line.split(",")[0]).split("###")[1]).strip()
        if finger_print == "" or label == "":
            print("Problem with finger_print or label!")
            exit(-1)
        return (finger_print, label)
    elif "New-Match:" in line:
        return ("-1xdummy", "dummy")
    else:
        print("Logic problem")
        exit(-1)

def get_fingerprint(lines, index):
    if "New-Match:" in lines[index]:
        return ((lines[index].split(",")[0]).split("New-Match:")[1]).strip()
    return "0xUnknown"

def get_binding(num,lines, index):
    if str(num)+":" in lines[index]:
        end=get_index_containing_substring(lines,index,";")+1
        binding_dirty = (" ".join(lines[index:end])).strip()
        binding_dirty = binding_dirty.split(";")[0]
        binding = binding_dirty.split(str(num)+":")[1].strip()
        binding = binding.split()
        binding = " ".join(binding)

        while index<len(lines) and ";" not in lines[index]:
            index=index+1
        return binding, index
    return "", index

def get_index_containing_substring(lines, index, substring):
    if substring in lines[index]:
        return index
    else:
        return get_index_containing_substring(lines, index+1, substring)

def get_trigger(lines, index):
    if "Pat:" in lines[index]:
        end=get_index_containing_substring(lines,index,", Father:")+1
        trigger_dirty = (" ".join(lines[index:end])).strip()
        trigger_dirty = trigger_dirty.split(", Father:")[0]
        trigger = trigger_dirty.split("Pat:")[1].strip()
        trigger = trigger.split()
        trigger = " ".join(trigger)
        while index<len(lines) and ", Father:" not in lines[index]:
            index=index+1
        return trigger,index
    return "", index

def get_fathers(lines, index):
    if "Father:" in lines[index]:
        fathers=lines[index].split(", Father:")[1].strip()
        return fathers.split()
    return []

def get_enode(line):
    if "EN:" in line:
        enode = (line.split("EN:")[1]).strip()
        return enode
    return ""

def build_single_instantiation(lines, index, current_node, label):
    current_node.set_label(label)
    current_node.set_line_number(index + 1)
    index = index + 1
    binding = 0
    while index < len(lines) and not "###" in lines[index] and not "New-Match:" in lines[index]:
        line = lines[index]
        if str(binding) + ":" in line:
            value_binding, index = get_binding(binding, lines, index)
            current_node.add_binding(value_binding)
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
    for enode in current_node.enodes:
        global_fathers_dict[enode]=current_node
    return index, current_node, (current_node.istrue or current_node.issat)


def get_node_from_finger_print(finger_print, nodes):
    i = len(nodes) - 1
    while i >= 0:
        if nodes[i].finger_print == finger_print:
            return nodes[i]
        i = i - 1
    return None


def find_father_in_list(node):
    father_exists=False
    for father in node.fathers:
        #In case the father has been previously saturated you cannot use it again.
        if not father.saturated:
            potential_father=global_fathers_dict.get(father.id)
            if not potential_father==None:
                father_exists=True
                father.saturated = True
                potential_father.add_kid(node)
                if onlyOneFather:
                    return True
    return father_exists


def build_graph_nodes(file_path):
    lines = open(file_path, "r").readlines()
    nodes = []
    index = 0
    node_index = 0

    ground_term = Node("0x00000000")
    ground_term.set_trigger("unknown")
    ground_term.set_label("ground_terms")

    try:
        while index < len(lines):
            print("Nodes:"+str(len(nodes)))
            while index < len(lines) and "New-Match:" in lines[index]:
                line = lines[index]
                # Collect all new-match tags.
                if "New-Match:" in line:
                    new_node, index = get_new_match(lines, index)
                    nodes.append(new_node)
                    index = index + 1
            if node_index < len(nodes):
                while index < len(lines) and node_index < len(nodes):
                    current_node = nodes[node_index]
                    fp, label = get_label_node(lines[index])
                    if fp != current_node.finger_print:
                        del nodes[node_index]
                    else:
                        index, current_node, is_dummy = build_single_instantiation(lines, index, current_node, label)
                        res=find_father_in_list(current_node)
                        if not res:
                            ground_term.add_kid(current_node)
                        node_index = node_index + 1
            else:
                while index < len(lines):
                    if "New-Match:" in lines[index]:
                        break
                    fp, label = get_label_node(lines[index])
                    father_node = get_node_from_finger_print(fp, nodes)
                    if father_node == None:
                        print("(Cache Instantiation) Father node not found!")
                        exit(-1)
                    current_node = Node(fp)
                    current_node.set_trigger("Cached Instantiation")
                    nodes.append(current_node)
                    father_node.add_kid(current_node)
                    index, current_node, is_dummy = build_single_instantiation(lines, index, current_node, label)
                    node_index = node_index + 1
    except:
        print("Something went wrong while parsing the trace.")
    finally:
        nodes.insert(0,ground_term)
    print("Done with parsing the trace")
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
    counter_labels = {}
    triggers = {}
    bindings = {}
    for ind_1, node_1 in enumerate(nodes):
        if strict:
            for kid in node_1.children:
                if (node_1.label, kid.label) in counter_labels:
                    counter_labels[(node_1.label, kid.label)] += 1
                    triggers[(node_1.label, kid.label)].append(kid.trigger)
                    bindings[(node_1.label, kid.label)].append(kid.get_bindings_as_string())
                else:
                    counter_labels[(node_1.label, kid.label)] = 1
                    triggers[(node_1.label, kid.label)] = []
                    triggers[(node_1.label, kid.label)].append(kid.trigger)
                    bindings[(node_1.label, kid.label)] = []
                    bindings[(node_1.label, kid.label)].append(kid.get_bindings_as_string())
        else:
            for kid in node_1.children:
                counter_labels[(node_1, kid)] = 1
                triggers[(node_1, kid)]=[kid.trigger]
                bindings[(node_1, kid)]=[kid.get_bindings_as_string()]
    return counter_labels, triggers, bindings

def create_node_with_color(dot, node):
    if node.istrue:
        col = "lightblue"
    elif node.issat:
        col = "tomato"
    else:
        col = "white"
    dot.node(node.label + "_" + str(node.line_number), node.label + "_" + str(node.line_number),fillcolor=col, style='filled')

def log_trigger_or_binding_line(file, source, dest, trigger_list):
    file.write("###"+source + " -> "+ dest + "###\n")
    trigger_set=set(trigger_list)
    for trigger in trigger_set:
        file.write("\tValue: "+str(trigger)+", Counter:"+str(trigger_list.count(trigger))+"\n")
    file.write("######\n")
    file.flush()

def plot_single_trace(counter_labels, triggers_original, bindings_original, limit):
    dot = Digraph(comment='Graph', strict=strict)
    name=output_folder+"Depth_" + str(depth) + \
         "_EdgeThreshold_" + str(limit) + "_OneFather_" + str(onlyOneFather) + "_Strict_" + str(strict)
    triggers=open(name+"_triggers.txt","w+")
    bindings=open(name+"_bindings.txt","w+")
    for val in counter_labels:
        if strict:
            if counter_labels[val] > limit or counter_labels[val] < -limit:  # consider both negative and positive edges
                dot.node(val[0], val[0], fillcolor="white", style='filled')
                dot.node(val[1], val[1], fillcolor="white", style='filled')
                dot.edge(val[0], val[1], label=str(counter_labels[val]))
                log_trigger_or_binding_line(triggers,val[0],val[1],triggers_original[val])
                log_trigger_or_binding_line(bindings,val[0],val[1],bindings_original[val])
        else:
            create_node_with_color(dot,val[0])
            create_node_with_color(dot,val[1])
            dot.edge(val[0].label + "_" + str(val[0].line_number), val[1].label + "_" + str(val[1].line_number))
            log_trigger_or_binding_line(triggers, val[0].label + "_" + str(val[0].line_number),
                                        val[1].label + "_" + str(val[1].line_number), triggers_original[val])
            log_trigger_or_binding_line(bindings, val[0].label + "_" + str(val[0].line_number),
                                        val[1].label + "_" + str(val[1].line_number), bindings_original[val])

    triggers.close()
    bindings.close()
    dot.render(name, view=False, format="pdf")
    sum_edges=compute_sum_of_all_edges(name)
    print("Removing all edges with weight < "+str(limit)+", total sum of the weights = "+str(sum_edges))


def build_dictionary_for_diff(counter_labels_original, counter_labels_comparison):
    counter_label_diff = {}
    for key_original in counter_labels_original:
        comp_value = counter_labels_comparison.get(key_original, 0)
        counter_label_diff[key_original] = comp_value - counter_labels_original[key_original]

    keys_orig = counter_labels_original.keys()
    keys_cmp = counter_labels_comparison.keys()
    difference = keys_cmp - keys_orig
    for key in difference:
        counter_label_diff[key] = counter_labels_comparison[key]
    return counter_label_diff

def compute_sum_of_all_edges(name):
    file = open(name, "r").readlines()
    sum = 0
    for line in file:
        if "[label=" in line and not "color" in line:
            sum = sum + int(line.split("[label=")[1].split("]")[0])
    return sum

# Merge quantifiers by QID. Usefull when playing with Move-Prover benchmarks.
strict = True
# Remove instantiations that are incomplete (due to the timeout)
removeUnknown = True
# Consider transitive relations between quantifiers instantiation(true) or only direct dependencies (false).
soundRelationship = False
# Connect with all fathers. In case it is False, we climb up to the root to look for "all the fathers".
# In case you set to True, we consider only the closest father (unsound but faster).
onlyOneFather = False
# In case depth is !=-1 we cut from the root, or from the leaves.
CutBeginTrueCutLeavesFalse = True
# Depth of the analysis. -1 means all nodes.
depths = [1000, 10000, 20000, -1]
# Ignore edges with weights less than:
counterLimit = [0, 50, 100, 500, 1000]

trace_path_original=".z3-trace_mul"

output_folder="./output/" + ntpath.basename(trace_path_original) + "/"

if os.path.exists(output_folder):
    print("Output Folder already exists")
    exit(-1)
else:
    os.makedirs(output_folder)

native_complete_nodes_original = build_graph_nodes(trace_path_original)

print("Total number of nodes original:"+str(len(native_complete_nodes_original)))

native_complete_nodes_original = remove_unknown(native_complete_nodes_original)

print("Running...")

print("Total number of nodes original (without unknown):"+str(len(native_complete_nodes_original)))



for depth in depths:

    complete_nodes_original = truncate_tree(depth, native_complete_nodes_original)
    print("Total number of nodes original (after truncate to depth="+str(depth)+"):" + str(len(complete_nodes_original)))
    counter_labels_original, triggers_original, bindings_original = build_dictionary_for_edges(complete_nodes_original)

    for limit in counterLimit:
        plot_single_trace(counter_labels_original, triggers_original, bindings_original, limit)
