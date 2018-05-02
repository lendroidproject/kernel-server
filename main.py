from flask import Flask, render_template, request, jsonify, abort
from flask_restplus import Resource, Api
from google.appengine.api import app_identity
from flask_cors import CORS

import models

app = Flask(__name__)
# Add CORS support for all domains
CORS(app, origins="*", allow_headers=[
    "Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
    supports_credentials=True)
# Add support for Restplus api
api = Api(app)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404


@api.route('/offers', endpoint='offers')
class Offers(Resource):
    def get(self):
        """ Return a list of existing loan offers"""
        offers = models.OfferModel.query().fetch()
        offers_list = [offer.to_dict() for offer in offers]
        return jsonify(offers=offers_list)

    def post(self):
        """ Create / update an offer"""
        try:
            data = request.get_json(force=True)
            offer = models.OfferModel(**request.json)
            key = offer.put()
            return { 'id': key.id() }, 201
        except AttributeError as exc:
            abort(400, {"error": exc.message})
        except Exception as exc:
            abort(400, {"error": exc.message })


if __name__ == '__main__':
    app.run(debug=True)
