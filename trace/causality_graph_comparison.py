from setup import strict,depths,counterLimit,onlyOneFather,soundRelationship,removeUnknown,CutBeginTrueCutLeavesFalse
import os
import ntpath
from collections import Counter
from causality_graph import build_graph_nodes, build_dictionary_for_edges, remove_unknown, truncate_tree, \
    build_dictionary_for_diff, plot_single_trace

def build_dictionary_for_diff_lists(counter_labels_original, counter_labels_comparison):
    counter_label_diff = {}
    for key_original in counter_labels_original:
        comp_value = Counter(counter_labels_comparison.get(key_original, []))
        diff=comp_value - Counter(counter_labels_original[key_original])
        counter_label_diff[key_original] = list(diff.elements())

    keys_orig = counter_labels_original.keys()
    keys_cmp = counter_labels_comparison.keys()
    difference = keys_cmp - keys_orig
    for key in difference:
        counter_label_diff[key] = counter_labels_comparison[key]
    return counter_label_diff

def create_output_path(output_folder, name_original):
    if os.path.exists(output_folder + name_original):
        print("Output Folder already exists: " + str(name_original))
        exit(-1)
    else:
        os.makedirs(output_folder + name_original)

if __name__ == "__main__":

    folder_path_comparison = "./paxos/"
    trace_path_original = ".z3-trace-shuffle19"
    output_folder="./output/"

    name_original = ntpath.basename(trace_path_original).replace(".", "")

    create_output_path(output_folder, name_original)

    trace_path_comparisons = []

    for file in os.listdir(folder_path_comparison):
        if ".z3-trace" in file:
            trace_path_comparisons.append(folder_path_comparison+file)


    native_complete_nodes_original = build_graph_nodes(folder_path_comparison+trace_path_original)
    counter_labels_original, triggers_original, bindings_original = build_dictionary_for_edges(
        native_complete_nodes_original)

    native_complete_nodes_original = remove_unknown(native_complete_nodes_original)


    for trace_path_comparison in trace_path_comparisons:

        name_comparison = ntpath.basename(trace_path_comparison).replace(".", "")

        if name_comparison==name_original:
            continue
        create_output_path(output_folder, name_comparison)

        print(name_comparison)

        name_diff = "diff_" + name_original + "_" + name_comparison

        create_output_path(output_folder, name_diff)

        native_complete_nodes_comparison = build_graph_nodes(trace_path_comparison)

        print("Total number of nodes original:" + str(len(native_complete_nodes_original)))
        print("Total number of nodes comparison:" + str(len(native_complete_nodes_comparison)))

        print("Running...")

        native_complete_nodes_comparison = remove_unknown(native_complete_nodes_comparison)

        print("Total number of nodes original (without unknown):" + str(len(native_complete_nodes_original)))
        print("Total number of nodes comparison (without unknown):" + str(len(native_complete_nodes_comparison)))

        for depth in depths:

            complete_nodes_original = truncate_tree(depth, native_complete_nodes_original)
            complete_nodes_comparison = truncate_tree(depth, native_complete_nodes_comparison)

            print("Total number of nodes original (after truncate to depth=" + str(depth) + "):"
                  + str(len(complete_nodes_original)))
            print("Total number of nodes comparison (after truncate to depth=" + str(depth) + "):"
                  + str(len(complete_nodes_comparison)))

            counter_labels_original, triggers_original, bindings_original = build_dictionary_for_edges(complete_nodes_original)
            counter_labels_comparison, triggers_comparison, bindings_comparison = build_dictionary_for_edges(complete_nodes_comparison)

            diff_original_vs_comparison_labels      = build_dictionary_for_diff(counter_labels_original, counter_labels_comparison)
            diff_original_vs_comparison_triggers    = build_dictionary_for_diff_lists(triggers_original, triggers_comparison)
            diff_original_vs_comparison_bindings    = build_dictionary_for_diff_lists(bindings_original, bindings_comparison)

            for limit in counterLimit:

                final_path_original = output_folder+ name_original + "/"+"Depth_" + str(depth) + "_EdgeThreshold_" + str(limit)
                final_path_comparison = output_folder + name_comparison + "/" + "Depth_" + str(depth) + "_EdgeThreshold_" + str(limit)
                final_path_diff = output_folder + name_diff+ "/" + "Depth_" + str(depth) + "_EdgeThreshold_" + str(limit)

                plot_single_trace(final_path_original, counter_labels_original, triggers_original, bindings_original, limit)
                plot_single_trace(final_path_comparison, counter_labels_comparison, triggers_comparison, bindings_comparison, limit)
                plot_single_trace(final_path_diff, diff_original_vs_comparison_labels, diff_original_vs_comparison_triggers,
                                  diff_original_vs_comparison_triggers, limit)