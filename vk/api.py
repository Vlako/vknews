import aiohttp
import asyncio
import time
from vk.access_token import access_token


class VKApi:

    def __init__(self):
        self.access_token = access_token
        self.session = aiohttp.ClientSession()

    def __del__(self):
        self.session.close()

    async def get_user_info(self, user_id):
        async with self.session.get('https://api.vk.com/method/users.get',
                                    params={'user_ids': user_id,
                                            'fields': 'photo_max',
                                            'version': '5.60',
                                            'access_token': self.access_token}) as response:
            user_info = (await response.json())['response'][0]
            return user_info

    async def get_friends(self, user_id):
        async with self.session.get('https://api.vk.com/method/friends.get',
                                    params={'user_id': user_id,
                                            'fields': 'photo_max',
                                            'version': '5.60',
                                            'access_token': self.access_token}) as response:
            try:
                friends = (await response.json())['response']
            except KeyError :
                friends = []
            return friends

    async def get_group_members(self, group_id):
        async with self.session.get('https://api.vk.com/method/groups.getMembers',
                                    params={'group_id': group_id,
                                            'fields': 'photo_max',
                                            'version': '5.60',
                                            'access_token': self.access_token}) as response:
            return (await response.json())['response']['users']

    async def get_user_posts(self, user_id, count, offset=0):
        time.sleep(0.3)
        async with self.session.get('https://api.vk.com/method/wall.get',
                                    params={'owner_id': user_id,
                                            'count': count,
                                            'offset': offset,
                                            'filter': 'owner',
                                            'version': '5.60',
                                            'access_token': self.access_token}) as response:
            return (await response.json())['response'][1:]

    async def get_user_wall(self, user_id, count=float('inf')):
        time.sleep(0.3)
        async with self.session.get('https://api.vk.com/method/wall.get',
                                    params={'owner_id': user_id,
                                            'count': 0,
                                            'filter': 'owner',
                                            'version': '5.60',
                                            'access_token': self.access_token}) as response:
            try:
                tasks = [asyncio.ensure_future(self.get_user_posts(user_id, 100, offset))
                         for offset in range(0, min((await response.json())['response'][0], count), 100)]
                wall = []
                for i in await asyncio.gather(*tasks):
                    wall += i
                return wall
            except KeyError:
                return []