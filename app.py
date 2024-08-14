from flask import Flask, render_template
import json


def create_app():

    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.j2', page='HOME')


    @app.route('/ctfs')
    def ctfs():
        return render_template('ctfs.j2', page='CTFs')


    @app.route('/blog')
    def blog():
        return render_template('blog.j2', page='BLOG')


    @app.route('/resume')
    def resume():
        return render_template(
            'resume.j2',
            page='RESUME',
            skills=json.load(open('static/skills.json')),
            experience=json.load(open('static/experience.json'))
        )

    return app
