import base64, codecs, json, requests


REST_HOST = 'alice-tap:8089'
MACAROON_PATH = '/home/tap/.tapd/data/regtest/admin.macaroon'
TLS_PATH = '/home/tap/.tapd/tls.cert'
base_url = f'https://{REST_HOST}/v1/taproot-assets'


def create_asset(asset, amount):
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/assets'
    data = {
        'asset': {
            'asset_type': 'NORMAL',
            'amount': amount,
            'name': asset,
        },
        'enable_emission': True,
        'short_response': False,
    }

    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def finalize_asset_creation():
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/assets/mint/finalize'
    data = {
        'short_response': False,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def list_assets():
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/assets'
    res = requests.get(url, headers=headers, verify=TLS_PATH)
    return res.json()

def get_transfers():
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/assets/transfers'
    res = requests.get(url, headers=headers, verify=TLS_PATH)
    return res.json()

def burn_asset(asset_id, amount):
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/burn'
    data = {
        'asset_id_str': asset_id,
        'amount_to_burn': amount,
        'confirmation_text': "assets will be destroyed",
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def generate_address(asset_id, amount):
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/addrs'
    data = {
        'asset_id': asset_id,
        'amt': amount,
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()

def send_asset(address):
    macaroon = codecs.encode(open(MACAROON_PATH, 'rb').read(), 'hex')
    headers = {'Grpc-Metadata-macaroon': macaroon}
    url = f'{base_url}/send'
    data = {
        'tap_addrs': [address],
    }
    res = requests.post(url, headers=headers, data=json.dumps(data), verify=TLS_PATH)
    return res.json()