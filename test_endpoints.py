import pytest
import bcrypt
import json

from app import create_app
from sqlalchemy import create_engine, text

db = {
    'user'     : 'connectuser',
    'password' : 'Connect123!@#',
    'host'     : 'localhost',
    'port'     : 5000,
    'database' : 'practice1'
}
test_config = {
    'DB_URL'                : f"mysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8",
    'JWT_SECRET_KEY'        : 'SOME_SUPER_SECRET_KEY',
    'JWT_EXP_DELTA_SECONDS' : 7 * 24 * 60 * 60
}

database = create_engine(test_config['DB_URL'], encoding= 'utf-8', max_overflow = 0)

def setup_function():
    database.execute(text("""
        INSERT INTO accounts (
            id,
            account_type
        ) VALUES (1, 'VIP'), (2, 'PREMIUM')
    """))

    ## Create a test user
    hashed_password = bcrypt.hashpw(
        b"test password",
        bcrypt.gensalt()
    )
    new_users = [
        {
            'id'           : 1,
            'name'         : "vip",
            'email'        : "vip@test.com",
            'password'     : hashed_password,
            'account_type' : 'VIP'
        },
        {
            'id'           : 2,
            'name'         : "premium",
            'email'        : "premium@test.com",
            'password'     : hashed_password,
            'account_type' : 'PREMIUM'
        }
    ]

    database.execute(text("""
        INSERT INTO users (
            id,
            name,
            email,
            hashed_password,
            account_id
        ) SELECT
            :id,
            :name,
            :email,
            :password,
            accnt.id
        FROM accounts as accnt
        WHERE accnt.account_type = :account_type
    """), new_users)

def teardown_function():
    database.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    database.execute(text("TRUNCATE users"))
    database.execute(text("TRUNCATE accounts"))
    database.execute(text("SET FOREIGN_KEY_CHECKS=1"))

@pytest.fixture
def api():
    app = create_app(test_config)
    app.config['TESTING'] = True
    api = app.test_client()

    yield api

def test_ping(api):
    resp = api.get('/ping')
    assert b'pong' in resp.data

def test_all_users(api):
    resp = api.get('/users')
    assert resp.status_code == 401

    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'vip@test.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp  = api.get('/users', headers = {'Authorization' : access_token})
    users = json.loads(resp.data.decode('utf-8'))

    assert users == [
        {
            "id"           : 1,
            "account_type" : "VIP",
            "email"        : "vip@test.com",
            "name"         : "vip"
        },
        {
            "account_type" : "PREMIUM",
            "email"        : "premium@test.com",
            "id"           : 2,
            "name"         : "premium"
            }
    ]


####################
## 여기서부터는 과제 부분 ##
####################

def test_all_users_non_vip(api):
    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'premium@test.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp  = api.get('/users', headers = {'Authorization' : access_token})
    assert resp.status_code == 401


"""
def test_get_user(api):
    for i in [1,2]:
    # db 안의 1번, 2번 데이터를 가져오는 절차 / 1번 유저의 데이터를 가져오는 절차
        resp = api.get(f'/user/{i}')
        assert resp.status_code == 200
        # 여기서 status_code 를 401로 하면 Assertion_Error 발생 // 200 을 놓음으로써 해결

        # login 권한이 최초로 실행되야 하므로, 위 부분의 login 부분을 그대로 차용
        resp = api.post(
            '/login',
            data         = json.dumps({'email' : 'vip@test.com', 'password' : 'test password'}),
            content_type = 'application/json'
        )
        resp_json    = json.loads(resp.data.decode('utf-8'))
        access_token = resp_json['access_token']

        resp  = api.get(f'/user/{i}', headers = {'Authorization' : access_token})
        users = json.loads(resp.data.decode('utf-8'))

        #여기를 이렇게 db 를 다 놓으면 해결이 되고,
        #1번 DB 만 추출하고싶어서 assert 에 1번 db만 놓으면 실행이 안됨
        #이유가 궁금함

        # user/1 << 처럼 하나만 리턴하는 경우,
        # list 안에 dictionary 를 가둘필요가 없고, 그냥 딕셔너리형으로만 assert
        if i == 1:
            assert users == {
                "id"           : 1,
                "account_type" : "VIP",
                "email"        : "vip@test.com",
                "name"         : "vip"
                }
        else:
            assert users == {
                "account_type" : "PREMIUM",
                "email"        : "premium@test.com",
                "id"           : 2,
                "name"         : "premium"
                }

"""

def test_get_user(api):
    resp = api.get('/user/1')
    assert resp.status_code == 200

    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'vip@test.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp = api.get('/user/1', headers = {'Authorization' : access_token})
    user = json.loads(resp.data.decode('utf-8'))

    assert user == {
        "id"           : 1,
        "account_type" : "VIP",
        "email"        : "vip@test.com",
        "name"         : "vip"
    }

    resp = api.get('/user/2', headers = {'Authorization' : access_token})
    user = json.loads(resp.data.decode('utf-8'))

    assert user == {
        "account_type" : "PREMIUM",
        "email"        : "premium@test.com",
        "id"           : 2,
        "name"         : "premium"
    }

def test_login(api):
    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'vip@test.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    assert b"access_token" in resp.data


def test_create_user(api):
    resp = api.get('/user')
    assert resp.status_code == 405

    resp = api.post(
        '/login',
        data         = json.dumps({'email' : 'vip@test.com', 'password' : 'test password'}),
        content_type = 'application/json'
    )
    resp_json    = json.loads(resp.data.decode('utf-8'))
    access_token = resp_json['access_token']

    resp  = api.get('/users', headers = {'Authorization' : access_token})
    users = json.loads(resp.data.decode('utf-8'))

    assert users == [
        {
            "id"           : 1,
            "account_type" : "VIP",
            "email"        : "vip@test.com",
            "name"         : "vip"
        },
        {
            "account_type" : "PREMIUM",
            "email"        : "premium@test.com",
            "id"           : 2,
            "name"         : "premium"
            }
    ]

    new_user = {
        'name'         : 'new_user',
        'email'        : 'new@test.com',
        'password'     : 'test',
        'account_type' : 'PREMIUM'
    }
    resp = api.post(
        '/user',
        data         = json.dumps(new_user),
        content_type = 'application/json'
    )
    assert resp.status_code == 200

    resp  = api.get('/users', headers = {'Authorization' : access_token})
    users = json.loads(resp.data.decode('utf-8'))
    database.execute(text("UPDATE users SET id = 3 WHERE id not in (1, 2)"))
    assert users == [
        {
            "id"           : 1,
            "account_type" : "VIP",
            "email"        : "vip@test.com",
            "name"         : "vip"
        },
        {
            "account_type" : "PREMIUM",
            "email"        : "premium@test.com",
            "id"           : 2,
            "name"         : "premium"
        },
        {
            'name'         : 'new_user',
            'email'        : 'new@test.com',
            'id'           : 3,
            'account_type' : 'PREMIUM'
        }
    ]
