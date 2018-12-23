import requests
import random


class TestOfferModelEndpoints(object):

    def __init__(self, *args, **kwargs):
        self.api_uri = 'http://localhost:20080'
        self.random_gae_entity_id = None
        self.existent_offer_id = None

    def set_random_gae_entity_id(self):
        id_range = list(map(str, range(10)))
        self.random_gae_entity_id = ''.join([random.choice(id_range) for _ in range(16)])

    def test_localhost(self):
        response = requests.get(self.api_uri)
        assert response.status_code == 200
        print("\ntest_localhost works!")

    def test_get_all_offers(self):
        response = requests.get('{0}/offers'.format(self.api_uri))
        assert response.status_code == 200
        response_jsonified = response.json()
        assert 'result' in response_jsonified
        assert type(response_jsonified['result']) == list
        print("\ntest_get_all_offers works!")

    def test_get_inexistent_offer(self):
        self.set_random_gae_entity_id()
        response = requests.get('{0}/offers/{1}'.format(self.api_uri, self.random_gae_entity_id))
        assert response.status_code == 404
        print("\ntest_get_inexistent_offer works!")

    def test_create_offer(self):
        data = {
          "borrower": "0x0000000000000000000000000000000000000000",
          "closureFeeLST": "0",
          "collateralAmount": "0",
          "collateralToken": "0xd0A1E359811322d97991E03f863a0C30C2cF029C",
          "creatorSalt": "0x4032ba01e54f710e5b2c4cc06c7ec29050fd81bb",
          "ecSignatureCreator": "0x2dfb5e24fd40ba73dc562cd4d1fe479baff116218665920a3674e9bba017e88f7219192dd4276cc63c680d8c48214754241bf953a64be129363c19e61903ac471b",
          "interestRatePerDay": "10000000000000000000",
          "lender": "0x1220Afd4F1A93ea4C25bcf0a030D98C080EAC935",
          "loanAmountOffered": "10000000000000000000",
          "loanDuration": "475200",
          "loanToken": "0xC4375B7De8af5a38a93548eb8453a498222C4fF2",
          "monitoringFeeLST": "0",
          "offerExpiry": "1537682982",
          "rCreator": "0x2dfb5e24fd40ba73dc562cd4d1fe479baff116218665920a3674e9bba017e88f",
          "relayer": "0x0000000000000000000000000000000000000000",
          "relayerFeeLST": "0",
          "rolloverFeeLST": "0",
          "sCreator": "0x7219192dd4276cc63c680d8c48214754241bf953a64be129363c19e61903ac47",
          "vCreator": 27,
          "wrangler": "0x0f02a30cA336EC791Ac8Cb40816e4Fc5aeB57E38"
        }
        response = requests.post('{0}/offers'.format(self.api_uri), json=data)
        assert response.status_code == 201
        response_jsonified = response.json()
        assert 'result' in response_jsonified
        self.existent_offer_id = response_jsonified['result']
        print("\ntest_create_offer works!")

    def test_fill_inexistent_offer(self):
        self.set_random_gae_entity_id()
        fill_value = '1000000000000000000'
        response = requests.post('{0}/offers/fill/{1}/{2}'.format(self.api_uri, self.random_gae_entity_id, fill_value))
        assert response.status_code == 404
        print("\ntest_fill_inexistent_offer works!")

    def test_fill_existent_offer(self):
        fill_value = '1000000000000000000'
        response = requests.post('{0}/offers/fill/{1}/{2}'.format(self.api_uri, self.existent_offer_id, fill_value))
        assert response.status_code == 201
        print("\ntest_fill_existent_offer works!")

    def test_fill_existent_offer_with_wrong_values(self):
        # existent_id = '5021194726146048'
        # fill_value = '1000000000000000000'
        # response = requests.post('{0}/offers/fill/{1}/{2}'.format(self.api_uri, existent_id, fill_value))
        # # assert response.status_code == 405
        print("\ntest_fill_existent_offer_with_wrong_values works!")

    def test_delete_inexistent_offer(self):
        self.set_random_gae_entity_id()
        response = requests.delete('{0}/offers/{1}'.format(self.api_uri, self.random_gae_entity_id))
        assert response.status_code == 404
        print("\ntest_delete_inexistent_offer works!")

    def test_delete_existent_offer(self):
        response = requests.delete('{0}/offers/{1}'.format(self.api_uri, self.existent_offer_id))
        assert response.status_code == 201
        print("\ntest_delete_existent_offer works!")

tester = TestOfferModelEndpoints()
tester.test_localhost()
tester.test_get_all_offers()
tester.test_get_inexistent_offer()
tester.test_fill_inexistent_offer()
tester.test_delete_inexistent_offer()
tester.test_create_offer()
tester.test_fill_existent_offer()
tester.test_delete_existent_offer()
