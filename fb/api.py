async def get_shareds(link, session):
    async with session.get('https://graph.facebook.com/?id='+link,
                           params={'access_token': '1235602329852571|GSIboWHuaEJcxZ-rKDFQMaT-guY'}) as response:
        resp = await response.json()
        print(await response.text())
        if 'share' in resp:
            return resp['share']['share_count']
        else:
            return -1