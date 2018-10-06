import json

from flask_cors    import CORS
from flask import Flask, jsonify, request

# app 은 앞으로 사용할 서버의 이름
# __name__ : 이름을 대체해주는 환경변수 (그때그때 모듈네임을 알아서 입력)

app = Flask(__name__)
app.debug = True
# 코드를 고치면 알아서 디버깅을 해줌

# list 안에 dictunary 가 있는데, 이것보다 더 빠른 정보탐색을 하는 방법?
# 이중 딕셔너리 : 각 딕셔너리에 key 값을 새로 부여한다.

# users = [
users = {
	1: {
		'id' : 1,
		'name' : '이예원',
		'account_type' : 'PREMIUM'
	},
	2: {
		'id' : 2,
		'name' : '예원',
		'account_type' : 'BASIC'
	}
#]
}

CORS(app)
# endpoint 로 decorator 를 달고 서버에 핑 보내면 404 에러가 뜸
# 데코레이터를 route 로 변경후 재실행

@app.route('/users', methods=['GET', 'POST'])
def all_users():
	# 이중 딕셔너리를 써서 지금 리스트 형식이 아니므로
	# return 해줄때는 jsonify 안에 list 로 감싼다음, value 값만 리턴 해준다
	# 작은 딕셔너리 자체가 앞에 인덱싱 넘버를 달게 됨으로써 그 자체가 value 가 됨
	"""return jsonify(users)"""
	return jsonify(list(users.values()))

@app.route('/user/<int:id>', methods=['GET']) ## /user/1
def get_user(id):
	user = None
	
	# 아래 for loop 보다 훨씬 빠르게 정보탐색 가능 (이중 딕셔너리)
	if (id in users):
		return jsonify(users[id]) 
	"""for u in users:
		if u['id'] == id:
			return jsonify(u)

	return '', 404""" 

@app.route('/ping', methods=['GET'])
def ping():
	return 'pong'

@app.route('/user', methods=['POST'])
def create_user():
	# json 파일을 받아오고 dictionary 파일로 변환해줌
	new_user = request.json
	# my_dict[2] = "내용" << 이렇게 추가하는거랑 똑같음, key 와 value 를추가함
	users[new_user['id']] = new_user
	
	return '', 200
