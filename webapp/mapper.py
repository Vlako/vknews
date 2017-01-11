from webapp.models import *
from db.models import Post as DBPost, db_session

def get_user_from_dbuser(user) -> User:
    return User(user_id=user.user_id,
                first_name=user.first_name,
                last_name=user.last_name,
                photo=user.photo)


def get_post_from_dbpost(post) -> Post:
    original_posts = [get_post_from_dbpost(DBPost[post.original_post])] if len(post.original_post) else []
    if len(original_posts):
        original_posts += original_posts[-1].original_post
    return Post(id=post.id,
                text=post.text.replace('<br>', '\n'),
                date=post.date.strftime('%Y-%m-%d %H:%M'),
                photos=post.photos,
                comments=post.comments,
                reposts=post.reposts,
                likes=post.likes,
                link=post.link,
                original_post=original_posts)