from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Complaint
from router_system import route_complaint, predict_priority

app = Flask(__name__)
app.secret_key = "civxpert2024"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///civxpert.db"
db.init_app(app)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = username
            session["role"] = user.role
            if user.role == "authority":
                return redirect(url_for("authority_dashboard"))
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        existing = User.query.filter_by(username=username).first()
        if existing:
            return render_template("register.html", error="Username already exists")
        user = User(username=username, password=password, role="public")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    result = None
    if request.method == "POST":
        text = request.form["complaint"]
        department, category = route_complaint(text)
        priority = predict_priority(text)
        complaint = Complaint(
            text=text,
            category=category,
            department=department,
            priority=priority,
            username=session["user"]
        )
        db.session.add(complaint)
        db.session.commit()
        result = {"department": department, "category": category, "priority": priority}
    complaints = Complaint.query.filter_by(username=session["user"]).all()
    return render_template("dashboard.html", result=result, complaints=complaints)

@app.route("/authority")
def authority_dashboard():
    if "user" not in session or session.get("role") != "authority":
        return redirect(url_for("login"))
    complaints = Complaint.query.all()
    dept_counts = {}
    for c in complaints:
        dept_counts[c.department] = dept_counts.get(c.department, 0) + 1
    return render_template("authority.html", complaints=complaints, dept_counts=dept_counts)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="officer1").first():
            db.session.add(User(username="officer1", password="admin123", role="authority"))
            db.session.commit()
    app.run(debug=True)
