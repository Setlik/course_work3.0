from typing import Any, Dict, List, Optional

import requests


def get_employer_data(employer_id: str) -> Optional[Dict[str, Any]]:
    """Получение данных о работодателе по его ID."""
    employer_url = f"https://api.hh.ru/employers/{employer_id}"
    try:
        employer_response = requests.get(employer_url)
        employer_response.raise_for_status()
        return employer_response.json()
    except requests.RequestException as e:
        print(f"Ошибка при получении данных о работодателе {employer_id}: {e}")
        return None


def get_vacancies_by_employer(employer_id: str) -> List[Dict[str, Any]]:
    """Получение вакансий для работодателя по его ID."""
    vacancies_url = f"https://api.hh.ru/vacancies?employer_id={employer_id}"
    try:
        vacancies_response = requests.get(vacancies_url)
        vacancies_response.raise_for_status()
        return vacancies_response.json().get("items", [])
    except requests.RequestException as e:
        print(f"Ошибка при получении вакансий для работодателя {employer_id}: {e}")
        return []
