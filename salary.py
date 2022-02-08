import os
import requests

from dotenv import load_dotenv
from itertools import count
from terminaltables import AsciiTable


def get_hh_ru_pages(hh_ru_url, language):
    hh_ru_pages = list()
    for page in count(0):
        params = {
            'text': f'NAME:Программист {language}',
            'area': 1,
            'period': 30,
            'page': page,
        }
        page_response = requests.get(hh_ru_url, params=params)
        page_response.raise_for_status()
        page_data = page_response.json()
        hh_ru_pages.append(page_data)
        if page >= page_data.get('pages') or page >= 99:
            break
    return hh_ru_pages


def get_sj_pages(sj_url, language, api_sj):
    headers = {'X-Api-App-Id': api_sj}
    superjob_pages = list()
    for page in count(0):
        params = {
            'town': 'Москва',
            'keyword': f'Программист {language}',
            'page': page,
        }
        page_response = requests.get(
            sj_url,
            headers=headers,
            params=params,
        )
        page_response.raise_for_status()
        page_data = page_response.json()
        superjob_pages.append(page_data)
        if not page_data.get('more'):
            break
    return superjob_pages


def hh_ru_vacansies(hh_ru_pages):
    salaries = list()
    for items in hh_ru_pages:
        vacancies_found = items.get('found')
        items = items.get('items')
        salary = list()
        for vacancy in items:
            average = predict_rub_salary_hh(vacancy)
            if not average:
                continue
            salary.append(average)
        salaries.append(salary)
    average_salary = int(sum(sum(salaries, []))/len(sum(salaries, [])))
    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': len(sum(salaries, [])),
        'average_salary': average_salary,
    }


def sj_vacansies(sj_pages):
    salaries = list()
    for vacancies in sj_pages:
        vacancies_found = vacancies.get('total')
        salary = list()
        for vacancy in vacancies.get('objects'):
            average = predict_rub_salary_sj(vacancy)
            if not average:
                continue
            salary.append(average)
        salaries.append(salary)
    average_salary = int(sum(sum(salaries, []))/len(sum(salaries, [])))
    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': len(sum(salaries, [])),
        'average_salary': average_salary,
    }


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


def predict_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    if not salary_from:
        return salary_to * 0.8
    if not salary_to:
        return salary_from * 1.2
    else:
        return (salary_from + salary_to) / 2


def get_table(language, title):
    table_colums = [
        [
            'Язык програмированния',
            'Вакансий найдено',
            'Вакансий Обработано',
            'Средняя зарплата',
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
    sj_language = dict()
    load_dotenv()
    api_sj = os.getenv('API_SUPERJOB')
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
    hh_ru_url = 'https://api.hh.ru/vacancies'
    sj_url = 'https://api.superjob.ru/2.0/vacancies/'
    for language in languages:
        hh_ru_pages = get_hh_ru_pages(hh_ru_url, language)
        sj_pages = get_sj_pages(sj_url, language, api_sj)
        hh_ru_vacancy = hh_ru_vacansies(hh_ru_pages)
        sj_vacancy = sj_vacansies(sj_pages)
        hh_ru_language.update({language: hh_ru_vacancy})
        sj_language.update({language: sj_vacancy})
    print(get_table(hh_ru_language, title='HeadHunter Moscow'))
    print(get_table(sj_language, title='SuperJob Moscow'))


if __name__ == '__main__':
    main()
