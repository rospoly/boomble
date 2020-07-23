from graphviz import Digraph

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
        self.fathers.append(father_id)

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
    else:
        print("Problem with ### in line: "+str(line)+"\n")
        raise Exception("Parser Exception!")

def get_binding(line):
    if ":" in line:
        binding=(line.split(":")[1]).strip()
        return binding

def get_enode(line):
    if "EN:" in line:
        enode=(line.split("EN:")[1]).strip()
        return enode

def build_single_instantiation(lines, index, current_node):
    fp, label = get_label_node(lines[index])
    current_node.set_label(label)
    current_node.set_line_number(index+1)
    if not fp in current_node.finger_print:
        print("Finger print does not match!")
        exit(-1)
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
    return index, current_node

def get_node_from_finger_print(finger_print, nodes):
    for node in nodes[::-1]:
        if node.finger_print==finger_print:
            return node
    print("Node not found")
    return None

def build_graph_nodes(file_path):
    lines=open(file_path, "r").readlines()
    nodes=[]
    index=0
    node_index=0
    try:
        while index < len(lines):
            while index<len(lines) and "New-Match:" in lines[index]:
                line = lines[index]
                if "New-Match:" in line:
                    nodes.append(get_new_match(line))
                    index=index+1
                    continue
            if node_index < len(nodes):
                while index < len(lines) and node_index<len(nodes):
                    current_node=nodes[node_index]
                    index, current_node = build_single_instantiation(lines, index, current_node)
                    node_index=node_index+1
            else:
                while index < len(lines):
                    if "New-Match:" in lines[index]:
                        break
                    fp, label = get_label_node(lines[index])
                    father_node=get_node_from_finger_print(fp, nodes)
                    if father_node==None:
                        print("Father node not found!")
                        exit(-1)
                    current_node=Node(fp)
                    nodes.append(current_node)
                    father_node.add_kid(current_node)
                    index, current_node = build_single_instantiation(lines, index, current_node)
                    node_index = node_index + 1
    except Exception as e:
        print("Exception:"+str(e))
    return nodes

#Merge quantifiers by QID.
strict=True
#Remove dummy instantiations.
noDummy=True
#Remove instantiations that are incomplete (due to timeout)
removeUnknown=True
#Consider transitive relations between quantifeirs (true) or only direct ones (false).
soundRelationship=False
#Depth of the analysis. -1 means all nodes.
depth=-1

dot = Digraph(comment='Graph', strict=strict)
nodes=build_graph_nodes(".z3-trace")
print("Running...")

if removeUnknown:
    while(nodes[-1].label=="unknown"):
        nodes=nodes[:-1]

if depth!=-1:
    nodes=nodes[0:depth]

for node in nodes:
    #print(node.label, node.finger_print, node.fathers, node.enodes)
    if noDummy and (node.istrue or node.issat):
        continue
    if strict:
        dot.node(node.label, node.label)
    else:
        if node.istrue:
            col="lightblue"
        elif node.issat:
            col="tomato"
        else:
            col="white"
        dot.node(str(node.line_number)+"_"+node.finger_print, node.label, fillcolor=col, style='filled')

#print(len(nodes))
counter_labels={}

for ind_1, node_1 in enumerate(nodes):
    for node_2 in nodes[0:ind_1][::-1]:
        if node_1!=node_2:
            if noDummy and (node_1.istrue or node_1.issat):
                continue
            #commons=set(node_2.enodes).intersection(node_1.fathers)
            match=any(i in node_1.fathers for i in node_2.enodes)
            if match>0 or (node_1 in node_2.children):
                if strict:
                    if (node_2.label, node_1.label) in counter_labels:
                        counter_labels[(node_2.label, node_1.label)] += 1
                    else:
                        counter_labels[(node_2.label, node_1.label)] = 1
                else:
                    counter_labels[(str(node_2.line_number)+"_"+node_2.finger_print, str(node_1.line_number)+"_"+node_1.finger_print)] = 1
                #in case we remove this break we climb up to the root to look for "all the fathers".
                #in case you keep this break, we consider only the closest father.
                break

for val in counter_labels:
    if strict:
        dot.edge(val[0], val[1], label=str(counter_labels[val]))
    else:
        dot.edge(val[0], val[1])

dot.render('test-output/round-table.gv', view=True)