from flask import Flask, request, render_template, redirect
from os import urandom

from coredumped.blog import blog

GITHUB_URL: str = "https://github.com/Barkerprooks/udp-tunnel/releases/download"

UDPTUN_VERSION_LIST: list[str] = ["1.1.1", "1.1.0", "1.0.1", "1.0.0"]
UDPTUN_MIN_VERSION_LIST: list[str] = ["1.1.1", "1.1.0", "1.0.1"]

app: Flask = Flask(__name__)
app.register_blueprint(blog)


@app.get("/")
async def index():
    """The first page everyone sees"""
    return render_template("index.html", banner="Segfault City", page="home")


@app.get("/download/udptun")
async def udptun():
    """Easy interface to download udptun releases from github"""

    version: str = request.args.get("v", UDPTUN_VERSION_LIST[0])
    minified: bool = request.args.get("min", False, type=bool)
    versions: list[str] = UDPTUN_VERSION_LIST
    file: str = "udptun.py"

    if minified:
        versions = UDPTUN_MIN_VERSION_LIST
        file = "udptun.min.py"

    if version not in versions:
        return render_template("404.html", message="Version not found")

    return redirect(f"{GITHUB_URL}/v{version}/{file}")


@app.get("/api/coinflip")
def coin():
    """A 'true' random coin flip"""
    return {"result": urandom(1)[0] & 1}
