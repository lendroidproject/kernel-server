
from google.appengine.ext import ndb


class OfferModel(ndb.Model):
    created_at = ndb.DateTimeProperty(indexed=True, auto_now_add=True)
    lender = ndb.StringProperty(indexed=False, required=True)
    borrower = ndb.StringProperty(indexed=False, required=True)
    relayer = ndb.StringProperty(indexed=False, required=True)
    wrangler = ndb.StringProperty(indexed=False, required=True)
    collateralToken = ndb.StringProperty(indexed=False, required=True)
    loanToken = ndb.StringProperty(indexed=False, required=True)
    collateralAmount = ndb.StringProperty(indexed=False, required=True)
    loanAmountOffered = ndb.StringProperty(indexed=False, required=True)
    interestRatePerDay = ndb.StringProperty(indexed=False, required=True)
    loanDuration = ndb.StringProperty(indexed=False, required=True)
    offerExpiry = ndb.StringProperty(indexed=False, required=True)
    relayerFeeLST = ndb.StringProperty(indexed=False, required=True)
    monitoringFeeLST = ndb.StringProperty(indexed=False, required=True)
    rolloverFeeLST = ndb.StringProperty(indexed=False, required=True)
    closureFeeLST = ndb.StringProperty(indexed=False, required=True)
    creatorSalt = ndb.StringProperty(indexed=False, required=True)
    vCreator = ndb.StringProperty(indexed=False, required=True)
    rCreator = ndb.StringProperty(indexed=False, required=True)
    sCreator = ndb.StringProperty(indexed=False, required=True)
    ecSignatureCreator = ndb.StringProperty(indexed=False, required=True)

    loanAmountFilled = ndb.StringProperty(indexed=False, required=False)
    is_filled_or_expired = ndb.BooleanProperty(default=False)

    @classmethod
    def get_valid_offers(cls):
        return cls.query(cls.is_filled_or_expired == False).fetch()

    @classmethod
    def fill(cls, id, value):
        _key = ndb.Key(cls, id)
        order = _key.get()
        if order:
            filledAmount = int(order.loanAmountFilled) if order.loanAmountFilled else 0
            order.loanAmountFilled = str(filledAmount + int(value))
            if int(order.loanAmountOffered) == int(order.loanAmountFilled):
                order.is_filled_or_expired = True
            order.put()
            return True
        return False

    @classmethod
    def delete_by_id(cls, id):
        _key = ndb.Key(cls, id)
        if _key.get():
            _key.delete()
            return True
        return False

    def to_dict(self):
        result = super(OfferModel, self).to_dict()
        result['id'] = self.key.id() #get the key as a string
        return result
