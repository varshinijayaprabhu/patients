# 🏥 Patients API

A public REST API built with **FastAPI** serving patient records from a CSV data source.

---

## 🚀 Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload

# 3. Open in browser
# API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check + total count |
| GET | `/patients` | Get all patients (with filters) |
| GET | `/patients/{patient_id}` | Get a single patient by ID |
| GET | `/search/patients?name=` | Search by first or last name |
| GET | `/stats` | Summary statistics |

---

## 🔍 Query Parameters

### `GET /patients`
| Param | Type | Description |
|-------|------|-------------|
| `gender` | string | Filter by `M` or `F` |
| `insurance_provider` | string | Filter by provider name (partial match) |
| `limit` | int | Max records (default: 50) |
| `offset` | int | Pagination offset (default: 0) |

---

## 📦 Example Requests

```bash
# All patients
curl http://localhost:8000/patients

# Filter by gender
curl http://localhost:8000/patients?gender=F

# Filter by insurance provider
curl "http://localhost:8000/patients?insurance_provider=HealthIndia"

# Get single patient
curl http://localhost:8000/patients/P001

# Search by name
curl "http://localhost:8000/search/patients?name=David"

# Stats
curl http://localhost:8000/stats
```

---

## ☁️ Deploy to Render (Free)

1. Push this folder to a GitHub repo
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` → click **Deploy**
5. Your API goes live at: `https://patients-api.onrender.com`

## ☁️ Deploy to Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Railway picks up `Procfile` automatically
4. Done!

---

## 🗂 Project Structure

```
patients-api/
├── main.py           # FastAPI app with all endpoints
├── patients.csv      # Data source
├── requirements.txt  # Python dependencies
├── render.yaml       # Render deployment config
├── Procfile          # Railway deployment config
└── README.md
```
