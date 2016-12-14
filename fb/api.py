import requests


def get_shareds(link):
    resp = requests.get('http://graph.facebook.com/?id='+link).json()
    if 'share' in resp:
        return resp['share']['share_count']
    else:
        return -1