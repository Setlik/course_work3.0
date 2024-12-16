import os
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from psycopg2 import connect

load_dotenv()


class DBManager:
    def __init__(self) -> None:
        """Инициализация подключения к базе данных."""
        params: Dict[str, Any] = {
            'dbname': 'hh',
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
        }

        self.connection = connect(**params)
        self.cursor = self.connection.cursor()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """Получение списка компаний и количества их вакансий."""
        query = """
        SELECT e.name, COUNT(v.id)
        FROM employers e
        LEFT JOIN vacancies v ON e.id = v.employer_id
        GROUP BY e.name;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получение всех вакансий с информацией о компании."""
        query = """
        SELECT e.name, v.title, v.salary_min, v.salary_max, e.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id;
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def get_avg_salary(self) -> float:
        """Получение средней зарплаты по всем вакансиям."""
        query = """
        SELECT AVG(salary_min) AS avg_salary
        FROM vacancies
        WHERE salary_min IS NOT NULL;
                """
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchone()
            return result[0] if result is not None else 0.0
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return 0.0

    def get_vacancies_with_higher_salary(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получение вакансий с зарплатой выше средней."""
        avg_salary = self.get_avg_salary()
        query = """
        SELECT e.name, v.title, v.salary_min, v.salary_max, e.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        WHERE v.salary_min > %s;
        """
        try:
            self.cursor.execute(query, (avg_salary,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """Получение вакансий, содержащих ключевое слово в названии."""
        query = """
        SELECT e.name, v.title, v.salary_min, v.salary_max, e.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        WHERE v.title ILIKE %s;
        """
        try:
            self.cursor.execute(query, (f'%{keyword}%',))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            return []

    def close(self) -> None:
        """Закрытие курсора и соединения с базой данных."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
