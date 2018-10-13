import jwt
import bcrypt

from sqlalchemy import create_engine, text
from flask import Flask, jsonify, request, Response, g, current_app
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta

################################
# Authentication wrapper
################################
def decode(access_token):
    try:
        payload = jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'], 'HS256')
    except jwt.InvalidTokenError:
        payload = None

    return payload

def get_user_info(id):
    sql = text("""
        SELECT
            u.id,
            u.name,
            u.email,
            accnt.account_type
        FROM users as u
        JOIN accounts accnt ON u.account_id = accnt.id
        WHERE u.id = :id
    """)
    parameters = {'id' : id}
    row        = current_app.database.execute(sql, parameters).fetchone()

    return {
        'id'           : row['id'],
        'name'         : row['name'],
        'email'        : row['email'],
        'account_type' : row['account_type']
    }  if row else None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get('Authorization')

        if access_token is not None:
            payload = decode(access_token)

            if payload is None: return Response(status=401)

            user_id   = payload['user_id']
            g.user_id = user_id
            g.user    = get_user_info(user_id) if user_id else None
        else:
            return Response(status = 401)

        return f(*args, **kwargs)
    return decorated_function

def vip_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(g, 'user', None)

        if not user or not user['account_type'] == 'VIP':
            return Response(status = 401)

        return f(*args, **kwargs)

    return decorated_function


def create_app(test_config = None):
    app = Flask(__name__)
    app.debug = True

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        print(f"test config == {test_config}")
        app.config.update(test_config)

    database     = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
    app.database = database


    CORS(app)

    @app.route('/ping', methods=['GET'])
    def ping():
        return jsonify('{"name" : "pong"}')

    @app.route('/users', methods=['GET'])
    @login_required
    @vip_required
    def all_users():
       rows = database.execute(text("""
       SELECT
           u.id,
           u.name,
           u.email,
           accnt.account_type
       FROM users as u
       JOIN accounts accnt ON u.account_id = accnt.id
       """)).fetchall()
       if rows is None:
           return '', 404
       return jsonify([{
           'id'            : row['id'],
           'name'          : row['name'],
           'email'         : row['email'],
           'account_type'  : row['account_type']
       }for row in rows])

    @app.route('/user/<int:id>', methods=['GET'])  ## /user/1
    def get_user(id):
       sql = text("""
           SELECT
               u.id,
               u.name,
               u.email,
               accnt.account_type
           FROM users as u
           JOIN accounts accnt ON u.account_id = accnt.id
           WHERE u.id = :id
           """)

       parameters = {'id' : id}
       row = database.execute(sql, parameters).fetchone()

       return jsonify({
           'id': row['id'],
           'name': row['name'],
           'email': row['email'],
           'account_type': row['account_type']
       }) if row else ('', 404)

    @app.route('/login', methods=['POST'])
    def login():
        credential = request.json
        email      = credential['email']
        password   = credential['password']
        row        = database.execute(text("""
            SELECT
                id,
                hashed_password
            FROM users
            WHERE email = :email
        """), {'email' : email}).fetchone()

        if row and bcrypt.checkpw(password.encode('UTF-8'), row['hashed_password'].encode('UTF-8')):
            user_id = row['id']
            payload = {
                'user_id' : user_id,
                'exp'     : datetime.utcnow() + timedelta(seconds = app.config['JWT_EXP_DELTA_SECONDS'])
            }
            token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], 'HS256')

            return jsonify({
                'access_token' : token.decode('UTF-8')
            })
        else:
            return '', 401


    @app.route('/user', methods=['POST'])
    def create_user():
        new_user             = request.json
        new_user['password'] = bcrypt.hashpw(
            new_user['password'].encode('UTF-8'),
            bcrypt.gensalt()
        )

        print(f"new user ==> {new_user}")

        rowcount = database.execute(text("""
            INSERT INTO users (
                name,
                email,
                hashed_password, account_id
            ) SELECT
                :name,
                :email,
                :password,
                accnt.id
            FROM accounts as accnt
            WHERE accnt.account_type = :account_type
        """), new_user).rowcount

        print(f"row count == {rowcount}")

        return ('', 200) if rowcount == 1 else ('', 500)

    return app
