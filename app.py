import pymssql
import os
from flask import Flask
from flask_restful import Api, Resource, reqparse
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from validators import non_empty_string, age_validator

app = Flask(__name__)
api = Api(app)
JWTManager(app)
app.config.from_mapping(JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
                        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=2))


class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return {"access_token": access_token}


class LogIn(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=non_empty_string, required=True, nullable=False,
                            help='username field required!', location='json')
        parser.add_argument('password', type=non_empty_string, required=True, nullable=False,
                            help='password field required!', location='json')
        args = parser.parse_args()
        conn = pymssql.connect(server='127.0.0.1', database="diver")
        cursor = conn.cursor()
        cursor.execute("SELECT Username, Password FROM Users WHERE Username = %s ;", args.get('username'))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], args.get('password')):
            access = create_access_token(identity=user[0])
            refresh = create_refresh_token(identity=user[0])
            return {"user": {
                "username": user[0],
                "access_token": access,
                "refresh_token": refresh
            }}
        else:
            return {"error": "wrong credentials!"}


class WriteProfile(Resource):

    @jwt_required()
    def put(self):
        username = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument('lastname', required=False)
        parser.add_argument('firstname', required=False)
        parser.add_argument('age', type=age_validator, required=False)
        parser.add_argument('city', required=False)
        args = parser.parse_args()
        conn = pymssql.connect(server='127.0.0.1', database="diver")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username=%s ;", username)
        user = cursor.fetchone()
        if args.get("lastname") is not None:
            lastname = args.get("lastname")
        else:
            lastname = user[2]
        if args.get("firstname") is not None:
            firstname = args.get("firstname")
        else:
            firstname = user[3]
        if args.get("age") is not None:
            age = args.get("age")
        else:
            age = user[4]
        if args.get("city") is not None:
            city = args.get("city")
        else:
            city = user[5]
        cursor.callproc('write_profile', (lastname, firstname, age, city, username))
        conn.commit()
        conn.close()
        return {"user": {"username": username, "lastname": lastname,
                         "firstname": firstname, "age": age, "city": city}}


class ReadProfile(Resource):

    def get(self, username):
        conn = pymssql.connect(server='127.0.0.1', database="diver")
        cursor = conn.cursor()
        cursor.execute("SELECT Username, Lastname, Firstname, Age, City FROM Users WHERE Username=%s;", username)
        user = cursor.fetchone()
        conn.close()
        if user:
            return {"user": {"username": user[0], "lastname": user[1],
                             "firstname": user[2], "age": user[3], "city": user[4]}}
        else:
            return {"error": "there is not a user with this username"}


class ReadAllProfiles(Resource):

    def get(self):
        conn = pymssql.connect(server="127.0.0.1", database="Diver")
        cursor = conn.cursor()
        cursor.execute("SELECT Username, Lastname, Firstname, Age, City FROM Users;")
        result = cursor.fetchall()
        users = dict()
        conn.close()
        for num, row in enumerate(result):
            users[f"user{num+1}"] = {"username": row[0], "lastname": row[1],
                                   "firstname": row[2], "age": row[3], "city": row[4]}
        return users


api.add_resource(Refresh, '/refresh')
api.add_resource(LogIn, '/login')
api.add_resource(WriteProfile, '/write-profile')
api.add_resource(ReadProfile, '/read-profile/<string:username>')
api.add_resource(ReadAllProfiles, '/read-all-profiles')

if __name__ == '__main__':
    app.run(debug=True)
