import re, time, json, logging, hashlib, base64, asyncio

from www.coroweb import get, post

from www.models import User, Comment, Blog, next_id

from apis import APIValueError

from aiohttp import web

COOKIE_NAME='awesession'

@get('/')
def index(request):
    num=yield from Blog.findNumber('count(id)')
    if num==0:
        blogs=[]
    else:
        blogs=yield from Blog.findAll()
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/api/user')
def aip_get_user(request):
    users=yield from User.findAll(orderBy='created_at desc');
    return dict(userList=users);
@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }

@get('/manange/blogs/create')
def register():
    return {
        '__template__': 'manage_blog_edit.html'
    }

@get('/blog/{id}')
def get_blog(id):
    blog=yield from Blog.find(id)
    comments=yield from Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    return {
        '__template__':'blog.html',
        'blog':blog,
        'comments':comments
    }
@post('/api/blogs/{id}/comments')
def api_create_comment(id, request, *, content):
    blog=yield from Blog.findAll(id)
    print(blog)
    print(content)
    comment=Comment(blog_id=id,user_id='0015302547958723f7da9d783434468901251428ea85d4c000',user_name='xuehh',user_image='http://www.gravatar.com/avatar/067bf298c6244dd085d9b4b7d9f3e0ba?d=mm&s=120',content=content.strip())
    yield from comment.save()
    return comment
@get('/register')
def register():
    return {
        '__template__':'register.html'
    }
@get('/singin')
def singin():
    return {
        '__template__': 'singin.html'
    }
@post('/api/users')
def api_register_user(*,email,name,passwd):
    if not name or not name.strip():
        raise APIValueError('email','Invalid email.')
    if not passwd:
        raise APIValueError('passwd','Invalid password')
    users=yield from User.findAll('email=?',[email])
    if len(users)>0:
        raise APIValueError('register:failed', 'email', 'Email is already in use.')
    uid=next_id()
    user=User(id=uid,name=name,email=email,passwd=passwd,image='http://www.gravatar.com/avatar/%s?d=mm&s=120',created_at='1532590440.177')
    yield from user.save()

    r=web.Response()
    r.set_cookie(COOKIE_NAME,user,max_age=0,httponly=True)
    r.content_type=''
    r.body=json.dump(user,ensure_ascii=False).encode('utf-8')
    return r

@post('/api/authenticate')
def authenticate(*,email,passwd):
    if not email:
        raise APIValueError('email','Invalid email')
    if not passwd:
        raise APIValueError('passwd','Invalid password')
    users=yield from User.findAll('email=?',[email])
    if len(users)==0:
        raise APIValueError('email','Email not exits')
    user=users[0]
    if user.passwd!= passwd:
        raise APIValueError('passwd', 'Invalid password.')

    r=web.Response()

    return r

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

def get_page_index(page_str):
    p=1
    try:
        p=int(page_str)
    except ValueError as e:
        pass
    if p<1:
        p=1


