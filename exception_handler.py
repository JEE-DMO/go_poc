
import requests

def classify_exception(exc) -> tuple[int, str, str]:
    """
    Retourne (status_code, user_message, tech_message)
    """

    if isinstance(exc, requests.exceptions.Timeout):
        return (
            408,
            "Le service Airflow ne répond pas (timeout).",
            f"Timeout: {str(exc)}"
        )

    if isinstance(exc, requests.exceptions.ConnectionError):
        return (
            0,
            "Impossible d’atteindre l’instance Airflow.",
            f"ConnectionError: {str(exc)}"
        )

    if isinstance(exc, requests.exceptions.SSLError):
        return (
            495,
            "Erreur SSL lors de la communication avec Airflow.",
            f"SSLError: {str(exc)}"
        )

    if isinstance(exc, requests.exceptions.TooManyRedirects):
        return (
            310,
            "Redirections multiples détectées.",
            f"TooManyRedirects: {str(exc)}"
        )

    if isinstance(exc, requests.exceptions.HTTPError):
        return (
            520,
            "Erreur HTTP renvoyée par Airflow.",
            f"HTTPError: {str(exc)}"
        )

    if isinstance(exc, requests.exceptions.RequestException):
        return (
            500,
            "Erreur de communication avec Airflow.",
            f"RequestException: {str(exc)}"
        )

    return (
        500,
        "Erreur interne lors de la vérification de santé.",
        f"Unexpected exception: {type(exc).__name__} – {str(exc)}"
    )
