import numpy as np
from numpy import genfromtxt

from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import GradientBoostingClassifier

# Matplot to plot
import matplotlib.pyplot as plt

CROSS_FOLDS = 4

np.set_printoptions(threshold=np.nan)

# Uses the Mean Average Precision at 5 (MAP@5) evaluation
def map5eval(estimator, train, target):
    prediction = estimator.predict_proba(train)
    actual = target
    predicted = prediction.argsort(axis=1)[:,-np.arange(1,6)]
    metric = 0.
    for i in range(5):
        metric += np.sum(actual==predicted[:,i])/(i+1)
    metric /= actual.shape[0]
    return metric

def main():
    # The competition datafiles are in the directory /input

    # Training cols
    print ("Loading training csv.")
    training = genfromtxt(open('input/train_1000.csv', 'r'), delimiter=',', dtype='f8')[1:]
    # All columns except target
    train = [x[:-1] for x in training]
    train = np.nan_to_num(train)

    # Only target column
    target = [x[-1:] for x in training]
    target = np.nan_to_num(target)
    target = target.ravel()
    print ("Loading done.")

    print ("Training Gradient Boosting and doing Grid search with cross folds.")
    # Settings
    estimate_range = range(1, 20, 2)
    #learningrate = [x * 0.01 for x in range(5, 10)]
    learningrate = [0.02]
    #depth = range(1, 3)
    depth = [2]

    # Generate parameters to search for
    tuned_parameters = []
    for n in estimate_range:
        params = {'n_estimators': [n]}
        for m in learningrate:
            params['learning_rate'] = [m]
            for d in depth:
                params['max_depth'] = [d]
            tuned_parameters.append(params)

    # Create Gradient Boosting estimator model
    gradientboosting = GradientBoostingClassifier()

    # Create GridSearch with params and fit to training
    gridsearch    = GridSearchCV(estimator=gradientboosting, param_grid=tuned_parameters, cv=CROSS_FOLDS, scoring=map5eval, verbose=2)
    gridsearch.fit(train, target)
    print ("Searching done.")

    # Summarize the results of the grid search
    print ("\n------------------------")
    print ("Best score: \t" + str(gridsearch.best_score_))
    print ("Best params: \t" + str(gridsearch.best_params_))
    print ("------------------------")

    # The mean score, the 95% confidence interval and the scores are printed and prepared for the plot
    # Scores for each n_estimators are added independent of depth or learning rate
    estimate_scores = []
    for params, mean_score, score in gridsearch.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r" % (mean_score, score.std() * 2, params))

        # For every same param, increase average of score
        estimators = params['n_estimators']
        add = True
        for index_estimator, k_estimator in enumerate(estimate_range):
            for index_score, k_score in enumerate(estimate_scores):
                if estimators == k_estimator:
                    if index_estimator == index_score:
                        estimate_scores[index_score] = (estimate_scores[index_score] + mean_score) / 2
                        add = False
        if add:
            estimate_scores.append(mean_score)
    print ("------------------------")

    # Round for nicer matplot
    for index, k in enumerate(estimate_scores):
        estimate_scores[index] = round(estimate_scores[index], 4)

    # Plot result for estimators independent of depth or learning rate
    plt.plot(estimate_range, estimate_scores)
    plt.xlabel('Value of estimators for Gradient Boosting Classifier')
    plt.ylabel('Cross-Validated Accuracy')
    plt.savefig('gradientboosting_grid_search.png')
    plt.show()

    print ("Done.")

if __name__=="__main__":
    main()

