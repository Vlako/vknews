from flask import Flask, render_template
from webapp import mapper
from db.models import User as DBUser, Group as DBGroup, Post as DBPost, db_session, select, desc, avg, count

app = Flask(__name__)


@app.route("/")
def index():
    with db_session:
        members = select(member
                         for member in DBUser
                         if DBGroup['csu_iit'] in member.groups).order_by(DBUser.user_id)
        return render_template('index.html', members=[mapper.get_user_from_dbuser(member)
                                                      for member in members])


@app.route('/thread/<user_id>/<sort>/<page>')
def thread(user_id, sort, page):
    with db_session:
        if sort == 'comments':
            sort_field = desc(lambda post : desc(post.comments / (avg(p.comments for p in post.user.posts) + 1)))
        elif sort == 'reposts':
            sort_field = desc(lambda post : desc(post.reposts / (avg(p.reposts for p in post.user.posts) + 1)))
        else:
            sort_field = desc(lambda post : desc(post.likes / (avg(p.likes for p in post.user.posts) + 1)))

        page = int(page)
        news = select(post
                      for post in DBPost
                      if post.user in DBUser[user_id].friends).order_by(sort_field)[page*20 : (page+1)*20]
        news = [mapper.get_post_from_dbpost(post)
                for post in news]

        users = {}
        for i in news:
            users[i.from_id] = mapper.get_user_from_dbuser(DBUser[i.from_id])
            for j in i.original_post:
                users[j.from_id] = mapper.get_user_from_dbuser(DBUser[j.from_id])

        news_count = select(count(post) for post in DBPost if post.user in DBUser[user_id].friends)
        has_next = True
        if len(news) < 20 or page * 20 + len(news) == news_count:
            has_next = False

        return render_template('thread.html',
                               news=news,
                               users=users,
                               user=DBUser[user_id].first_name+' '+DBUser[user_id].last_name,
                               user_id=user_id,
                               page=page,
                               has_next=has_next)


@app.route('/news/<user_id>/<page>')
def news(user_id, page):
    with db_session:

        page = int(page)

        news = select(post
                      for post in DBPost
                      if post.user in DBUser[user_id].friends
                        and post.link is not None)

        news = [mapper.get_post_from_dbpost(post)
                for post in news
                if post.link['shareds'] >= 0]
        news.sort(key=lambda post: post.link['shareds'], reverse=True)

        news_count = len(news)
        news = news[page*20 : (page+1)*20]

        users = {}
        for i in news:
            users[i.from_id] = mapper.get_user_from_dbuser(DBUser[i.from_id])
            for j in i.original_post:
                users[j.from_id] = mapper.get_user_from_dbuser(DBUser[j.from_id])

        has_next = True
        if len(news) < 20 or page * 20 + len(news) == news_count:
            has_next = False

        return render_template('news.html',
                               news=news[:100],
                               users=users,
                               user=DBUser[user_id].first_name+' '+DBUser[user_id].last_name,
                               user_id=user_id,
                               page=page,
                               has_next=has_next)


if __name__ == "__main__":
    app.run()