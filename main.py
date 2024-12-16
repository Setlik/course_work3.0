from src.api import get_vacancies_by_employer, get_employer_data
from src.config import config
from src.db_manager import DBManager
from src.utils import save_data_to_database, create_database


def main() -> None:
    """Главная функция для работы пользователя с базой данных."""
    params = config()
    database_name = 'hh'

    employer_ids = ['58320', '3529', '4181', '78638', '3776', '2180', '87021', '2460946', '53417',
                    '916364']  # Список ID работодателей
    data = []

    for employer_id in employer_ids:
        employer_data = get_employer_data(employer_id)
        if employer_data:
            vacancies = get_vacancies_by_employer(employer_id)
            data.append({
                'employer': employer_data,
                'vacancies': vacancies
            })
        else:
            print(f"Не удалось получить данные о работодателе {employer_id}")

    create_database(database_name, params)
    save_data_to_database(data, database_name, params)
    db = DBManager()

    while True:
        print("\nВыберите действие:")
        print("1 - Посмотреть компании и количество вакансий")
        print("2 - Посмотреть все вакансии")
        print("3 - Узнать среднюю зарплату по вакансиям")
        print("4 - Посмотреть вакансии с зарплатой выше средней")
        print("5 - Найти вакансии по ключевому слову")
        print("0 - Выход")

        choice = input("Введите номер действия: ")

        if choice == '1':
            companies = db.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            for company in companies:
                print(f"{company[0]}: {company[1]} вакансий")

        elif choice == '2':
            vacancies = db.get_all_vacancies()
            print("\nВсе вакансии:")
            for vacancy in vacancies:
                print(
                    f"Компания: {vacancy[0]}, "
                    f"Вакансия: {vacancy[1]}, "
                    f"Зарплата: {vacancy[2] if vacancy[2] is not None else 'не указана'}, "
                    f"Ссылка: {vacancy[4]}"
                )
        elif choice == '3':
            avg_salary = db.get_avg_salary()
            print(f"\nСредняя зарплата по вакансиям: {avg_salary if avg_salary is not None else 'недоступна'}")

        elif choice == '4':
            higher_salary_vacancies = db.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            for vacancy in higher_salary_vacancies:
                print(
                    f"Компания: {vacancy[0]}, "
                    f"Вакансия: {vacancy[1]}, "
                    f"Зарплата: {vacancy[2] if vacancy[2] is not None else 'не указана'}, "
                    f"Ссылка: {vacancy[4]}"
                )

        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска: ")
            keyword_vacancies = db.get_vacancies_with_keyword(keyword)
            print(f"\nВакансии с ключевым словом '{keyword}':")
            for vacancy in keyword_vacancies:
                print(
                    f"Компания: {vacancy[0]}, "
                    f"Вакансия: {vacancy[1]}, "
                    f"Зарплата: {vacancy[2] if vacancy[2] is not None else 'не указана'}, "
                    f" Ссылка: {vacancy[4]}"
                )

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Некорректный ввод, пожалуйста, выберите действие из меню.")

    db.close()


if __name__ == "__main__":
    main()
