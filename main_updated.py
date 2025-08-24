from flask import Flask, flash, jsonify, render_template, request
from datetime import datetime as dt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, URLField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash
#🔽---------------------------------------------------------------🔽#
year = dt.now().date()

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.secret_key = os.getenv("APIK")
app.config['CKEDITOR_SERVE_LOCAL'] = True
ckeditor = CKEditor(app)
#🔽---------------------------------------------------------------🔽#
log_manager = LoginManager()
log_manager.init_app(app)

@log_manager.user_loader
def load_user(user_id):
    return db.get_or_404(UserData, user_id)
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
        
class UserData(UserMixin, db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    pswrd: Mapped[str] = mapped_column(nullable=False)


with app.app_context():
    db.create_all()

#🔽---------------------------------------------------------------🔽#
#🔽---------------------------------------------------------------🔽#
class MyForm(FlaskForm):
    email = StringField('', validators=[DataRequired()])
    pw = PasswordField('', validators=[DataRequired()])
    submit = SubmitField("Submit")
    
class RegisterForm(FlaskForm):
    name = StringField('', [validators.Length(min=6, max=120)])
    email = EmailField('', [validators.Length(min=6, max=120)])
    pw = PasswordField('', [validators.Length(min=6, max=120)])
    submit = SubmitField("Register")
    
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
    return render_template("index.html",  all_posts=response_blog)

@app.route('/new_post', methods=['POST', 'GET'])
def create_post():
   pform = PostForm()
    if pform.validate_on_submit():
        nw_pst = BlogPost(
                  title=pform.title.data,
                  date=year,
                  body=pform.body.data,
                  author=pform.body.data,
                  img_url=pform.img_url.data,
                  subtitle=pform.subt.data

        )
        db.session.add(nw_pst)
        db.session.commit()
        return redirect(url_for('main_page'))

    return render_template('make_post.html', form=pform )

@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)
    edit_form = PostForm(
                title=post_to_edit.title,
                subt=post_to_edit.subtitle,
                author=post_to_edit.author,
                img_url=post_to_edit.img_url,
                body=post_to_edit.body)

    if edit_form.validate_on_submit():
        post_to_edit.title = edit_form.title.data
        post_to_edit.body = edit_form.body.data
        post_to_edit.author = edit_form.author.data
        post_to_edit.img_url = edit_form.img_url.data
        post_to_edit.subtitle = edit_form.subt.data

        db.session.commit()
        return redirect(url_for('post_page', post_id=post_to_edit.id))
    return render_template('make_post.html', form=edit_form, is_edit=True)

@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('main_page'))


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
    form = MyForm()
    if form.validate_on_submit():
        query_user = db.session.execute(db.select(UserData).where(UserData.email == form.email.data)).scalar()
        if query_user:
            if check_password_hash(query_user.pswrd, form.pw.data):
                login_user(query_user)
                return redirect(url_for('main_page'))
            else:
                flash("Invalid password", 'error')
                return redirect(url_for('login_page'))
        flash("This Email doesn't exist", "error")
        return redirect(url_for('login_page'))
       
    return render_template("login.html", form=form)

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        query_user = db.session.execute(db.select(UserData).where(UserData.email == form.email.data)).scalar()
        if query_user:
            flash("This Email is already Exist. Log in instead!")
            return redirect(url_for('login_page'))
        else:
            hashed_pw = generate_password_hash(form.pw.data,
                                            method='pbkdf2:sha256:600000',
                                            salt_length=8)
            new_user = UserData()
            new_user.name = form.name.data
            new_user.email = form.email.data
            new_user.pswrd = hashed_pw
    
            db.session.add(new_user)
            db.session.commit()
    
            login_user(new_user)
            return redirect(url_for('main_page'))
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    return redirect(url_for('main_page'))
#
app.run(debug=True)


