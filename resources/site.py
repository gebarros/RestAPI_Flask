from flask_restful import Resource
from models.site import SiteModel


class Sites(Resource):
    def get(self):
        return {'sites': [site.json() for site in SiteModel.query.all()]}

class Site(Resource):
    def get(self, url):
        site = SiteModel.find_site(url)
        if site:
            return site.json()
        return {'message': 'Site not found'}, 404

    def post(self, url):
        if SiteModel.find_site(url):
            return {'message': 'The site "{}" already exists'.format(url)}, 400 #Bad request
        site = SiteModel(url)
        try:
            site.save_site()
        except:
            {'message': 'An error ocurred trying to create a new site.'},500 # Internal Server Error
        return site.json()

    def delete(self, url):
        site = SiteModel.find_site(url)
        if site:
            try: 
                site.delete_site()
            except:
                {'message': 'An error ocurred trying to delete site.'},500 # Internal Server Error
            return {'message': 'Site deleted.'}
        return {'message': 'Site not found.'}, 404