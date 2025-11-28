import requests
from typing import List, Dict, Any
from datetime import datetime
import logging
from collections import defaultdict

from airflow_health.models import AirflowInstance, HealthStatus
from exception_handler import classify_exception


logger = logging.getLogger(__name__)

def check_all_instances(instances: List[AirflowInstance]) -> List[HealthStatus]:
    return list(check_instance_health(inst) for inst in instances)


def check_instance_health(instance: AirflowInstance, timeout: int = 10) -> HealthStatus:
    health_status = HealthStatus(instance=instance, status_code=None)

    try:
        api_response = requests.get(instance.url, timeout=timeout)
        health_status.status_code = api_response.status_code

        if 200 <= api_response.status_code < 300:
            try:
                json_data = api_response.json()
                health_status.scheduler_status     = json_data.get("scheduler", {}).get("status", "N/A")
                health_status.dag_processor_status = json_data.get("dag_processor", {}).get("status", "N/A")
                health_status.triggerer_status     = json_data.get("triggerer", {}).get("status", "N/A")
                health_status.metadatabase_status  = json_data.get("metadatabase", {}).get("status", "N/A")
            except Exception as exc:
                health_status.error_message = f"Invalid JSON from API – {str(e)}"
        else:
            tech = (r.text or "").strip()[:300]
            h.error_message = f"HTTP {r.status_code}: {tech}"

    except Exception as exc:
        code, user_msg, tech_msg = classify_exception(exc)
        health_status.status_code = code
        health_status.error_message = f"{user_msg} | Details: {tech_msg}"

    return health_status


def aggregate_health_summary(health_statuses: List[HealthStatus]) -> Dict[str, Any]:
    total = len(health_statuses)
    healthy = sum(s.is_healthy for s in health_statuses)

    env_stats = defaultdict(lambda: {'total': 0, 'healthy': 0, 'unhealthy': 0})
    bl_stats = defaultdict(lambda: {'total': 0, 'healthy': 0, 'unhealthy': 0})

    for s in health_statuses:
        env, bl = s.instance.environment, s.instance.business_line
        for stats in (env_stats[env], bl_stats[bl]):
            stats['total'] += 1
            stats['healthy'] += s.is_healthy
            stats['unhealthy'] += not s.is_healthy

    return {
        'total_instances': total,
        'healthy_instances': healthy,
        'unhealthy_instances': total - healthy,
        'health_percentage': round((healthy / total * 100), 2) if total else 0,
        'by_environment': dict(env_stats),
        'by_business_line': dict(bl_stats),
        'checked_at': datetime.now().isoformat()
    }
    
    
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
def get_instances_from_airflowctl(airflowctl_command: str, environments: List[str]) -> List[AirflowInstance]:
    
    logger.info(f"Récupération des instances pour les environnements: {environments}")
    instances_data = get_running_instances(environments)
    
    instances = [
        AirflowInstance(
            app_code=data['app_code'],
            release=data['release'],
            version=data['version'],
            uid=data['uid'],
            environment=data['environment']
        )
        for data in instances_data
    ]
    
    logger.info(f"{len(instances)} instances récupérées")
    return instances




