import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from plant_simulator import PlantSimulator
from ml_model import DummyAnomalyModel

app = FastAPI(title="Plant Monitoring Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = PlantSimulator()
ml_model = DummyAnomalyModel()

class AnomalyRequest(BaseModel):
    mode: str

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulator.start_loop())

@app.on_event("shutdown")
def shutdown_event():
    simulator.stop_loop()

@app.get("/api/state")
def get_plant_state():
    """
    Returns current telemetry combined with ML evaluation.
    This replaces the frontend tick logic.
    """
    sim_state = simulator.get_state()
    eval_result = ml_model.evaluate(sim_state["metrics"])
    
    return {
        **sim_state,
        "eval": eval_result
    }

@app.post("/api/anomaly")
def trigger_anomaly(req: AnomalyRequest):
    """
    Trigger or reset an anomaly mode via the dashboard.
    Modes: NONE, REACTOR, CONVERTER, TANK
    """
    if req.mode == "NONE":
        simulator.reset()
    else:
        simulator.set_anomaly(req.mode)
    return {"status": "success", "mode": simulator.anomaly_mode}

@app.get("/esp32/{node_id}/status")
def get_esp_status(node_id: str):
    """
    ESP32 devices poll this route to get their status.
    node_id: reactor, converter, tank
    Returns JSON with node, status and message.
    """
    sim_state = simulator.get_state()
    eval_result = ml_model.evaluate(sim_state["metrics"])
    
    status = eval_result["espStatus"].get(node_id, "NORMAL")
    message = eval_result["simulatedLcdText"] if status != "NORMAL" else "SYSTEM NORMAL"
    
    return {
        "node": node_id,
        "status": status,
        "message": message
    }
