# CODE TO AUTOMATICALLY CREATE EPOCHS BINS BASED ON DECISION TREE LOGIC 

# CODE AUTHORED BY: CHISOM SOPURUCHI	
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - num_bins  = number of bins the epoch should be split into
#   - Xy_array	= 2D array containing time index as one column and biometric variable as the other. This is the predictor.

# OUTPUTS
#   - epoch_dict = dictionary where key is epoch number and value is a list containing the epoch edges.
#   ~ example: {'1': [0, 99], '2': [100, 150]} dictionary with 2 epochs, where the first epoch spans the first hundred records of x and the second spans the next 51.

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================


# import libraries
import pandas as pd
import math
# import class
from sklearn.tree import DecisionTreeRegressor

def decisionTree_epochDetection(num_bins,Xy_array):
    # exception handling 
    # max_leaf_nodes must either be None or larger than 1
    # therefore num_bins must be at least 2
    if(num_bins < 2):
        print("num_bins must be greater than one")
        print("Changing value of num_bins to minimum possible value")
        num_bins = 2
    # fitting the regression tree X as features/predictor and y as label/target
    clf = DecisionTreeRegressor(max_leaf_nodes = num_bins).fit(Xy_array[:,0].reshape(-1, 1), Xy_array[:,1])
    
    # variables creation
    num_nodes = clf.tree_.node_count
    left_child = clf.tree_.children_left
    right_child = clf.tree_.children_right
    threshold = clf.tree_.threshold
    # list to store the bin edges
    bin_edges = [0,146884]

    # loop through all the nodes
    for i in range(num_nodes):
        # If the left and right child of a node is not the same(-1) we have an internal node
        # which we will append to bin_node list
        if left_child[i]!=right_child[i]:
            bin_edges.append(math.ceil(threshold[i]))
    # sort the nodes in increasing order
    bin_edges.sort()  
    # create dictionary to store epoch bin edges
    epoch_dict = {}
    # put in each dictionary index 2 consecutive bin edges 
    for i in range(num_bins):
        epoch_dict[str(i+1)] = [bin_edges[i], bin_edges[i+1]]
    return epoch_dict


