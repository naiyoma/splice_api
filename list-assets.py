import base64, codecs, json, requests
import binascii


REST_HOST = 'localhost:8289'
MACAROON_PATH = './volumes/tapd/alice-tap/data/regtest/admin.macaroon'
TLS_PATH = './volumes/tapd/alice-tap/tls.cert'
batch_key_hex = '03a198628bf4c6b2d20ad62da4c6dd7f5325c2b3131aa6055864e577e5fb37a97b'
batch_key = binascii.b2a_base64(bytes.fromhex(batch_key_hex)).decode()

url = f'https://{REST_HOST}/v1/taproot-assets/assets/mint/batches/{batch_key}'
macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
headers = {'Grpc-Metadata-macaroon': macaroon}
r = requests.get(url, headers=headers, verify=TLS_PATH)
print(r.json())