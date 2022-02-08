# Сравниваем вакансии программистов

Скрипт скачивает  данные по вакансиям программистов с сайтов [HeadHunter](https://hh.ru/) и [SuperJob](https://russia.superjob.ru/), по городу Москва за последние 30 дней.

### Как установить
Python3 должен быть установлен. Затем используйте `pip`

```bash
pip install -r requirements.txt
```
Скрипт использует закрытый ключ к API сервиса [SuperJob](https://russia.superjob.ru/).
Для получения API нужно зарегистрироваться, затем используйте файл `.env`.

Пример файла `.env`:

```
API_SUPERJOB='Ваш ключ к API SuperJob'
```

### Как запустить

Для запуска скрипта введите:

```bash
python salary.py
```
Примерный результат работы скрипта:

```
+SuperJob Moscow--------+------------------+---------------------+------------------+
| Язык програмированния | Вакансий найдено | Вакансий Обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Python                | 77               | 53                  | 146505           |
| Java                  | 49               | 33                  | 200406           |
| JavaScript            | 105              | 85                  | 141670           |
| Ruby                  | 7                | 7                   | 161857           |
| PHP                   | 67               | 53                  | 144961           |
| C++                   | 50               | 36                  | 174791           |
| C#                    | 39               | 26                  | 183000           |
| C                     | 43               | 33                  | 185206           |
| Go                    | 17               | 14                  | 217914           |
| Scala                 | 1                | 1                   | 240000           |
+-----------------------+------------------+---------------------+------------------+
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык програмированния | Вакансий найдено | Вакансий Обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| Python                | 1977             | 527                 | 203275           |
| Java                  | 2856             | 501                 | 242254           |
| JavaScript            | 4013             | 937                 | 184455           |
| Ruby                  | 208              | 72                  | 219562           |
| PHP                   | 1632             | 805                 | 170015           |
| C++                   | 1459             | 441                 | 180863           |
| C#                    | 1664             | 477                 | 184782           |
| C                     | 2446             | 730                 | 184114           |
| Go                    | 741              | 184                 | 246486           |
| Scala                 | 178              | 34                  | 275882           |
+-----------------------+------------------+---------------------+------------------+

```

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).