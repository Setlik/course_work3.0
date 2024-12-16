from typing import Any, Dict, List

import psycopg2


def create_database(database_name: str, params: Dict[str, str]) -> None:
    """Создание базы данных и таблиц для сохранения данных."""

    conn = psycopg2.connect(dbname='postgres', user=params['user'], password=params['password'], host=params['host'],
                            port=params.get('port', 5432))
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
    exists = cur.fetchone()

    if exists:
        cur.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{database_name}';
        """)
        cur.execute(f"DROP DATABASE {database_name};")

    cur.execute(f"CREATE DATABASE {database_name};")
    conn.close()

    conn = psycopg2.connect(dbname=database_name, user=params['user'], password=params['password'],
                            host=params['host'], port=params.get('port', 5432))

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                hh_id BIGINT UNIQUE NOT NULL,
                name VARCHAR(255) NOT NULL,
                url VARCHAR(255)
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                employer_id BIGINT REFERENCES employers(id),
                title VARCHAR(255) NOT NULL,
                salary_min INTEGER,
                salary_max INTEGER,
                area VARCHAR(255),
                published_at TIMESTAMP
            );
        """)
    conn.commit()
    conn.close()


def save_data_to_database(data: List[Dict[str, Any]], database_name: str, params: Dict[str, str]) -> None:
    """Сохранение данных о работодателях и вакансиях в базу данных."""

    conn = None
    try:
        conn = psycopg2.connect(dbname=database_name, user=params['user'], password=params['password'],
                                host=params['host'], port=params.get('port', 5432))
        with conn.cursor() as cur:
            for item in data:
                employer_data = item.get('employer')

                if employer_data is None:
                    print(f"Предупреждение: 'employer' не найден в элементе: {item}")
                    continue

                hh_id = employer_data.get('id')
                name = employer_data.get('name')
                url = employer_data.get('alternate_url')

                if hh_id is None or name is None or url is None:
                    print(f"Предупреждение: отсутствует обязательное поле работодателя в элементе: {employer_data}")
                    continue

                cur.execute("""
                    INSERT INTO employers (hh_id, name, url)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (hh_id)
                    DO UPDATE SET name = EXCLUDED.name, url = EXCLUDED.url
                    RETURNING id;
                """, (hh_id, name, url))

                employer_id = cur.fetchone()
                if employer_id is None:
                    print("Ошибка: ID работодателя не был возвращён после вставки/обновления.")
                    continue

                employer_id = employer_id[0] if isinstance(employer_id, tuple) else employer_id

                vacancies = item.get('vacancies', [])
                if not isinstance(vacancies, list):
                    print(
                        f"Предупреждение: 'vacancies' не является списком для работодателя ID {hh_id}."
                        f" Данные: {vacancies}")
                    continue

                for vacancy in vacancies:
                    title = vacancy.get('name')
                    vacancy_url = vacancy.get('alternate_url')
                    salary = vacancy.get('salary')
                    salary_min = salary.get('from') if salary else None
                    salary_max = salary.get('to') if salary else None
                    date_posted = vacancy.get('published_at')
                    area_name = vacancy.get('area', {}).get('name')

                    if title is None or vacancy_url is None or area_name is None:
                        print(
                            f"Предупреждение: отсутствует обязательное поле вакансии: title: {title}, "
                            f"vacancy_url: {vacancy_url}, area_name: {area_name}")
                        print(f"Данные вакансии: {vacancy}")
                        continue

                    cur.execute("""
                        INSERT INTO vacancies (employer_id, title, salary_min, salary_max, area, published_at)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """, (employer_id, title, salary_min, salary_max, area_name, date_posted))

            conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении данных в базу данных: {e}")
    finally:
        if conn:
            conn.close()
