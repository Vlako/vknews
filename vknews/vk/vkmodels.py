class VKUser:

    def __init__(self, user_id, first_name, last_name, photo_100, photo_200):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.photo_100 = photo_100
        self.photo_200 = photo_200


class VKPost:

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