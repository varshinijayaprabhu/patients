from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional

app = FastAPI(
    title="Patients API",
    description="REST API for patient records — powered by CSV data source",
    version="1.0.0"
)

# Allow all origins (good for demo purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load CSV once at startup
df = pd.read_csv("patients.csv", dtype={"contact_number": str})

# ─────────────────────────────────────────────
# GET /                  → health check
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Patients API is running",
        "total_patients": len(df),
        "docs": "/docs"
    }

# ─────────────────────────────────────────────
# GET /patients           → all patients (with optional filters)
# ─────────────────────────────────────────────
@app.get("/patients", tags=["Patients"])
def get_all_patients(
    gender: Optional[str] = Query(None, description="Filter by gender (M or F)"),
    insurance_provider: Optional[str] = Query(None, description="Filter by insurance provider"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Skip N records (for pagination)")
):
    result = df.copy()

    if gender:
        result = result[result["gender"].str.upper() == gender.upper()]
    if insurance_provider:
        result = result[result["insurance_provider"].str.lower().str.contains(insurance_provider.lower())]

    total = len(result)
    result = result.iloc[offset: offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": result.to_dict(orient="records")
    }

# ─────────────────────────────────────────────
# GET /patients/{patient_id}  → single patient
# ─────────────────────────────────────────────
@app.get("/patients/{patient_id}", tags=["Patients"])
def get_patient(patient_id: str):
    patient = df[df["patient_id"].str.upper() == patient_id.upper()]
    if patient.empty:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    return patient.iloc[0].to_dict()

# ─────────────────────────────────────────────
# GET /patients/search    → search by name
# ─────────────────────────────────────────────
@app.get("/search/patients", tags=["Search"])
def search_patients(
    name: str = Query(..., description="Search by first or last name")
):
    mask = (
        df["first_name"].str.lower().str.contains(name.lower()) |
        df["last_name"].str.lower().str.contains(name.lower())
    )
    result = df[mask]
    if result.empty:
        raise HTTPException(status_code=404, detail=f"No patients found matching '{name}'")
    return {
        "total": len(result),
        "data": result.to_dict(orient="records")
    }

# ─────────────────────────────────────────────
# GET /stats              → summary statistics
# ─────────────────────────────────────────────
@app.get("/stats", tags=["Stats"])
def get_stats():
    return {
        "total_patients": len(df),
        "gender_distribution": df["gender"].value_counts().to_dict(),
        "insurance_providers": df["insurance_provider"].value_counts().to_dict(),
        "registrations_by_year": df["registration_date"].str[:4].value_counts().sort_index().to_dict()
    }
