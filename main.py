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

@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')
        

@app.route('/blog', methods=['POST', 'GET'])
def blog_page():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        entry = Blog.query.get(blog_id)
        return render_template('page.html',titlebase = 'Build a Blog!', entry=entry)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', titlebase = 'Build a Blog!', blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title_name = request.form['title']
        body_name = request.form['body']
        
        title_error=''
        body_error=''

        if len(title_name) == 0:
            title_error = "You Must Enter a Title!"
        if len(body_name) == 0:
            body_error = "You Must Enter A Body!"

        if title_error or body_error:
            return render_template('newpost.html', titlebase="New Entry", title_error = title_error, body_error = body_error, title=title_name, body_name=body_name)
        else:
            if len(title_name) or len(body_name) > 0:
                new_entry = Blog(title_name, body_name)
                db.session.add(new_entry)
                db.session.commit()
                q = "/blog?id=" + str(new_entry.id)
                return redirect(q)
    return render_template('newpost.html', titlebase="Its a Blog!")

if __name__ == '__main__':
    app.run()