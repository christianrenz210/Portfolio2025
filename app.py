from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', name='Christian Renz Ledesma')

@app.route('/termsofuse')
def show_terms():
    return render_template('termsofuse.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

if __name__ == '__main__':
    app.run(debug=True)
