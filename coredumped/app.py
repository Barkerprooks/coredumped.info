from flask import Flask, render_template, redirect


from coredumped import get_banner
from coredumped.blog import blog


app = Flask(__name__)
app.register_blueprint(blog)


@app.get("/")
async def index():
    return render_template("index.html", banner=await get_banner(), page="home")


@app.get("/tools/udptun.py")
async def udptun_content():
    return redirect("https://raw.githubusercontent.com/Barkerprooks/udp-tunnel/main/udptun.py")


@app.get("/tools/udptun.min.py")
async def udptun_min_content():
    return redirect("https://raw.githubusercontent.com/Barkerprooks/udp-tunnel/main/udptun.min.py")
