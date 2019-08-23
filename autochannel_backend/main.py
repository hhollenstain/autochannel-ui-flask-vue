import os
import logging
import coloredlogs
import requests
from flask import Flask, session, request, url_for, render_template, redirect, \
 jsonify, flash, abort, Response
from requests_oauthlib import OAuth2Session
from itsdangerous import JSONWebSignatureSerializer
from autochannel_backend import login_required
from autochannel_backend.lib import utils

LOG = logging.getLogger(__name__)

"""
OAUTH2 client 
"""
OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

"""
Discord specific
"""
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
AVATAR_BASE_URL = "https://cdn.discordapp.com/avatars/"
DEFAULT_AVATAR = "https://discordapp.com/assets/"\
                "1cbd08c76f8af6dddce02c5138971129.png"
TOKEN_URL = API_BASE_URL + '/oauth2/token'

"""
Flask configs
"""
template_dir = os.path.abspath('autochannel_frontend/dist')
# app = Flask(__name__,
#             static_folder = "./dist/static",
#             template_folder = "./dist")
app = Flask(__name__,
            static_folder = f'{template_dir}/static',
            template_folder = template_dir)

app.debug = False
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'

@app.route('/avatar-test')
def avatar_test():
    token = session['oauth2_token']
    user = get_user(token)
    return avatar(user)

def avatar(user):
    if user.get('avatar'):
        return AVATAR_BASE_URL + user['id'] + '/' + user['avatar'] + '.jpg'
    else:
        return DEFAULT_AVATAR

def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


@app.route('/')
def index():
    if 'oauth2_token' in session:
        return redirect(url_for('.me'))
    
    return redirect(url_for('login')) 

@app.route('/api/login')
def login():
    # scope = request.args.get(
    #     'scope',
    #     'identify email connections guilds guilds.join')
    scope = ['identify', 'email', 'guilds', 'connections', 'guilds.join']
    discord = make_session(scope=scope)
    authorization_url, state = discord.authorization_url(
        AUTHORIZATION_BASE_URL,
        # access_type="offline"
    )
    session['oauth2_state'] = state
    return redirect(authorization_url) 

@app.route('/ohno')
def ohno():
    return jsonify(error="something went wrong")

@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    discord_token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    if not discord_token:
        return redirect(url_for('ohno'))

    session['oauth2_token'] = discord_token

# Fetch the user
    user = get_user(discord_token)
    # if not user:
    #     return redirect(url_for('logout'))
    # Generate api_key from user_id
    serializer = JSONWebSignatureSerializer(app.config['SECRET_KEY'])
    api_key = str(serializer.dumps({'user_id': user['id']}))
    # Store api_token in client session
    api_token = {
        'api_key': api_key,
        'user_id': user['id']
    }
    session.permanent = True
    session['api_token'] = api_token
    return redirect(url_for('.me'))

@app.route('/me')
@login_required
def me():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    connections = discord.get(API_BASE_URL + '/users/@me/connections').json()
    return jsonify(user=user, guilds=guilds, connections=connections)

@app.route('/whoami')
@login_required
def whoami():
    token = session['oauth2_token']
    return jsonify(user=get_user(token))

@app.route('/api/user')
@login_required
def user():
    token = session['oauth2_token']
    user_info = get_user(token)
    return jsonify(user=get_user(token))

def user_data_builder(user):
    
    return user_data

def get_user_guilds(token):
    # If it's an api_token, go fetch the discord_token
    if token.get('api_key'):
        user_id = token['user_id']
    else:
        user_id = get_user(token)['id']

    discord = make_session(token=token)

    req = discord.get(API_BASE_URL + '/users/@me/guilds')
    if req.status_code != 200:
        abort(req.status_code)

    guilds = req.json()
    return guilds

@app.route('/managed-guilds')
@login_required
def managed_guilds():
    token = session['oauth2_token']
    user = get_user(token)
    guilds = get_user_guilds(token)
    user_servers = sorted(
        get_user_managed_servers(user, guilds),
        key=lambda s: s['name'].lower()
    )
    return jsonify(managedGuilds=user_servers)

def get_user_managed_servers(user, guilds):
    return list(
        filter(
            lambda g: (g['owner'] is True) or
            bool((int(g['permissions']) >> 5) & 1),
            guilds)
    )

def get_user(token):
    if 'user' in session:
        return session['user']

    discord = make_session(token=token)
    try:
        req = discord.get(API_BASE_URL + '/users/@me')
    except Exception:
        return None

    if req.status_code != 200:
        abort(req.status_code)

    user = req.json()
    # Saving that to the session for easy template access
    session['user'] = user
    return user

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

def main():
    args = utils.parse_arguments()
    logging.basicConfig(level=logging.INFO)
    coloredlogs.install(level=0,
                        fmt="[%(asctime)s][%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                        isatty=True)
    if args.debug:
        l_level = logging.DEBUG
        app.debug = True
    else:
        l_level = logging.INFO

    logging.getLogger(__package__).setLevel(l_level)
    logging.getLogger('websockets.protocol').setLevel(l_level)
    logging.getLogger('urllib3').setLevel(l_level)

    app.run()

if __name__ == '__main__':
    main()
