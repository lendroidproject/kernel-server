
from google.appengine.ext import ndb


class OfferModel(ndb.Model):
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    lender = ndb.StringProperty(required=True)
    borrower = ndb.StringProperty(required=True)
    relayer = ndb.StringProperty(required=True)
    wrangler = ndb.StringProperty(required=True)
    collateralToken = ndb.StringProperty(required=True)
    loanToken = ndb.StringProperty(required=True)
    collateralAmount = ndb.StringProperty(required=True)
    loanAmountOffered = ndb.StringProperty(required=True)
    interestRatePerDay = ndb.StringProperty(required=True)
    loanDuration = ndb.StringProperty(required=True)
    offerExpiry = ndb.StringProperty(required=True)
    relayerFeeLST = ndb.StringProperty(required=True)
    monitoringFeeLST = ndb.StringProperty(required=True)
    rolloverFeeLST = ndb.StringProperty(required=True)
    closureFeeLST = ndb.StringProperty(required=True)
    creatorSalt = ndb.StringProperty(required=True)
    vCreator = ndb.StringProperty(required=True)
    rCreator = ndb.StringProperty(required=True)
    sCreator = ndb.StringProperty(required=True)
