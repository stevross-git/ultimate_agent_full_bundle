# core/health.py - REPLACE PLACEHOLDER
import psutil
from datetime import datetime
from typing import Dict, Any

class HealthChecker:
    def __init__(self, server):
        self.server = server
    
    def check_database(self) -> Dict[str, Any]:
        try:
            # Test database connection
            result = self.server.db.session.execute("SELECT 1").fetchone()
            return {"status": "healthy", "details": "Database responsive"}
        except Exception as e:
            return {"status": "unhealthy", "details": f"Database error: {str(e)}"}
    
    def check_system_resources(self) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        status = "healthy"
        if cpu > 80 or memory.percent > 80:
            status = "warning"
        if cpu > 95 or memory.percent > 95:
            status = "critical"
        
        return {
            "status": status,
            "cpu_percent": cpu,
            "memory_percent": memory.percent
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        db_health = self.check_database()
        system_health = self.check_system_resources()
        
        overall = "healthy"
        if any(h["status"] == "critical" for h in [db_health, system_health]):
            overall = "critical"
        elif any(h["status"] == "warning" for h in [db_health, system_health]):
            overall = "warning"
        
        return {
            "overall_status": overall,
            "database": db_health,
            "system": system_health,
            "timestamp": datetime.now().isoformat()
        }