# import libraries and methods
from flask import Flask, flash, render_template, redirect, request, make_response, jsonify
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Items, Users
import random, string, httplib2, json, requests

# set up database and session interface
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# set up CLIENT_ID
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)

@app.route('/')
def homepage():
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Items).order_by(Items.cat_name)
    return render_template('homepage.html', categories = categories, items = items)

@app.route('/catalog/<category>/items')
def category_page(category):
    categories = session.query(Category).order_by(Category.name)
    items = session.query(Items).filter_by(cat_name = category).all()
    return render_template('category_page.html', categories = categories, items = items, cat_name = category)

@app.route('/catalog/<category>/<item>')
def item_page(category, item):
    item = session.query(Items).filter_by(cat_name = category).filter_by(name = item).one()
    return render_template('item_page.html', item = item)

@app.route('/catalog/<cat_name>/new', methods = ['GET', 'POST'])
def add_item(cat_name):
    select_tab = session.query(Category).filter_by(name = cat_name).one()
    # protect this page in case somebody not logged in tries to access via the URL
    if 'username' not in login_session:
        return redirect('/')
    # if the user has logged in, we will tell the difference between a get and a post request
    categories = session.query(Category).order_by(Category.name)
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        image = request.form['image']
        # check that all the fields have been filled in
        if not name or not description or not image:
            flash('Please fill in all the fields!')
            return render_template('add_item.html', select_tab = select_tab.name, categories = categories)
        else:
            try:
                # if they have filled everything in, we will add an entry to the database and redirect them
                newItem = Items(name = name, cat_name = category, description = description, image = image, user_id = login_session['user_id'])
                session.add(newItem)
                session.commit()
                return redirect('/')
            except exc.IntegrityError:
                session.rollback()
                flash("Invalid Entry")
                return render_template('add_item.html', select_tab = select_tab.name, categories= categories)
    else:
        return render_template('add_item.html', select_tab = select_tab.name, categories = categories)

@app.route('/catalog/<item>/edit', methods = ['GET', 'POST'])
def edit_item(item):
    item = session.query(Items).filter_by(name = item).one()
    # protect the page so that users who didn't create the entry cannot edit via the url
    if login_session['user_id'] != item.user_id:
        return redirect('/')
    # if the user is allowed to edit the entry
    else:
        categories = session.query(Category).order_by(Category.name)
        if request.method == 'POST':
            name = request.form['name']
            category = request.form['category']
            description = request.form['description']
            image = request.form['image']
            # check to make sure all the fields are filled in
            if not name or not description or not image:
                flash('Please fill in all the fields!')
                return render_template('edit_item.html', item = item, categories = categories)
            else:
                try:
                    # update the database and redirect
                    item.name = name
                    item.cat_name = category
                    item.description = description
                    item.image = image
                    session.add(item)
                    session.commit()
                    return render_template('item_page.html', item = item, category = item.cat_name)
                except exc.IntegrityError:
                    session.rollback()
                    flash('Invalid Entry')
                    return render_template('edit_item.html', item = item, categories = categories)
        else:
            # if it is a get request we will simply render the form
            return render_template('edit_item.html', item = item, categories = categories)

@app.route('/catalog/<item>/delete', methods = ['GET', 'POST'])
def delete_item(item):
    item = session.query(Items).filter_by(name = item).one()
    # protect the page to prevent users who didn't create the entry from deleting it
    if login_session['user_id'] != item.user_id:
        return redirect('/')
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect('/')
    else:
        return render_template('delete_item.html', item = item)

# the implementation for Google OAuth is based on Lorenzo's course
@app.route('/catalog/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        # we will generate our unique session token and pass it into our template
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html', STATE = state)
    else:
        # guard against CSRF attacks
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] ='application/json'
            return response
        
        # collect one time use code and exchange it
        code = request.data
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorisation code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # is there a valid access token inside the credentials object we have exchanged for?
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')),500)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # compare the credentials object user_id to the user_id returned by the Google server
        google_id = credentials.id_token['sub']
        if result['user_id'] != google_id:
            response = make_response(json.dumps('Token user ID does not match given user ID'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # compare client IDs of credentials object to that retured by Google server
        if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("Token's client ID does not match application"), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # check if user is already logged in
        stored_credentials = login_session.get('credentials')
        stored_google_id = login_session.get('google_id')
        if stored_credentials is not None and google_id == stored_google_id:
            response = make_response(json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        
        # let's store the the user information
        login_session['credentials'] = credentials.access_token
        login_session['google_id'] = google_id
        
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token' : credentials.access_token, 'alt' : 'json'}
        answer = requests.get(userinfo_url, params=params)
        data = answer.json()
        
        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        
        # check for user in database and create new entry if not
        if user_id(login_session['email']) == None:
            login_session['user_id'] = create_user(login_session)
        else:
            login_session['user_id'] = user_id(login_session['email'])
            
        return login_session['username']

# the implementation for logging out is based on Lorenzo's course
@app.route('/catalog/logout')
def logout():
    # do we have the access token?
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        return response
    else:
        # let's do a GET request for Google to revoke the current token
        url ='https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        if result['status'] == '200':
            del login_session['credentials']
            del login_session['google_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            response = make_response(json.dumps('Successfully Disconnected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        else:
            response = make_response(json.dumps("Unable to revoke token"), 400)
            response.headers['Content-Type'] = 'application/json'
            return response

# we are adding some helper functions in relation to user_id
def create_user(login_session):
    new_user = Users(name = login_session['username'], picture = login_session['picture'], email = login_session['email'])
    session.add(new_user)
    session.commit()
    user = session.query(Users).filter_by(email = login_session['email']).one()
    return user.id

def user_id(email):
    try:
        user = session.query(Users).filter_by(email = email).one()
        return user.id
    except:
        return None

# let's implement a JSON endpoint
@app.route('/catalog/JSON')
def itemsJSON():
    items = session.query(Items).all()
    return jsonify(items = [item.serialize for item in items])
    
if __name__ == '__main__':
    app.debug = True
    app.run()
