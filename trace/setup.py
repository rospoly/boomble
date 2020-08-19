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
depths = [1000, -1]
# Ignore edges with weights less than:
counterLimit = [0, 100, 500, 1000]