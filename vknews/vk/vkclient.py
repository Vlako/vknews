import asyncio
import datetime
from typing import List, Dict

from vknews.vk.vkapi import VKApi
from vknews.vk.vkmodels import VKUser, VKPost


class VKClient:

    def __init__(self):
        self.__api = VKApi()
        self.__default_photo_100 = "https://vk.com/images/deactivated_hid_100.gif"
        self.__default_photo_200 = "https://vk.com/images/deactivated_hid_200.gif"

    def __get_user_from_json(self, user) -> VKUser:
        return VKUser(user_id=user['uid'],
                      first_name=user['first_name'],
                      last_name=user['last_name'],
                      photo_100=user['photo_100'] if 'photo_100' in user else self.__default_photo_100,
                      photo_200=user['photo_200'] if 'photo_200' in user else self.__default_photo_200)

    def __get_post_from_json(self, post) -> VKPost:
        if post['post_type'] == 'post':
            return VKPost(post_id=post['id'],
                          from_id=post['from_id'],
                          date=datetime.datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M'),
                          text=post['text'],
                          attachments=post['attachments'] if 'attachments' in post else [],
                          comments=post['comments']['count'],
                          likes=post['likes']['count'],
                          reposts=post['reposts']['count'],
                          original_post=[self.__get_post_from_json(original_post)
                                         for original_post in post['copy_history']]
                                         if 'copy_history' in post else None)
        else:
            post['post_type'] = 'post'
            return VKPost(post_id=post['id'],
                          from_id=post['from_id'],
                          date=datetime.datetime.fromtimestamp(post['date']).strftime('%Y-%m-%d %H:%M'),
                          text=post['copy_text'] if 'copy_text' in post else '',
                          attachments=[],
                          comments=post['comments']['count'],
                          likes=post['likes']['count'],
                          reposts=post['reposts']['count'],
                          original_post=[self.__get_post_from_json(post)])

    async def get_graph(self, group_id) -> Dict[int, List[int]]:
        tasks = []
        members = []
        for user in await self.__api.get_group_members(group_id):
            members.append(user['uid'])
            tasks.append(asyncio.ensure_future(self.__api.get_friends(user['uid'])))
        graph = dict(zip(members, await asyncio.gather(*tasks)))
        return graph

    async def get_user_news(self, user_id, sort_key='likes', count=100) -> List[VKPost]:
        tasks = [asyncio.ensure_future(self.__api.get_user_wall(friend.user_id))
                 for friend in await self.get_friends(user_id)]
        news = []
        for i in await asyncio.gather(*tasks):
            news += i
        news.sort(key=lambda x: x[sort_key]['count'], reverse=True)
        return [self.__get_post_from_json(post) for post in news[:count]]

    async def get_user(self, user_id) -> VKUser:
        user = await self.__api.get_user_info(user_id)
        return self.__get_user_from_json(user)

    async def get_group_members(self, group_id) -> List[VKUser]:
        return [self.__get_user_from_json(user)
                for user in await self.__api.get_group_members(group_id)]

    async def get_friends(self, user_id) -> List[VKUser]:
        return [self.__get_user_from_json(user)
                for user in await self.__api.get_friends(user_id)]
