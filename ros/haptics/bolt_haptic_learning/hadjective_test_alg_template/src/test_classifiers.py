#!/usr/bin/env python
import roslib; roslib.load_manifest("hadjective_test_alg_template")
import rospy
import numpy as np
import sys 
import os
from optparse import OptionParser
import cPickle
import pickle
import bolt_learning_utilities as utilities
import extract_features as extract_features
import matplotlib.pyplot as plt 
import sklearn.decomposition

from bolt_feature_obj import BoltFeatureObj
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics import classification_report
from sklearn.datasets.samples_generator import make_blobs
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
from sklearn import cross_validation
from sklearn import preprocessing



# Loads the data from h5 table and adds labels
# Returns the dictionary of objects
def loadDataFromH5File(input_file, adjective_file):
   
    # Takes the input h5 file and converts into bolt object data
    all_bolt_data = utilities.convertH5ToBoltObjFile(input_file, None, False);
   
    # Inserts adjectives into the bolt_data  
    all_bolt_data_adj = utilities.insertAdjectiveLabels(all_bolt_data, "all_objects_majority4.pkl", adjective_file, True)

    return all_bolt_data_adj


# Takes the bolt data and extracts features to run
def BoltMotionObjToFeatureObj(all_bolt_data):
    """
    Pull out PCA components from all data

    For each object - pull out features and store in feature_obj
    with the same structure as all_bolt_data
   
        Dictionary - "tap", "slide", "slow_slide", 
                     "thermal_hold", "squeeze"

    """
    # DO PCA Calculations here 
    
    # Store in feature class object
    all_features_obj_dict = dict();

    for motion_name in all_bolt_data:
        trial_list = all_bolt_data.get(motion_name)
        print motion_name

        feature_list = list()
        # For all objects
        for trial in trial_list:
            
            bolt_feature_obj = extract_features.extract_features(trial)
            
            feature_list.append(bolt_feature_obj)

        # Store all of the objects away
        all_features_obj_dict[motion_name] = feature_list
            
    return all_features_obj_dict        
    

def bolt_obj_2_feature_vector(all_features_obj_dict, feature_name_list):
    """
    Pull out PCA components from all data

    For each object - pull out features and store in feature_obj
    with the same structure as all_bolt_data
   
        Dictionary - "tap", "slide", "slow_slide", 
                     "thermal_hold", "squeeze"

    Directly store the features into a vector
    See createFeatureVector for more details on structure

    """
    
    # DO PCA Calculations here 
     


    # Store in feature class object
    all_features_vector_dict = dict()
    
    # Store labels
    for motion_name in all_features_obj_dict:
        
        feature_obj_list = all_features_obj_dict.get(motion_name)

        all_adjective_labels_dict = dict()
        feature_vector_list = list()

        # For all objects
        for bolt_feature_obj in feature_obj_list:

            # Create feature vector
            feature_vector = utilities.createFeatureVector(bolt_feature_obj, feature_name_list) 
            feature_vector_list.append(feature_vector)

            # Create label dictionary
            labels = bolt_feature_obj.labels
            for adjective in labels:
                # Check if it is the first time adjective added
                if (all_adjective_labels_dict.has_key(adjective)):
                    adjective_array = all_adjective_labels_dict[adjective]
                else:
                    adjective_array = list()
                
                # Store array
                adjective_array.append(labels[adjective])
                all_adjective_labels_dict[adjective] = adjective_array

        # Store all of the objects away
        all_features_vector_dict[motion_name] = np.array(feature_vector_list)
        
    
    return (all_features_vector_dict, all_adjective_labels_dict)      



    """
    def true_false_results(predicted_labels, true_labels):
 
    #FP = (predicted_labels - true_labels).tolist().count(1)
    #FN = (predicted_labels - true_labels).tolist().count(-1)
    #TP = (predicted_labels & true_labels).tolist().count(1)
    #TN = ((predicted_labels | true_labels) ^ True).tolist().count(1)


    return(TP, TN, FP, FN)


    #def matthews_corr_coef(TP,TN,FP,FN):

    try:
        MCC = (TP*TN - FP*FN)/(np.sqrt(((TP+FP)*(TP+FN)*(TN+FP)*(TN+FN))))
    except:
        MCC = (TP*TN - FP*FN)/1

    return (MCC)
    """


#def train_knn(train_vector, train_labels, test_vector, test_labels):
    """
    train_knn - expects a vector of features and a nx1 set of
                corresponding labels.  Finally the number of
                neighbors used for comparison

    Returns a trained knn classifier
    """
 
    """
    # Data scaling
    train_vector_scaled = preprocessing.scale(train_vector)
    test_vector_scaled = preprocessing.scale(test_vector)

    # Grid search with nested cross-validation
    parameters = [{'n_neighbors': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]}]
    knn = GridSearchCV(KNeighborsClassifier(), parameters, score_func=f1_score, cv=8)
    knn.fit(train_vector_scaled, train_labels)
    score = knn.grid_scores_
    knn_best = knn.best_estimator_
    report = classification_report(test_labels, knn.predict(test_vector_scaled))

    return (knn_best, score, report)
    """


def train_svm(train_vector, train_labels, test_vector, test_labels):
    """ 
    train_svm - expects a vector of features and a nx1 set of
                corresponding labels

    Returns a trained SVM classifier
    """
 
    
    # Data scaling
    train_vector_scaled = preprocessing.scale(train_vector)
    test_vector_scaled = preprocessing.scale(test_vector)
    
    # Grid search with nested cross-validation
    parameters = {'kernel': ['rbf'], 'C': [1, 1e1, 1e2, 1e3, 1e4], 'gamma': [1, 1e-1, 1e-2, 1e-3, 1e-4]}
    #parameters = {'kernel': ['poly'], 'C': [1, 1e1, 1e2, 1e3, 1e4], 'degree': [1, 2, 3, 4, 5], 'gamma': [1, 1e-1, 1e-2, 1e-3, 1e-4]} 
    svm = GridSearchCV(SVC(), parameters, score_func=f1_score, cv=8)
    svm.fit(train_vector_scaled, train_labels)
    score = svm.grid_scores_
    svm_best = svm.best_estimator_
    report = classification_report(test_labels, svm.predict(test_vector_scaled))

    return (svm_best, score, report)


def AdjectiveClassifiers(adjectives, test_vector)
    """ 
    Feed the probabilities/labels from 5 classifiers for one adjective into a SVM and train.
    Return a single final classifier for each adjective
    """
    labels = dict()
    final_classifiers = dict()
    num_raw = results[adj][motion_name].shape
    feature_vector = np.zeros((num_raw,5))
    results = cPickle.load(open('test_results.pkl',"r"))
          
    for adj in adjectives:
        labels[adj] = adjectives[adj]
        for motion_name in test_vector  #here the train_vetor should be test_vector
            feature_vector = np.append(feature_vector, results[adj][motion_name][0].tolist(), 1)
            
        # Train on features
        adj_classifier, grid_search_scores, final_report, probabilities, predicted_results = train_svm(feature_vector, labels[adj], test_vector, labels[adj] )
        
        final_classifiers[adj] = adj_classifier

    cPickle.dump(final_classifiers, open("AdjectiveClassifiers.pkl", "w"), cPickle.HIGHEST_PROTOCOL)
     
    return final_classifier




#def single_train(feature_vector, labels):
    """
    single_train - expects a vector of features and an nx1 set of
                   corresponding labels to train a single classifier
                   on 1 motion

    Returns trained KNN and SVM classifiers that have been optimized
    using grid search
    """

    """
    # Split data
    train_vector, test_vector, train_labels, test_labels = train_test_split(feature_vector, labels, test_size=0.25)

    # Run KNN
    knn, knn_score, knn_report = train_knn(train_vector, train_labels, test_vector, test_labels)
    print "Ran KNN"

    # Run SVM
    svm, svm_score, svm_report = train_svm(train_vector, train_labels, test_vector, test_labels)
    print "Ran SVM"

    return(knn, knn_report, svm, svm_report)


    #def full_train(train_feature_vector, adjective_dictionary):
    

    #import pdb; pdb.set_trace()

    # Fun full training
    report_file_knn = open("Full_KNN_reports.txt", "a")
    report_file_svm = open("Full_SVM_reports.txt", "a")
    
    adjectives = adjective_dictionary.keys()
    
    for adj in adjectives:
        knn_classifiers = dict()
        svm_classifiers = dict()
         
        #pkl_file_name = adj.replace("'",'"')
             
        for motion_name in train_feature_vector:
            
            print "Training KNN and SVM classifiers for adjective %s, phase %s \n" %(adj, motion_name)
            
            knn, knn_report, svm, svm_report = single_train(train_feature_vector[motion_name], adjective_dictionary[adj])

            # Store classifiers for each motion
            knn_classifiers[motion_name] = knn
            svm_classifiers[motion_name] = svm
 
            # Store the reports into text files
            report_file_knn.write('Adjective: '+adj+'   Motion name: '+motion_name)
            report_file_knn.write('\nKNN report\n'+knn_report+'\n\n')
            report_file_svm.write('Adjective: '+adj+'   Motion name: '+motion_name)
            report_file_svm.write('\nSVM report\n'+svm_report+'\n\n')
  
        # When trainings for a certain adjective with all five motions are done, save these classifiers
        cPickle.dump(knn_classifiers, open('adjective_classifiers/'+adj+'_knn.pkl', "w"), cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(svm_classifiers, open('adjective_classifiers/'+adj+'_svm.pkl', "w"), cPickle.HIGHEST_PROTOCOL)
        
        print "Stored KNN and SVM classifiers for adjective %s in the directory adjective_classifiers " %(adj)

    
    report_file_knn.close()
    report_file_svm.close()
    """


# MAIN FUNCTION
def main(input_file, adjective_file, train_feature_pkl, test_feature_plk):


    print "Loading data from file"
    # If no features, load data from either an
    # h5 and adjective file or directly from
    # a saved pkl file
    if input_file.endswith(".h5"):
        all_data = loadDataFromH5File(input_file, adjective_file)
    else:
        all_data = utilities.loadBoltObjFile(input_file)

    print "loaded data"

    
    # Split the data into train and test
    train_data, test_data = utilities.split_data(all_data, 0.9)
        
    # Convert motion objects into feature objects
    test_all_features_obj_dict = BoltMotionObjToFeatureObj(test_data)

    print "loaded data"

    # Take loaded data and extract out features
    feature_name_list = ["pdc_rise_count", "pdc_area", "pdc_max", "pac_energy", "pac_sc", "pac_sv", "pac_ss", "pac_sk", "tac_area", "tdc_exp_fit"]


    # Pull desired features from feature objects
    test_feature_vector, test_adjective_dictionary = bolt_obj_2_feature_vector(test_all_features_obj_dict, feature_name_list)

    # Preprocess the data by scaling
    test_feature_vector_scaled = preprocessing.scale(test_feature_vector)
    print("Created feature vector containing %s" % feature_name_list)

    



    report_file = open("Test_results.txt","a")
    results = dict()
     
    # adjective_list has NOT been created
     
    for adj in test_adjective_dictionary
        print "Start testing on adjective %s" %(adj)
         
        labels = dict()
        knn_clf_ptr = open('adjective_classifiers/'+adj+'_knn.pkl', "r")
        svm_clf_ptr = open('adjective_classifiers/'+adj+'_svm.pkl', "r")
        
        # Load the pickle file which is the corresponding adjective classifier
        adj_clf_knn = cPickle.load(knn_clf_ptr)
        adj_clf_svm = cPickle.load(svm_clf_ptr)
        report_file.write('----- Adjective: ')
        report_file.write(adj)
        report_file.write(' -----\n')
 
        for motion_name in test_feature_vector
            knn_predicted = adj_clf_knn[motion_name].predict_proba(test_feature_vector_scaled[motion_name])
            svm_predicted = adj_clf_svm[motion_name].predict_proba(test_feature_vector_scaled[motion_name])

            report_file.write('Motion:  '+motion_name+'\n')
            
            # Is proba a list of float values??
            report_file.write('KNN labels with proba: ')
            report_file.write('SVM labels with proba: ')

            labels[motion_name] = [knn_predicted, svm_predicted]

        results[adj] = labels
        # In the future, we may store the results by motion in the order how well it performs

        print "Tesing on adjective %s is DONE" %(adj)

    file_name = "test_result.pkl"
    cPickle.dump(results, open(file_name, "w"), cPickle.HIGHEST_PROTOCOL)


    # Use the output from classifiers by motions to create a single classifier for each adjective
    final_classifier = AdjectiveClassifiers(test_adjective_dictionary, test_feature_vector)

# Parse the command line arguments
def parse_arguments():
    """
    Parses the arguments provided at command line.
    
    Returns:
    (input_file, adjective_file, range)
    """
    parser = OptionParser()
    parser.add_option("-i", "--input_file", action="store", type="string", dest = "in_h5_file")
    parser.add_option("-o", "--output", action="store", type="string", dest = "out_file", default = None) 
    parser.add_option("-a", "--input_adjective", action="store", type="string", dest = "in_adjective_file")
    parser.add_option("-n", "--input_train_feature_pkl", action="store", type="string", dest = "in_train_feature_pkl", default = None)
    parser.add_option("-s", "--input_test_feature_pkl", action="store", type="string", dest = "in_test_feature_pkl", default = None)

    (options, args) = parser.parse_args()
    input_file = options.in_h5_file #this is required
   
    if options.out_file is None:
        (_, name) = os.path.split(input_file)
        name = name.split(".")[0]
        out_file = name + ".pkl"
    else:    
        out_file = options.out_file
        if len(out_file.split(".")) == 1:
            out_file = out_file + ".pkl"
    
    adjective_file = options.in_adjective_file

    train_feature_pkl = options.in_train_feature_pkl
    test_feature_pkl = options.in_test_feature_pkl

    return input_file, out_file, adjective_file, train_feature_pkl, test_feature_pkl


if __name__ == "__main__":
    input_file, out_file, adjective_file, train_feature_pkl, test_feature_pkl = parse_arguments()
    main(input_file, adjective_file)
