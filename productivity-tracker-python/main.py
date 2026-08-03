import os, sqlite3
from datetime import date
from functools import wraps
from pathlib import Path
from uuid import uuid4
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-before-deployment")
DB=Path(__file__).with_name("productivity_tracker.db")
BACKEND=os.environ.get("DATA_BACKEND","sqlite").lower()
_firestore=None

def fs():
    global _firestore
    if _firestore is None:
        from google.cloud import firestore
        _firestore=firestore.Client()
    return _firestore

def init_db():
    con=sqlite3.connect(DB)
    con.executescript("""CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS activities(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id TEXT NOT NULL,activity_name TEXT NOT NULL,category TEXT NOT NULL,importance_level TEXT NOT NULL,duration_minutes INTEGER NOT NULL,activity_date TEXT NOT NULL);""")
    con.close()

def con():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def create_account(username,password_hash):
    if BACKEND=="firestore":
        key=username.lower(); ref=fs().collection("accounts").document(key)
        if ref.get().exists: return None
        ref.set({"username":username,"password_hash":password_hash}); return key
    c=con()
    try:
        cur=c.execute("INSERT INTO accounts(username,password_hash) VALUES(?,?)",(username,password_hash)); c.commit(); return str(cur.lastrowid)
    except sqlite3.IntegrityError: return None
    finally: c.close()

def find_account(username):
    if BACKEND=="firestore":
        snap=fs().collection("accounts").document(username.lower()).get()
        if not snap.exists: return None
        d=snap.to_dict(); return {"id":snap.id,**d}
    c=con(); r=c.execute("SELECT id,username,password_hash FROM accounts WHERE username=?",(username,)).fetchone(); c.close()
    return None if r is None else {"id":str(r["id"]),"username":r["username"],"password_hash":r["password_hash"]}

def add_activity(user_id,a):
    if BACKEND=="firestore":
        fs().collection("activities").document(str(uuid4())).set({"user_id":user_id,**a}); return
    c=con(); c.execute("""INSERT INTO activities(user_id,activity_name,category,importance_level,duration_minutes,activity_date) VALUES(?,?,?,?,?,?)""",(user_id,a["activity_name"],a["category"],a["importance_level"],a["duration_minutes"],a["activity_date"])); c.commit(); c.close()

def get_activities(user_id):
    if BACKEND=="firestore":
        docs=fs().collection("activities").where("user_id","==",user_id).stream()
        return sorted([d.to_dict() for d in docs],key=lambda x:x.get("activity_date",""),reverse=True)
    c=con(); rows=c.execute("""SELECT activity_name,category,importance_level,duration_minutes,activity_date FROM activities WHERE user_id=? ORDER BY activity_date DESC,id DESC""",(user_id,)).fetchall(); c.close(); return [dict(r) for r in rows]

def login_required(view):
    @wraps(view)
    def wrapped(*args,**kwargs):
        if "user_id" not in session:
            flash("Please log in first.","error"); return redirect(url_for("login"))
        return view(*args,**kwargs)
    return wrapped

@app.route("/")
def index(): return redirect(url_for("dashboard" if "user_id" in session else "login"))

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form.get("username","").strip(); p=request.form.get("password",""); cp=request.form.get("confirm_password","")
        if not 3<=len(u)<=30: flash("Username must be between 3 and 30 characters.","error")
        elif not u.replace("_","").isalnum(): flash("Use only letters, numbers, and underscores.","error")
        elif len(p)<8: flash("Password must contain at least 8 characters.","error")
        elif p!=cp: flash("Passwords do not match.","error")
        elif create_account(u,generate_password_hash(p)) is None: flash("That username is already registered.","error")
        else: flash("Account created. You can now log in.","success"); return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        a=find_account(request.form.get("username","").strip()); p=request.form.get("password","")
        if a and check_password_hash(a["password_hash"],p):
            session.clear(); session["user_id"]=a["id"]; session["username"]=a["username"]; return redirect(url_for("dashboard"))
        flash("Invalid username or password.","error")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    acts=get_activities(session["user_id"])
    return render_template("dashboard.html",activities=acts,total_minutes=sum(int(a["duration_minutes"]) for a in acts),high_importance=sum(a["importance_level"]=="High" for a in acts))

@app.route("/activities/new",methods=["GET","POST"])
@login_required
def create_activity():
    cats=["School","Work","Exercise","Personal","Entertainment","Other"]; levels=["Low","Medium","High"]
    if request.method=="POST":
        name=request.form.get("activity_name","").strip(); cat=request.form.get("category",""); level=request.form.get("importance_level",""); ds=request.form.get("duration_minutes","").strip(); ad=request.form.get("activity_date","")
        try: minutes=int(ds)
        except ValueError: minutes=0
        if not name: flash("Activity name is required.","error")
        elif cat not in cats: flash("Choose a valid category.","error")
        elif level not in levels: flash("Choose a valid importance level.","error")
        elif not 1<=minutes<=1440: flash("Duration must be between 1 and 1,440 minutes.","error")
        elif not ad: flash("Date is required.","error")
        else:
            add_activity(session["user_id"],{"activity_name":name,"category":cat,"importance_level":level,"duration_minutes":minutes,"activity_date":ad})
            flash("Activity added successfully.","success"); return redirect(url_for("dashboard"))
    return render_template("create_activity.html",categories=cats,importance_levels=levels,today=date.today().isoformat())

@app.route("/logout")
def logout():
    session.clear(); flash("You have been logged out.","success"); return redirect(url_for("login"))

if __name__=="__main__":
    if BACKEND=="sqlite": init_db()
    app.run(host="0.0.0.0",port=8080,debug=True)
