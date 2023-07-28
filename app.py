from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import datetime
from bson import ObjectId
from utils import mongo_to_dict

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = '62a22a0e4b74c6959e638a0b0a1ac0de'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=7)

jwt = JWTManager(app)

client = MongoClient(
    "mongodb://reid:reid2243@172.17.10.165:8082/?authMechanism=DEFAULT")
db = client["FruitShop"]
users_collection = db["users"]
projects_collection = db["projects"]


@app.route('/login', methods=['POST'])
def login():
    login_details = request.get_json()
    user_from_db = users_collection.find_one(
        {'username': login_details['username']})
    if user_from_db and login_details['password'] == user_from_db['password']:
        access_token = create_access_token(
            identity=user_from_db['username'])  # create jwt token
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'The username or password is incorrect'}), 401

# Users Management Section


@app.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can get users"}), 401
    users = users_collection.find({})
    return jsonify(mongo_to_dict(users)), 200


@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can create users"}), 401
    new_user = request.get_json()
    doc = users_collection.find_one({"username": new_user["username"]})
    if doc:
        return jsonify({'msg': 'Username already exists'}), 409
    users_collection.insert_one(new_user)
    return jsonify({'msg': 'User created successfully'}), 201


@app.route('/users/<id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can update users"}), 401

    if not users_collection.find_one({"_id": ObjectId(id)}):
        return jsonify({'msg': 'User does not exist'}), 404

    user = request.get_json()
    users_collection.update_one({"_id": ObjectId(id)}, {"$set": user})
    return jsonify({'msg': 'User updated successfully'}), 200


@app.route('/users/<id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can create users"}), 401

    if not users_collection.find_one({"_id": ObjectId(id)}):
        return jsonify({'msg': 'User already does not exist'}), 404

    users_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({'msg': 'User deleted successfully'}), 200

# Projects Management Section


@app.route('/projects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can create projects"}), 401
    projects = projects_collection.find({})
    return jsonify(mongo_to_dict(projects)), 200


@app.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can create projects"}), 401

    new_project = request.get_json()
    doc = projects_collection.find_one({"name": new_project["name"]})
    if doc:
        return jsonify({'msg': 'Project already exists'}), 409
    projects_collection.insert_one(new_project)
    return jsonify({'msg': 'Project created successfully'}), 201


@app.route('/projects/<id>', methods=['PUT'])
@jwt_required()
def update_project(id):
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can update projects"}), 401

    if not projects_collection.find_one({"_id": ObjectId(id)}):
        return jsonify({'msg': 'Project does not exist'}), 404

    project = request.get_json()
    projects_collection.update_one({"_id": ObjectId(id)}, {"$set": project})
    return jsonify({'msg': 'Project updated successfully'}), 200


@app.route('/projects/<id>', methods=['DELETE'])
@jwt_required()
def delete_project(id):
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})
    if user_from_db['role'] != 'ADMIN':
        return jsonify({"status": "Only ADMIN can delete projects"}), 401

    if not projects_collection.find_one({"_id": ObjectId(id)}):
        return jsonify({'msg': 'Project already does not exist'}), 404

    projects_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({'msg': 'Project deleted successfully'}), 200


@app.route('/myprojects', methods=['GET'])
@jwt_required()
def get_my_projects():
    current_user = get_jwt_identity()
    projects = projects_collection.find(
        {"$or": [{"reviewer": current_user}, {"annotator": current_user}]})
    return jsonify(mongo_to_dict(projects)), 200


@app.route('/projects/<id>/assign', methods=['PUT'])
@jwt_required()
def assign_project(id):
    current_user = get_jwt_identity()
    user_from_db = users_collection.find_one({'username': current_user})

    if user_from_db['role'] != 'REVIEWER':
        projects_collection.update_one({"_id": ObjectId(id)}, {"$set": {"reviewer": current_user, "status": "in review"
                                                                        }})
        return jsonify({'msg': 'Project assigned successfully'}), 200
    elif user_from_db['role'] != 'ANNOTATOR':
        projects_collection.update_one({"_id": ObjectId(id)}, {"$set": {"annotator": current_user, "status": "in annotation"
                                                                        }})
        return jsonify({'msg': 'Project assigned successfully'}), 200

    return jsonify({"status": "Only REVIEWER or ANNOTATOR can assign projects"}), 401


'''
example of a user:
{
        "number_of_completed_projects": 0,
        "number_of_ongoing_projects": 0,
        "password": "13771210",
        "role": "REVIEWER",
        "username": "reviewer"
}

example of a project:
{
		"annotator": "user3",
        "reviewer": "user2",
        "name": "project1",
        "status": "unassigned",
        "id_counter": 0
}
'''

if __name__ == '__main__':
    app.run(debug=True)
