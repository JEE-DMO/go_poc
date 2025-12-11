def debug_xcom(**context):
    ti = context["ti"]
    results = {}

    # Méthode 1 : ti.xcom_pull simple
    try:
        results["m1"] = ti.xcom_pull(task_ids="generate_report", key="email_subject")
    except Exception as e:
        results["m1"] = f"FAILED: {e}"

    # Méthode 2 : xcom_pull sans key
    try:
        results["m2"] = ti.xcom_pull(task_ids="generate_report")
    except Exception as e:
        results["m2"] = f"FAILED: {e}"

    # Méthode 3 : XComArg (si le DAG le permet)
    try:
        from airflow.models.xcom_arg import XComArg
        results["m3"] = XComArg(context["dag"].get_task("generate_report"))["email_subject"]
    except Exception as e:
        results["m3"] = f"FAILED: {e}"

    # Méthode 4 : récupération brute dans la DB XCom
    try:
        from airflow.models import XCom
        res = XCom.get_one(
            execution_date=context["execution_date"],
            task_id="generate_report",
            dag_id=context["dag"].dag_id,
            key="email_subject",
        )
        results["m4"] = res
    except Exception as e:
        results["m4"] = f"FAILED: {e}"

    # Log des résultats
    print("===== XCOM DEBUG RESULTS
