db = {
    'user'     : 'root',
    'password' : 'Youbastard123!',
    'host'     : 'python-backend-test.c4uxqdncx4mg.ap-northeast-2.rds.amazonaws.com',
    'port'     : 3306,
    'database' : 'python_test'
}

DB_URL                = f"mysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY        = 'SOME_SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60
