import unittest
import asyncio, aiohttp
from vkclient import VKClient


class TestVKClient(unittest.TestCase):

    def test_get_user_info(self):
        with aiohttp.ClientSession() as session:
            loop = asyncio.get_event_loop()
            user_id = 1
            vkclient = VKClient()
            user_info = loop.run_until_complete(vkclient.get_user_info(user_id))
            self.assertIsInstance(user_info, dict)
            self.assertEqual(user_info['first_name'], 'Павел')
            self.assertEqual(user_info['last_name'], 'Дуров')
