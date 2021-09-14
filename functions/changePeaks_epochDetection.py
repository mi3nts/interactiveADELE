# CODE TO AUTOMATICALLY DETECT EPOCHS BASED ON PEAKS IN INPUT BIOMETRIC VARIABLE
# CHANGES

# CODE AUTHORED BY: SHAWHIN TALEBI
# PROJECT: interactiveADELE
# GitHub: https://github.com/mi3nts/interactiveADELE

# INPUTS
#   - x = 1D numpy array for biometric variable to use for epoch definition
#   - numEpochs = integer. number of desired epochs.
#   - minEpochLength = integer. minimum duration in seconds of epochs.
#   - sampleRate = integer. sample rate in hertz data contained in x

# OUTPUTS
#   - epoch_dict = dictionary where key is epoch number and value is a list
#   containing the epoch edges.
#   ~ example: {'1': [0, 99], '2': [100, 150]} dictionary with 2 epochs, where
#   the first epoch spans the first hundred records of x and the second spans
#   the next 51.

# ADELE DEPENDENCIES
#   - none

# ADELE DEPENDERS
#   - none
# ==============================================================================

# import modules
import pandas as pd
import numpy as np

# import functions
from statsmodels.sandbox.tsa import movmean
from scipy.signal import find_peaks


def changePeaks_epochDetect(x, numEpochs, minEpochLength, sampleRate):

    # compute min epoch size based on min
    minEpochSize = minEpochLength*sampleRate;

    # PREP DATA
    # ~~~~~~~~~~~
    # replace negative values with nan
    x[x<0] = np.nan

    # interpolate over nans
    x = x.interpolate()
    # perform rolling average
    x = x.rolling(minEpochSize).mean()

    # compute gradient
    grad = np.gradient(x);
    # square and perform rolling average
    grad2 = grad**2
    grad2_rolled = movmean(grad2, minEpochSize, 'centered')

    # FIND PEAKS
    # ~~~~~~~~~~~
    # find peaks
    pks, prop = find_peaks(grad2_rolled, distance=minEpochSize);

    # compute number of peaks
    numPeaks = len(pks)

    # sort peak locations and stort in desceding order
    igrad2_rolled_sorted = np.argsort(grad2_rolled[pks])
    igrad2_rolled_sorted = pks[igrad2_rolled_sorted[::-1]]

    # EDGE CASES
    # ~~~~~~~~~~~
    # case: not enough peaks for input number of epochs
    if numPeaks<numEpochs-1:
        print("~~~ Not enough peaks to make " + str(numEpochs) +
        " epochs. Using max number " + str(numPeaks+1) + " instead. ~~~")
        numEpochs = numPeaks+1

    # case: last peak is last record
    if igrad2_rolled_sorted[0]==len(x):
        numEpochs = numEpochs + 1

    # GET EPOCH EDGES AND SAVE IN DICTIONARY
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # get locations of tallest peaks and sort in ascending order
    middleEpochEdges = igrad2_rolled_sorted[:numEpochs-1][::-1]

    # define final epoch edges
    epochEdges = np.append(0, middleEpochEdges, len(x))

    # create dictionary with epoch labels and edges
    epoch_dict = {}
    for i in range(len(epochEdges)-1):
        epoch_dict[str(i+1)] = [epochEdges[i], epochEdges[i+1]]

    return epoch_dict
