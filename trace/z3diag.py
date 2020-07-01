# -*- python 3 -*-

# giant term table.  Maps name '#23' or 'datatype#3' to a tuple like "pi" or ('mk-app', '#23', 'pi')

def print_quant(id, level=0, cutoff=None):
    kids = term_dict[id]
    print("(", kids[1], sep="", end=" ")
    num_vars = kids[2]
    vars = tuple([("var_" + str(i)) for i in range(0, int(num_vars))])
    print("(", " ".join(vars), ")", sep="", end="")
    for child_ind in kids[3:]:
        print(" ", sep="", end="")
        print_term_as_tree(child_ind, level+1, cutoff)
    print(")")

def meaning(thing):
    return meaning_dict.get(thing, thing)

def print_term_as_tree(id, level=0, cutoff=None):
#    print(id, ":", end=" ", flush=True)
    mng = meaning_dict.get(id, None);
    if mng is not None:
        print(id, ": ",  mng, sep="", end="")
        return
    if cutoff is not None and level > cutoff:
        print(" ... ", sep="", end="")
        return
    term_info = term_dict[id]
    term_type = term_info[0]
    kids = term_info[1:]
    if term_type == 'app' or term_type == 'proof':
        if len(kids) == 1:
            print(id, ":", meaning(kids[0]), end="", flush=True)
        else:
            print(id, ":(", meaning(kids[0]), sep="", end="")
            for child_ind in kids[1:]:
                print("\n", " "*2*(level+1), sep="", end="")
                print_term_as_tree(child_ind, level+1)
            print(")", sep="", end="")
    elif term_type == 'var':
        print('var_', kids[0], sep="", end="")
    if level==0:
        print("")


def process_token_list(token_list):
    global term_dict, meaning_dict, var_name_dict, quant_inst_count_dict
    kind = token_list[0]
    if kind == '[mk-app]':
        tmp = ['app']
        tmp.extend(token_list[2:])
        term_dict[token_list[1]] = tuple(tmp)
    elif kind == '[mk-var]':
        tmp = ['var']
        tmp.extend(token_list[2:])
        term_dict[token_list[1]] = tuple(tmp)
    elif kind == '[mk-quant]':
        tmp = ['quant']
        tmp.extend(token_list[2:])
        term_dict[token_list[1]] = tuple(tmp)
#        print("****************\nquant:", token_list[1])
#        print_quant(token_list[1])
    elif kind == '[mk-lambda]':
        tmp = ['lambda']
        tmp.extend(token_list[2:])
        term_dict[token_list[1]] = tuple(tmp)
#        print("****************\nlambda:", token_list[1])
#        print_quant(token_list[1])
    elif kind == '[attach-var-names]':
        var_name_dict[token_list[1]] = tuple(token_list[1:])
    elif kind == '[mk-proof]':
        tmp = ['proof']
        tmp.extend(token_list[2:])
        term_dict[token_list[1]] = tuple(tmp)
            #        print("****************\nproof:", token_list[1])
            #        print_term_as_tree(token_list[1], level=0)
    elif kind == '[attach-meaning]':
        meaning_dict[token_list[1]] = "".join(token_list[3:])
    elif kind == '[new-match]':
        # Trigger caused the quantifier instantiation
        # for now, just incr quantifier count
        quantifier_id = token_list[2]
        quant_inst_count_dict[quantifier_id] = quant_inst_count_dict.get(quantifier_id, 0) + 1
    elif kind == '[inst-discovered]':
        #usually used for theory axioms "theory-solving" in the trace
        pass


def show_inst_counts(how_many=100):
    global quant_inst_count_dict
    pairs = sorted(list(quant_inst_count_dict.items()), key=lambda pair: pair[1], reverse=True)
    for pair in pairs:
        if how_many == 0:
            break
        print(pair[0], pair[1], term_dict[pair[0]][1])
        how_many -= 1


def process_log(log_file_name):
    linecount = 0
    with open(log_file_name) as fp:
        for line in fp:
            token_list = line.rstrip().split(' ')
#            print(token_list, flush=True)
            process_token_list(token_list)
#            if linecount == 20000:
#                break
            linecount += 1
            if linecount % 10000 == 0:
                print(".", sep="", end="", flush=True)
    print("")

def main():
    global term_dict, meaning_dict, var_name_dict, quant_inst_count_dict
    term_dict = dict();
    meaning_dict = dict();
    var_name_dict = dict();
    quant_inst_count_dict = dict();
#    process_log("foo.log")
#    process_log("head.log")
    process_log("z3.log")
#    process_log("/Users/dill/Work/CODE/libra/language/move-prover/bug41_z3.log")
    ## show the top 100 most frequent instantiations
    show_inst_counts(100)

if __name__ == "__main__":
    main()



# print(term_dict)
