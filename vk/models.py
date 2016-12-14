class User:

    def __init__(self, user_id, first_name, last_name, photo):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo


class Post:

    def __init__(self, post_id, from_id, date, text, attachments, comments, likes, reposts, original_post):
        self.post_id = post_id
        self.from_id = from_id
        self.date = date
        self.text = text
        self.attachments = attachments
        self.comments = comments
        self.likes = likes
        self.reposts = reposts
        self.original_post = original_post