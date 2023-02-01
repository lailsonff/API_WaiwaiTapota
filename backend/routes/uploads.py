from flask import Flask, request, jsonify, Blueprint, redirect, url_for
from factory.database import Database
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import palavras, upload
import mimetypes
from mimetypes import guess_type

uploads = Blueprint('uploads', __name__)
gridfs = Database()
_palavras = palavras.Palavra()
_uploads = upload.Upload()

# Todo: Verificar token do usuário logado para postar a imagem e anexar email do token ✔️
# Todo: Checar se tipo de arquivo já está vinculado ao ID da palavra ✔️
# Todo: Verificar se oidword é válido para criar no BD ✔️
@uploads.route('/', methods=['POST'])
@jwt_required()
def create_upload():
    identity = get_jwt_identity()
    if request.method == "POST":
        oidWord = request.form["oidword"]
        if oidWord:
            _check = _palavras.find_by_id(oidWord)
            if not _check:
                return dict(error="Palavra inexistente! Insira um ID válido."), 404
            else:
                if _check['user'] != identity:
                    return dict(error="Palavra não pertence ao usuário!"), 401
                else:
                    file = request.files["file"]
                    content_type, _ = guess_type(file.filename)
                    if content_type is None:
                        return dict(error="Tipo de arquivo não suportado!"), 400
                    else:
                        if content_type.startswith('audio'):
                            _check_audio = _uploads.find(word_id=oidWord,content_type='audio')
                            if _check_audio:
                                return dict(error="Já existe um áudio vinculado a essa palavra!"), 400
                            _oid = gridfs.save_file(file.filename, file, oidword=oidWord, user=identity)
                            return dict(filename=str(_oid)), 201
                        elif content_type.startswith('image'):
                            _check_image = _uploads.find(word_id=oidWord,content_type='image')
                            if _check_image:
                                return dict(error="Já existe uma imagem vinculada a essa palavra!"), 400
                            _oid = gridfs.save_file(file.filename, file, oidword=oidWord, user=identity)
                            return dict(filename=str(_oid)), 201
                        else:
                            return dict(error="Tipo de arquivo não suportado!"), 400
        else:
            return dict(error="Informe o ID da palavra!"), 400

# Todo: Verificar token do usuário logado para deletar a imagem/audio, caso pertença a ele o upload
@uploads.route('/<path:filename>', methods=['DELETE'])
@jwt_required()
def delete_upload(filename=None):
    identity = get_jwt_identity()
    _check = gridfs.find_by_id(filename, "fs.files")
    if _check['user'] != identity:
        return dict(error="Upload não pertence ao usuário!"), 401
    else:
        gridfs.delete_file(filename)
        return "", 202
    

# Todo: Para consultar imagens necessário autenticação
@uploads.route('/<path:filename>', methods=['GET'])
def get_upload(filename=None):
    if request.method == "GET":
        return gridfs.send_file(filename)