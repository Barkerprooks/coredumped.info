from flask import Blueprint, Response, render_template
from markdown import markdown
import os


BLOG_DAY_PATH = "static/blog/day"
BLOG_HTB_PATH = "static/blog/ctf/htb"
BLOG_NOTES_PATH = "static/blog/ctf/notes"


async def generate_markdown(path: str) -> str:
    """
    creates a markdown file with syntax highlighting supported
    """
    
    if not os.path.isfile(path):
        return "<center>error generating markdown :(</centrer>"
    
    with open(path) as file:
        return markdown(
            text=file.read(),
            extensions=["codehilite"],
            extension_configs={"codehilite": { 
                "linenums": True, 
                "guess_lang": False 
            }}
        )


async def human_readable_post_date(date: int) -> str:
    name = f"{date:06}"
    if len(name) != 6:
        return "--/--/--"
    return name[2:4] + "/" + name[4:] + "/" + name[:2]


async def collect_day_posts() -> list[str]:
    return [path.replace('.md', '') for path in os.listdir(BLOG_DAY_PATH)]


async def load_day_post(date: int) -> str:
    name = f"{date:06}"
    if name not in await collect_day_posts():
        return ''
    return await generate_markdown(os.path.join(BLOG_DAY_PATH, f"{name}.md"))


async def collect_ctf_posts() -> list[str]:
    posts = {}
    for parent, _, files in os.walk('static/blog/ctf'):
        for file in [file.replace('.md', '') for file in files]:
            posts[file] = ('lol', os.path.basename(parent))
    return posts


async def load_ctf_htb_post(name: str) -> str:
    if name not in await collect_ctf_posts():
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_HTB_PATH, f"{name}.md"))


async def load_ctf_notes_post(name: str) -> str:
    if name not in await collect_ctf_posts():
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_NOTES_PATH, f"{name}.md"))


blog = Blueprint("blog", __name__, url_prefix="/blog")


@blog.get("/")
async def index() -> Response:
    return render_template("blog.html", posts=await collect_day_posts())


@blog.get("/ctfs")
async def ctfs_index() -> Response: 
    return render_template("ctfs.html", posts=await collect_ctf_posts())


# date based posts
@blog.get("/<int:date>")
async def post(date: int) -> Response:
    return render_template("post.html", markdown=await load_day_post(date))


# hack the box writeups
@blog.get("/ctfs/htb/<string:name>")
async def htb(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_htb_post(name))


# general infosec notes
@blog.get("/ctfs/notes/<string:name>")
async def notes(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_notes_post(name))