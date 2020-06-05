import os
import spotipy
from festival import app, db, bcrypt
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required
from festival.models import User
from festival.forms import RegistrationForm, LoginForm
from secrets import token_hex


REDIRECT_URI = "http://localhost:5000/"
SCOPE = 'playlist-modify-private,playlist-modify-public,user-top-read'
CACHE = '.spotipyoauthcache'
CLIENT_ID=os.environ['SPOTIPY_CLIENT_ID']
CLIENT_SECRET=os.environ['SPOTIPY_CLIENT_SECRET']


@app.route('/')
@app.route('/home')
def home():
    code=request.args.get('code')
    if code:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET ,redirect_uri=REDIRECT_URI,scope=SCOPE, show_dialog=True, cache_path=CACHE+current_user.username)
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        refresh_token = token_info['refresh_token']
        current_user.access_token = access_token
        current_user.refresh_token = refresh_token
        current_user.token_info = token_info
        db.session.commit()
        print(current_user.token_info)
    if current_user.is_authenticated:
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET ,redirect_uri=REDIRECT_URI,scope=SCOPE, show_dialog=True, cache_path=CACHE+current_user.username)
        if current_user.access_token is not None:
            if sp_oauth.is_token_expired(current_user.token_info):      
                token_info = sp_oauth.refresh_access_token(current_user.refresh_token)
                access_token = token_info['access_token']
                refresh_token = token_info['refresh_token']
                current_user.access_token = access_token
                current_user.refresh_token = refresh_token
                db.session.commit()
        else:
            return redirect(url_for('spotify_login'))
    return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Feel free to login now','success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register',form=form)



@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated and current_user.access_token is not None:
        return redirect(url_for('home'))
    elif current_user.is_authenticated:
        return redirect(url_for('spotify_login'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if current_user.access_token is None:
                return redirect(url_for('spotify_login'))
            elif next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check Username and Password', 'danger')
    return render_template('login.html',title='Login',form=form)


@app.route('/spotify_login')
def spotify_login():
    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET ,redirect_uri=REDIRECT_URI,scope=SCOPE, show_dialog=True, cache_path=CACHE+current_user.username)
    auth_url = sp_oauth.get_authorize_url()
    return render_template('spotify_login.html',auth_url=auth_url)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/favorite_artists')
@login_required
def favorite_artists():
    if current_user.access_token is None:
        return redirect(url_for('spotify_login'))
    sp = spotipy.Spotify(current_user.access_token)
    favorite_artists=sp.current_user_top_artists()
    artists=[]
    for item in favorite_artists["items"]:
        artists.append(item['name'])
    return render_template('favorite_artists.html', artists=artists, sp=sp)

    
@app.route('/favorite_tracks')
@login_required
def favorite_tracks():
    if current_user.access_token is None:
        return redirect(url_for('spotify_login'))
    sp = spotipy.Spotify(current_user.access_token)
    favorite_tracks = sp.current_user_top_tracks()
    tracks=[]
    for item in favorite_tracks["items"]:
        tracks.append(item['name'])
    return render_template('favorite_tracks.html', tracks=tracks, sp=sp)
