'''
    File name: autoencoder_test_MLP_sid.py
    Author: Lloyd Windrim
    Date created: August 2019
    Python package: deephyp

    Description: An example script for testing a trained MLP (or dense) autoencoder on the Pavia Uni hyperspectral
    dataset, using the spectral angle divergence (SID) loss function. Saves a figure of the latent space for each
    (plotting the two features with the highest variance).

'''

import scipy.io
import matplotlib.pyplot as plt
import os
import numpy as np
from utils import reporthook
try:
    from urllib import urlretrieve # python2
except:
    from urllib.request import urlretrieve # python3

# import toolbox libraries
import sys
sys.path.insert(0, '..')
from deephyp import autoencoder
from deephyp import data


if __name__ == '__main__':

    # read data into numpy array
    mat = scipy.io.loadmat( 'PaviaU.mat' )
    img = mat[ 'paviaU' ]

    # create a hyperspectral dataset object from the numpy array
    hypData = data.HypImg( img )

    # pre-process data to make the model easier to train
    hypData.pre_process( 'minmax' )

    # setup a network from a config file
    net = autoencoder.mlp_1D_network( configFile=os.path.join('models','test_ae_mlp_sid','config.json') )

    # assign previously trained parameters to the network, and name model
    net.add_model( addr=os.path.join('models','test_ae_mlp_sid','epoch_100'), modelName='sid_100' )

    # feed forward hyperspectral dataset through encoder (get latent encoding)
    dataZ = net.encoder( modelName='sid_100', dataSamples=hypData.spectraPrep )

    # feed forward latent encoding through decoder (get reconstruction)
    dataY = net.decoder(modelName='sid_100', dataZ=dataZ)


    #--------- visualisation ----------------------------------------

    # download dataset ground truth pixel labels (if already downloaded, comment this out)
    urlretrieve( 'http://www.ehu.eus/ccwintco/uploads/5/50/PaviaU_gt.mat',
                       os.path.join(os.getcwd(), 'PaviaU_gt.mat'), reporthook )

    # read labels into numpy array
    mat_gt = scipy.io.loadmat( 'PaviaU_gt.mat' )
    img_gt = mat_gt['paviaU_gt']
    gt = np.reshape( img_gt , ( -1 ) )


    # save a scatter plot image of 2 of 3 latent dimensions
    idx = np.argsort(-np.std(dataZ, axis=0))
    fig, ax = plt.subplots()
    for i,gt_class in enumerate(['asphalt', 'meadow', 'gravel','tree','painted metal','bare soil','bitumen','brick','shadow']):
        ax.scatter(dataZ[gt == i+1, idx[0]], dataZ[gt == i+1, idx[1]], c='C%i'%i,s=5,label=gt_class)
    ax.legend()
    plt.title('latent representation: sid')
    plt.xlabel('latent feature %i' % (idx[0]))
    plt.ylabel('latent feature %i' % (idx[1]))
    plt.savefig(os.path.join('results', 'test_mlp_scatter_sid.png'))

