from flask import Flask, render_template, request, jsonify, abort
from flask_restplus import Resource, Api
from google.appengine.api import app_identity
from flask_cors import CORS

import models

app = Flask(__name__)
app.config['DEBUG'] = True
# Add CORS support for all domains
CORS(app,
    origins="*",
    allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True
)
# Add support for Restplus api
api = Api(app)


@api.route('/offers/<int:id>', endpoint='offer')
class OfferItem(Resource):
    def get(self, id):
        """ Return an existing loan offer"""
        offers = [models.OfferModel.get_by_id(id)]
        offers_list = [offer.to_dict() for offer in offers if offer]
        if not len(offers_list):
            abort(404, {"error": "offer not found"})
        return jsonify(result=offers_list)

    def delete(self, id):
        """ Delete an existing loan offer"""
        if models.OfferModel.delete_by_id(id):
            return {'result': True}, 201
        else:
            abort(404)


@api.route('/offers/fill/<int:id>/<string:value>', endpoint='fillOffer')
class FIllOfferItem(Resource):
    def post(self, id, value):
        """ Fill an offer"""
        # data = request.get_json(force=True)
        if models.OfferModel.fill(id, value):
            return {'result': True}, 201
        else:
            abort(404)

@api.route('/offers', endpoint='offers')
class OfferList(Resource):
    def get(self):
        """ Return a list of existing loan offers"""
        offers = models.OfferModel.get_valid_offers()
        offers_list = [offer.to_dict() for offer in offers]
        return jsonify(result=offers_list)

    def post(self):
        """ Create / update an offer"""
        try:
            data = request.get_json(force=True)
            offer = models.OfferModel(**request.json)
            key = offer.put()
            return { 'result': key.id() }, 201
        except AttributeError as exc:
            abort(400, {"error": exc.message})
        except Exception as exc:
            abort(400, {"error": exc.message })


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404


if __name__ == '__main__':
    app.run(debug=True)
