import os
import requests

from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary:
        return None
    if salary.get('currency') == 'RUR':
        salary_from = salary.get('from')
        salary_to = salary.get('to')
        return predict_salary(salary_from, salary_to)
    else:
        return None
    

def predict_rub_salary_sj(vacancy):
    if not vacancy.get('currency') == 'rub':
        return None
    else:
        salary_from = vacancy.get('payment_from')
        salary_to = vacancy.get('payment_to')
        return predict_salary(salary_from, salary_to)


def hh_ru_vacansies(hh_ru_pages):
    hh_ru_salaries = list()
    for items in hh_ru_pages:
        found_vacansies = items.get('found')
        items = items.get('items')
        salary = list()
        for vacancy in items:
            average = predict_rub_salary_hh(vacancy) 
            if not average:
                continue
            salary.append(average)
        hh_ru_salaries.append(salary)
    average_salary = int(sum(sum(hh_ru_salaries, []))/len(sum(hh_ru_salaries, [])))  
    return {
        "vacancies_found": found_vacansies,
        "vacancies_processed": len(sum(hh_ru_salaries, [])),
        "average_salary": average_salary,
    } 
    

def superjob_vacansies(superjob_pages):
    superjob_salaries = list()
    for vacancies in superjob_pages:
        salary = list()
        for vacancy in vacancies.get('objects'):
            average = predict_rub_salary_sj(vacancy)
            if not average:
                continue
            salary.append(average)
        superjob_salaries.append(salary)
    average_salary_superjob = int(sum(sum(superjob_salaries, []))/len(sum(superjob_salaries, [])))
    return {
        "vacancies_found": vacancies.get('total'),
        "vacancies_processed": len(sum(superjob_salaries, [])),
        "average_salary": average_salary_superjob,
    }


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


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return salary_to * 0.8
    if not salary_to:
        return salary_from * 1.2
    else:
        return (salary_from + salary_to) / 2


def get_number_of_pages_hh_ru(hh_ru_url, language):
    params = {
        'text': f'NAME:Программист {language}',
        'area': 1,
        'period': 30,
    }
    response = requests.get(hh_ru_url, params=params)
    response.raise_for_status()
    return response.json()['pages']


def get_hh_ru_pages(hh_ru_url, language, number_pages):
    hh_ru_pages = list()
    for page in range(number_pages):
        params = {
            'text': f'NAME:Программист {language}',
            'area': 1,
            'period': 30,
            'page': page,
        }
        page_response = requests.get(hh_ru_url, params=params)
        page_response.raise_for_status()
        hh_ru_pages.append(page_response.json())
    return hh_ru_pages


def get_table(language, title):
    table_colums = [
        [
        "Язык програмированния",
        "Вакансий найдено",
        "Вакансий Обработано",
        "Средняя зарплата",
        ]
    ]
    for language, language_data in language.items():
        data_for_one_language = list()
        data_for_one_language.append(language)
        for data in language_data.values():
            data_for_one_language.append(data)
        table_colums.append(data_for_one_language)
    table = AsciiTable(table_colums, title)
    return table.table


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
        hh_ru_vacancy = hh_ru_vacansies(hh_ru_pages)
        hh_ru_language.update({language: hh_ru_vacancy})
        superjob_url = 'https://api.superjob.ru/2.0/vacancies/'
        headers = {
            'X-Api-App-Id': api_superjob
        }
        superjob_pages = get_superjob_pages(superjob_url, language, headers)
        superjob_vacancy = superjob_vacansies(superjob_pages)
        superjob_language.update({language: superjob_vacancy})
    
    print(get_table(superjob_language, title='SuperJob Moscow'))
    print(get_table(hh_ru_language, title='HeadHunter Moscow'))


if __name__ == '__main__':
    main()
