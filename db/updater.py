import asyncio
import concurrent.futures
from vk.client import VKClient
from fb.api import get_shareds
from db.models import *
import zlib


async def update_all_users():
    with db_session:

        client = VKClient()
        group_name = 'csu_iit'
        Group(id=group_name)

        for group_member in await client.get_group_members(group_name):

            if User.get(user_id=group_member.user_id) is None:
                User(user_id=group_member.user_id,
                     first_name=group_member.first_name,
                     last_name=group_member.last_name,
                     photo=group_member.photo)
            else:
                User[group_member.user_id].first_name=friend.first_name,
                User[group_member.user_id].last_name=friend.last_name,
                User[group_member.user_id].photo=friend.photo

            Group[group_name].users.add(User[group_member.user_id])
            User[group_member.user_id].groups.add(Group[group_name])

            for friend in await client.get_friends(group_member.user_id):
                if User.get(user_id=friend.user_id) is None:
                    User(user_id=friend.user_id,
                         first_name=friend.first_name,
                         last_name=friend.last_name,
                         photo=friend.photo)
                else:
                    User[friend.user_id].first_name=friend.first_name,
                    User[friend.user_id].last_name=friend.last_name,
                    User[friend.user_id].photo=friend.photo
                User[group_member.user_id].friends.add(User[friend.user_id])


def update_user_posts(user_id, posts):
    with db_session:
        for post in posts:
            if Post.get(id=str(post.from_id)+'_'+str(post.post_id)) is None:
                Post(id=str(post.from_id)+'_'+str(post.post_id),
                     text=zlib.compress(post.text.encode()),
                     date=post.date,
                     photos=[attachment['photo']['src_big']
                             for attachment in post.attachments
                             if 'photo' in attachment],
                     comments=post.comments,
                     reposts=post.reposts,
                     likes=post.likes,
                     user=User[user_id])
            else:
                Post[str(post.from_id)+'_'+str(post.post_id)].comments=post.comments
                Post[str(post.from_id)+'_'+str(post.post_id)].reposts=post.reposts
                Post[str(post.from_id)+'_'+str(post.post_id)].likes=post.likes
            for attachment in post.attachments:
                if 'link' in attachment:
                    image = attachment['link']['image_src'] if 'image_src' in attachment['link'] else None
                    Post[str(post.from_id)+'_'+str(post.post_id)].link={'title': attachment['link']['title'],
                                                                        'url': attachment['link']['url'],
                                                                        'description': attachment['link']['description'],
                                                                        'image': image,
                                                                        'shareds': get_shareds(attachment['link']['url'])}
    return True


async def update_posts():
    vkclient = VKClient()
    user_counter = 0
    with db_session:
        users = list(select(user.user_id for user in User))
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for user_id in users:
            user_counter += 1
            print(user_counter)
            posts = await vkclient.get_user_wall(user_id, 100)
            futures.append(executor.submit(update_user_posts, user_id, posts))
        concurrent.futures.as_completed(futures)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_all_users())
    loop.run_until_complete(update_posts())
