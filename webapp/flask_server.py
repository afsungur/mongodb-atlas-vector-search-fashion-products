from sentence_transformers import SentenceTransformer, util

from flask import Flask, render_template, request, jsonify
import os, sys
import pymongo
import ssl
from bson import json_util
import json

sys.path.insert(1, '../config/')
from config import mongo_uri, db, collection, sentence_transformers_text_model_name, number_of_dimensions

app = Flask(__name__,             
            static_url_path='',
            static_folder='../encoder/' 
            )
            
connection = pymongo.MongoClient(mongo_uri)
product_collection = connection[db][collection]
preTrainedModelName = sentence_transformers_text_model_name
model = SentenceTransformer(preTrainedModelName)

@app.route('/search', methods=['GET'])
def search():

    vector_text = request.args.get('vector', default=None, type=str)
    vector_query = model.encode(vector_text).tolist()
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "imageVector",
                "queryVector": vector_query,
                "numCandidates": 1000,
                "limit": 10
            }
        },
        {
            "$project": {
                "imageVector": {"$slice": ["$imageVector", 5]},
                "imageFile": 1,
                "price": 1,
                "discountPercentage": 1,
                "averageRating" : 1,
                "_id": 0,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]

    # Execute the pipeline
    docs = list(product_collection.aggregate(pipeline))

    # Return the results unders the docs array field
    json_result = json_util.dumps({'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    
    return jsonify(json_result)

@app.route('/searchAdvanced', methods=['GET'])
def searchAdvanced():

    vector_text = request.args.get('vector', default=None, type=str)
    minRating = request.args.get('minRating', default=3, type=float)
    minDiscount = request.args.get('minDiscount', default=5, type=float)
    maximumPrice = request.args.get('maxPrice', default=75, type=float)
    sortBy = request.args.get('sortBy', default=None, type=str)

    print(f"Parameters: {vector_text}, {minRating}, {minDiscount}, {maximumPrice}, {sortBy}")

    sort = {"score": 1}

    if (sortBy=="price"):
        sort = {"price":1}
    elif (sortBy=="averageRating"):
        sort = {"averageRating":-1}
  
    vector_query = model.encode(vector_text).tolist()
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "imageVector",
                "queryVector": vector_query,
                "numCandidates": 200,
                "limit": 10,
                "filter": {
                    "$and": [
                        {
                            "price": {'$lte': maximumPrice}
                        },
                        {
                            "averageRating": {'$gte': minRating}
                        },
                        {
                            "discountPercentage": {'$gte': minDiscount}
                        }
                    ]
                }
            }
        },
        {
            "$project": {
                "imageVector": {"$slice": ["$imageVector", 5]},
                "imageFile": 1,
                "price": 1,
                "discountPercentage": 1,
                "averageRating" : 1,
                "_id": 0,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        },
        {
            "$sort" : sort
        }
    ]

    # Execute the pipeline
    docs = list(product_collection.aggregate(pipeline))

    # Return the results unders the docs array field
    json_result = json_util.dumps({'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    
    return jsonify(json_result)


# page
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/advanced')
def advanced():
    return render_template("advanced.html")

if __name__ == '__main__':
    app.run(host="localhost", port=5010, debug=True)
