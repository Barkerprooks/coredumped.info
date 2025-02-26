from flask import Flask, render_template


from coredumped import get_random_banner
from coredumped.blog import blog


app = Flask(__name__)


app.register_blueprint(blog)


@app.get("/")
async def index():
    return render_template("index.html", banner=await get_random_banner(), page="i n d e x")
    
