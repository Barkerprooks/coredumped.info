from flask import Flask, render_template_string, render_template
import json
import markdown
import random
import os

skills_path = "static/skills.json"
experience_path = "static/experience.json"


def load_blog_post_title(date: int):
    with open(f"static/blog/{date}.md") as file:
        return markdown.markdown(file.readline())


def load_blog_post(date: int):
    with open(f"static/blog/{date}.md") as file:
        return markdown.markdown(file.read(), extensions=["codehilite"])


def all_blog_posts():
    posts = {}
    for date in map(lambda path: path.removesuffix(".md"), os.listdir("static/blog")):
        posts[date] = load_blog_post_title(date)
    return posts


def create_app():
    app = Flask(__name__)

    @app.get("/")
    def index():
        with open("static/banners.json") as file:
            banners = json.load(file)
            return render_template(
                "index.j2",
                banner=random.choice(banners),
                page="HOME",
            )

    @app.get("/blog")
    def blog():
        return render_template(
            "blog.j2",
            posts=all_blog_posts(),
            page="BLOG",
        )

    @app.get("/blog/<int:date>")
    def blog_post(date: int):
        return render_template(
            "post.j2",
            markdown=load_blog_post(date),
            page="BLOG",
        )

    @app.route("/resume")
    def resume():
        return render_template_string(
            "<center>resume machine broke :/ I have a job</center>"
        )
        # with open(skills_path) as skills, open(experience_path) as experience:
        #     return render_template(
        #         "resume.j2",
        #         skills=json.load(skills),
        #         experience=json.load(experience),
        #         page="RESUME",
        #     )

    return app
