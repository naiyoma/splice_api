import base64, codecs, json, requests

REST_HOST = 'localhost:8289'
MACAROON_PATH = './volumes/tapd/alice-tap/data/regtest/admin.macaroon'
TLS_PATH = './volumes/tapd/alice-tap/tls.cert'

url = f'https://{REST_HOST}/v1/taproot-assets/assets'
macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
headers = {'Grpc-Metadata-macaroon': macaroon}
data = {
  'asset': {
    'asset_type': 'NORMAL',
    'amount': 100000000,
    'name': 'KES',
  },
  'enable_emission': True,
}
r = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
print(r.json())