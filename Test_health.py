from dataclasses import dataclass
from datetime import datetime

@dataclass
class AirflowInstance:
    url: str
    app_code: str
    environment: str
    region: str

    def health_url(self) -> str:
        return f"{self.url}/api/v1/health"

    @property
    def url_label(self) -> str:
        return f"Astronomer-{self.app_code}-{self.environment}-{self.region}"


@dataclass
class HealthStatus:
    instance: AirflowInstance
    status_code: int
    scheduler_status: str = "N/A"
    dag_processor_status: str = "N/A"
    trigger_status: str = "N/A"
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

    @property
    def is_all_healthy(self) -> bool:
        checks = {
            "status_code": self.status_code == 200,
            "scheduler_status": self.scheduler_status.lower() == "healthy",
            "dag_processor_status": self.dag_processor_status.lower() == "healthy",
            "trigger_status": self.trigger_status.lower() == "healthy",
            "metadatabase_status": self.metadatabase_status.lower() == "healthy"
        }

        for component, healthy in checks.items():
            if not healthy:
                print(f"[DEBUG] {component} is not healthy: {getattr(self, component) if hasattr(self, component) else 'N/A'}")

        return all(checks.values())


def mock_airflow_health_response():
    """Simule une réponse typique de /api/v1/health"""
    return {
        "status_code": 200,
        "scheduler_status": "healthy",
        "dag_processor_status": "healthy",
        "trigger_status": "healthy",
        "metadatabase_status": "healthy"
    }


def main():
    # Simuler une instance Airflow
    instance = AirflowInstance(
        url="http://localhost:8080",
        app_code="myapp",
        environment="dev",
        region="eu"
    )

    # Simuler une réponse de santé
    response = mock_airflow_health_response()

    # Construire l'objet HealthStatus
    health = HealthStatus(
        instance=instance,
        status_code=response["status_code"],
        scheduler_status=response["scheduler_status"],
        dag_processor_status=response["dag_processor_status"],
        trigger_status=response["trigger_status"],
        metadatabase_status=response["metadatabase_status"]
    )

    print(f"Health check for {instance.url_label}")
    print("All components healthy ✅" if health.is_all_healthy else "Some components are unhealthy ❌")


if __name__ == "__main__":
    main()
