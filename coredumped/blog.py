from flask import Blueprint, Response, render_template
from markdown import markdown
import os


BLOG_DAY_PATH = "static/blog/day"
BLOG_HTB_PATH = "static/blog/ctf/htb"
BLOG_NOTES_PATH = "static/blog/ctf/notes"
BLOG_TOOLS_PATH = "static/blog/ctf/tools"


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


async def collect_day_posts() -> list[str]:
    posts = {}
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
    posts = {}
    for parent, _, files in os.walk('static/blog/ctf'):
        for file in files:
            path = os.path.join(parent, file)
            name = file.removesuffix('.md')
            posts[name] = (await load_post_title(path), os.path.basename(parent))
    return posts


async def load_ctf_htb_post(name: str) -> str:
    if name not in await collect_ctf_posts():
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_HTB_PATH, f"{name}.md"))


async def load_ctf_notes_post(name: str) -> str:
    if name not in await collect_ctf_posts():
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_NOTES_PATH, f"{name}.md"))


async def load_ctf_tools_post(name: str) -> str:
    if name not in await collect_ctf_posts():
        return '' # return empty string if it's an invalid name
    return await generate_markdown(os.path.join(BLOG_TOOLS_PATH, f"{name}.md"))


blog = Blueprint("blog", __name__, url_prefix="/blog")


@blog.get("/")
async def index() -> Response:
    return render_template("blog.html", posts=await collect_day_posts(), page="b l o g")


@blog.get("/ctfs")
async def ctfs_index() -> Response: 
    return render_template("ctfs.html", posts=await collect_ctf_posts(), page="c t f s")


# date based posts
@blog.get("/<int:date>")
async def post(date: int) -> Response:
    human_readable_date = await human_readable_post_date(date)
    title_date = ' '.join(list(human_readable_date))
    return render_template("post.html", markdown=await load_day_post(date), date=human_readable_date, page=title_date)


# hack the box writeups
@blog.get("/ctfs/htb/<string:name>")
async def htb(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_htb_post(name), page="h t b")


# general infosec notes
@blog.get("/ctfs/notes/<string:name>")
async def notes(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_notes_post(name), page="n o t e s")


# infosec tools (maybe general networking tools and stuff too at a later date)
@blog.get("/ctfs/tools/<string:name>")
async def tools(name: str) -> Response:
    return render_template("post.html", markdown=await load_ctf_tools_post(name), page='t o o l s')