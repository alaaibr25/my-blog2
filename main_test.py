from flask import Flask, render_template
from datetime import datetime as dt
import requests


app = Flask(__name__)
year = dt.now().year

blog_url = "https://api.npoint.io/c790b4d5cab58020d391"
response_blog = requests.get(blog_url).json()




@app.route('/')
def main_page():
    return render_template("index.html", this_year=year, all_posts=response_blog)



@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route('/about')
def about_page():
    return render_template("about.html")



















app.run()
