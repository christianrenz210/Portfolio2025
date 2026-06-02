from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', name='Christian Renz Ledesma')

@app.route('/about')
def about():
    return render_template('about.html', name='Christian Renz Ledesma')

@app.route('/skills')
def skills():
    return render_template('skills.html', name='Christian Renz Ledesma')

@app.route('/projects')
def projects():
    return render_template('projects.html', name='Christian Renz Ledesma')

@app.route('/contact')
def contact():
    return render_template('contact.html', name='Christian Renz Ledesma')

@app.route('/termsofuse')
def show_terms():
    return render_template('termsofuse.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

