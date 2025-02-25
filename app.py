from flask import Flask, render_template_string, render_template
import json
import markdown
import random
import os
import datetime

skills_path = "static/skills.json"
experience_path = "static/experience.json"


def human_readable_post_date(date: int):
    post = str(date)
    if len(post) != 6:
        return "--/--/--"
    return post[2:4] + "/" + post[4:] + "/" + post[:2]


def load_blog_post_title(date: int):
    if os.path.isdir():
        with open(f"static/blog/{date}.md") as file:
            return markdown.markdown(file.readline() + file.readline())


def load_blog_post(date: int):
    filepath = f"static/blog/{date}.md"
    with open(filepath) as file:
        return (
            markdown.markdown(
                file.read(),
                extensions=["codehilite"],
                extension_configs={"codehilite": {"linenums": True}},
            ),
            datetime.datetime.fromtimestamp(os.stat(filepath).st_mtime),
        )


def all_blog_posts():
    posts = {}
    for date in map(lambda path: path.removesuffix(".md"), os.listdir("static/blog")):
        posts[date] = (load_blog_post_title(date), human_readable_post_date(date))
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
        markdown, modified = load_blog_post(date)
        return render_template(
            "post.j2",
            markdown=markdown,
            modified=modified,
            created=human_readable_post_date(date),
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
