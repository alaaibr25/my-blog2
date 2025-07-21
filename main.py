from flask import Flask, render_template, request
from datetime import datetime as dt
import requests
import smtplib

PW = "find ur App passwords"
my_email = "mail"

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



@app.route('/contact', methods=['POST', 'GET'])
def contact_page():
    if request.method == 'POST':
        nm = request.form['nm']
        mail = request.form['mail']
        phone = request.form['phone']
          with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=PW)
            connection.sendmail(from_addr=my_email, to_addrs="alaa@gmail.com",
                                msg=f"Subject:Hallo\n\nName: {nm}\nEmail: {mail}\nPhone:{phone}")

                return render_template("contact.html", msg_sent=True)

    return render_template("contact.html", msg_sent=False)

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



















app.run()
