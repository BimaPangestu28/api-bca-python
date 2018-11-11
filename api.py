import requests
import json
import base64
import hmac
import hashlib
import datetime
from cpybca.bca import Bca

class api_bca():
    def __init__(self, api_key, api_secret, client_id, client_secret, host = 'https://sandbox.bca.co.id'):
        self.__api_key          = api_key
        self.__api_secret       = api_secret
        self.__client_id        = client_id
        self.__client_secret    = client_secret
        self.__host             = host
        self.__data             = client_id + ':' + client_secret
        self.__encode           = str(base64.b64encode(self.__data.encode()).decode('UTF-8'))
        self.sign()

    def sign(self):
        self.data_request       = 'grant_type=client_credentials'
        headers_request    = {
                                      'Content-Type': 'application/x-www-form-urlencoded',
                                      'Authorization': 'Basic ' + self.__encode
                                  }
        url                     = self.__host + '/api/oauth/token'
        response                = requests.post(url, data=self.data_request, headers=headers_request)
        data                    = response.json()
        self.__access_token     = data['access_token']
        return data

    def signature(self, http_method, relative_url, request_body = b'', timestamp = ''):
        signature = hmac.new(self.__api_secret.encode(), digestmod=hashlib.sha256)
        print(relative_url)

        string_to_sign = http_method + ':' + relative_url + ':' + self.__access_token + \
                         ':' + hashlib.sha256(request_body.replace(b' ', b'')).hexdigest() + ':' + timestamp

        signature.update(string_to_sign.encode())

        return signature.hexdigest()

    def get_balance(self, corporateID, AccountNumber):
        if(isinstance(AccountNumber, list)):
            AccountNumber = '%2C'.join(AccountNumber)

        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
        timestamp = timestamp[:23] + timestamp[26:]

        relative_url    =   '/banking/v3/corporates/' + corporateID + '/accounts/' + AccountNumber
        signature       =   self.signature('GET', relative_url, timestamp=timestamp)
        url             =   self.__host + relative_url

        headers         =   {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json',
            'origin': 'localhost',
            'X-BCA-Key': self.__api_key,
            'X-BCA-Timestamp': timestamp,
            'X-BCA-Signature': signature
        }

        response    =   requests.get(url, headers=headers)

        return response.json()

    def account_statement(self, corporateID, AccountNumber, StartDate, EndDate):
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
        timestamp = timestamp[:23] + timestamp[26:]

        relative_url = '/banking/v3/corporates/{}/accounts/{}/statements?EndDate={}&StartDate={}'.format(corporateID, AccountNumber, EndDate, StartDate)
        url = self.__host + relative_url

        signature = self.signature('GET', relative_url, timestamp=timestamp)

        headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json',
            'origin': 'localhost',
            'X-BCA-Key': self.__api_key,
            'X-BCA-Timestamp': timestamp,
            'X-BCA-Signature': signature
        }

        response = requests.get(url, headers=headers)

        return response.json()

    def fund_transfer(self, CorporateID, SourceAccountNumber, TransactionID, TransactionDate, ReferenceID, CurrencyCode, Amount, BeneficiaryAccountNumber, Remark1, Remark2):
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
        timestamp = timestamp[:23] + timestamp[26:]

        relative_url = '/banking/corporates/transfers'
        url = self.__host + relative_url

        data = {
            "CorporateID" : CorporateID,
            "SourceAccountNumber" : SourceAccountNumber,
            "TransactionID" : TransactionID,
            "TransactionDate" : TransactionDate,
            "ReferenceID" : ReferenceID,
            "CurrencyCode" : CurrencyCode,
            "Amount" : Amount,
            "BeneficiaryAccountNumber" : BeneficiaryAccountNumber,
            "Remark1" : Remark1,
            "Remark2" : Remark2
        }

        data = json.dumps(data, separators=(',', ':')).encode()
        signature = self.signature('POST', relative_url, data, timestamp)

        headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json',
            'origin': 'localhost',
            'X-BCA-Key': self.__api_key,
            'X-BCA-Timestamp': timestamp,
            'X-BCA-Signature': signature,
        }

        response = requests.post(url, data=data, headers=headers)
        print(data)

        return response.json()


    def domestic_fund_transfer(self, ChannelID, CredentialID, TransactionID, TransactionDate, ReferenceID, SourceAccountNumber, BeneficiaryAccountNumber, BeneficiaryBankCode, BeneficiaryName, Amount, TransferType, BeneficiaryCustType, BeneficiaryCustResidence, CurrencyCode, Remark1, Remark2):
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
        timestamp = timestamp[:23] + timestamp[26:]

        relative_url = '/banking/corporates/transfers/domestic'
        url = self.__host + relative_url

        data    =   {
            "TransactionID" : TransactionID,
            "TransactionDate" : TransactionDate,
            "ReferenceID": ReferenceID,
            "SourceAccountNumber" : SourceAccountNumber,
            "BeneficiaryAccountNumber" : BeneficiaryAccountNumber,
            "BeneficiaryBankCode" : BeneficiaryBankCode,
            "BeneficiaryName" : BeneficiaryName,
            "Amount" : Amount,
            "TransferType" : TransferType,
            "BeneficiaryCustType" : BeneficiaryCustType,
            "BeneficiaryCustResidence" : BeneficiaryCustResidence,
            "CurrencyCode" : CurrencyCode,
            "Remark1" : Remark1,
            "Remark2" : Remark2
        }

        data = json.dumps(data, separators=(',', ':')).encode()
        signature = self.signature('POST', relative_url, data, timestamp)

        headers = {
            'Authorization': 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json',
            'origin': 'localhost',
            'X-BCA-Key': self.__api_key,
            'X-BCA-Timestamp': timestamp,
            'X-BCA-Signature': signature,
            'ChannelID': ChannelID,
            'CredentialID': CredentialID,
        }

        response = requests.post(url, data=data, headers=headers)
        print(data)

        return response.json()



bca =   api_bca('520290a2-0800-4577-b2a2-5612b0b63a81', '46065b5c-664b-41a5-8758-714280790630', '57c72ee8-9cc9-443f-87bc-b3ef895535ba', '6a120b20-5bf9-4e35-b248-25ec22624ed7')

# print(bca.fund_transfer('BCAAPI2016', '0201245680', '00000001', '2018-10-26', '12345/PO/2016', 'IDR', '100000.00', '0201245681', 'Transfer Test', 'Online Transfer'))
print(bca.domestic_fund_transfer('95051', 'BCAAPI', '00000001', '2018-10-26', '12345/PO/2016', '0201245680', '0201245681', 'BRONINJA', 'Tester', '100000.00', 'LLG', '1', '1', 'IDR', 'Transfer Test', 'Online Transfer'))
# bca = Bca('520290a2-0800-4577-b2a2-5612b0b63a81', '46065b5c-664b-41a5-8758-714280790630')
# bca.sign_in('57c72ee8-9cc9-443f-87bc-b3ef895535ba', '6a120b20-5bf9-4e35-b248-25ec22624ed7')
# print(bca.account_statement('BCAAPI2016', '0201245680', '2016-08-29', '2016-09-01'))
# print(bca.get_statement('BCAAPI2016', '0201245680', '2016-08-29', '2016-09-01'))
# print(bca.sign())