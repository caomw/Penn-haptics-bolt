#! /usr/bin/python

import adjective_classifier
import upenn_features
import numpy as np
from sklearn.decomposition import PCA

import cPickle
import utilities
from sklearn.externals.joblib import Parallel, delayed
import sys
import glob
import os

class FeaturesAdjectiveClassifier(adjective_classifier.AdjectiveClassifier):
    """This class is like AdjectiveClassifier in that it uses the HMMs to create
    features. In addition it uses the features developed by UPenn to verify
    if classification improves.
    """
    def __init__(self, adjective, 
                 electrodes_pca = None,
                 base_directory = None):
        super(FeaturesAdjectiveClassifier, self).__init__(adjective, 
                                                          base_directory)
        self.electrodes_pca = electrodes_pca
    
    def extract_features(self, X):
        """
        X: list of dictionaries d, each with the structure:
            d[phase][sensor] = data
        """
        if type(X) is not list:
            X = [X]        
        hmm_features = super(FeaturesAdjectiveClassifier,self).extract_features(X)
        
        if self.electrodes_pca is None:
            all_electrodes = [v['electrodes'] for data in X for v in data.values()]
            electrodes = np.vstack(all_electrodes)
            self.electrodes_pca = PCA(4).fit(electrodes)
        
        additional_features = np.hstack(upenn_features.get_all_features(ep)
                                        for x in X
                                        for ep in x.values()
                                        ).tolist()
        ret = np.hstack(hmm_features + [additional_features])
        
        return ret
    
adjectives = utilities.adjectives

def test_adjective(adjective, chains_path, adjectives_path):
    pattern = "/*"+adjective+"*.pkl"
    test_len = len(utilities.phases) * len(utilities.sensors)

    number_of_chains = len(glob.glob(chains_path + pattern))
    test_chain =  number_of_chains >= test_len
    
    test_a = len(glob.glob(adjectives_path + pattern)) == 0
    
    if not test_chain:
        print "Adjective %s has only %d chains" % (adjective, number_of_chains)
    if not test_a:
        print "Adjective %s already has a file" % adjective    
        
    return test_chain and test_a

def create_clf(a, chains_directory, adjectives_directory, h5_db):
    print "Creating classifier for adjective ", a
    clf = FeaturesAdjectiveClassifier(a, 
                                      base_directory=chains_directory)

    assert all(l == 4 for l in (len(v) for v in clf.chains.itervalues()))
    
    clf.create_features_set(h5_db, store=True, verbose=False)    
    classifier_file = os.path.join(adjectives_directory, 
                                   clf.adjective + ".pkl")
    print "Saving file: ", classifier_file
    with open(classifier_file, "w") as f:
        cPickle.dump(clf, f, cPickle.HIGHEST_PROTOCOL)    
    
    return clf   

def main(db_filename, base_directory, nj=6):
    
    chains_directory = os.path.join(base_directory, "chains")
    adjectives_directory = os.path.join(base_directory, "untrained_adjectives")
    
    p = Parallel(n_jobs=nj,verbose=10)
    p(delayed(create_clf)(a, chains_directory, 
                          adjectives_directory,
                          db_filename) 
      for a in adjectives 
      if test_adjective(a, 
                        chains_directory,
                        adjectives_directory))

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "usage: %s database base_directory n_jobs" % sys.argv[0]
        print "chains are in base_directory/chains"
        print "adjectives will be saved in base_directory/untrained_adjectives"
        sys.exit(1)
    
    db, base_dir, n_jobs = sys.argv[1:]
    n_jobs = int(n_jobs)
    main(db, base_dir, n_jobs)