import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Complaint
from router_system import route_complaint, predict_priority
from services.duplicate_detector import ComplaintSimilarity

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///civxpert.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
similarity = ComplaintSimilarity(threshold=0.55)


def analyze(text):
    department, category = route_complaint(text)
    priority, confidence = predict_priority(text)
    return {"department": department, "category": category, "priority": priority, "confidence": confidence}


def current_user():
    username = session.get("user")
    return User.query.filter_by(username=username).first() if username else None


@app.route("/")
def home():
    if session.get("user"):
        return redirect(url_for("authority_dashboard" if session.get("role") == "authority" else "dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.clear()
            session["user"] = user.username
            session["role"] = user.role
            return redirect(url_for("authority_dashboard" if user.role == "authority" else "dashboard"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            return render_template("register.html", error="Username must be 3+ characters and password 6+ characters")
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="Username already exists")
        user = User(username=username, password=generate_password_hash(password), role="public")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if session.get("role") != "public":
        return redirect(url_for("login"))

    result = None
    similar = []
    if request.method == "POST":
        text = request.form.get("complaint", "").strip()
        if not text:
            return render_template("dashboard.html", result=None, complaints=[], similar=[], error="Please describe your complaint.")
        if len(text) > 2000:
            return render_template("dashboard.html", result=None, complaints=[], similar=[], error="Complaint must be under 2000 characters.")

        result = analyze(text)
        similar = similarity.find_similar(text, Complaint.query.order_by(Complaint.created_at.desc()).limit(500).all())
        complaint = Complaint(text=text, category=result["category"], department=result["department"],
                              priority=result["priority"], priority_confidence=result["confidence"], username=session["user"])
        db.session.add(complaint)
        db.session.commit()
        result["reference"] = complaint.reference

    complaints = Complaint.query.filter_by(username=session["user"]).order_by(Complaint.created_at.desc()).all()
    return render_template("dashboard.html", result=result, complaints=complaints, similar=similar)


@app.route("/analyzer", methods=["GET", "POST"])
def analyzer():
    result = None
    if request.method == "POST":
        text = request.form.get("complaint", "").strip()
        if text:
            result = analyze(text)
    return render_template("analyzer.html", result=result)


@app.route("/authority")
def authority_dashboard():
    if session.get("role") != "authority":
        return redirect(url_for("login"))
    query = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    priority = request.args.get("priority", "").strip()
    department = request.args.get("department", "").strip()
    complaints_query = Complaint.query
    if query:
        complaints_query = complaints_query.filter(Complaint.text.ilike(f"%{query}%"))
    if status:
        complaints_query = complaints_query.filter_by(status=status)
    if priority:
        complaints_query = complaints_query.filter_by(priority=priority)
    if department:
        complaints_query = complaints_query.filter_by(department=department)
    complaints = complaints_query.order_by(Complaint.created_at.desc()).all()

    all_complaints = Complaint.query.all()
    dept_counts, priority_counts = {}, {"High": 0, "Medium": 0, "Low": 0}
    status_counts = {}
    for complaint in all_complaints:
        dept_counts[complaint.department] = dept_counts.get(complaint.department, 0) + 1
        if complaint.priority in priority_counts:
            priority_counts[complaint.priority] += 1
        status_counts[complaint.status] = status_counts.get(complaint.status, 0) + 1
    departments = sorted(d for d in dept_counts if d)
    return render_template("authority.html", complaints=complaints, dept_counts=dept_counts,
                           priority_counts=priority_counts, status_counts=status_counts,
                           departments=departments, filters={"q": query, "status": status, "priority": priority, "department": department})


@app.route("/authority/complaint/<int:complaint_id>/status", methods=["POST"])
def update_status(complaint_id):
    if session.get("role") != "authority":
        return redirect(url_for("login"))
    complaint = db.session.get(Complaint, complaint_id)
    status = request.form.get("status")
    if complaint and status in {"Submitted", "Under Review", "In Progress", "Resolved"}:
        complaint.status = status
        complaint.updated_at = datetime.utcnow()
        db.session.commit()
    return redirect(request.referrer or url_for("authority_dashboard"))


@app.route("/delete/<int:complaint_id>", methods=["POST"])
def delete_complaint(complaint_id):
    if session.get("role") != "public":
        return redirect(url_for("login"))
    complaint = db.session.get(Complaint, complaint_id)
    if complaint and complaint.username == session["user"]:
        db.session.delete(complaint)
        db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        officer = User.query.filter_by(username="officer1").first()
        if not officer:
            officer = User(username="officer1", password=generate_password_hash(os.environ.get("AUTHORITY_PASSWORD", "admin123")), role="authority")
            db.session.add(officer)
            db.session.commit()
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
