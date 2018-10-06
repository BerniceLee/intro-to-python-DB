db = {
    'user'     : 'connectuser',
    'password' : 'Connect123!@#',
    'host'     : 'localhost',
    'port'     : 5000,
    'database' : 'practice1'
}

DB_URL                = f"mysql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY        = 'SOME_SUPER_SECRET_KEY'
JWT_EXP_DELTA_SECONDS = 7 * 24 * 60 * 60
