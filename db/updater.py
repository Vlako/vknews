import asyncio
import aiohttp

from vk.client import VKClient
from fb.api import get_shareds
from db.models import *


async def update_all_users():
    with db_session:

        client = VKClient(aiohttp.ClientSession())
        group_name = 'csu_iit'
        if Group.get(id=group_name) is None:
            Group(id=group_name)

        group_members = await client.get_group_members(group_name)

        for group_member in group_members:

            if User.get(user_id=group_member.user_id) is None:
                User(user_id=group_member.user_id,
                     first_name=group_member.first_name,
                     last_name=group_member.last_name,
                     photo=group_member.photo)
            else:
                User[group_member.user_id].first_name=group_member.first_name
                User[group_member.user_id].last_name=group_member.last_name
                User[group_member.user_id].photo=group_member.photo

            friends = await client.get_friends(group_member.user_id)

            for friend in friends:
                if User.get(user_id=friend.user_id) is None:
                    User(user_id=friend.user_id,
                         first_name=friend.first_name,
                         last_name=friend.last_name,
                         photo=friend.photo)
                else:
                    User[friend.user_id].first_name=friend.first_name
                    User[friend.user_id].last_name=friend.last_name
                    User[friend.user_id].photo=friend.photo

            friends = set(friend.user_id for friend in friends)
            User[group_member.user_id].friends = select(user for user in User if user.user_id in friends)[:]

        group_members = set(group_member.user_id for group_member in group_members)
        Group[group_name].users = select(user for user in User if user.user_id in group_members)[:]


async def update_user_posts(user_id, vkclient, session):
    with db_session:
        posts = await vkclient.get_user_wall(user_id, 20)
        for post in posts:
            if Post.get(id=str(post.from_id)+'_'+str(post.post_id)) is None:
                Post(id=str(post.from_id)+'_'+str(post.post_id),
                     text=post.text,
                     date=post.date,
                     photos=[attachment['photo']['src_big']
                             for attachment in post.attachments
                             if 'photo' in attachment],
                     comments=post.comments,
                     reposts=post.reposts,
                     likes=post.likes,
                     user=User[user_id])
                post_id = str(post.from_id)+'_'+str(post.post_id)

                for original_post in post.original_post:

                    if original_post.from_id > 0:
                        user = await vkclient.get_user(original_post.from_id)
                        if User.get(user_id=user.user_id) is None:
                            User(user_id=user.user_id,
                                 first_name=user.first_name,
                                 last_name=user.last_name,
                                 photo=user.photo)
                        else:
                            User[user.user_id].first_name=user.first_name
                            User[user.user_id].last_name=user.last_name
                            User[user.user_id].photo=user.photo

                        if Post.get(id=str(original_post.from_id)+'_'+str(original_post.post_id)) is None:
                            Post(id=str(original_post.from_id)+'_'+str(original_post.post_id),
                                 text=original_post.text,
                                 date=original_post.date,
                                 photos=[attachment['photo']['src_big']
                                         for attachment in original_post.attachments
                                         if 'photo' in attachment],
                                 comments=original_post.comments,
                                 reposts=original_post.reposts,
                                 likes=original_post.likes,
                                 user=User[user.user_id])

                        Post[post_id].original_post = str(original_post.from_id)+'_'+str(original_post.post_id)
                        post_id = str(original_post.from_id)+'_'+str(original_post.post_id)
                    else: break

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
                                                                        'shareds': await get_shareds(attachment['link']['url'], session)}


async def update_posts():
    session = aiohttp.ClientSession()
    vkclient = VKClient(session)
    with db_session:
        users = list(set(select(user.friends for user in User if user in Group['csu_iit'].users)))
    for i in range(len(users) // 100 + 1):
        print(i*100)
        futures = []
        for user in users[i*100: (i+1)*100]:
            futures.append(update_user_posts(user.user_id, vkclient, session))
        await asyncio.wait(futures)


async def main():
    await update_all_users()
    await update_posts()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
