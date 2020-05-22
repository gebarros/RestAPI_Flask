from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import normalize_path_params, consulta_com_cidade, consulta_sem_cidade
from flask_jwt_extended import jwt_required
import sqlite3 # ou mysql.connector


# path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=int)
path_params.add_argument('offset', type=int)

class Hoteis(Resource):
    def get(self):
        #conn = mysql.connector.connect(user='', password='', host='', database='')
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()

        dados  = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_sem_cidade, tupla) #sqlite

            # cursor.execute(consulta_sem_cidade, tupla) #mysql
            # resultado = cursor.fetchall() #mysql

        else:
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_com_cidade, tupla)
        
        hoteis = []
        for linha in resultado:
            hoteis.append({
            'hotel_id': linha[0],
            'nome': linha[1],
            'estrelas': linha[2],
            'diaria': linha[3],
            'cidade': linha[4],
            'site_id': linha[5]
            })

        return {'hoteis':hoteis} 

class Hotel(Resource):
    argumentos = reqparse.RequestParser() # add_argument só utilizado qdo tem método post
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank") # Json não pode vir sem nome
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas' cannot be left blank")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help='Every hotel needs to be linked to a site.')


    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()

        return {'message': 'Hotel not found'}, 404 #not found

    @jwt_required
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists".format(hotel_id)}, 400 # Bad request

        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
           return {'message': 'The hotel needs to be associated to a valid site id.'}, 400

        try:
            hotel.save_hotel()
        except:
            {'message': 'An error ocurred trying to save hotel.'}, 500 # Internal Server Error
        return hotel.json()
    
    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            try:
                hotel_encontrado.save_hotel()
            except:
                {'message': 'An error ocurred trying to update hotel.'}, 500 # Internal Server Error
            return hotel_encontrado.json(), 200 # ok
        
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            {'message': 'An error ocurred trying to save hotel.'},500 # Internal Server Error
        return hotel.json(), 201 # created

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try: 
                hotel.delete_hotel()
            except:
                {'message': 'An error ocurred trying to delete hotel.'},500 # Internal Server Error
            return {'message': 'Hotel deleted.'}
        return {'message': 'Hotel not found.'}, 404