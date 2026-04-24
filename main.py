from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import polars as pl
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
df = pl.read_csv("patients.csv", dtypes={"contact_number": pl.Utf8})

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
    result = df.clone()

    if gender:
        result = result.filter(pl.col("gender").str.to_uppercase() == gender.upper())
    if insurance_provider:
        result = result.filter(pl.col("insurance_provider").str.to_lowercase().str.contains(insurance_provider.lower()))

    total = len(result)
    result = result.slice(offset, limit)

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "data": result.to_dicts()
    }

# ─────────────────────────────────────────────
# GET /patients/{patient_id}  → single patient
# ─────────────────────────────────────────────
@app.get("/patients/{patient_id}", tags=["Patients"])
def get_patient(patient_id: str):
    patient = df.filter(pl.col("patient_id").str.to_uppercase() == patient_id.upper())
    if len(patient) == 0:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")
    return patient[0].to_dict()

# ─────────────────────────────────────────────
# GET /patients/search    → search by name
# ─────────────────────────────────────────────
@app.get("/search/patients", tags=["Search"])
def search_patients(
    name: str = Query(..., description="Search by first or last name")
):
    result = df.filter(
        pl.col("first_name").str.to_lowercase().str.contains(name.lower()) |
        pl.col("last_name").str.to_lowercase().str.contains(name.lower())
    )
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=f"No patients found matching '{name}'")
    return {
        "total": len(result),
        "data": result.to_dicts()
    }

# ─────────────────────────────────────────────
# GET /stats              → summary statistics
# ─────────────────────────────────────────────
@app.get("/stats", tags=["Stats"])
def get_stats():
    gender_dist = df.group_by("gender").agg(pl.count().alias("count")).to_dicts()
    gender_dict = {row["gender"]: row["count"] for row in gender_dist}
    
    insurance_dist = df.group_by("insurance_provider").agg(pl.count().alias("count")).to_dicts()
    insurance_dict = {row["insurance_provider"]: row["count"] for row in insurance_dist}
    
    year_dist = df.with_columns(
        pl.col("registration_date").str.slice(0, 4).alias("year")
    ).group_by("year").agg(pl.count().alias("count")).sort("year").to_dicts()
    year_dict = {row["year"]: row["count"] for row in year_dist}
    
    return {
        "total_patients": len(df),
        "gender_distribution": gender_dict,
        "insurance_providers": insurance_dict,
        "registrations_by_year": year_dict
    }
