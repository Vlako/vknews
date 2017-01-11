import asyncio
import datetime
from typing import List

from vk.api import VKApi

from vk.models import User, Post


class VKClient:

    def __init__(self, session):
        self.__api = VKApi(session)
        self.__default_photo = "https://vk.com/images/deactivated_hid_200.gif"

    def __get_user_from_json(self, user) -> User:
        return User(user_id=user['uid'],
                    first_name=user['first_name'],
                    last_name=user['last_name'],
                    photo=user['photo_max'] if 'photo_max' in user else self.__default_photo)

    def __get_post_from_json(self, post) -> Post:
        if post['post_type'] == 'post':
            return Post(post_id=post['id'],
                        from_id=post['from_id'],
                        date=datetime.datetime.fromtimestamp(post['date']),
                        text=post['text'],
                        attachments=post['attachments'] if 'attachments' in post else [],
                        comments=post['comments']['count'],
                        likes=post['likes']['count'],
                        reposts=post['reposts']['count'],
                        original_post=[self.__get_post_from_json(original_post)
                                         for original_post in post['copy_history']]
                                         if 'copy_history' in post else [])
        else:
            post['post_type'] = 'post'
            post_id = post['id']
            from_id = post['from_id']
            date = datetime.datetime.fromtimestamp(post['date'])
            post['date'] = post['copy_post_date']
            post['id'] = post['copy_post_id']
            post['from_id'] = post['copy_owner_id']
            return Post(post_id=post_id,
                        from_id=from_id,
                        date=date,
                        text=post['copy_text'] if 'copy_text' in post else '',
                        attachments=[],
                        comments=post['comments']['count'],
                        likes=post['likes']['count'],
                        reposts=post['reposts']['count'],
                        original_post=[self.__get_post_from_json(post)])

    async def get_user_news(self, user_id, sort_key='likes', count=100) -> List[Post]:
        tasks = [asyncio.ensure_future(self.__api.get_user_wall(friend.user_id))
                 for friend in await self.get_friends(user_id)]
        news = []
        for i in await asyncio.gather(*tasks):
            news += i
        news.sort(key=lambda x: x[sort_key]['count'], reverse=True)
        return [self.__get_post_from_json(post) for post in news[:count]]

    async def get_user(self, user_id) -> User:
        user = await self.__api.get_user_info(user_id)
        return self.__get_user_from_json(user)

    async def get_group_members(self, group_id) -> List[User]:
        return [self.__get_user_from_json(user)
                for user in await self.__api.get_group_members(group_id)]

    async def get_friends(self, user_id) -> List[User]:
        return [self.__get_user_from_json(user)
                for user in await self.__api.get_friends(user_id)]

    async def get_user_wall(self, user_id, count=float('inf')) -> List[Post]:
        return [self.__get_post_from_json(post)
                for post in await self.__api.get_user_wall(user_id, count)]
