

from flask import request, jsonify, Blueprint
from models import usuarios  # call model file
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import get_jwt, create_access_token, get_jwt_identity, jwt_required, create_refresh_token



auth = Blueprint('auth', __name__)

_usuarios = usuarios.Usuario()

@auth.route('/register', methods=['POST'])
def create_user():
    if request.method == "POST":
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        _check = _usuarios.find({ "$or": [ {"username": username }, {"email": email} ] })
        if _check:
            return jsonify(error="Email ou usuário em uso"), 400
        else:
            _usuarios.create({
                "username":username,
                "email":email,
                "password":generate_password_hash(password)
            })
            return '', 201

@auth.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if password and email:
        _check = _usuarios.find( {"email": email})
        if _check:
            if check_password_hash(_check[0]['password'], password):
                additional_claims = {"email": _check[0]['email']}
                access_token = create_access_token(identity=_check[0]['username'], additional_claims=additional_claims)
                refresh_token = create_refresh_token(identity=_check[0]['username'])
                return jsonify(access_token=access_token, refresh_token=refresh_token)
            else:
                return jsonify(error="Senha ou email errados"), 400
        else: 
            return jsonify(error="Conta não encontrada"), 400
    else: 
        return jsonify(error="Necessário informário email e senha"), 401
    

@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

@auth.route("/hello")
@jwt_required()
def protected():
    identity = get_jwt_identity()
    return jsonify(msg=f"Olá {identity}")
