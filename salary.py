import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def get_table_superjob(superjob_language, title='SuperJob Moscow'):
    table_colums = [
        [
            "Язык програмированния",
            "Вакансий найдено",
            "Вакансий Обработано",
            "Средняя зарплата"
        ]
    ]
    for language, language_data in superjob_language.items():
        data_for_one_language = list()
        data_for_one_language.append(language)
        for data in language_data.values():
            data_for_one_language.append(data)
        table_colums.append(data_for_one_language)
    table = AsciiTable(table_colums, title)
    return table.table


def get_superjob_pages(superjob_url, language, headers):
    superjob_pages = list()
    for page in range(500):
        params = {
            'town': 'Москва',
            'keyword': f'Программист {language}',
            'page': page,
        }
        page_response = requests.get(
                                    superjob_url,
                                    headers=headers,
                                    params=params,
                                    )
        page_response.raise_for_status()
        superjob_pages.append(page_response.json())
        if not page_response.json()['more']:
            break
    return superjob_pages


def predict_rub_salary_for_superJob(vacancy):
    average = 0
    if not vacancy.get('payment_from') and not vacancy.get('payment_to'):
        return
    if not vacancy.get('payment_from'):
        average = vacancy.get('payment_to') * 0.8
    if not vacancy.get('payment_to'):
        average = vacancy.get('payment_from') * 1.2
    if vacancy.get('payment_from') and vacancy.get('payment_to'):
        average = (vacancy.get('payment_from') + vacancy.get('payment_to')) / 2
    return int(average)


def get_number_of_pages_hh_ru(hh_ru_url, language):
    params = {
        'text': f'NAME:Программист {language}',
        'area': 1,
        'period': 30,
        }
    response = requests.get(
                            hh_ru_url,
                            params=params,
                            )
    response.raise_for_status()
    return response.json()['pages']


def get_table_hh_ru(hh_ru_language, title='HeadHunter Moscow'):
    table_colums = [
        [
            "Язык програмированния",
            "Вакансий найдено",
            "Вакансий Обработано",
            "Средняя зарплата"
        ]
    ]
    for language, language_data in hh_ru_language.items():
        data_for_one_language = list()
        data_for_one_language.append(language)
        for data in language_data.values():
            data_for_one_language.append(data)
        table_colums.append(data_for_one_language)
    table = AsciiTable(table_colums, title)
    return table.table


def get_hh_ru_pages(hh_ru_url, language, number_pages):
    hh_ru_pages = list()
    for page in range(number_pages):
        params = {
            'text': f'NAME:Программист {language}',
            'area': 1,
            'period': 30,
            'page': page,
        }
        page_response = requests.get(
                                    hh_ru_url,
                                    params=params,
                                    )
        page_response.raise_for_status()
        hh_ru_pages.append(page_response.json())
    return hh_ru_pages


def get_hh_ru_rawsalary(items):
    salaries = list()
    for salary in items:
        salaries.append(salary.get('salary'))
    return salaries


def predict_hh_ru_rub_salary(raw_salaries):
    average_salaries = list()
    average = 0
    for salary in raw_salaries:
        salary = salary
        if not salary:
            continue
        if not salary.get('currency') == 'RUR':
            continue
        if not salary.get('from'):
            average = salary.get('to') * 0.8
        if not salary.get('to'):
            average = salary.get('from') * 1.2
        if salary.get('from') and salary.get('to'):
            average = (salary.get('from') + salary.get('to')) / 2
        average_salaries.append(average)
    return average_salaries


def main():
    hh_ru_language = dict()
    superjob_language = dict()
    load_dotenv()
    api_superjob = os.getenv('API_SUPERJOB')
    languages = [
            'Python',
            'Java',
            'JavaScript',
            'Ruby',
            'PHP',
            'C++',
            'C#',
            'C',
            'Go',
            'Scala',
    ]
    url = 'https://api.hh.ru/vacancies'
    for language in languages:
        number_pages = get_number_of_pages_hh_ru(url, language)
        hh_ru_pages = get_hh_ru_pages(url, language, number_pages)
        average_salaries_hh_ru = list()
        for items in hh_ru_pages:
            found_pages = items.get('found')
            items = items.get('items')
            raw_salaries = get_hh_ru_rawsalary(items)
            average_salaries = predict_hh_ru_rub_salary(raw_salaries)
            average_salaries_hh_ru.append(average_salaries)
        average_salary_hh_ru = int(sum(sum(average_salaries_hh_ru, []))/len(sum(average_salaries_hh_ru, [])))
        hh_ru_language.update(
            {language: {
                    "vacancies_found": found_pages,
                    "vacancies_processed": len(sum(average_salaries_hh_ru, [])),
                    "average_salary": average_salary_hh_ru,
            }
            })
        superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {
            'X-Api-App-Id': api_superjob
        }
        superjob_pages = get_superjob_pages(superjob_url, language, headers)
        superjob_salaries = list()
        for vacancies in superjob_pages:
            salary = list()
            for vacancy in vacancies.get('objects'):
                average = predict_rub_salary_for_superJob(vacancy)
                if not average:
                    continue
                salary.append(average)
            superjob_salaries.append(salary)
        average_salary_superjob = int(sum(sum(superjob_salaries, []))/len(sum(superjob_salaries, [])))
        superjob_language.update(
            {language: {
                    "vacancies_found": vacancies.get('total'),
                    "vacancies_processed": len(sum(superjob_salaries, [])),
                    "average_salary": average_salary_superjob,
            }
            })
    print(get_table_superjob(superjob_language, title='SuperJob Moscow'))
    print(get_table_hh_ru(hh_ru_language, title='HeadHunter Moscow'))


if __name__ == '__main__':
    main()
