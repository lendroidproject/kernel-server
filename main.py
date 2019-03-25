from datetime import datetime as dt

from google.appengine.ext import ndb
from google.appengine.ext import deferred

from flask import Flask, render_template, request, jsonify, abort
from flask_restplus import Resource, Api
from google.appengine.api import app_identity
from flask_cors import CORS

import logging

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


def update_offer_if_expired(offer_id):
    # Get Offer
    offer = ndb.Key('OfferModel', offer_id).get()
    if int(offer.offerExpiry) <= (dt.utcnow() - dt(1970, 1, 1)).total_seconds():
        offer.is_filled_or_expired = True
        offer.put()


@app.route('/cron/update_expired_kernels', methods=['GET', 'POST'])
def update_expired_kernels():
    """Update expired kernels cron job"""

    # get offer entities
    q = models.OfferModel.query(models.OfferModel.is_filled_or_expired == False)

    # update status for each registration entities
    for offer_key in q.iter(keys_only=True):
        try:
            # refetch since it's way slow
            deferred.defer(update_offer_if_expired, offer_key.id())
        except Exception as e:
            app.logger.error(e)
            logging.error("Error calling deferred task to update_offer_if_expired: " + e)

    return 'Success'


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
