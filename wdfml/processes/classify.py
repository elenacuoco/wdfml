import numpy as np
from sklearn import decomposition
from sklearn import neural_network
from sklearn import manifold, preprocessing
import sklearn.mixture  as mix
from sklearn.pipeline import Pipeline
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.cluster import Birch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def GMMpipeline(matrix, upper_bound, pca_components, spectral_emb_coeff, n_neighbors):
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
        print("\n\tWARNING: Not enough samples (less than the minimum %i) to run GaussianMixture." % (upper_bound))
        print("\t Only one cluster is returned.\n")
        return [0] * len(matrix)
    pca = decomposition.PCA(n_components=pca_components, whiten=True)
    Embedding = manifold.SpectralEmbedding(n_components=spectral_emb_coeff,
                                           affinity='nearest_neighbors',
                                           gamma=None, random_state=0,
                                           n_neighbors=n_neighbors)
    GaussianMixture = mix.GaussianMixture(n_components=upper_bound, covariance_type='full', \
                                          random_state=1, max_iter=1000, n_init=1)

    clf = Pipeline([('pca', pca), ('gmm', GaussianMixture)])
    clf.fit(matrix)
    return clf


def gaussian_mixture(matrix, upper_bound):
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
        logging.info(
            "\n\tWARNING: Not enough samples (less than the minimum %i) to run GaussianMixture." % (upper_bound))
        logging.info("\t Only one cluster is returned.\n")
        return [0] * len(matrix)

    j = 0
    lowest_bic = np.infty
    bic = []
    n_components_range = range(1, upper_bound + 1)
    cv_types = ['spherical', 'tied', 'diag', 'full']
    for cv_type in cv_types:
        for n in n_components_range:
            GaussianMixture = mix.GaussianMixture(n_components=n, covariance_type=cv_type, random_state=1,
                                                  max_iter=1000, n_init=1)
            GaussianMixture.fit(matrix)
            bic.append(GaussianMixture.bic(matrix))
            if bic[-1] < lowest_bic:
                lowest_bic = bic[-1]
                best_GaussianMixture = GaussianMixture

    best_GaussianMixture.fit(matrix)
    res = best_GaussianMixture.predict(matrix)

    return res

def BGMM(matrix, n_clusters):
    '''
    This function clusters the input matrix using the GaussianMixture algorithm (gaussian mixture model)
    The number of clusters is found by running the algorithm for n_components = 2 to upper_bound
    and chosing the model which minimized the BIC.

    Returns the labels for each observation.
    :type upper_bound: int
    :param upper_bound: max number of clusters

    :type matrix: numpy matrix
    '''




    GaussianMixture = mix.BayesianGaussianMixture(n_components=n_clusters, covariance_type="full", random_state=1,
                                                  max_iter=1000, n_init=1)
    GaussianMixture.fit(matrix)

    res = GaussianMixture.predict(matrix)

    return res

def birtch_partial(matrix,n_cluster):
    brc = Birch(branching_factor=100, n_clusters=n_cluster, threshold=1.0, compute_labels = True)
    model=brc.partial_fit(matrix)

    res = model.predict(matrix)

    return res

class WDFMLClassify(object):
    def __init__(self, Waves_Coefficients):
        """


        :type Waves_Coefficients: numpy matrix

        :param Waves_Coefficients: numpy Matrix containing the Wavelets coefficients

        """

        self.Waves_Coefficients = Waves_Coefficients

    def PreprocessingSimple(self):
        """
        simple Standard Scaler
        """
        self.X_red = preprocessing.StandardScaler().fit_transform(self.Waves_Coefficients)

        return self.X_red

    def PreprocessingSimplePCA(self, PCA_coefficients, whiten=True):
        """
        simple PCA
        """
        self.PCA_coefficients = PCA_coefficients

        self.pca = decomposition.PCA(n_components=self.PCA_coefficients, whiten=whiten)
        self.X_red = self.pca.fit_transform(self.Waves_Coefficients)
        return self.X_red

    def PreprocessingEmb(self, MNE_coefficients, N_neighbors):
        """
        :type MNE_coefficients: int

        :param MNE_coefficients: number of coefficients for mns projection

        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients

        self.N_neighbors = N_neighbors
        self.X_red = preprocessing.StandardScaler().fit_transform(self.Waves_Coefficients)
        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=0,
                                                    n_neighbors=self.N_neighbors)

        self.X_red = self.Embedding.fit_transform(self.X_red)
        return self.X_red

    def PreprocessingPCA(self, PCA_coefficients, MNE_coefficients, N_neighbors, whiten=True):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors
        self.pca = decomposition.PCA(n_components=self.PCA_coefficients, whiten=whiten)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=11,
                                                    n_neighbors=self.N_neighbors)

        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red

    def PreprocessingICA(self, PCA_coefficients, MNE_coefficients, N_neighbors, whiten=True):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors
        self.pca = decomposition.FastICA(n_components=self.PCA_coefficients, algorithm='parallel', whiten=whiten,
                                         fun='logcosh', fun_args=None, max_iter=200, tol=0.0001, w_init=None,
                                         random_state=0)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=11,
                                                    n_neighbors=self.N_neighbors)

        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red

    def PreprocessingSparsePCA(self, PCA_coefficients, MNE_coefficients, N_neighbors):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors

        self.pca = decomposition.SparsePCA(n_components=self.PCA_coefficients,
                                           alpha=0.5, ridge_alpha=0.01, max_iter=1000,
                                           tol=1e-06, method='lars',
                                           n_jobs=-1, U_init=None,
                                           V_init=None, verbose=False,
                                           random_state=0)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=0,
                                                    n_neighbors=self.N_neighbors)
        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red

    def PreprocessingRandomizedPCA(self, PCA_coefficients, MNE_coefficients, N_neighbors, whiten=True):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors

        self.pca = decomposition.RandomizedPCA(n_components=self.PCA_coefficients, whiten=whiten)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=0,
                                                    n_neighbors=self.N_neighbors)
        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red

    def PreprocessingPCA(self, PCA_coefficients, MNE_coefficients, N_neighbors, whiten=True):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors
        self.pca = decomposition.PCA(n_components=self.PCA_coefficients, whiten=whiten)
        # self.pca = decomposition.SparsePCA(n_components=self.PCA_coefficients, random_state=0)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=0,
                                                    n_neighbors=self.N_neighbors)

        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red

    def PreprocessingPCATSNE(self, PCA_coefficients, MNE_coefficients, N_neighbors, whiten=True):
        """
        :type MNE_coefficients: int
        :type PCA_coefficients: int
        :param MNE_coefficients: number of coefficnents for mns projection
        :param PCA_coefficients: number of n_coefficients for PCA transform
        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients
        self.PCA_coefficients = PCA_coefficients
        self.N_neighbors = N_neighbors
        self.pca = decomposition.PCA(n_components=self.PCA_coefficients, whiten=whiten)
        # self.pca = decomposition.SparsePCA(n_components=self.PCA_coefficients, random_state=0)

        self.Embedding = manifold.TSNE(n_components=2, perplexity=40.0, early_exaggeration=4.0,
                                       learning_rate=100.0, n_iter=1000, n_iter_without_progress=30,
                                       min_grad_norm=1e-07, \
                                       metric='euclidean', init='random', verbose=0, random_state=0,
                                       method='barnes_hut', angle=0.5)

        self.X_pca = self.pca.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_pca)
        return self.X_red
    def PreprocessingTSNE(self, MNE_coefficients, N_neighbors, whiten=True):
        """
        :param MNE_coefficients: number of coefficnents for mns projection

        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients

        self.N_neighbors = N_neighbors


        self.Embedding = manifold.TSNE(n_components=2, perplexity=40.0, early_exaggeration=4.0,
                                       learning_rate=100.0, n_iter=1000, n_iter_without_progress=30,
                                       min_grad_norm=1e-07, \
                                       metric='euclidean', init='random', verbose=0, random_state=0,
                                       method='barnes_hut', angle=0.5)


        self.X_red = self.Embedding.fit_transform(self.Waves_Coefficients)
        return self.X_red

    def PreprocessingRBM(self, components, MNE_coefficients, N_neighbors):
        """
        :type MNE_coefficients: int

        :param MNE_coefficients: number of coefficnents for mns projection

        :param N_neighbors: number of neighbors for embedding
        """
        self.MNE_coefficients = MNE_coefficients

        self.N_neighbors = N_neighbors

        self.rbm = neural_network.BernoulliRBM(n_components=components,
                                               learning_rate=0.05, batch_size=10,
                                               n_iter=100, verbose=0, random_state=0)

        self.Embedding = manifold.SpectralEmbedding(n_components=self.MNE_coefficients,
                                                    affinity='nearest_neighbors',
                                                    gamma=None, random_state=0,
                                                    n_neighbors=self.N_neighbors)
        self.X_rbm = self.rbm.fit_transform(self.Waves_Coefficients)
        self.X_red = self.Embedding.fit_transform(self.X_rbm)
        return self.X_red

    def ClassifyGMM(self, num_clusters):
         self.labels = gaussian_mixture(self.X_red, num_clusters)
         n_c = len(np.unique(self.labels))
         logger.info('number of clusters: %s' % n_c)
         return self.labels
    def ClassifyBGMM(self, num_clusters):
         self.labels = BGMM(self.X_red, num_clusters)
         n_c = len(np.unique(self.labels))
         logger.info('number of clusters: %s' % n_c)
         return self.labels

    def ClassifyBirtch(self, num_clusters):
        self.labels = birtch_partial(self.X_red,num_clusters)
        n_c = len(np.unique(self.labels))
        logger.info('number of clusters: %s' % n_c)
        return self.labels
    def PlotClustering(self):
        data = pd.DataFrame(self.X_red, columns=["DIM_1", "DIM_2"])
        data['LABEL'] = self.labels
        plt.figure(figsize=(8.0, 7.0))
        sns.lmplot(x="DIM_1", y="DIM_2", data=data, fit_reg=False, legend=True, size=9,
                   hue='LABEL', scatter_kws={"s": 100, "alpha": 0.3})
