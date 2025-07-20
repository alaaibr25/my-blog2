from flask import Flask, render_template, request
from datetime import datetime as dt
import requests


app = Flask(__name__)
year = dt.now().year

blog_url = "https://api.npoint.io/{id}"
response_blog = requests.get(blog_url).json()
posts_list = []
for post in response_blog:
    posts_list.append(post)



@app.route('/')
def main_page():
    return render_template("index.html", this_year=year, all_posts=response_blog)



@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/<int:indx>')
def post_page(indx):
    requested_page = None
    for p in posts_list:
        if p['id'] == indx:
            requested_page = p
    return render_template("post.html", req_post=requested_page)


@app.route("/form-entry", methods=['POST'])
def receive_data():

    nm = request.form['nm']
    mail = request.form['mail']
    phone = request.form['phone']
    return f"<h1> {nm}-{mail}-{phone} </h1>"
















app.run()
