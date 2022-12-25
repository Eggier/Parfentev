from prettytable import PrettyTable
from functools import cmp_to_key
import csv
import re
from datetime import datetime as dt
import os.path


class Vacancy:
    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name, published_at):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency


class DataSet:
    def __init__(self, file_name, vacancies_objects):
        self.file_name = file_name
        self.vacancies_objects = vacancies_objects


class InputConnect:
    def __init__(self):
        self.file_name = ''
        self.request_param = ''
        self.column_title_for_sort = ''
        self.reversed_sort = ''
        self.index_parts = ''
        self.params_input = ''
        self.error_msg = ''
        self.salary_req = None
        self.request_param_ok = None
        self.reversed_flag = None
        self.indexes = []
        self.params = []
        self.indexes_ok = True
        self.bad_param_found = False
        self.file_name_ok = True

    def read_user_input(self):
        self.file_name = input('Введите название файла: ')
        self.request_param = input('Введите параметр фильтрации: ')
        self.column_title_for_sort = input('Введите параметр сортировки: ')
        self.reversed_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.index_parts = input('Введите диапазон вывода: ').split()
        self.params_input = input('Введите требуемые столбцы: ')


        if not (len(self.file_name) > 4 and self.file_name.endswith('.csv') and os.path.exists('work_files/' + self.file_name)):
            self.file_name_ok = False

        if len(self.column_title_for_sort) > 0 and self.column_title_for_sort not in rus_eng_title:
            self.column_title_for_sort = None

        if self.reversed_sort == 'Да':
            self.reversed_flag = True
        elif self.reversed_sort == 'Нет' or self.reversed_sort == '':
            self.reversed_flag = False

        self.params = self.params_input.split(', ')
        for index_part in self.index_parts:
            try:
                self.indexes.append(int(index_part))
            except ValueError:
                self.indexes_ok = False
                break

        if self.indexes_ok:
            if len(self.indexes) > 2:
                self.indexes_ok = False
            elif not all_are_pos(self.indexes):
                self.indexes_ok = False
            elif len(self.indexes) == 2 and self.indexes[0] >= self.indexes[1]:
                self.indexes_ok = False

        for param in self.params:
            if param not in rus_eng_title:
                self.bad_param_found = True
                break

        self.process_request_params()

    def process_request_params(self):
        self.request_param_ok = False, False
        if self.request_param == '':
            self.request_param_ok = True, True
        elif len(self.request_param) > 0:
            if ': ' not in self.request_param:
                pass
            else:
                self.request_param_ok = True, False
                request_data = self.request_param.split(': ')
                if request_data[0] in rus_eng_title.keys():
                    self.request_param_ok = True, True

                if all(self.request_param_ok):
                    if request_data[0] in columns_for_exact_match:
                        req_value = rus_eng_currency[request_data[1]] if request_data[1] in rus_eng_currency else request_data[1]
                        req_value = rus_eng_work_experience[request_data[1]] if request_data[1] in rus_eng_work_experience else req_value
                        req_value = rus_eng_prem_vac[request_data[1]] if request_data[1] in rus_eng_prem_vac else req_value
                        dict_for_exact_match[rus_eng_title[request_data[0]]] = req_value
                    elif request_data[0] in columns_for_items_match:
                        dict_for_items_match[rus_eng_title[request_data[0]]] = request_data[1].split(', ')
                    elif request_data[0] in columns_for_substring_match:
                        date_parts = request_data[1].split('.')
                        if len(date_parts) != 3:
                            print('Некорпектный формат даты')
                        else:
                            date_str = date_parts[2] + '-' + date_parts[1] + '-' + date_parts[0] + 'T'
                            dict_for_substring_match[rus_eng_title[request_data[0]]] = date_str
                    elif request_data[0] in columns_for_range_match:
                        self.salary_req = float(request_data[1])

    def full_check_error_not_found(self):
        if not self.file_name_ok:
            print('название файла некорректно или файл не найден')
            return False
        elif not self.request_param_ok[0]:
            print("Формат ввода некорректен")
            return False
        elif not self.request_param_ok[1]:
            print("Параметр поиска некорректен")
            return False
        elif self.column_title_for_sort is None:
            print('Параметр сортировки некорректен')
            return False
        elif self.reversed_flag is None:
            print('Порядок сортировки задан некорректно')
            return False
        elif not self.indexes_ok:
            print('некорректеные индексы')
            return False
        elif len(self.params_input) > 0 and self.bad_param_found:
            print('Параметры демонстрации некорректны')
            return False
        else:
            return True


    def standard_process(self):
        title, value = csv_reader('work_files/' + self.file_name)
        data = csv_filler(value, title, dict_for_exact_match, dict_for_items_match, dict_for_substring_match, self.salary_req)
        if len(data) == 0:
            print('Ничего не найдено')
            exit()
        if self.column_title_for_sort == '':
            pass  # пустой параметр сортировки = отсутствие сортировки
        else:
            eng_title_for_sort = rus_eng_title[self.column_title_for_sort]
            if self.column_title_for_sort in columns_for_lexi_sort:
                data.sort(key=cmp_to_key(lambda x, y: -1 if x[eng_title_for_sort] < y[eng_title_for_sort] else 1 if x[eng_title_for_sort] > y[eng_title_for_sort] else 0), reverse=self.reversed_flag)
            elif self.column_title_for_sort in columns_for_date_sort:
                date_format = "%Y-%m-%dT%H:%M:%S%z"
                data.sort(key=cmp_to_key(lambda x, y: -1 if dt.strptime(x[eng_title_for_sort], date_format) < dt.strptime(y[eng_title_for_sort], date_format) else 1 if dt.strptime(x[eng_title_for_sort], date_format) > dt.strptime(y[eng_title_for_sort], date_format) else 0), reverse=self.reversed_flag)
            elif self.column_title_for_sort in columns_for_line_count_sort:
                data.sort(key=cmp_to_key(lambda x, y: -1 if len(x[eng_title_for_sort].split('\n')) < len(y[eng_title_for_sort].split('\n')) else 1 if len(x[eng_title_for_sort].split('\n')) > len(y[eng_title_for_sort].split('\n')) else 0), reverse=self.reversed_flag)
            elif self.column_title_for_sort in columns_for_salary_sort:
                data.sort(key=cmp_to_key(lambda x, y: sort_dict_by_salary(x, y)), reverse=self.reversed_flag)
            elif self.column_title_for_sort in columns_for_work_experience_sort:
                data.sort(key=cmp_to_key(lambda x, y: -1 if work_experience_enum[x[eng_title_for_sort]] < work_experience_enum[y[eng_title_for_sort]] else 1 if work_experience_enum[x[eng_title_for_sort]] > work_experience_enum[y[eng_title_for_sort]] else 0), reverse=self.reversed_flag)
        form_data = [formatter(d, eng_rus_title, eng_rus_currency, eng_rus_work_experience) for d in data]

        print_vacancies_table(form_data, self.indexes, self.params)


def csv_reader(file_name):
    file_csv = csv.reader(open(file_name, encoding='utf_8_sig'))
    list_data = [x for x in file_csv]
    check_valid_file(list_data)
    titles = list_data[0]
    values = [x for x in list_data[1:] if x.count('') == 0 and len(x) == len(titles)]
    return titles, values


def check_valid_file(list_data):
    if len(list_data) == 1:
        print('Нет данных')
        exit()
    if len(list_data) == 0:
        print('Пустой файл')
        exit()


def csv_filler(reader, list_naming, exact_match_dict, items_dict, substring_dict, salary_req):
    list_of_dic = []
    for vac in reader:
        dic = {}
        row_ok = True
        for i in range(0, len(list_naming)):
            cell = clean_string(vac[i], True if i == 2 else False)
            if list_naming[i] == 'salary_from' and salary_req is not None:
                if salary_req < float(cell):
                    row_ok = False
                    break
            if list_naming[i] == 'salary_to' and salary_req is not None:
                if salary_req > float(cell):
                    row_ok = False
                    break
            if list_naming[i] in exact_match_dict.keys():
                if exact_match_dict[list_naming[i]] != cell:
                    row_ok = False
                    break
            if list_naming[i] in items_dict:
                my_items = items_dict[list_naming[i]]
                vac_items = cell.split('\n')
                good_match = True
                for m_i in my_items:
                    if m_i not in vac_items:
                        good_match = False
                        break
                if not good_match:
                    row_ok = False
                    break
            if list_naming[i] in substring_dict:
                if substring_dict[list_naming[i]] not in cell:
                    row_ok = False
                    break
            dic[list_naming[i]] = cell
        if row_ok:
            list_of_dic.append(dic)
    return list_of_dic


def print_vacancies_table(data_vacancies, indexes, parameters):
    table = create_table(data_vacancies)
    actual_range = make_range(indexes, data_vacancies)
    print(table.get_string(fields=['№', *parameters] if parameters.count('') == 0 else table.field_names,
                           start=actual_range[0],
                           end=actual_range[1]))


def make_range(indexes, data_vacancies):
    if len(indexes) == 0:
        return 0, len(data_vacancies)
    elif len(indexes) == 1:
        return indexes[0] - 1, len(data_vacancies)
    else:
        return indexes[0] - 1, indexes[1] - 1


def clean_string(string, is_skills):
    string = re.sub(r'<[^>]*>', '', string)
    string = ' '.join(string.split(' ')) if is_skills else ' '.join(string.split())
    return string


def formatter(row, dic_naming, eng_rus_currency, eng_rus_work_experience):
    salary_gross = {
        'True': 'Без вычета налогов',
        'False': 'С вычетом налогов'
    }
    table_col_title_pub_at = 'published_at'
    table_col_title_exp_id = 'experience_id'
    table_col_title_salary_info = 'Оклад'

    separator_by_thousand = lambda number: '{:,}'.format(int(float(number))).replace(',', ' ')
    row[table_col_title_salary_info] = f'{separator_by_thousand(row["salary_from"])} - {separator_by_thousand(row["salary_to"])} ' \
                   f'({eng_rus_currency[row["salary_currency"]]}) ({salary_gross[row["salary_gross"]]})'

    key_to_func = {
        'name' : None,
        'description' : None,
        'key_skills' : None,
        table_col_title_exp_id : (lambda exp_value: eng_rus_work_experience[exp_value]),
        'premium' : None,
        'employer_name': None,
        table_col_title_salary_info : None,
        'area_name': None,
        table_col_title_pub_at: (lambda pub_date_value: dt.strptime(pub_date_value, "%Y-%m-%dT%H:%M:%S%z").strftime(
            "%d.%m.%Y"))
    }
    result_dic = {}
    for key in key_to_func:
        value = row[key]
        if key_to_func[key] is not None:
            value = key_to_func[key](value)
        value = 'Да' if value == 'True' else 'Нет' if value == 'False' else value
        result_dic[dic_naming[key] if key in dic_naming.keys() else key] = value
    return result_dic


def format_for_table(vacancy):
    result_list = []
    for key, value in vacancy.items():
        formatted_str = value
        if len(formatted_str) > 100:
            formatted_str = value[:100] + '...'
        result_list.append(formatted_str)
    return result_list


def create_table(data):
    result_table = PrettyTable()
    result_table.field_names = ['№', *data[0].keys()]
    for i in range(len(data)):
        result_table.add_row([str(i + 1), *format_for_table(data[i])])
    result_table.align = 'l'
    result_table.hrules = 1
    result_table.max_width = 20
    return result_table


def sort_dict_by_salary(x, y):
    currency_to_rub = {
        "AZN": 35.68,
        "BYR": 23.91,
        "EUR": 59.90,
        "GEL": 21.74,
        "KGS": 0.76,
        "KZT": 0.13,
        "RUR": 1,
        "UAH": 1.64,
        "USD": 60.66,
        "UZS": 0.0055,
    }
    x_nom = x['salary_currency']
    y_nom = y['salary_currency']
    x_factor = currency_to_rub[x_nom]
    y_factor = currency_to_rub[y_nom]
    x_rub = (float(x['salary_from']) + float(x['salary_to'])) * x_factor / 2
    y_rub = (float(y['salary_from']) + float(y['salary_to'])) * y_factor / 2

    return -1 if x_rub < y_rub else 1 if x_rub > y_rub else 0


def all_are_pos(a):
    for x in a:
        if x < 0:
            return False
    return True


eng_rus_title = {
    'name': 'Название',
    'description': 'Описание',
    'key_skills': 'Навыки',
    'experience_id': 'Опыт работы',
    'premium': 'Премиум-вакансия',
    'employer_name': 'Компания',
    'salary_from': 'Нижняя граница вилки оклада',
    'salary_to': 'Верхняя граница вилки оклада',
    'salary_gross': 'Оклад указан до вычета налогов',
    'salary_currency': 'Идентификатор валюты оклада',
    'area_name': 'Название региона',
    'published_at': 'Дата публикации вакансии',
    'salary': 'Оклад'
}

eng_rus_currency = {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум"
    }

eng_rus_work_experience = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }

rus_eng_prem_vac = {
    'Да': 'True',
    'Нет': 'False'
}

work_experience_enum = {
    "noExperience": 0,
    "between1And3": 1,
    "between3And6": 2,
    "moreThan6": 3
}

columns_for_exact_match = {'Название', 'Описание', 'Компания', 'Идентификатор валюты оклада',
                           'Опыт работы', 'Название региона', 'Премиум-вакансия'}
columns_for_items_match = {'Навыки'}
columns_for_substring_match = {'Дата публикации вакансии'}
columns_for_range_match = {'Оклад'}
columns_for_prem_match = {'Премиум-вакансия'}

columns_for_lexi_sort = {'Название', 'Описание', 'Компания', 'Идентификатор валюты оклада', 'Название региона'}
columns_for_date_sort = {'Дата публикации вакансии'}
columns_for_line_count_sort = {'Навыки'}
columns_for_salary_sort = {'Оклад'}
columns_for_work_experience_sort = {'Опыт работы'}

dict_for_exact_match = {}
dict_for_items_match = {}
dict_for_substring_match = {}
salary_req = None

rus_eng_title = {}
rus_eng_currency = {}
rus_eng_work_experience = {}

def main_5_2():
    for key, value in eng_rus_title.items():
        rus_eng_title[value] = key

    for key, value in eng_rus_currency.items():
        rus_eng_currency[value] = key

    for key, value in eng_rus_work_experience.items():
        rus_eng_work_experience[value] = key

    user_input = InputConnect()
    user_input.read_user_input()

    if not user_input.full_check_error_not_found():
        exit()
    else:
        user_input.standard_process()
'''
vacancies_medium.csv
Опыт работы: От 3 до 6 лет
Опыт работы
Нет
1
Название, Оклад, Дата публикации вакансии, Навыки, Опыт работы
'''