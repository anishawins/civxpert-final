# CivXpert 🏛️

### AI-Powered Civic Grievance Intelligence Platform

CivXpert is a full-stack civic complaint triage system that uses **NLP and fine-tuned DistilBERT models** to understand citizen grievances, classify them into civic categories, route them to the appropriate government department, and estimate operational priority.

The goal is simple: **turn an unstructured citizen complaint into an actionable government work item.**

---

## ✨ What it does

```text
Citizen complaint
       ↓
Text normalization & validation
       ↓
┌──────────────────────────────┐
│      AI TRIAGE PIPELINE      │
│                              │
│  Department BERT → Category   │
│  Priority BERT   → Urgency    │
└──────────────────────────────┘
       ↓
Department routing + confidence
       ↓
Complaint reference (CX-xxxxx)
       ↓
Authority operations dashboard
       ↓
Status: Submitted → Review → In Progress → Resolved
```

## 🚀 Core features

### Citizen portal
- Account registration and secure password hashing
- Natural-language complaint submission
- Automatic AI classification
- Government department routing
- High / Medium / Low priority prediction
- Model confidence display
- Unique complaint references
- Personal complaint history
- Complaint lifecycle tracking

### Authority console
- Role-based authority access
- Total and priority-level KPIs
- Department workload visualization
- Priority distribution chart
- Searchable operational complaint queue
- Status updates: **Submitted, Under Review, In Progress, Resolved**
- AI confidence surfaced alongside each complaint

### ML / NLP layer
- Fine-tuned **DistilBERT** for department classification
- Fine-tuned **DistilBERT** for priority classification
- Stratified validation split for department training
- Class-imbalance handling during department training
- Confidence scores from model probabilities
- Safety-oriented keyword overrides for clearly urgent civic incidents

---

## 🧠 Technology stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite, Flask-SQLAlchemy |
| NLP | Hugging Face Transformers, DistilBERT |
| Deep Learning | PyTorch |
| ML evaluation | scikit-learn |
| Data processing | pandas |
| Frontend | HTML, CSS, JavaScript |
| Visualization | Chart.js |
| Development | Git / GitHub |

---

## 📁 Project structure

```text
civxpert-final/
├── app.py                    # Flask application and routes
├── models.py                 # SQLAlchemy data models
├── router_system.py          # AI inference and routing logic
├── train_department_bert.py  # Department model training
├── train_priority_bert.py    # Priority model training
├── templates/                # Citizen, analyzer and authority UIs
├── data/                     # Local training datasets
├── models/                   # Generated model artifacts (gitignored)
├── requirements.txt
└── README.md
```

---

## 🔬 Machine learning approach

CivXpert uses two independent text-classification models rather than attempting to solve every task with a single classifier.

**Department model** predicts the civic category, which is mapped to a government-facing department such as Public Works, Water Supply, Electricity, Health, Police, Transport, or Sanitation.

**Priority model** predicts one of three operational levels: **High, Medium, Low**. For explicitly safety-critical terms, a deterministic override layer prevents an obviously urgent complaint from being downgraded solely because of model uncertainty.

This separation makes the system easier to evaluate, debug, and extend independently.

> Model performance numbers should be reported from the actual validation output produced by the training scripts rather than hard-coded into the documentation.

---

## 🛠️ Local setup

### 1. Clone the repository

```bash
git clone https://github.com/anishawins/civxpert-final.git
cd civxpert-final
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare / train the models

```bash
python3 train_department_bert.py
python3 train_priority_bert.py
```

The generated model artifacts are intentionally excluded from Git because of their size.

### 5. Configure the application

For local development, the app has safe development defaults. For deployment, set environment variables:

```bash
export SECRET_KEY="replace-with-a-long-random-secret"
export AUTHORITY_PASSWORD="replace-with-a-secure-password"
```

### 6. Start CivXpert

```bash
python3 app.py
```

Open the local Flask address shown in the terminal.

---

## 🔐 Security notes

CivXpert uses hashed passwords for newly created accounts and keeps the Flask secret key configurable through the environment. Production deployments should additionally use HTTPS, a production WSGI server, CSRF protection, rate limiting, secure cookie settings, and a production database.

The repository does **not** store trained model artifacts or local civic datasets in version control.

---

## 🎯 Example workflow

**Input:**

> “A large pothole has formed outside the school gate and vehicles are swerving into oncoming traffic to avoid it.”

**CivXpert produces:**

- Category → Roads
- Department → Public Works Department
- Priority → model-determined urgency
- Confidence → probability-based score
- Reference → `CX-xxxxx`
- Status → Submitted

The authority can then move the complaint through its operational lifecycle.

---

## 🔭 Future improvements

- Geolocation and map-based complaint clustering
- Duplicate complaint detection
- Multilingual / regional-language support
- Image evidence upload and computer-vision classification
- SLA monitoring and escalation alerts
- Department-specific analytics
- REST API for municipal integrations
- PostgreSQL deployment
- Automated model evaluation and CI/CD

---

## 📌 Project status

**CivXpert v1.0 — Full-stack prototype / academic project**

The project demonstrates an end-to-end pipeline from citizen input to AI-assisted civic triage and authority-side resolution tracking.
