import asyncio
import unittest

from vk.client import VKClient


class TestVKClient(unittest.TestCase):

    def test_get_user_info(self):
        loop = asyncio.get_event_loop()
        user_id = 1
        vkclient = VKClient()
        user = loop.run_until_complete(vkclient.get_user(user_id))
        self.assertEqual(user.first_name, 'Павел')
        self.assertEqual(user.last_name, 'Дуров')
