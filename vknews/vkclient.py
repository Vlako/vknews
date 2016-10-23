import aiohttp, asyncio


class VKClient:

    def __init__(self):
        self.session = aiohttp.ClientSession()

    def __del__(self):
        self.session.close()

    async def get_user_info(self, user_id):
        async with self.session.get('https://api.vk.com/method/users.get',
                               params={'user_ids': user_id,
                                       'fields': 'photo_100'}) as response:
            user_info = (await response.json())['response'][0]
            return user_info

    async def get_friends(self, user_id):
        async with self.session.get('https://api.vk.com/method/friends.get',
                                params={'user_id': user_id}) as response:
            try:
                friends = (await response.json())['response']
            except KeyError:
                friends = []
            return friends

    async def get_group_members(self, group_id):
        async with self.session.get('https://api.vk.com/method/groups.getMembers',
                               params={'group_id': group_id, 'fields': 'photo_200'}) as response:
            return (await response.json())['response']['users']

    async def get_graph(self, group_id):
        tasks = []
        members = []
        for user in await self.get_group_members(group_id):
            members.append(user['uid'])
            tasks.append(asyncio.ensure_future(self.get_friends(user['uid'])))
        graph = dict(zip(members, await asyncio.gather(*tasks)))
        return graph

    async def __get_user_posts(self, user_id, count, offset):
        async with self.session.get('https://api.vk.com/method/wall.get',
                               params={'owner_id': user_id,
                                       'count': count,
                                       'offset': offset,
                                       'filter': 'owner'}) as response:
            return (await response.json())['response'][1:]

    async def get_user_wall(self, user_id):
        async with self.session.get('https://api.vk.com/method/wall.get',
                                    params={'owner_id': user_id,
                                            'count': 0,
                                            'filter': 'owner'}) as response:
            try:
                tasks = []
                for offset in range(0, (await response.json())['response'][0], 100):
                    task = asyncio.ensure_future(self.__get_user_posts(user_id, 100, offset))
                    tasks.append(task)
                wall = []
                for i in await asyncio.gather(*tasks):
                    wall += i
                return wall
            except KeyError:
                return []

    async def get_user_news(self, user_id, sort_key='likes'):
        tasks = []
        for friend in await self.get_friends(user_id):
            tasks.append(asyncio.ensure_future(self.get_user_wall(friend)))
        news = []
        for i in await asyncio.gather(*tasks):
            news += i
        news.sort(key=lambda x: x[sort_key]['count'], reverse=True)
        return news



