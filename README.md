# CivXpert 🧠
AI-powered civic complaint management system that automatically classifies public grievances into relevant government departments and assigns priority using NLP and Machine Learning.

## Tech Stack
- Flask + SQLAlchemy (Backend)
- DistilBERT / PyTorch (Priority Prediction)
- RapidFuzz (Department Routing)
- TailwindCSS + Chart.js (Frontend)
- SQLite (Database)

## Features
- Dual login: Public & Authority roles
- BERT-powered priority detection (High/Medium/Low)
- Fuzzy matching department routing
- Live Chart.js dashboard for authorities

## Run Locally
```bash
pip install -r requirements.txt
python3 train_priority_bert.py
python3 app.py
```

## Authority Login
- Username: officer1
- Password: admin123
