from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS


app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
api = Api(app)

# URL = "http://" + requests.get("http://169.254.169.254/latest/meta-data/public-hostname").text
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"], support_credentials=True)

client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["Users"]
stats = db["Stats"]

def user_exists(username):
    if users.find({"Username": username}).count() == 0:
        return False
    else:
        return True

def email_exists(email):
    if users.find({"Email": email}).count() == 0:
        return False
    else:
        return True

class SaveStats(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        program = posted_data["program"]
        rounds = posted_data["rounds"]
        total_time = posted_data["totalTime"]
        set_data = posted_data["set"]

        
        stats.insert({
            "Username": username,
            "Program": program,
            "Rounds": rounds,
            "TotalTime": total_time,
            "Set": set_data
        })
        ret_json = {
            "status": 200,
            "msg": "You've successfully added data to the database!"
        }
        return jsonify(ret_json)

 
    #     this.data = {
    #         "random": {
    #             "rounds": {
    #                 "3": {
    #                     "0": {
    #                         "totalTime": 6,
    #                         "set": {"1": 2, "2": 4, "3": 6}
    #                     },
    #                     "1": {
    #                         "totalTime": 8,
    #                         "set": {"1": 3, "2": 5, "3": 8}
    #                     },
    #                     "2": {
    #                         "totalTime": 10,
    #                         "set": {"1": 2, "2": 6, "3": 10}
    #                     },
    #                 },
    #                 "4": {
    #                     "0": {
    #                         "totalTime": 10,
    #                         "set": {"1": 2, "2": 5, "3": 7, "4": 10}
    #                     },
    #                     "1": {
    #                         "totalTime": 12,
    #                         "set": {"1": 2, "2": 5, "3": 8, "4": 12}
    #                     },   
    #                     "2": {
    #                         "totalTime": 15,
    #                         "set": {"1": 3, "2": 9, "3": 12, "4": 15}
    #                     },                        

    #                 }
    #             }
    #         },
    #         "sprint": {
    #             "0": 10,
    #             "1": 15,
    #             "2": 14,
    #             "3": 12
    #         }
    #     }
        
    # }

class Stats(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        print_data = []        
        data = stats.find({"Username": username})
        for i in data:

            print_data.append(i)

        ret_data = {}
        for i in range(len(print_data)):   
            d = print_data[i]
            print(d, flush=True)
            id_tag = str(d["_id"])
            ret_data[id_tag] = {"rounds": d["Rounds"], "totalTime": d["TotalTime"], "set": d["Set"], "program": d["Program"]}
        print(ret_data, flush=True)
        ret_json = {
            "status": 200,
            "msg": "You've succesfully extracted data!",
            "data": ret_data
        }
        return jsonify(ret_json)
        



class Register(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]
        email = posted_data["email"]
        address = posted_data["address"]
        first_name = posted_data["firstName"]
        last_name = posted_data["lastName"]

        if user_exists(username):
            ret_json = {
                "status": 301,
                "msg": "Invalid Username"
            }
            return jsonify(ret_json)

        if email_exists(email):
            ret_json = {
                "status": 301,
                "msg": "Invalid Email"
            }

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Email": email,
            "Address": address
        })
        ret_json = {
            "status": 200,
            "msg": "You've successfully signed up!"
        }
        return jsonify(ret_json)

class Login(Resource):
    def post(self):
        posted_data = request.get_json()

        username = posted_data["username"]
        password = posted_data["password"]

        ret_json, error = verify_credentials(username, password)
        if error:
            return jsonify(ret_json)        

        ret_json = {
            "status": 200,
            "msg": "You've successfully logged in"
        }

        return jsonify(ret_json)


def verify_pw(username, password):
    if not user_exists(username):
        return False
    
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode("utf-8"), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def cash_with_user(username):
    cash = users.find({
        "Username": username
    })[0]["Own"]
    return cash

def debt_with_user(username):
    debt = users.find({
        "Username": username
    })[0]["Debt"]
    return debt

def generate_return_dict(status, message):
    ret_json = {
        "status": status,
        "message": message
    }
    return ret_json

def verify_credentials(username, password):
    if not user_exists(username):
        return generate_return_dict(301, "Invalid Username"), True
    
    correct_pw = verify_pw(username, password)

    if not correct_pw:
        return generate_return_dict(302, "Invalid Password"), True

    return None, False

def update_account(username, balance):
    users.update({
        "Username": username
    }, {
        "$set": {
            "Own": balance
        }
    })

def update_debt(username, balance):
    users.update({
        "Username": username
    }, {
        "$set": {
            "Debt": balance
        }
    })


api.add_resource(Register, "/register")
api.add_resource(Login, "/login")
api.add_resource(Stats, "/stats")
api.add_resource(SaveStats, "/save-stats")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
