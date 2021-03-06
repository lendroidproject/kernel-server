from datetime import datetime as dt

from google.appengine.ext import ndb
from google.appengine.ext import deferred
from google.appengine.api import urlfetch

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

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
WRANGLER_URL = 'https://lendroidwrangler.com'


def update_offer_if_expired(offer_id):
    # Get Offer
    offer = ndb.Key('OfferModel', offer_id).get()
    if offer and int(offer.offerExpiry) <= (dt.utcnow() - dt(1970, 1, 1)).total_seconds():
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


@api.route('/offers/<int:id>', endpoint='offer')
class OfferItem(Resource):

    def get(self, id):
        """ Return an existing loan offer"""
        offers = [models.OfferModel.get_by_id(id)]
        offers_list = [offer.to_dict() for offer in offers if offer]
        if not len(offers_list):
            abort(404, {"error": "offer not found"})
        return jsonify(result=offers_list)


@api.route('/offers/delete', endpoint='deleteOffer')
class DeleteOfferItem(Resource):

    def post(self):
        """ Delete an existing loan offer"""
        data = request.get_json(force=True)
        id = data['id']
        offer = models.OfferModel.get_by_id(id)
        if not offer:
            abort(404)
        creator = offer.lender if offer.lender != ZERO_ADDRESS else offer.borrower
        url = '{0}/is_valid_protocol_transaction_sender/{1}/{2}'.format(
            WRANGLER_URL,
            creator,
            data['txHash']
        )
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            abort(404)
        else:
            offer.key.delete()
            return {'result': True}, 201


@api.route('/offers/fill', endpoint='fillOffer')
class FIllOfferItem(Resource):

    def post(self):
        """ Fill an offer"""
        data = request.get_json(force=True)
        id = data['id']
        value = data['value']
        url = '{0}/is_valid_protocol_transaction_sender/{1}/{2}'.format(
            WRANGLER_URL,
            data['fillerAddress'],
            data['txHash']
        )
        result = urlfetch.fetch(url)
        if result.status_code != 200:
            abort(404)

        if models.OfferModel.fill(id, value):
            return {'result': True}, 201
        else:
            abort(404)


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404


if __name__ == '__main__':
    app.run(debug=True)
