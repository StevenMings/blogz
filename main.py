from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '4fmz7jnexg'

class Blog(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(120))
	body = db.Column(db.String(255))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, title, body, owner):
		self.title = title
		self.body = body
		self.owner = owner


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	blogs = db.relationship('Blog', backref='owner')
	
	def __init__(self, username, password):
		self.username = username
		self.password = password


@app.before_request
def require_login():
	allowed_routes = ['login', 'register', 'signup', 'startup', 'index', 'blog']
	if request.endpoint not in allowed_routes and 'username' not in session:
		return redirect('/login')


@app.route('/login', methods=['POST','GET'])
def login():
	if request.method == 'POST':
		username = request.form['email']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user and user.password == password:
			session['username'] = username
			flash('You have been logged in with ' + username , 'success')
			print(session)
			return redirect('/newpost')
		else:
			flash('User password incorrect, or user does not exist', 'error')
	return render_template('login.html')

@app.route('/logout')
def logout():
	del session['username']
	flash('You have successfully logged out', 'success')
	return redirect('/blog')

@app.route('/signup', methods=['POST','GET'])
def signup():
	if request.method == 'POST':
		username = request.form['email']
		password = request.form['password']
		verify = request.form['verify'] 

		
		# Username
		if len(username) > 20 or len(username) < 3:
			username_error = flash("Username value out of range (Between 3 - 20 Characters Only)", 'error')
			return redirect('/signup')
		
		if " " in username:
			username_error = flash("Spaces are not allowed", 'error')
			return redirect('/signup')

		if len(username) == 0:
			username_error = flash("This cannot be blank!", 'error')
			return redirect('/signup')
		


		
		# Password
		if len(password) > 20 or len(password) < 3:
			password_error = flash("Password value out of range (Between 3 - 20 Characters Only)", 'error')
			return redirect('/signup')

		if " " in password:
			password_error = flash("Spaces are not allowed", 'error')
			return redirect('/signup')
			

		if len(password) == 0:
			password_error = flash("The Password cannot be blank!", 'error')
			return redirect('/signup')

		
	   # Password Verify    
		if password != verify:
			verify_error = flash("The passwords do not match!", 'error')
			return redirect('/signup')

		if len(verify) > 20 or len(verify) < 3:
			verify_error = flash("Password value out of range (Between 3 - 20 Characters Only)", 'error')
			return redirect('/signup')

		if " " in verify:
			verify_error = flash("Spaces are not allowed", 'error')
			return redirect('/signup')

		if len(verify) == 0:
			verify_error = flash("The Password cannot be blank!", 'error')
			return redirect('/signup')

		existing_user = User.query.filter_by(username=username).first()
		if not existing_user:
			new_user = User(username, password)
			db.session.add(new_user)
			db.session.commit()
			session['username'] = username
			flash('Welcome! Your signup was successful', 'success')
			return redirect('/newpost')
		else:
			flash('This username already exists, please try again', 'error' )
			return render_template('signup.html', titlebase="Try again!")

	return render_template('signup.html', titlebase="Try again!")
			
		

@app.route('/index')
def index():
	users = User.query.all()
	return render_template('index.html', users=users)


@app.route('/', methods=['POST', 'GET'])
def startup():
	return redirect('/index')
		

@app.route('/blog', methods=['GET'])
def blog():
    user = request.args.get('user')
    blog_id = request.args.get('id')
    
    if blog_id != None:
        entry = Blog.query.get(blog_id)
        user_obj = User.query.filter_by(id=entry.owner_id).first()
        return render_template('page.html', titlebase="All Blogs!", entry=entry, user=user_obj)

    if user == None:
        blogs = Blog.query.all()
        return render_template('blog.html', titlebase='All Blogs!', blogs=blogs)
    
    else:
        user_obj = User.query.filter_by(username=user).first()
        blogs = Blog.query.filter_by(owner_id=user_obj.id).all()
        return render_template('singleUser.html', titlebase = 'This is ' + user_obj.username + "'s blog", 
                                blogs=blogs, user=user_obj)


		


	
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
	owner = User.query.filter_by(username=session['username']).first()

	if request.method == 'POST':
		title_name = request.form['title']
		body_name = request.form['body']
		
		title_error = ""
		body_error = ""
		

		if len(title_name) == 0:
			title_error = flash("You Must Enter a Title!", 'error')
		if len(body_name) == 0:
			body_error = flash("You Must Enter A Body!", 'error')

		if title_error or body_error:
			return render_template('newpost.html', titlebase="New Entry", title_error = title_error, body_error = body_error, title=title_name, body_name=body_name)
		else:
			if len(title_name) or len(body_name) > 0:
				new_entry = Blog(title_name, body_name, owner)
				db.session.add(new_entry)
				db.session.commit()
				q = "/blog?id=" + str(new_entry.id)
				flash("You have Successfully made a post", 'success')
				return redirect(q)
	return render_template('newpost.html', titlebase="Its a Blog!")

if __name__ == '__main__':
	app.run()