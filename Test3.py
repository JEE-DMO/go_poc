subject="{{ ti.xcom_pull(task_ids='generate_report', key='email_subject') }}"
html_content="{{ ti.xcom_pull(task_ids='generate_report', key='html_content') }}"
