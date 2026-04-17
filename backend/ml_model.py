import random

class DummyAnomalyModel:
    """
    Simulates an ML model that predicts anomalies before they become critical.
    In a real scenario, this would be an ONNX/TensorFlow/PyTorch model file
    evaluating rolling windows of sensor data.
    """
    def __init__(self):
        # Learned safe bounds
        self.bounds = {
            "reactorTemp": {"min": 320, "warning": 385, "critical": 420},
            "pressure": {"min": 1.8, "warning": 2.5, "critical": 3.0},
            "converterFlow": {"min": 85, "warning": 70, "critical": 40}, # Drops under
            "tankLevel": {"min": 20, "warning": 85, "critical": 95}
        }

    def evaluate(self, telemetry: dict) -> dict:
        """
        Evaluate full plant state and return ml context.
        """
        temp = telemetry.get("reactorTemp", 345)
        flow = telemetry.get("converterFlow", 98)
        level = telemetry.get("tankLevel", 72)
        
        result = {
            "status": "NORMAL",
            "modelExplanation": {
                "severity": "NORMAL",
                "area": "-",
                "parameter": "-",
                "reason": "System is operating within safe parameters.",
                "details": "All metrics are stable. Continuous ML monitoring active."
            },
            "espStatus": {
                "reactor": "NORMAL",
                "converter": "NORMAL",
                "tank": "NORMAL"
            },
            "simulatedLcdText": "SYSTEM NORMAL\n\n"
        }

        # Priority 1: Critical checks
        if temp > self.bounds["reactorTemp"]["critical"]:
            self._set_critical(result, "reactor", "Reactor-1", "Temperature", 
                               f"Temperature > {self.bounds['reactorTemp']['critical']}°C. Imminent containment breach risk.",
                               "Automated emergency shutdown sequence recommended immediately.",
                               "CRITICAL:\nRUNAWAY REACTION RISK")
            return result
        elif flow < self.bounds["converterFlow"]["critical"]:
            self._set_critical(result, "converter", "Converter-1", "Flow Rate",
                               f"Flow < {self.bounds['converterFlow']['critical']} Nm³/h. Catalyst bed damage likely.",
                               "Pressure building up rapidly due to blockage.",
                               "CRITICAL:\nCONVERTER BLOCKED")
            return result
        elif level > self.bounds["tankLevel"]["critical"]:
            self._set_critical(result, "tank", "Storage Tank A", "Level",
                               f"Tank Level > {self.bounds['tankLevel']['critical']}%. Overflow imminent.",
                               "Check output valve operations.",
                               "CRITICAL:\nTANK OVERFLOW RISK")
            return result

        # Priority 2: Warning checks
        if temp > self.bounds["reactorTemp"]["warning"]:
            self._set_warning(result, "reactor", "Reactor-1", "Temperature",
                              "Rising temperature trend beyond learned safe range.",
                              "⚠ Reactor temperature is increasing abnormally.\n\nPossible cause:\n- Cooling system failure\n- Excessive SO₂ feed\n\nCurrent trend suggests critical condition may occur within 2 minutes.",
                              "WARNING:\nReactor Temp Rising")
            return result
        elif flow < self.bounds["converterFlow"]["warning"]:
            self._set_warning(result, "converter", "Converter-1", "Flow Rate",
                              "Rapid decrease in gas flow detected.",
                              "⚠ Possible catalyst bed fouling or upstream valve failure.",
                              "WARNING:\nConverter Flow Drop")
            return result
        elif level > self.bounds["tankLevel"]["warning"]:
            self._set_warning(result, "tank", "Storage Tank A", "Level",
                              "Level increasing beyond operational setpoints.",
                              "⚠ Inflow significantly exceeds outflow.",
                              "WARNING:\nTank Level High")
            return result
            
        return result

    def _set_critical(self, result, node, area, parameter, reason, details, lcd):
        result["status"] = "CRITICAL"
        result["espStatus"][node] = "CRITICAL"
        result["simulatedLcdText"] = lcd
        result["modelExplanation"] = {
            "severity": "CRITICAL",
            "area": area,
            "parameter": parameter,
            "reason": reason,
            "details": details
        }
        
    def _set_warning(self, result, node, area, parameter, reason, details, lcd):
        result["status"] = "WARNING"
        result["espStatus"][node] = "WARNING"
        result["simulatedLcdText"] = lcd
        result["modelExplanation"] = {
            "severity": "WARNING",
            "area": area,
            "parameter": parameter,
            "reason": reason,
            "details": details
        }
