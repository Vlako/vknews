class User:

    def __init__(self, user_id, first_name, last_name, photo):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo


class Post:

    def __init__(self, id, text, date, photos, comments, reposts, likes, link, original_post):
        self.id = id
        self.from_id=int(id.split('_')[0])
        self.text = text
        self.date = date
        self.photos = photos
        self.comments = comments
        self.reposts = reposts
        self.likes = likes
        self.link = link
        self.original_post = original_post
