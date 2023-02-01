import os

from flask import Flask, request, jsonify
from flask_cors import CORS  # to avoid cors error in different frontend like react js or any other

from flask_jwt_extended import jwt_required,get_jwt, JWTManager

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from routes.palavras import palavra
from routes.usuarios import usuario 
from routes.auth import auth 
from routes.uploads import uploads


from config import config
import redis

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup the Flask-JWT-Extended extension

# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True

app.config["JWT_SECRET_KEY"] = config["SECRET_KEY"]  # Change this!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=config["ACCESS_TOKEN_EXPIRES"])
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=config["REFRESH_TOKEN_EXPIRES"])

jwt = JWTManager(app)

# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
jwt_redis_blocklist = redis.Redis(
    host="redis", port=6379, db=0, decode_responses=True
)

# Callback function to check if a JWT exists in the redis blocklist
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None

@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    # jwt_redis_blocklist.set(jti, '', ex=config['ACCESS_TOKEN_EXPIRES']))
    jwt_redis_blocklist.set(jti, '')
    return jsonify(msg="Access token revoked")


@app.route('/', methods=['GET'])
def hello():
    return {"hello": "world"}, 200

@app.errorhandler(404)
def not_found(error=None):
    return jsonify(error="Not found"), 404

app.register_blueprint(palavra, url_prefix='/palavras')
app.register_blueprint(usuario, url_prefix='/usuarios')
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(uploads, url_prefix='/uploads')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True )