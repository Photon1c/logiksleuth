from __future__ import annotations

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from .scan_controller import ScanController, ScanConfig
from .config import CONFIG, AppConfig
from .test_mode import test_procedure_mappability


app = FastAPI(title="CaseLinker Advanced Mode", version="0.1.0")
controller = ScanController()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    csv_path: Optional[str] = None
    duration_hours: Optional[float] = 0.1  # short demo
    similarity_threshold: Optional[float] = None
    year_window: Optional[int] = None
    geo_window: Optional[int] = None


@app.post("/scan/start")
def start_scan(req: StartRequest, tasks: BackgroundTasks):
    if controller.is_running():
        raise HTTPException(status_code=409, detail="Scan already running")
    csv_path = req.csv_path or CONFIG.csv_path
    thr = req.similarity_threshold if req.similarity_threshold is not None else CONFIG.similarity_threshold
    yw = req.year_window if req.year_window is not None else CONFIG.year_window
    gw = req.geo_window if req.geo_window is not None else CONFIG.geo_window
    cfg = ScanConfig(csv_path=csv_path, duration_hours=req.duration_hours or 0.1, similarity_threshold=thr, year_window=yw, geo_window=gw)
    tasks.add_task(controller.run, cfg)
    return {"status": "started"}


@app.get("/scan/status")
def scan_status():
    return controller.status()


@app.get("/scan/results")
def scan_results(view: str = "summary"):
    if controller.is_running():
        raise HTTPException(status_code=409, detail="Scan in progress")
    data = controller.results(view=view)
    return data


@app.get("/config")
def get_config():
    return CONFIG.to_dict()


class UpdateConfigRequest(BaseModel):
    csv_path: Optional[str] = None
    similarity_threshold: Optional[float] = None
    year_window: Optional[int] = None
    geo_window: Optional[int] = None
    sample_limit: Optional[int] = None


@app.post("/config")
def update_config(req: UpdateConfigRequest):
    CONFIG.update_from({k: v for k, v in req.model_dump().items() if v is not None})
    return CONFIG.to_dict()


@app.get("/case/{case_id}")
def get_case(case_id: str):
    case = controller.get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/test/procedure")
def test_procedure(csv_path: Optional[str] = None, sample_limit: int = 10000):
    path = csv_path or CONFIG.csv_path
    return test_procedure_mappability(path, sample_limit=sample_limit)


