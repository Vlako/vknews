from flask import Flask, render_template
import zlib
from webapp.models import *
from db.models import User as DBUser, Group as DBGroup, Post as DBPost, db_session, select, desc, avg

app = Flask(__name__)


@app.route("/")
def index():
    with db_session:
        members = select(member
                         for member in DBUser
                         if DBGroup['csu_iit'] in member.groups).order_by(DBUser.user_id)
        return render_template('index.html', members=[User(user_id=member.user_id,
                                                           first_name=member.first_name,
                                                           last_name=member.last_name,
                                                           photo=member.photo)
                                                      for member in members])


@app.route('/thread/<id>/<sort>')
def thread(id, sort):
    with db_session:
        user_id = id
        if sort == 'comments':
            sort_field = desc(DBPost.comments)
        elif sort == 'reposts':
            sort_field = desc(DBPost.reposts)
        elif sort == 'normalization':
            sort_field = lambda post : desc(post.likes / (avg(p.likes for p in post.user.posts) + 1))
        else:
            sort_field = desc(DBPost.likes)
        news = select(post
                      for post in DBPost
                      if post.user in DBUser[user_id].friends).order_by(sort_field)[:100]
        news = [Post(id=post.id,
                     text=zlib.decompress(post.text).decode(),
                     date=post.date.strftime('%Y-%m-%d %H:%M'),
                     photos=post.photos,
                     comments=post.comments,
                     reposts=post.reposts,
                     likes=post.likes,
                     link=post.link)
                for post in news]
        friends = DBUser[id].friends
        friends = {friend.user_id: User(user_id=friend.user_id,
                                        first_name=friend.first_name,
                                        last_name=friend.last_name,
                                        photo=friend.photo)
                   for friend in friends}
        return render_template('thread.html',
                               news=news,
                               users=friends,
                               user=DBUser[user_id].first_name+' '+DBUser[user_id].last_name,
                               user_id=user_id)


@app.route('/news/<id>')
def news(id):
    with db_session:
        user_id = id
        news = select(post
                      for post in DBPost
                      if post.user in DBUser[user_id].friends
                        and post.link is not None)
        news = [Post(id=post.id,
                     text=zlib.decompress(post.text).decode(),
                     date=post.date.strftime('%Y-%m-%d %H:%M'),
                     photos=post.photos,
                     comments=post.comments,
                     reposts=post.reposts,
                     likes=post.likes,
                     link=post.link)
                for post in news
                if post.link['shareds'] >= 0]
        news.sort(key=lambda post: post.link['shareds'], reverse=True)

        friends = DBUser[user_id].friends
        friends = {friend.user_id: User(user_id=friend.user_id,
                                        first_name=friend.first_name,
                                        last_name=friend.last_name,
                                        photo=friend.photo)
                   for friend in friends}
        return render_template('news.html',
                               news=news[:100],
                               users=friends,
                               user=DBUser[user_id].first_name+' '+DBUser[user_id].last_name,
                               user_id=user_id)


if __name__ == "__main__":
    app.run()