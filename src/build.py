from surprise import Dataset
from surprise import Reader
import couchdb
import pandas as pd
from top_n_recommendations import get_top_n,KNN_top_n
from surprise import SVD
import os
from surprise import dump
from collections import defaultdict
from MovieLens import MovieLens

ml = MovieLens()

def load_from_couchDB(couchserver):
    userIds = []
    movieIds = []
    ratings = []
    tstamps = []

    rating_db = couchserver['test_ratings']
    for item in rating_db.view('rating_design1/view1'):
        i = item['id']
        if "_design" in i:
            continue
        doc = rating_db[i]
        userIds.append(doc['userId'])
        movieIds.append(doc['movieId'])
        ratings.append(doc['rating'])
        tstamps.append(doc['tstamp'])

    ratings_dict = {'UserIds':userIds,
                        'MovieIds':movieIds,
                        'Ratings':ratings,
                        'tstamps':tstamps}

    df = pd.DataFrame(ratings_dict)
    print(df)
    # print(type(df['UserIds']))
    # print(df)
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(df[['UserIds','MovieIds','Ratings']], reader)
    return data


# Train SVD model using ml-100k dataset
def train_SVD():
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    algo = SVD()
    algo.fit(trainset)

    # Dump algorithm and reload it.
    file_name = os.path.expanduser('./SVD_model')
    dump.dump(file_name, algo=algo)
    print("file dumped")

    # Load a model:
    _, loaded_algo = dump.load('./SVD_model')
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    #print(predictions_loaded_algo)


def main():
    #### Make predictions by calling functions in top_n_recommendations
    #### Predict based on data from couchDB
    # users_top_n()
    
    print("Loading movie ratings...")
    data = ml.loadMovieLensLatestSmall()
    print("Finished loading data")
    print("making predictions...")
    KNN_top_n(data)

    #### Train SVD model:
    #train_SVD()

if __name__=="__main__":
    main()
