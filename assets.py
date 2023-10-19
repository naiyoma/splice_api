from .models import CurrencyEnum
import base64, codecs, json, requests


REST_HOST = 'localhost:8289'
MACAROON_PATH = './volumes/tapd/alice-tap/data/regtest/admin.macaroon'
TLS_PATH = './volumes/tapd/alice-tap/tls.cert'
base_url = f'https://{REST_HOST}/v1/taproot-assets'
macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
headers = {'Grpc-Metadata-macaroon': macaroon}

def create_asset(asset, amount):
    url = f'{base_url}/assets'
    data = {
        'asset': {
            'asset_type': 'NORMAL',
            'amount': amount,
            'name': asset.value,
        },
        'enable_emission': True,
        'short_response': True,
    }

    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def finalize_asset_creation():
    url = f'{base_url}/assets/mint/finalize'
    data = {
        'short_response': True,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def exchange_asset(to_burn, amount_to_burn, to_mint, amount_to_mint):
    pass

def burn_asset(asset_id, amount):
    url = f'{base_url}/burn'
    data = {
        'asset_id': base64.b64encode(bytes.fromhex(asset_id)),
        'asset_id_str': asset_id,
        'amount_to_burn': amount,
        'confirmation_text': "Burn successful",
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def generate_address(asset_id, amount):
    url = f'{base_url}/addrs'
    data = {
        'asset_id': base64.b64encode(bytes.fromhex(asset_id)),
        'amt': amount,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def send_asset(address):
    url = f'{base_url}/send'
    data = {
        'tap_addrs': address,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()