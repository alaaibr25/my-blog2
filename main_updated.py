from flask import Flask, jsonify, render_template, request
from datetime import datetime as dt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, URLField
from flask_bootstrap import Bootstrap5
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from flask_ckeditor import CKEditor, CKEditorField
#🔽---------------------------------------------------------------🔽#
year = dt.now().year

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.secret_key = os.getenv("APIK")
app.config['CKEDITOR_SERVE_LOCAL'] = True
ckeditor = CKEditor(app)
#🔽---------------------------------------------------------------🔽#
#🟢# CREATE DATABASE, sqlalchemy

class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('BLG')
db.init_app(app)

# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    date: Mapped[str] = mapped_column(nullable=False)
    body: Mapped[str] = mapped_column(nullable=False)
    author: Mapped[str] = mapped_column(nullable=False)
    img_url: Mapped[str] = mapped_column(nullable=False)
    subtitle: Mapped[str] = mapped_column(nullable=False)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


with app.app_context():
    db.create_all()

#🔽---------------------------------------------------------------🔽#
#🔽---------------------------------------------------------------🔽#
class MyForm(FlaskForm):
    email = StringField('email', [validators.Length(min=6, max=120),
                                  validators.Email(message="@example.com", allow_empty_local=False)])
    pw = PasswordField('Password', [validators.length(min=8)])
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField('title', [validators.length(min=6, max=120)])
    subt = StringField('Subtitle', [validators.length(min=6, max=200)])
    author = StringField('Author', [validators.data_required()])
    img_url = URLField('Image URL')
    body = CKEditorField('Body')
    submit = SubmitField('Create')



#🔽---------------------------------------------------------------🔽#



@app.route('/')
def main_page():
    response_blog = db.session.execute(db.select(BlogPost).order_by(BlogPost.id)).scalars().all()
    return render_template("index.html", this_year=year, all_posts=response_blog)

@app.route('/new_post', methods=['POST', 'GET'])
def create_post():
    post_form = PostForm()
    if post_form.validate_on_submit():
        return "success"

    return render_template('make_post.html', form=post_form )

@app.route('/contact', methods=['POST', 'GET'])
def contact_page():
    if request.method == 'POST':
        nm = request.form['nm']
        mail = request.form['mail']
        phone = request.form['phone']

        return render_template("contact.html", is_msg=True)
    return render_template("contact.html", is_msg=False)

@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/<int:post_id>')
def post_page(post_id):
    #🟧 post_id before '?', So we can't get it by req.args.get('id')
    requested_page = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", req_post=requested_page)

@app.route('/log', methods=['POST', 'GET'])
def login_page():
    fform = MyForm()
    if fform.validate_on_submit():
        return "Success"
    return render_template("login.html", form=fform)
#
app.run(debug=True)


