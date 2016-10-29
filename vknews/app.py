import aiohttp_jinja2
import jinja2
from aiohttp import web

from vknews.vk.vkclient import VKClient

app = web.Application()

aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./templates'))


@aiohttp_jinja2.template('index.html')
async def index(request):
    vkclient = VKClient()
    members = await vkclient.get_group_members('csu_iit')
    return {'members': members}


@aiohttp_jinja2.template('news.html')
async def news(request):
    vkclient = VKClient()
    news = await vkclient.get_user_news(request.match_info['id'], sort_key='reposts')
    users = await vkclient.get_friends(request.match_info['id'])
    users = {user.user_id: user for user in users}
    return {'news': news[:100], 'users': users}


app.router.add_route('GET', '/', index)
app.router.add_route('GET', '/news/{id}', news)
app.router.add_static('/static/', path='static')

if __name__ == '__main__':
    web.run_app(app)