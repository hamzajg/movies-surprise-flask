from flask import Flask, redirect, url_for
from flask import render_template
from flask import request, jsonify
from top_n_recommendations import get_top_n, get_all_recs
from collections import defaultdict
import os
from surprise import dump
from surprise import SVD
from surprise import Dataset

app = Flask(__name__)
@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def score():
    print("request received!")
    score_request = request.get_json()
    userId = score_request.get("userId")
    candidateIds  = score_request.get("candidateIds")
    excludeIds  = score_request.get("excludeIds")
    # offset  = score_request.get('offset')
    limit  = score_request.get("limit")
    # retrievalCriteria  = score_request.get('retrievalCriteria')

    # load data and model
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo)[int(userId)]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}
    i = 0

    # Format recommendations
    for i in range(0, len(recs)):
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

# The results are ranked
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


@app.route('/rank', methods=['POST'])
def rank():
    print("request received!")
    rank_request = request.get_json()
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

'''
A HTML page that displays recommendations for a user.
Returns recommendations in JSON format.
'''
# At this point, algorithm is hard coded.
@app.route('/recs',methods=['POST'])
def recommend_from_form():
    userId = request.form['userId']
    limit = int(request.form['limit'])
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")

    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_top_n(predictions_loaded_algo,limit)[int(userId)]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}
    i = 0

    while (len(response_list['predictedRatings']) < limit and i < len(recs)):
        response = {
                'movieId':recs[i][0],
                'predicted rating':recs[i][1]
        }
        response_list['predictedRatings'].append(response)
        response_list['movieIds'].append(recs[i][0])
        print(response_list)
        i = i+1
    return jsonify(response_list)

'''
An API that returns 10 recommendations in JSON format for a user.
Example: http://127.0.0.1:5000/api/?userid=2
returns 10 recommendations for user 2
'''
@app.route('/api/')
def recommend_from_param():
    # TODO: add algorithm as a parameter
    userId = request.args['userid']
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")

    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_top_n(predictions_loaded_algo,10)[int(userId)]
    print(recs)
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}

    for i in range(10):
        response = {
            'movieId':recs[i][0],
            'predicted rating':recs[i][1]
        }
        response_list['predictedRatings'].append(response)
        response_list['movieIds'].append(recs[i][0])
        print(response_list)
    return jsonify(response_list)


@app.route('/manage_link', methods=['POST'])
def manage_link():
    print("manage_link")
    newrequest = request.form
    print(newrequest)
    userId = request.form['userId']
    print("Hi" + userId)
    # recommend(userId)
    return redirect(url_for('recommend_from_form',newrequest=newrequest))



if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=12345)
