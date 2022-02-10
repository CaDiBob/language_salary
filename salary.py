import os
import requests
import statistics

from dotenv import load_dotenv
from statistics import mean
from terminaltables import AsciiTable


def get_hh_ru_pages(language, url):
    hh_ru_pages = list()
    for page in range(1):
        params = {
            'text': f'NAME:Программист {language}',
            'area': 1, # id г.Москва в запросах к HeadHunter API
            'period': 30,
            'page': page,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        response = response.json()
        hh_ru_pages.append(response)
    return hh_ru_pages


def get_sj_pages(language, api_sj, url):
    headers = {'X-Api-App-Id': api_sj}
    superjob_pages = list()
    for page in range(1):
        params = {
            'town': 'Москва',
            'keyword': f'Программист {language}',
            'page': page,
        }
        response = requests.get(
            url,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        response = response.json()
        superjob_pages.append(response)
    return superjob_pages


def get_hh_ru_vacansies(hh_ru_pages):
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
    salaries = [item for salary in salaries for item in salary]
    average_salary = int(mean(salaries))
    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': len(salaries),
        'average_salary': average_salary,
    }


def get_sj_vacansies(sj_pages):
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
    salaries = [item for salary in salaries for item in salary]
    average_salary = int(mean(salaries))
    return {
        'vacancies_found': vacancies_found,
        'vacancies_processed': len(salaries),
        'average_salary': average_salary,
    }


def predict_rub_salary_hh(vacancy):
    salary = vacancy.get('salary')
    if not salary:
        return
    if salary.get('currency') == 'RUR':   
        salary_from = salary.get('from')
        salary_to = salary.get('to')
        return predict_salary(salary_from, salary_to)


def predict_rub_salary_sj(vacancy):
    if vacancy.get('currency') == 'rub':
        salary_from = vacancy.get('payment_from')
        salary_to = vacancy.get('payment_to')
        return predict_salary(salary_from, salary_to)


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from:
        return salary_from * 1.2
    if salary_to:
        return salary_to * 0.8


def get_table(languages, title):
    table_colums = [
        [
            'Язык програмированния',
            'Вакансий найдено',
            'Вакансий Обработано',
            'Средняя зарплата',
        ]
    ]
    for language, language_statistics in languages.items():
        programming_language = list()
        programming_language.append(language)
        for statistic in language_statistics.values():
            programming_language.append(statistic)
        table_colums.append(programming_language)
    table = AsciiTable(table_colums, title)
    return table.table


def main():
    hh_ru_languages = dict()
    sj_languages = dict()
    load_dotenv()
    api_sj = os.getenv('API_SUPERJOB')
    languages = [
        'COBOL',
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
    for language in languages:
        try:
            hh_ru_pages = get_hh_ru_pages(
                language, 
                url='https://api.hh.ru/vacancies',
                )
            sj_pages = get_sj_pages(
                language,
                api_sj,
                url='https://api.superjob.ru/2.0/vacancies/',
                )
            hh_ru_vacancy = get_hh_ru_vacansies(hh_ru_pages)
            sj_vacancy = get_sj_vacansies(sj_pages)
            hh_ru_languages.update({language: hh_ru_vacancy})
            sj_languages.update({language: sj_vacancy})
        except statistics.StatisticsError:
            print(f'Вакансий по языку {language} не найдено!')
            continue
    print(get_table(hh_ru_languages, title='HeadHunter Moscow'))
    print(get_table(sj_languages, title='SuperJob Moscow'))


if __name__ == '__main__':
    main()
