from typing import List, Dict, Any
from datetime import datetime
from airflow.models import Variable
from airflow_health.models import AirflowInstance, HealthStatus


HTML_TEMPLATE = Variable.get("HTML_TEMPLATE", default_var="")

def build_environment_details_html(summary: Dict[str, Any], by_key: str, cards_per_row: int = 3) -> str:

    data = summary[by_key]
    max_per_row = max(1, int(cards_per_row))
    
    html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" border="0"
           style="margin-top:20px;border-collapse:collapse;border:none;border-spacing:0;">
        <tr>
            <td colspan="{max_per_row}" style="padding-bottom:10px;border:none;">
                <h2 style="color:#003366;margin:0 0 10px 0;">📊 {by_key.replace('_',' ').title()}</h2>
            </td>
        </tr>
        <tr>
    """

    col = 0
    for key, stats in data.items():

        pct = round((stats["healthy"]/stats["total"]*100) if stats["total"] else 0, 2)
        if pct > 80:
            bg = "#d6f3e4"; border = "#0f8b4b"
        else:
            bg = "#f8d7da"; border = "#d43f3a"

        html += f"""
        <td width="{100/max_per_row}%" style="padding:8px;border:none;vertical-align:top;">
            <table width="100%" cellpadding="8" cellspacing="0" 
                   style="background:{bg};border-collapse:collapse;border-left:4px solid {border};
                          border-radius:6px;text-align:center;">
                <tr>
                    <td style="font-size:14px;color:#666;font-weight:600;border:none;">
                        {key}
                    </td>
                </tr>
                <tr>
                    <td style="font-size:28px;font-weight:bold;color:#003366;border:none;">
                        {stats['healthy']}/{stats['total']}
                    </td>
                </tr>
            </table>
        </td>
        """

        col += 1
        if col == max_per_row:
            html += "</tr><tr>"
            col = 0

    if col != 0:
        while col < max_per_row:
            html += f'<td width="{100/max_per_row}%" style="border:none;"></td>'
            col += 1

    html += "</tr></table>"
    return html

def build_instance_row_html(status: HealthStatus) -> str:
    instance = status.instance

    def badge_symbol(text: str) -> str:
        if text == "healthy":
            return "✅"
        if text == "N/A":
            return "⚠️"
        return "❌"
    status_symbol = "✅" if status.is_healthy else "❌"

    error_cell = f'<span style="color:#d43f3a;font-size:12px;font-style:italic;text-align:center;">{status.error_message}</span>' if status.error_message else '-'

    def td_center(content: str) -> str:
        return f'<td style="text-align:center;font-size:15px;">{content}</td>'

    return f'''
    <tr style="border-bottom:1px solid #ddd;">
        {td_center(instance.business_line)}
        {td_center(instance.environment)}
        <td><a href="{instance.url}">{instance.url_label}</a></td>
        {td_center(instance.version)}
        {td_center(status_symbol)}
        {td_center(badge_symbol(status.dag_processor_status))}
        {td_center(badge_symbol(status.scheduler_status))}
        {td_center(badge_symbol(status.triggerer_status))}
        {td_center(badge_symbol(status.metadatabase_status))}

        <td>{error_cell}</td>
    </tr>
    '''
def format_envs(env_list: list[str]) -> str:
    return " | ".join(e.upper() for e in env_list)


def build_html_report(health_statuses: List[HealthStatus], summary: Dict[str, Any], environment_label: str) -> str:

    instances_rows = '\n'.join([build_instance_row_html(status) for status in sorted(health_statuses, key=lambda s: s.instance.business_line)])
    environment_details = build_environment_details_html(summary, "by_environment", 3)
    business_line_details = build_environment_details_html(summary, "by_business_line", 5)
    
    html = HTML_TEMPLATE.format(
        environment_label=format_envs(environment_label),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_instances=summary['total_instances'],
        healthy_instances=summary['healthy_instances'],
        unhealthy_instances=summary['unhealthy_instances'],
        health_percentage=summary['health_percentage'],
        environment_details=environment_details,
        business_line_details=business_line_details,
        instances_rows=instances_rows
    )
    
    return html




def get_email_subject(summary: Dict[str, Any], environment_label: str) -> str:

    status_emoji = "✅" if summary['unhealthy_instances'] == 0 else "⚠️"
    return (f"{status_emoji} Airflow Health Report • {format_envs(environment_label)} - "
            f"{summary['healthy_instances']}/{summary['total_instances']} OK "
            # f"({summary['health_percentage']}%)"
            )