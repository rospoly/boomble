from graphviz import Digraph
import ntpath
from causality_graph import build_graph_nodes, build_dictionary_for_edges, remove_unknown, truncate_tree, \
    build_dictionary_for_diff, plot_single_trace

# Merge quantifiers by QID.
strict = True
# Remove instantiations that are incomplete (due to timeout)
removeUnknown = True
# Consider transitive relations between quantifiers instantiation(true) or only direct dependencies (false).
soundRelationship = False
# Connect with all fathers. In case it is False, we climb up to the root to look for "all the fathers".
# In case you set to True, we consider only the closest father.
onlyOneFather = False
# In case depth is !=-1 we cut from the root, or from the leaves.
CutBeginTrueCutLeavesFalse = True
# Depth of the analysis. -1 means all nodes.
depths = [1000, 10000, 20000, -1]
# Ignore edges with weights less than:
counterLimit = [0, 50, 100, 500]

trace_path_original = "./.z3-trace"
output_folder="./output/" + ntpath.basename(trace_path_original) + "/"

trace_path_comparisons = []
for i in range(0, 101):
    trace_path_comparisons.append("../logs_is_step_a_paxos_desugared/.z3-trace-shuffle" + str(i))

print(trace_path_comparisons)

native_complete_nodes_original = build_graph_nodes(trace_path_original)
counter_labels_original, triggers_original, bindings_original = build_dictionary_for_edges(
    native_complete_nodes_original)

native_complete_nodes_original = remove_unknown(native_complete_nodes_original)

for trace_path_comparison in trace_path_comparisons:

    print(ntpath.basename(trace_path_comparison))

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
        diff_original_vs_comparison_triggers    = build_dictionary_for_diff(triggers_original, triggers_comparison)
        diff_original_vs_comparison_bindings    = build_dictionary_for_diff(bindings_original, bindings_comparison)

        for limit in counterLimit:
            plot_single_trace(counter_labels_original, triggers_original, bindings_original, limit, )
            plot_single_trace(counter_labels_comparison, triggers_comparison, bindings_comparison, limit, trace_path_comparison)
            plot_single_trace(diff_original_vs_comparison_labels, diff_original_vs_comparison_triggers,
                              diff_original_vs_comparison_triggers, limit)