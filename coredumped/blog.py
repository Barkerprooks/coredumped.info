from flask import Blueprint, Response, render_template
from markdown import markdown
import os


BLOG_DAY_PATH = "coredumped/static/blog/day"
BLOG_HTB_PATH = "coredumped/static/blog/ctf/htb"
BLOG_NOTES_PATH = "coredumped/static/blog/ctf/notes"
BLOG_TOOLS_PATH = "coredumped/static/blog/ctf/tools"


async def generate_markdown(path: str) -> str:
    if not os.path.isfile(path):
        return "<center>error generating markdown :(</centrer>"
    
    with open(path) as file:
        return markdown(
            text=file.read(),
            extensions=["codehilite"],
            extension_configs={
                "codehilite": { 
                    "guess_lang": False,
                    "linenums": False
                }
            }
        )


async def human_readable_post_date(date: int) -> str:
    name = f"{date:06}"
    if len(name) != 6:
        return "--/--/--"
    return name[2:4] + "/" + name[4:] + "/" + name[:2]


async def load_post_title(path: str) -> str:
    with open(path) as file:
        return markdown(text=file.readline())


async def load_post_title_and_subtitle(path: str) -> str:
    with open(path) as file:
        return markdown(text=file.readline() + file.readline())


async def collect_day_posts() -> list[str]:
    posts = {}
    if os.path.isdir(BLOG_DAY_PATH):
        for file in os.listdir(BLOG_DAY_PATH):
            name = file.removesuffix('.md')
            date = await human_readable_post_date(name)
            path = os.path.join(BLOG_DAY_PATH, file)
            posts[name] = (await load_post_title(path), date)
    return posts


async def load_day_post(date: int) -> str:
    name = f"{date:06}"
    if name not in await collect_day_posts():
        return ''
    return await generate_markdown(os.path.join(BLOG_DAY_PATH, f"{name}.md"))


async def collect_ctf_posts() -> list[str]:
    groups = {}
    for parent, _, files in os.walk('coredumped/static/blog/ctf'):
        group = os.path.basename(parent)
        
        if group == 'ctf':
            continue # TODO: this can probably be handled better
        
        groups[group] = {}
        for file in files:
            name = file.removesuffix('.md')
            group = os.path.basename(parent)
            groups[group][name] = await load_post_title_and_subtitle(os.path.join(parent, file))
    return groups


async def load_ctf_htb_post(name: str) -> str:
    groups = await collect_ctf_posts()
    if name not in groups["htb"]:
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_HTB_PATH, f"{name}.md"))


blog = Blueprint("blog", __name__, url_prefix="/blog")


@blog.get("/")
async def index() -> Response:
    return render_template("blog.html", posts=await collect_day_posts(), page="blog")


@blog.get("/ctfs")
async def ctfs_index() -> Response:
    return render_template("ctfs.html", groups=await collect_ctf_posts(), page="ctfs")


# date based posts
@blog.get("/date/<int:date>")
async def get_blog_post(date: int) -> Response:
    human_readable_date = await human_readable_post_date(date)
    return render_template("post.html", markdown=await load_day_post(date), date=human_readable_date, page=human_readable_date)


# hack the box writeups
@blog.get("/htb/<string:name>")
async def get_htb_post(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_htb_post(name), page="htb")
