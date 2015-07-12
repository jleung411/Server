import bottle
import beaker.middleware
from bottle import route, redirect, post, run, request, hook
from instagram import client, subscriptions

bottle.debug(True)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
}

app = beaker.middleware.SessionMiddleware(bottle.app(), session_opts)

CONFIG = {
    'client_id': '15abe927b3f2475e80fe9aa94b796918',
    'client_secret': '42caae5b4f9747a79c34902dc1f27a72',
    'redirect_uri': 'http://52.27.220.75:5000/oauth_callback'
}

unauthenticated_api = client.InstagramAPI(**CONFIG)

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

def process_tag_update(update):
    print(update)

reactor = subscriptions.SubscriptionsReactor()
reactor.register_callback(subscriptions.SubscriptionType.TAG, process_tag_update)

@route('/')
def home():
    try:
        url = unauthenticated_api.get_authorize_url(scope=["likes","comments"])
        return '<a href="%s">Connect with Instagram</a>' % url
    except Exception as e:
        print(e)

@route('/oauth_callback')
def on_callback(): 
    code = request.GET.get("code")
    if not code:
        return 'Missing code'
    try:
        access_token, user_info = unauthenticated_api.exchange_code_for_access_token(code)
        if not access_token:
            return 'Could not get access token'
        api = client.InstagramAPI(access_token=access_token)
        request.session['access_token'] = access_token
        print ("access token="+access_token)
    except Exception as e:
        print(e)
    return get_nav()

@route('/api/followed_by/<id>')
def api_followed_by(id):
    access_token = request.query['access_token']
    result = {"users" : [], "error": ""}
    if not access_token:
        result["error"] = "Missing Access Token"
        return result
    try:
        api = client.InstagramAPI(access_token=access_token)
        user_follows, next = api.user_followed_by(id)
        users = []
        for user in user_follows:
            result["users"].append({"username": user.username, "id": user.id})
    except Exception as e:
        result["error"] = e
    return result

@route('/api/like_user_photos', method='POST')
def api_like_user_photos():
    access_token = request.query['access_token']
    result = {"images" : [], "error": ""}
    if not access_token:
        result["error"] = "Missing Access Token"
        return result
    try:
        api = client.InstagramAPI(access_token=access_token)

        postdata = request.body.read()
        print postdata

        users = request.json 

        print users

        result["images"].append("1234")
        result["images"].append("5678")

    except Exception as e:
        result["error"] = e
    return result


bottle.run(app=app, host='0.0.0.0', port=5000, reloader=True)
