from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank")
atributos.add_argument('ativado', type=bool )

class User(Resource):
    # usuario/{user_id}    
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()

        return {'message': 'User not found'}, 404 #not found

    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try: 
                user.delete_user()
            except:
                {'message': 'An error ocurred trying to delete user.'},500 # Internal Server Error
            return {'message': 'User deleted.'}
        return {'message': 'User not found.'}, 404

class UserRegister(Resource):
    # /cadastro
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists".format(dados['login'])}
        
        user = UserModel(**dados)
        user.ativado = False
        try:
            user.save_user()
            return {'message': 'User created success.'}, 201
        except:
            return {'message': 'An error ocurred trying to save user.'}, 500 # Internal Server Error

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()
        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            if user.ativado:
                token_de_acesso = create_access_token(identity=user.user_id)
                return {'access_token': token_de_acesso}, 200
            return {'message': 'User not confirmed.'}, 400
        return {'message': 'The username or password is incorrect.'}, 401 #Unauthorized

class UserLogout(Resource):

    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti'] # JWT Token Identifier - pega o id do token
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged out successfully'}, 200

class UserConfirm(Resource):
    #raiz do site /confirmacao/user_id
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_user(user_id)
        if not user:
            return {'message': 'User id "{}" not found!'.format(user_id)}, 404 # not found

        user.ativado = True
        user.save_user()
        return {'message': "User id '{}' confirmed".format(user_id)}, 200
