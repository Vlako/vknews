from datetime import datetime
from pony.orm import *
from db.config import user, password, host, database

db = Database()


class User(db.Entity):
    user_id = PrimaryKey(int)
    first_name = Optional(str)
    last_name = Optional(str)
    photo = Required(str)
    friends = Set('User', reverse='friends')
    groups = Set('Group')
    posts = Set('Post')


class Group(db.Entity):
    id = PrimaryKey(str)
    users = Set(User)


class Post(db.Entity):
    id = PrimaryKey(str)
    text = Optional(str)
    date = Required(datetime)
    photos = Optional(Json)
    comments = Required(int)
    reposts = Required(int)
    likes = Required(int)
    user = Required(User)
    link = Optional(Json)
    original_post = Optional(str)


db.bind('postgres', user=user, password=password, host=host, database=database)
db.generate_mapping(create_tables=True)
