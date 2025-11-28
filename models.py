from dataclasses import dataclass
from datetime import datetime


@dataclass
class AirflowInstance:
    business_line: str
    app_code: str
    environment: str
    release_uid: str
    version: str
    
    @property
    def url(self) -> str:
        return f"https://astronomer_{self.app_code}-{self.environment}-{self.release_uid}.data.gouv.fr" #.data.cloud.net.intradata.eu"
    
    @property
    def health_url(self) -> str:
        return "http://8b040c531832:8080/api/v1/health"  #f"{self.url}/api/v1/health"

    @property
    def url_label(self) -> str:
        return f"astronomer_{self.app_code}-{self.environment}-{self.release_uid}"
    

@dataclass
class HealthStatus:
    instance: AirflowInstance
    status_code: int
    scheduler_status: str = "N/A"
    dag_processor_status: str = "N/A"
    triggerer_status: str = "N/A"
    metadatabase_status: str = "N/A"
    last_heartbeat: str = None
    heartbeat_age: str = None
    error_message: str = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.checked_at is None:
            self.checked_at = datetime.now()
    
    @property
    def is_healthy(self) -> bool:
        return self.status_code == 200