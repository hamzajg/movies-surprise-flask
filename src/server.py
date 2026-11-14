from flask import Flask, redirect, url_for, abort
from flask import render_template
from flask import request, jsonify
from top_n_recommendations import get_top_n, get_all_recs
from collections import defaultdict
import os
from surprise import dump
from surprise import SVD
from surprise import Dataset

app = Flask(__name__)


def _recommendation_params():
    """Parse and validate the JSON body shared by /score, /retrieve and /rank.

    Returns (user_id, candidate_ids, exclude_ids, limit); aborts 400 on bad input.
    """
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        abort(400, description='JSON body with userId, candidateIds and limit is required')
    try:
        user_id = int(body['userId'])
        limit = int(body['limit'])
    except (KeyError, TypeError, ValueError):
        abort(400, description='userId and limit are required integers')
    candidate_ids = body.get('candidateIds')
    if not isinstance(candidate_ids, list):
        abort(400, description='candidateIds must be a list')
    exclude_ids = body.get('excludeIds') or []
    if not isinstance(exclude_ids, list):
        abort(400, description='excludeIds must be a list')
    return user_id, candidate_ids, exclude_ids, limit


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/score', methods=['POST'])
def score():
    print("request received!")
    user_id, candidate_ids, exclude_ids, limit = _recommendation_params()

    # load data and model
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo).get(user_id, [])
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}

    # Format recommendations
    for rec in recs:
        if (len(response_list['movieIds']) >= limit):
            break;
        if (rec[0] in candidate_ids) and (rec[0] not in exclude_ids):
            response = {
                    'movieId':rec[0],
                    'predicted rating':rec[1]
            }
            response_list['predictedRatings'].append(response)
            response_list['movieIds'].append(rec[0])
            print(response_list)
    return jsonify(response_list)

# The results are ranked
@app.route('/retrieve', methods=['POST'])
def retrieve():
    print("request received!")
    user_id, candidate_ids, exclude_ids, limit = _recommendation_params()

    # load data and model, get recommendations
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo).get(user_id, [])
    # recs = get_top_n(predictions_loaded_algo,limit)[user_id]
    response_list = {'source':{"id":"SVD_model"},'movieIds':[]}

    # Format recommendations
    for rec in recs:
        if (len(response_list['movieIds']) >= limit):
            break;
        if (rec[0] in candidate_ids) and (rec[0] not in exclude_ids):
            response_list['movieIds'].append(rec[0])
    return jsonify(response_list)


@app.route('/rank', methods=['POST'])
def rank():
    print("request received!")
    user_id, candidate_ids, exclude_ids, limit = _recommendation_params()

    # load data and model, get recommendations
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")
    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_all_recs(predictions_loaded_algo).get(user_id, [])
    response_list = {'source':{"id":"SVD_model"},'movieIds':[]}

    # Format recommendations
    for rec in recs:
        if (len(response_list['movieIds']) >= limit):
            break;
        if (rec[0] in candidate_ids) and (rec[0] not in exclude_ids):
            response_list['movieIds'].append(rec[0])
    return jsonify(response_list)

'''
A HTML page that displays recommendations for a user.
Returns recommendations in JSON format.
'''
# At this point, algorithm is hard coded.
@app.route('/recs',methods=['POST'])
def recommend_from_form():
    try:
        user_id = int(request.form['userId'])
        limit = int(request.form['limit'])
    except (KeyError, TypeError, ValueError):
        abort(400, description='userId and limit are required integers')
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")

    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_top_n(predictions_loaded_algo, limit).get(user_id, [])
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}

    for rec in recs[:limit]:
        response = {
                'movieId':rec[0],
                'predicted rating':rec[1]
        }
        response_list['predictedRatings'].append(response)
        response_list['movieIds'].append(rec[0])
        print(response_list)
    return jsonify(response_list)

'''
An API that returns 10 recommendations in JSON format for a user.
Example: http://127.0.0.1:5000/api/?userid=2
returns 10 recommendations for user 2
'''
@app.route('/api/')
def recommend_from_param():
    # TODO: add algorithm as a parameter
    try:
        user_id = int(request.args['userid'])
    except (KeyError, TypeError, ValueError):
        abort(400, description='userid is a required integer')
    data = Dataset.load_builtin('ml-100k')
    trainset = data.build_full_trainset()
    _, loaded_algo = dump.load(os.path.expanduser('./SVD_model_couchDB'))
    print("file loaded")

    predictions_loaded_algo = loaded_algo.test(trainset.build_testset())
    recs = get_top_n(predictions_loaded_algo, 10).get(user_id, [])
    print(recs)
    response_list = {'source':{"id":"SVD_model"},'movieIds':[],'predictedRatings':[]}

    for rec in recs:
        response = {
            'movieId':rec[0],
            'predicted rating':rec[1]
        }
        response_list['predictedRatings'].append(response)
        response_list['movieIds'].append(rec[0])
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
