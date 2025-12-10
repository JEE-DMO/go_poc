Mettre à jour __init__.py




from airflow.models.xcom_arg import XComArg

result = XComArg(generate_report_task)

send_email_task = EmailOperator(
    task_id='send_email',
    to=Variable.get("health_check_email_recipients", default_var="").split(","),
    subject=result["email_subject"],
    html_content=result["html_content"],
)
