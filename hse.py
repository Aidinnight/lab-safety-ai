from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///labs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# مدل دیتابیس
class LabAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.Integer)
    equipment = db.Column(db.String(500))
    staff = db.Column(db.Integer)
    ppe = db.Column(db.String(500))
    purpose = db.Column(db.String(500))
    score = db.Column(db.Integer)
    category = db.Column(db.String(100))

# تابع امتیازدهی
def score_lab(size, equipment, staff, ppe_list, purpose):
    score = 0

    if size >= 100:
        score += 20
    elif size >= 50:
        score += 10
    else:
        score += 5

    score += min(len(equipment.split(",")) * 2, 20)

    if staff >= 10:
        score += 15
    elif staff >= 5:
        score += 10
    else:
        score += 5

    score += min(len(ppe_list.split(",")) * 3, 25)

    if "ویروسی" in purpose or "پاتوژن" in purpose:
        score -= 10
    elif "آموزشی" in purpose:
        score += 10

    if score >= 70:
        category = "BSL-4 (بالاترین سطح ایمنی)"
    elif score >= 50:
        category = "BSL-3"
    elif score >= 30:
        category = "BSL-2"
    else:
        category = "BSL-1 (پایین‌ترین سطح)"

    return score, category

@app.before_first_request
def create_tables():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        size = int(request.form["size"])
        equipment = request.form["equipment"]
        staff = int(request.form["staff"])
        ppe = request.form["ppe"]
        purpose = request.form["purpose"]

        score, category = score_lab(size, equipment, staff, ppe, purpose)

        lab = LabAssessment(
            size=size,
            equipment=equipment,
            staff=staff,
            ppe=ppe,
            purpose=purpose,
            score=score,
            category=category
        )
        db.session.add(lab)
        db.session.commit()

        return render_template("index.html", score=score, category=category)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
