from flask import Flask, make_response
from flask_pymongo import PyMongo
from bson.json_util import dumps
from gridfs import GridFS, NoFile
from bson.objectid import ObjectId
from flask_cors import CORS
from flask import jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import re
import bcrypt
import jwt
import hashlib
import datetime
from flask import Flask, request, jsonify, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = "secret"

app.config["MONGO_URI"] = "mongodb://mongo:27017/waiwaitapota"
app.config['SECRET_KEY'] = 'waiwai'
mongo = PyMongo(app)
abc = JWTManager(app) # initialize JWTManager
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=15)

@app.route('/adicionarPalavra', methods=['POST'])
def adicionar_palavra():
    _json = request.json
    word_portugues = _json['word_portugues']
    translation_Waiwai = _json['translation_Waiwai']
    meaning_Portuguese = _json['meaning_Portuguese']
    meaningWaiwai = _json['meaningWaiwai']
    synonymPortugues = _json['synonymPortugues']
    synonymWaiwai = _json['synonymWaiwai']
    category = _json['category']

    if word_portugues and translation_Waiwai and meaning_Portuguese and meaningWaiwai and synonymPortugues and synonymWaiwai and category and request.method == 'POST':
        id = mongo.db.palavras.insert_one({'word_portugues': word_portugues, 'translation_Waiwai': translation_Waiwai, 'category':category, 'meaning_Portuguese':meaning_Portuguese,'meaningWaiwai':meaningWaiwai, 'synonymPortugues':synonymPortugues, 'synonymWaiwai':synonymWaiwai})

        resposta = jsonify("Palavra adicionada com sucesso")

        resposta.status_code = 200

        return resposta
    else:
        return not_found()

@app.route('/buscarPalavrasCategoria/<category>', methods=['GET'])
def visualizar_palavras(category):
    palavras = mongo.db.palavras.find({"category":category})
    resp = dumps(palavras)
    return resp

#rota para visualizar uma única palavra

@app.route('/buscarPalavraId/<id>', methods=['GET'])
def palavra(id):
    words = mongo.db.palavras.find_one({'_id':ObjectId(id)})
    resp = dumps(words)
    return resp


@app.route('/deletarPalavra/<id>', methods=['DELETE'])
def deletar_palavra(id):
    mongo.db.palavras.delete_one({'_id': ObjectId(id)})
    resp = jsonify("Palavra deletada com sucesso")
    resp.status_code = 200
    return resp


@app.route('/atualizarPalavra/<id>', endpoint="atualizarPalavra", methods=['PUT'])
def atualizar_palavra(id):
    _id = id
    _json = request.json
    word_portugues = _json['word_portugues']
    translation_Waiwai = _json['translation_Waiwai']
    meaning_Portuguese = _json['meaning_Portuguese']
    meaningWaiwai = _json['meaningWaiwai']
    synonymPortugues = _json['synonymPortugues']
    synonymWaiwai = _json['synonymWaiwai']
    category = _json['category']

    if _id and word_portugues and translation_Waiwai and meaning_Portuguese and meaningWaiwai and synonymPortugues and synonymWaiwai and request.method == 'PUT':
        mongo.db.palavras.update_one({'_id': ObjectId(_id['$oid']) if '$oid' in _id else ObjectId(_id)}, {'$set': {'word_portugues':word_portugues, 'translation_Waiwai':translation_Waiwai,'meaning_Portuguese':meaning_Portuguese, 'meaningWaiwai':meaningWaiwai,'synonymPortugues':synonymPortugues,'synonymWaiwai':synonymWaiwai,  'category':category}})

        resp = jsonify("Palavra atualizada com sucesso.")

        resp.status_code = 200

        return resp
    else:
        return not_found

#Rota para fazer busca de palavras específicas
@app.route('/buscarPalavras/<word_portugues>', methods=['GET'])
def buscarpalavras(word_portugues):
    palavras = mongo.db.palavras.find({'word_portugues':word_portugues})
    resp = dumps(palavras)
    return resp


#Rota para visualizar palavras

@app.route('/visualizarPalavras', methods=['GET'])
def visualizarPalavras():
    palavras = mongo.db.palavras.find().sort('word_portugues')
    resp = dumps(palavras)
    return resp
    
#Rota para adicionar palavras na collection de palavras temporárias
@app.route('/adicionarPalavrasTemporarias', methods=["POST"])
def add_palavras_temporarias():
    _json = request.json
    word_portugues = _json['word_portugues']
    translation_Waiwai = _json['translation_Waiwai']
    meaning_Portuguese = _json['meaning_Portuguese']
    meaningWaiwai = _json['meaningWaiwai']
    synonymPortugues = _json['synonymPortugues']
    synonymWaiwai = _json['synonymWaiwai']
    category = _json['category']

    if word_portugues and translation_Waiwai and meaning_Portuguese and meaningWaiwai and synonymPortugues and synonymWaiwai and category and request.method == 'POST':
        id = mongo.db.palavrasTemporarias.insert_one(
            {'word_portugues': word_portugues, 'translation_Waiwai': translation_Waiwai, 'category': category,
             'meaning_Portuguese': meaning_Portuguese, 'meaningWaiwai': meaningWaiwai,
             'synonymPortugues': synonymPortugues, 'synonymWaiwai': synonymWaiwai})

        resposta = jsonify("Palavra adicionada com sucesso")

        resposta.status_code = 200

        return resposta
    else:
        return not_found()


# Registro de users
@app.route("/registrarUsuarios", methods=["POST"])
def register():
    _json = request.json
    _username = _json['username']
    _email = _json['email']
    _password = _json['password']
    new_user = request.get_json() # store the json body request
    new_user['password'] = hashlib.sha256(new_user['password'].encode("utf-8")).hexdigest() # encrpt password
    doc = mongo.db.usuarios.find_one({'email': new_user['email']}) # check if user exist
    regex = '^[\w-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$'
    login_details = request.get_json()
    doc = mongo.db.usuarios.find_one({"email": _json["email"]})
    if not doc:
        if _username and _email and _password and request.method == 'POST':
            """login_details['password']= hashlib.sha256(_password['password'].encode("utf-8")).hexdigest()"""
            id = mongo.db.usuarios.insert_one({'username': _username, 'email': _email, 'password': _password})
            resposta = jsonify("Usuário adicionado com sucesso!")
            resposta.status_code = 200
            return resposta

    else:
        resposta = jsonify({'msg': 'Este usuário já está cadastrado no banco de dados!'}), 409
        return resposta

#rotas referentes ao TOKEN
# Rota de login
@app.route("/login", methods=["POST"])
def login4():
    _json = request.json
    email = _json['email']
    print(email)
    password = _json['password']
    print(password)
    usuario = mongo.db.usuarios.find({'password': _json['password'], 'email': _json['email']})
    print(usuario)
    login_details = request.get_json() # store the json body request
    user_from_db = mongo.db.usuarios.find_one({'email': login_details['email']})  # search for user in database
    print(login_details['password'])
    """password = hashlib.sha256(login_details['password'].encode("utf-8")).hexdigest()"""
    print(f"Senha encripitada enviada via postman {password}")

    if user_from_db:
        print(password)
        print(user_from_db['password'])
        if password == user_from_db['password']:
            access_token = create_access_token(identity=user_from_db['email'])  # create jwt token
            print(access_token)
            return jsonify(access_token=access_token), 200

    return jsonify({'msg': 'O nome de usuário ou senha está incorreto!'}), 401

@app.route("/userLog", methods=["GET"])
@jwt_required()
def profile():
    current_user = get_jwt_identity() # Get the identity of the current user
    user_from_db = mongo.db.usuarios.find_one({'email': current_user})
    if user_from_db:
        del user_from_db['_id'], user_from_db['password'] # delete data we don't want to return
        return jsonify({'profile': user_from_db }), 200
    else:
        return jsonify({'msg': 'Perfil Não Encontrado'}), 404

@app.route("/uploads/<path:filename>", methods=["GET"])
def get_upload(filename):
    print(GridFS())
    # print(mongo.send_file(filename, ))
    return {"teste": "aa"}

@app.route("/uploads/<path:filename>", methods=["POST"])
def save_upload(filename):
    mongo.save_file(filename, request.files["file"])
    # return {"file name": filename}
    return redirect(url_for("get_upload", filename=filename))

@app.errorhandler(404)
def not_found(error=None):
    mensagem = {
        'status': 404,
        'mensagem': 'Not found' + request.url
    }
    resposta = jsonify(mensagem)

    resposta.status_code = 404
    return resposta

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)