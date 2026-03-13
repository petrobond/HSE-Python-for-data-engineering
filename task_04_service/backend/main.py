from pathlib import Path
from datetime import datetime

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_PATH = Path(__file__).parent / "data.csv"

app = FastAPI()

# CORS: allow Streamlit Cloud and local dev
STREAMLIT_CLOUD_ORIGINS = [
    "https://share.streamlit.io",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=STREAMLIT_CLOUD_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecordCreate(BaseModel):
    timestep: datetime
    consumption_eur: float
    consumption_sib: float
    price_eur: float
    price_sib: float


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if "id" not in df.columns:
        df["id"] = range(len(df))
    return df


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_PATH, index=False)


@app.get("/records")
def get_records():
    try:
        df = load_data()
        # Ensure id is int for JSON
        if "id" in df.columns:
            df["id"] = df["id"].astype(int)
        return df.to_dict(orient="records")
    except (FileNotFoundError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"Failed to load data: {e!s}")


@app.post("/records", status_code=201)
def add_record(record: RecordCreate):
    try:
        df = load_data()
        new_id = 0 if df.empty else int(df["id"].max()) + 1
        row = {
            "id": new_id,
            "timestep": record.timestep.isoformat(sep=" ").replace("T", " ")[:16],
            "consumption_eur": record.consumption_eur,
            "consumption_sib": record.consumption_sib,
            "price_eur": record.price_eur,
            "price_sib": record.price_sib,
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        save_data(df)
        return row
    except (FileNotFoundError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"Failed to save data: {e!s}")


@app.delete("/records/{record_id}")
def delete_record(record_id: int):
    try:
        df = load_data()
        if "id" not in df.columns or record_id not in df["id"].values:
            raise HTTPException(status_code=404, detail="Record not found")
        df = df[df["id"] != record_id].copy()
        save_data(df)
        return {"deleted_id": record_id}
    except HTTPException:
        raise
    except (FileNotFoundError, OSError) as e:
        raise HTTPException(status_code=503, detail=f"Failed to modify data: {e!s}")
