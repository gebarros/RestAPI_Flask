from sql_alchemy import banco
from flask import request, url_for


class UserModel(banco.Model):
    __tablename__ = 'usuarios'

    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40), nullable=False)
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean, default=False)
   
    def __init__(self, login, senha, email, ativado): # não passando o user_id, sabendo que é Integer e PK, ele incrementa automaticamente
        self.login = login
        self.senha = senha
        self.ativado= ativado

    def send_confirmation_email(self):
        # http://127.0.0.1:5000/confirmacao/{user_id}
        link = request.url_root[:-1] + url_for('userconfirm', user_id = self.user_id) 
        

    def json(self):
        return{
            'user_id': self.user_id,
            'login': self.login,
            'login': self.email,
            'ativado': self.ativado}
    
    @classmethod
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first() 
        if user:
            return user
        return None
    
    @classmethod
    def find_by_login(cls, login):
        login = cls.query.filter_by(login=login).first() 
        if login:
            return login
        return None
    
    def save_user(self):
        banco.session.add(self)
        banco.session.commit()
    
    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()

