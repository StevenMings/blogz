from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app) 

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        

@app.route('/blog', methods=['POST', 'GET'])
def blog_page():

    if ['POST'] == True:
                
        title_name = request.form['title']
        body_name = request.form['body']
        new_entry = Blog(title_name, body_name)
        db.session.add(new_entry)
        db.session.commit()


    blogs = Blog.query.all()
    

    return render_template('blog.html', title="Its a Blog!", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    return render_template('newpost.html', titlebase = 'New Blog Post!')


@app.route('/validate_newpost', methods=['POST', 'GET'])
def validate_newpost():
    title = request.form['title']
    body = request.form['body']

    title_error=''
    body_error=''

#title
    if len(title) == 0:
        title_error = "You Must Enter a Title!"

# body
    if len(body) == 0:
        body_error = "You Must Enter A Body!"

    if not title_error and not body_error:
        return redirect('/blog')
    else:
        return render_template('newpost.html', title_error=title_error, body_error=body_error)


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')


if __name__ == '__main__':
    app.run()
