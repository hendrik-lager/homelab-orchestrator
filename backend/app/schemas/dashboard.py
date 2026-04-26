from pydantic import BaseModel

class DashboardSummary(BaseModel):
    hosts_total: int
    services_running: int
    services_down: int
    pending_updates: int
    security_updates: int
    active_alerts: int
