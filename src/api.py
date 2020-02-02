from flask import Flask, redirect, url_for
from flask import render_template
from flask import request, jsonify
from top_n_recommendations import get_top_n, get_all_recs
from collections import defaultdict
import os
from surprise import dump
from surprise import SVD
from surprise import Dataset
import ast


'''
This file contains the API endpoints.
For more functionalities, such as get recommendation by submitting a form, check 'server.py'
'''
app = Flask(__name__)
@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/score', methods=['POST'])
def score():
    print("request received!")
    score_request = request.form
    #score_json = score_request.get_json()
    userId = score_request.get("userId")
    candidateIds  = score_request.get("candidateIds")
    # print(candidateIds)
    excludeIds = []
    limit  = score_request.get("limit")
    # retrievalCriteria  = score_request.get('retrievalCriteria')

    # Parse a string representation of a list to a list
    candidateIds = ast.literal_eval(candidateIds)
    for i in candidateIds[1:-1]:
        i = int(i)

    # load data and model
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()

    # Make predictions on the testset
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model'))
    print("file loaded")
    predictions_loaded_algo = algo.test(trainset.build_testset())

    # Get recommendations for a given user
    recs = get_all_recs(predictions_loaded_algo)[int(userId)]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}
    i = 0

    # Format recommendations
    for i in range(0, len(recs)):
        print("i="+str(i))
        if (len(response_list['movieIds']) >= int(limit)):
            break;
        if (recs[i][0] in candidateIds) and (recs[i][0] not in excludeIds):
            response = {
                    'movieId':recs[i][0],
                    'predicted rating':recs[i][1]
            }
            response_list['predictedRatings'].append(response)
            response_list['movieIds'].append(recs[i][0])

    print(response_list)
    return jsonify(response_list)


# given a search, return a set of candidates
@app.route('/retrieve', methods=['POST'])
def retrieve():
    print("request received!")
    retrieve_request = request.get_json()
    userId = retrieve_request.get("userId")
    candidateIds  = retrieve_request.get("candidateIds")
    excludeIds  = retrieve_request.get("excludeIds")
    # offset  = retrieve_request.get('offset')
    limit  = retrieve_request.get("limit")
    # retrievalCriteria  = retrieve_request.get('retrievalCriteria')

    # load data and model, get recommendations
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo)[int(userId)]
    # recs = get_top_n(predictions_loaded_algo,int(limit))[int(userId)]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[]}
    i = 0

    # Format recommendations
    for i in range(0, len(recs)):
        if (len(response_list['movieIds']) >= int(limit)):
            break;
        if (recs[i][0] in candidateIds) and (recs[i][0] not in excludeIds):
            response_list['movieIds'].append(recs[i][0])
            i = i+1
    return jsonify(response_list)

# given a set of candidates (and a set of excludes) build a ranked list
@app.route('/rank', methods=['POST'])
def rank():
    print("request received!")
    rank_request = request.get_json(force=True)
    userId = rank_request.get("userId")
    candidateIds  = rank_request.get("candidateIds")
    excludeIds  = rank_request.get("excludeIds")
    # offset  = rank_request.get('offset')
    limit  = rank_request.get("limit")
    # retrievalCriteria  = rank_request.get('retrievalCriteria')

    # load data and model, get recommendations
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo)[int(userId)]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[]}
    i = 0

    # Format recommendations
    for i in range(0, len(recs)):
        if (len(response_list['movieIds']) >= int(limit)):
            break;
        if (recs[i][0] in candidateIds) and (recs[i][0] not in excludeIds):
            response_list['movieIds'].append(recs[i][0])
            i = i+1
    return jsonify(response_list)


if __name__=='__main__':
    app.run(debug=True)
