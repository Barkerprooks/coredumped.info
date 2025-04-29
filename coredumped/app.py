from flask import Flask, render_template, redirect


from coredumped.blog import blog


app = Flask(__name__)
app.register_blueprint(blog)


@app.get("/")
async def index():
    return render_template("index.html", banner="Here for when your brain has a segmentation fault.", page="home")


# >>> this is so stupid lmao, idc...
# main versions
@app.get("/utils/udptun.py")
@app.get("/utils/udptun-v1.1.0.py")
async def udptun_main():
    return redirect("https://github.com/Barkerprooks/udp-tunnel/releases/download/v1.1.0/udptun.py")

@app.get("/utils/udptun-v1.0.1.py")
async def udptun_v1_0_1():
    return redirect("https://github.com/Barkerprooks/udp-tunnel/releases/download/v1.0.1/udptun.py")

@app.get("/utils/udptun-v1.0.0.py")
async def udptun_v1_0_0():
    return redirect("https://github.com/Barkerprooks/udp-tunnel/releases/download/v1.0.0/udptun.py")

# minified versions
@app.get("/utils/udptun.min.py")
@app.get("/utils/udptun-v1.1.0.min.py")
async def udptun_min_main():
    return redirect("https://github.com/Barkerprooks/udp-tunnel/releases/download/v1.0.1/udptun.min.py")

@app.get("/utils/udptun-v1.0.1.min.py")
async def udptun_min_v1_0_1():
    return redirect("https://github.com/Barkerprooks/udp-tunnel/releases/download/v1.0.1/udptun.min.py")
