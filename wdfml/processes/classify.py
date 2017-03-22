import numpy as np
from sklearn import decomposition
from sklearn import neural_network
from sklearn import manifold, preprocessing
import sklearn.mixture  as mix
from sklearn.pipeline import Pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def GMMpipeline( matrix, upper_bound, pca_components, spectral_emb_coeff, n_neighbors ):
    '''
    This function clusters the input matrix using the GaussianMixture algorithm (gaussian mixture model)
    The number of clusters is found by running the algorithm for n_components = 2 to upper_bound
    and chosing the model which minimized the BIC.

    Returns the labels for each observation.
    :type upper_bound: int
    :param upper_bound: max number of clusters
    
    :type matrix: numpy matrix
    '''
    if (len(matrix) < upper_bound + 1):
        print ("\n\tWARNING: Not enough samples (less than the minimum %i) to run GaussianMixture." % (upper_bound))
        print ("\t Only one cluster is returned.\n")
        return [0] * len(matrix)
    pca = decomposition.PCA(n_components=pca_components, whiten=True)
    Embedding = manifold.SpectralEmbedding(n_components=spectral_emb_coeff,
                                           affinity='nearest_neighbors',
                                           gamma=None, random_state=0,
                                           n_neighbors=n_neighbors)
    GaussianMixture = mix.GaussianMixture(n_components=upper_bound, covariance_type='full', \
                                          random_state=1, max_iter=1000,n_init=1)

    clf=Pipeline([('pca',pca),('gmm',GaussianMixture)])
    clf.fit(matrix)
    return clf


