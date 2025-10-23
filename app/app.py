import os, subprocess
from flask import Flask, request, render_template, redirect
import pymysql, docker

DB = dict(host="localhost", user="execuser", password="execpass", database="execdb")
LOG_DIR = "/var/log/jobs"

app = Flask(__name__)
dcli = docker.from_env()

def db():
    return pymysql.connect(**DB, cursorclass=pymysql.cursors.DictCursor, autocommit=True)

@app.route("/")
def index():
    with db().cursor() as c:
        c.execute("SELECT * FROM jobs ORDER BY id DESC")
        jobs = c.fetchall()
    return render_template("index.html", jobs=jobs)

@app.post("/create")
def create():
    name = request.form["name"].strip()
    image = request.form["image"].strip()
    cmd   = request.form["cmd"]
    cpus  = float(request.form["cpus"])
    mem   = int(request.form["mem_mb"])
    io_w  = int(request.form["io_weight"])
    log_path = f"{LOG_DIR}/{name}.log"

    # garante imagem
    dcli.images.pull(image)

    # docker run com limites (CPU/Mem/IO) e redirecionamento de log
    # IO: io.weight (cgroup v2) mapeado pelo --blkio-weight em alguns setups; fallback: tenta
    run_cmd = [
        "docker","run","-d","--name",name,
        f"--cpus={cpus}",
        f"--memory={mem}m",
        f"--blkio-weight={io_w}",
        "-v", f"{LOG_DIR}:/logs",
        image, "bash","-lc", f"{cmd} &> /logs/{name}.log"
    ]
    try:
        subprocess.check_call(run_cmd)
        status = "running"
    except subprocess.CalledProcessError:
        status = "error"

    with db().cursor() as c:
        c.execute("""INSERT INTO jobs (name,image,cmd,cpus,mem_mb,io_weight,log_path,status)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                  (name,image,cmd,cpus,mem,io_w,log_path,status))
    return redirect("/")

@app.get("/refresh/<int:jid>")
def refresh(jid):
    with db().cursor() as c:
        c.execute("SELECT * FROM jobs WHERE id=%s", (jid,))
        j = c.fetchone()
    if not j: return redirect("/")
    # pega status real do container
    try:
        cont = dcli.containers.get(j["name"])
        status = cont.status
    except:
        status = "exited"
    with db().cursor() as c:
        c.execute("UPDATE jobs SET status=%s WHERE id=%s", (status,jid))
    return redirect("/")

@app.get("/stop/<int:jid>")
def stop(jid):
    with db().cursor() as c:
        c.execute("SELECT * FROM jobs WHERE id=%s", (jid,))
        j = c.fetchone()
    if j:
        subprocess.call(["docker","stop",j["name"]])
        with db().cursor() as c2:
            c2.execute("UPDATE jobs SET status='exited' WHERE id=%s", (jid,))
    return redirect("/")

@app.get("/rm/<int:jid>")
def rm(jid):
    with db().cursor() as c:
        c.execute("SELECT * FROM jobs WHERE id=%s", (jid,))
        j = c.fetchone()
    if j:
        subprocess.call(["docker","rm","-f",j["name"]])
        with db().cursor() as c2:
            c2.execute("DELETE FROM jobs WHERE id=%s", (jid,))
    return redirect("/")

@app.get("/log/<int:jid>")
def log(jid):
    with db().cursor() as c:
        c.execute("SELECT * FROM jobs WHERE id=%s", (jid,))
        j = c.fetchone()
    if not j: return redirect("/")
    content = ""
    try:
        with open(j["log_path"], "r", errors="ignore") as f:
            content = f.read()[-20000:]  # tail simples
    except FileNotFoundError:
        content = "(sem log ainda)"
    return render_template("log.html", id=jid, content=content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
