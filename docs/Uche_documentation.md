
# decisionTree_epochDetection.py
This function takes as
Inputs
  - num_bins  = number of bins the epoch should be split into
  - Xy_array     = 2D array containing time index as one column and biometric variable as the other.
and returns as
Outputs
  - epoch_dict = dictionary where key is epoch number and value is a list containing the epoch edges.
  ~ example: {'1': [0, 99], '2': [100, 150]} dictionary with 2 epochs, where the first epoch spans the first hundred records of x and the second spans the next 51.

#### This function uses decision trees to split the data into epochs.
## Concepts explained:
### What are epochs?
Epochs per our use refer to a data set split into multiple bins based on specific criteria. The criteria could be peaks as displayed below:
 
Figure 1.1 represents Heartrate against UTC Timestamps graph split into epochs based on the peaks.
### What are decision trees?
Decision Trees are classification and prediction tools. A simple example is trying to decide what to wear potential factors that could influence your decision are:
              > The weather
              > Budget
              > The occasion you are attending
              > Your style, among other criteria.
The factors listed would serve as predictors while "what to wear" is the target.
We make use of scikit-learn decision trees which comprises of DecisionTreeClassifiers and DecisionTreeRegressors. The Regressor takes a floating-point value for the target value whereas, the Classifier takes an integer. We make use of a regression tree.
Decision trees require a target(generally denoted as y) and predictor(s)(generally denoted X). In our case, we use the timesteps as predictors and the biometric variable as the target.           


 
## A detailed description of the function
We import the libraries and classes needed. Then a regressor tree is created by specifying the maximum number of leaf nodes, which cannot be less than two; therefore, we impose a condition to ensure the maximum number of leaves is at least 2. The decision tree gets fitted, and its size reshaped because the function naturally takes a multi-columned structure, but ours has only one column.
We loop through each node using the node_count tree_ attribute, checking if the left child is the same as the right child to distinguish internal nodes from leaf nodes. What happens when the left and right children are the same value? This condition is impossible if they are not leaf nodes. The children_right and children_left tree_ attributes, which we use to access the left and right children of a node, return the id of the child node accessed. The left and right children of leaf nodes have the same id value -1. The threshold of the leaf nodes is rounded using the math library's ceil function and appended to a list, bin_edges, which contains the start index 0 and final index(the length of the input Xy_array). We sort the variable bin_edges to accurately reflect the threshold at which each leaf gets split when reading the tree from left to right. Every two consecutive bin_edges represents an epoch and gets stored in a dictionary which we returned.







# biometricVar_per_epoch.py
This function takes as
Inputs
 - epoch_dict = dictionary where keys are integers corresponding to each epoch, and values are epoch time index ranges
  - eeg_data = pandas dataframe with columns as biometric variables and rows as timesteps
and returns as
Outputs
  - epochbm_dict = dictionary where keys are integers corresponding to each epoch and values are a list containing both epoch time index ranges and a pandas dataframe where rows are timesteps, and 1 column is heart value with rolling average.
  ~ example: {'1': [[0, 99], dataframe], '2': [[100, 150], dataframe]} dictionary with 2 epochs, where the first epoch spans the first hundred records of x, the second spans the next 51. Dataframe represents a pandas data frame with index as the records and columns as pre-determined rolling averaged biometric variables spanned by each epoch.
  ~ example: {'1': [[0, 99], dataframe]}, If the pre-determined biometric variable was 'HR', then the dataframe would have as index 0-99 and as columns, rolling averaged HR spanning index(0-99) in the input dataframe (eeg_data).  

#### This function computes the (non)biometric variables per epoch. These variables must be in the dataframe derived from the function read_eeg.

## Concepts explained:
### What is a rolling average?
Rolling average is a method used to reduce the noise in a data set. See the plotted graph below: 
 
Figure 2.1 represents a Temperature against index dataset on which rolling average was applied. The red line has the rolling average applied while the cyan does not.
Considering only the cyan part of the graph, we can't derive information from the graph because of our dataset. Can we streamline the dataset such that this graph is useful? Yes, this is where rolling average comes into play. We determine a window size on which we apply mean/average. The window is moved through the data retaining its size, we choose a windows size that will not lose critical insignt into the data while smoothening it out. The red line graph is a suitable rolled average graph.

## A detailed description of the function
We import the needed libraries. Next, we format the SpO2 column of the input dataframe, eeg_data, so that it accurately represents the percentage of blood oxygen saturation. The column names we want accessed are inputted in a list then converted to a dataframe, rolled_df, on which we apply rolling average to smoothen the data. Finally, a dictionary containing the range of the epochs and the columns from rolled_df with indices corresponding to those in the outlined range is returned.  



