import random
import time
import asyncio
from typing import Dict, Any

class PlantSimulator:
    def __init__(self):
        self.anomaly_mode = "NONE"
        self.metrics = {
            "reactorTemp": 345.0,
            "pressure": 2.2,
            "converterFlow": 98.0,
            "tankLevel": 72.0
        }
        self.is_running = False

    def reset(self):
        self.anomaly_mode = "NONE"
        self.metrics = {
            "reactorTemp": 345.0,
            "pressure": 2.2,
            "converterFlow": 98.0,
            "tankLevel": 72.0
        }

    def set_anomaly(self, mode: str):
        self.anomaly_mode = mode

    def tick(self):
        # Normal noise
        if self.anomaly_mode == "NONE":
            self.metrics["reactorTemp"] = 345 + (random.random() * 2 - 1)
            self.metrics["pressure"] = 2.2 + (random.random() * 0.1 - 0.05)
            self.metrics["converterFlow"] = 98 + (random.random() * 2 - 1)
            self.metrics["tankLevel"] = 72 + (random.random() * 1 - 0.5)
            
        # Reactor Overheating Anomaly
        elif self.anomaly_mode == "REACTOR":
            self.metrics["reactorTemp"] += 10 + (random.random() * 2)
            self.metrics["pressure"] += 0.05 + (random.random() * 0.02)
            self.metrics["converterFlow"] -= 1.5 + (random.random() * 0.5)
            
        # Converter Blockage Anomaly
        elif self.anomaly_mode == "CONVERTER":
            self.metrics["converterFlow"] -= 8 + (random.random() * 2)
            self.metrics["pressure"] += 0.1 + (random.random() * 0.05)
            self.metrics["tankLevel"] -= 2
            
        # Tank Overflow Anomaly
        elif self.anomaly_mode == "TANK":
            self.metrics["tankLevel"] += 5 + (random.random() * 1)
            self.metrics["converterFlow"] -= 0.5

        # formatting constraints
        self.metrics["pressure"] = round(self.metrics["pressure"], 2)
        self.metrics["reactorTemp"] = round(self.metrics["reactorTemp"], 1)
        self.metrics["converterFlow"] = round(self.metrics["converterFlow"], 1)
        self.metrics["tankLevel"] = round(self.metrics["tankLevel"], 1)

    async def start_loop(self):
        self.is_running = True
        while self.is_running:
            self.tick()
            await asyncio.sleep(1)

    def stop_loop(self):
        self.is_running = False

    def get_state(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "anomalyMode": self.anomaly_mode
        }
