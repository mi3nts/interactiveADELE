# brain_visual3.py

## combine_last_dim
Helper function taken from Plotly Dash sample app "3D image partitioning" to create the brain data array
## create_brain_data
Helper function taken from Plotly Dash sample app "3D image partitioning" to create the brain data array

## make_3d_fig
Function that creates the 3D brain figure with 3 plot points
- input 
	- data_brain: the brain data array
	- df: the dataframe of all electrode locations
	- callback_value: the list of the 3 electrodes to plot
	- band: the band being plotted for the title
- output 
	- the figure with the 3d brain and three electrode plots

Description:
The function first creates a graphic object figure containing the default brain model using the input data_brain array. It then adds a figure widget that will contain the plot points. For each electrode name in callback_value, the corresponding data in df is extracted and adjusted to align with the brain using offsets and figure transformations. The modiified coordinate data is then used to plot the electrode location. The first electrode is colored red, the second one is colored orange, and the third is colored yellow.

## brain_visual3
Function that interprets files into a brain data array and cartesian coordinate dataframe
- input
	- data_brain_file: filename of the input nii file
    - coordinate_file: filename of the electrode cartesian coordinates
- output
	- data_brain: the brain data array, used to make the 3D model
	- df: the dataframe of all electrode locations
	
Description:
The function loads the input nii file as an image and then uses create_brain_data to make the brain data array. It then reads the coordinate file using the pandas library and stores the data onto a dataframe.


# dashboard.py
## graph_biometric_selection
Function that returns a figure with the biometric graph for a selected epoch
- input
	- biometric: string name of the biometric to be graphed
	- epochbm_dict: the data dictionary
	- epoch: int value of the epoch
- output
	- the figure of the biometric graph
	
Description:
The function uses the epoch value to retrieve the range for the graph from the dictionary, dividing by 500 to convert into seconds. It retrieves the data values from the dictionary using the epoch values as well. Both are used in a graphics object figure that displays the graph.

## interactive_dashboard
Function that creates the website
- input
	- None
- output
	- None

Description:
The function uses hardcoded values and file names to perform the necessary data processing and make a data dictionary. The slider values are defined using the dictionary. The data for the 3D model and electrode coordinates is imported from an external file. The website layout is defined from top to bottom, and it is followed by callbacks for each plot in order for them to update according to the slider value.
