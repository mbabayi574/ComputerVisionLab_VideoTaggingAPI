from flask import Flask, request, jsonify, abort
from flask_pymongo import ObjectId
from pymongo import MongoClient
import bson

app = Flask(__name__)

client = MongoClient("mongodb://reid:reid2243@194.225.229.147:8082/")
db = client["FruitShop"]


def validate_user(request_body):
    required_fields = ['username', 'password']
    if not all([field in request_body for field in required_fields]):
        return 1

    # if "role" does not exist in request_body, set it to "ANNOTATOR"
    if "role" not in request_body:
        request_body['role'] = "ANNOTATOR"

    # if "token" does not exist in request_body, set it to ""
    if "token" not in request_body:
        request_body['token'] = ""

    if request_body['role'] not in ["ADMIN", "ANNOTATOR", "REVIEWER"]:
        return 2


@app.route('/Users/', methods=['POST'])
def create_user():
    error_code = validate_user(request.json)
    if (1 == error_code):
        return jsonify({"status": "username or password fields are missing"})
    elif (2 == error_code):
        return jsonify({"status": "Role can only be one of ['ADMIN', 'ANNOTATOR', 'REVIEWER']"})
    user = request.json
    inserted_id = db.Users.insert_one(user)
    user_id = str(inserted_id.inserted_id)
    return jsonify({"_id": user_id})


@app.route('/Users/', methods=['GET'])
def show_users():
    users = []
    for user in db.Users.find():
        user['_id'] = str(user['_id'])
        users.append(user)
    return jsonify({'Users': users})


@app.route('/Users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        error_code = validate_user(request.json)
        if (1 == error_code):
            return jsonify({"status": "username or password fields are missing"})
        elif (2 == error_code):
            return jsonify({"status": "Role can only be one of ['ADMIN', 'ANNOTATOR', 'REVIEWER']"})
        user = request.json

        response = db.Users.update_one(
            {'_id': ObjectId(user_id)}, {'$set': user})

        if response.matched_count == 0:
            abort(404, description="Resource not found")

        return jsonify({"status": "User updated"})
    except (bson.errors.InvalidId):
        return jsonify({"status": "User Not Found"})
    except Exception as e:
        return jsonify({"status": "An error occurred",
                        "error": str(e)
                        })


@app.route('/Users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        response = db.Users.delete_one({'_id': ObjectId(user_id)})
        if response.deleted_count == 0:
            abort(404, description="Resource not found")
        return jsonify({"status": "User deleted"})
    except (bson.errors.InvalidId):
        return jsonify({"status": "User Not Found"})
    except Exception as e:
        return jsonify({"status": "An error occurred",
                        "error": str(e)
                        })


if __name__ == "__main__":
    app.run()
