from collections import defaultdict
import os
from surprise import dump
from surprise import SVD
from surprise import KNNBasic
from surprise import Dataset

'''
Get the topN recommendations for users using SVD
The method can be edited to return the top-n recommendations for a specific user
'''
def SVD_top_n(data):
    # First train an SVD algorithm on the movielens dataset.
    # data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    # Than predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    top_n = get_top_n(predictions, n=10)

    # Dump algorithm and reload it.
    file_name = os.path.expanduser('./SVD_model_couchDB')
    dump.dump(file_name, algo=algo)
    print("file dumped")

    # Load a model:
    #_, loaded_algo = dump.load(file_name)
    #print("file loaded")
    predictions_loaded_algo = algo.test(trainset.build_testset())
    print(top_n[1])


'''
Get the topN recommendations for users using SVD
The method can be edited to return the top-n recommendations for a specific user
'''
def KNN_top_n(data):
    # First train an SVD algorithm on the movielens dataset.
    # data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    algo = KNNBasic()
    algo.fit(trainset)

    # Than predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = trainset.build_anti_testset()
    predictions = algo.test(testset)

    top_n = get_top_n(predictions, n=10)

    # Dump algorithm and reload it.
    file_name = os.path.expanduser('./KNNBasic_model_couchDB')
    dump.dump(file_name, algo=algo)
    print("file dumped")

'''Return the top-N recommendation for each user from a set of predictions.
Args:
    predictions(list of Prediction objects): The list of predictions, as
        returned by the test method of an algorithm.
    n(int): The number of recommendation to output for each user. Default
        is 10.
Returns:
A dict where keys are user (raw) ids and values are lists of tuples:
    [(raw item id, rating estimation), ...] of size n.
'''
def get_top_n(predictions, n=10):

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[int(uid)].append((int(iid), est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
    return top_n

'''Return all predicted scores.
Args:
    predictions(list of Prediction objects): The list of predictions, as
        returned by the test method of an algorithm.
Returns:
A dict where keys are user (raw) ids and values are lists of tuples:
    [(raw item id, rating estimation), ...] of size n.
'''
def get_all_recs(predictions):

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[int(uid)].append((int(iid), est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
    return top_n


# def main():
#     data = Dataset.load_builtin('ml-100k')
#     SVD_top_n(data)
#
# if __name__=="__main__":
#     main()
