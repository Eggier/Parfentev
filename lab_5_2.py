import datetime
from prettytable import PrettyTable
from functools import cmp_to_key
import csv
import re
import os.path
import cProfile
import pstats



class Vacancy:
    """
    Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        description (str): Описание вакансии
        key_skills (str): Навыки
        experience_id (str): Опыт работы
        premium (str): Премиум вакансия
        employer_name (str): Компания
        salary (Salary): Зарплата
        area_name (str): Город
        published_at (datetime): Дата публикации вакансии
    """
    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name, published_at):
        """
        Инициализирует объект Vacancy

        Args:
            name (str): Название вакансии
            description (str): Описание вакансии
            key_skills (str): Навыки
            experience_id (str): Опыт работы
            premium (str): Премиум вакансия
            employer_name (str): Компания
            salary (Salary): Зарплата
            area_name (str): Город
            published_at (datetime.pyi): Дата публикации вакансии
        """
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at

    def __str__(self):
        return f'{self.name} | {self.description} | {self.key_skills} | {self.experience_id} | {self.premium} | {self.employer_name} | {self.salary} | {self.area_name} | {self.published_at} \n'


class Salary:
    """
    Класс для представления зарплаты

    Attributes:
       salary_from (str): Нижняя граница вилки оклада
       salary_to (str): Верхняя граница вилки оклада
       salary_gross (bool): До или после вычета налогов
       salary_currency (str): Валюта оклада
    """
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """
        Инициализирует объект Salary
        Args:
           salary_from (str): Нижняя граница вилки оклада
            salary_to (str): Верхняя граница вилки оклада
            salary_gross (str): До или после вычета налогов
            salary_currency (str): Валюта оклада
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def __str__(self):
        salary_gross = {
            'True': 'Без вычета налогов',
            'False': 'С вычетом налогов'
        }

        separator_by_thousand = lambda number: '{:,}'.format(int(float(number))).replace(',', ' ')
        salary_info = f'{separator_by_thousand(self.salary_from)} - {separator_by_thousand(self.salary_to)} ' \
                      f'({eng_rus_currency[self.salary_currency]}) ({salary_gross[self.salary_gross]})'
        return salary_info


class DataSet:
    """
    Класс для предствления иформации о вакансиях

    Attributes:

    """
    def __init__(self, list_of_vac_str):
        self.list_of_vac_str = list_of_vac_str

    def refresh(self, new_list_of_vac_str):
        self.list_of_vac_str = new_list_of_vac_str

    def generate_vacs_from_strs(self, list_naming, exact_match_dict, items_dict, substring_dict, salary_req):
        """
        Создает список отфильтрованных вакансий
        Args:
            #reader (list): Список вакансий в виде списка строк
            list_naming (list): Список заголовков
            exact_match_dict (dict): Словарь, чтобы сравнивать вакансии значения по строке
            items_dict (dict): Словарь, чтобы обрабатывать список навыков
            substring_dict (dict): Словарь, чтобы обрабатывать дату
            salary_req (float or None): Отвечает за обработку параметра зарплаты

        Returns:
            list: Список отфильтрованных вакансий
        """
        list_of_vac = []
        for vac in self.list_of_vac_str:
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
                sal = Salary(dic['salary_from'], dic['salary_to'], dic['salary_gross'], dic['salary_currency'])
                list_of_vac.append(Vacancy(dic['name'], dic['description'], dic['key_skills'], dic['experience_id'],
                                           dic['premium'], dic['employer_name'], sal, dic['area_name'],
                                           datetime.datetime.strptime(dic['published_at'], '%Y-%m-%dT%H:%M:%S%z')))
        return list_of_vac


def profile(func):
    """Decorator for run function profile"""
    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result
    return wrapper


class InputConnect:
    """
    Класс для представления информации пользовательского ввода

    Attributes:
        file_name (str): Названия csv файла с исходными данными
        request_param (str): Параметр фильтрации
        column_title_for_sort (str): Параметр сортировки
        reversed_sort (str): Порядок сортировки
        index_parts (str): Диапозон вывода
        params_input (str): Требуемые столбцы
        error_msg (str): Сообщение об ошибке
        salary_req (float): Отвечает за параметр зарплаты
        request_param_ok (bool): Отвечает за корректность введенных параметров сортировки
        reversed_flag (bool): Отвечает за порядок сортировки
        indexes (list): Диапозон вывода в виде массива из двух чисел
        params (list): Список столбцов вывода
        indexes_ok (bool): Отвечает за корректность диапозона
        bad_param_found (bool): Отвечает за корректность введенных столбцов
        file_name_ok (bool): Отвечает за корректность имени файла
    """
    columns_for_exact_match = {'Название', 'Описание', 'Компания', 'Идентификатор валюты оклада',
                               'Опыт работы', 'Название региона', 'Премиум-вакансия'}
    columns_for_items_match = {'Навыки'}
    columns_for_substring_match = {'Дата публикации вакансии'}

    dict_for_exact_match = {}
    dict_for_items_match = {}
    dict_for_substring_match = {}

    def __init__(self):
        """
        Инициализирует объект InputConnect
        """
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

        if len(rus_eng_title) == 0:
            for key, value in eng_rus_title.items():
                rus_eng_title[value] = key

            for key, value in eng_rus_currency.items():
                rus_eng_currency[value] = key

            for key, value in eng_rus_work_experience.items():
                rus_eng_work_experience[value] = key

    def read_user_input(self):
        """
        Осуществляет считывание пользовательского ввода и уставку значений атрибутам
        """
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
        """
        Устонавливает значения в словари, используемые для фильтрации
        """
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
                    if request_data[0] in InputConnect.columns_for_exact_match:
                        req_value = rus_eng_currency[request_data[1]] if request_data[1] in rus_eng_currency else request_data[1]
                        req_value = rus_eng_work_experience[request_data[1]] if request_data[1] in rus_eng_work_experience else req_value
                        req_value = rus_eng_prem_vac[request_data[1]] if request_data[1] in rus_eng_prem_vac else req_value
                        InputConnect.dict_for_exact_match[rus_eng_title[request_data[0]]] = req_value
                    elif request_data[0] in InputConnect.columns_for_items_match:
                        InputConnect.dict_for_items_match[rus_eng_title[request_data[0]]] = request_data[1].split(', ')
                    elif request_data[0] in InputConnect.columns_for_substring_match:
                        date_parts = request_data[1].split('.')
                        if len(date_parts) != 3:
                            print('Некорректный формат даты')
                        else:
                            date_str = date_parts[2] + '-' + date_parts[1] + '-' + date_parts[0] + 'T'
                            InputConnect.dict_for_substring_match[rus_eng_title[request_data[0]]] = date_str
                    elif request_data[0] in columns_for_range_match:
                        self.salary_req = float(request_data[1])

    def full_check_error_not_found(self):
        """
        Осуществляет проверку всех возможных ошибок ввода
        Returns:
            bool: успех/неудача проверки
        """
        if not self.file_name_ok:
            print('Название файла некорректно или файл не найден')
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

    @staticmethod
    def compare_by_exp(x, y):
        """
        Осуществляет сранение вакансий по опыту
        Args:
            x (Vacancy): Первая вакансия
            y (Vacancy): Вторая вакансия
        Returns:
            int: -1 если опыт первой меньше, 1 если опыт первой больше, 0 если опыт первой равен опыту второй
        """
        return -1 if work_experience_enum[x.experience_id] < work_experience_enum[y.experience_id] else 1 if \
        work_experience_enum[x.experience_id] > work_experience_enum[y.experience_id] else 0

    @staticmethod
    def compare_by_sal(x, y):
        """
        Осуществляет сранение вакансий по зарплате
        Args:
            x (Vacancy): Первая вакансия
            y (Vacancy): Вторая вакансия
        Returns:
            int: -1 если зарплата первой меньше, 1 если зарплата первой больше, 0 если зарплата первой равен зарплате второй
        """
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
        x_nom = x.salary.salary_currency
        y_nom = y.salary.salary_currency
        x_factor = currency_to_rub[x_nom]
        y_factor = currency_to_rub[y_nom]
        x_rub = (float(x.salary.salary_from) + float(x.salary.salary_to)) * x_factor / 2
        y_rub = (float(y.salary.salary_from) + float(y.salary.salary_to)) * y_factor / 2

        return -1 if x_rub < y_rub else 1 if x_rub > y_rub else 0

    @profile
    def standard_process(self):
        """
        Осуществляет формирование списка вакансий и их отправку на печать
        """
        title, value = csv_reader('work_files/' + self.file_name)
        data_set = DataSet(value)
        data = data_set.generate_vacs_from_strs(title, InputConnect.dict_for_exact_match, InputConnect.dict_for_items_match, InputConnect.dict_for_substring_match, self.salary_req)
        if len(data) == 0:
            print('Ничего не найдено')
            exit()
        if self.column_title_for_sort == '':
            pass  # пустой параметр сортировки = отсутствие сортировки
        else:
            eng_title_for_sort = rus_eng_title[self.column_title_for_sort]
            if self.column_title_for_sort in columns_for_work_experience_sort:
                data.sort(key=cmp_to_key(InputConnect.compare_by_exp), reverse=self.reversed_flag)
            elif eng_title_for_sort == 'name':
                data.sort(key=lambda x: x.name, reverse=self.reversed_flag)
            elif eng_title_for_sort == 'description':
                data.sort(key=lambda x: x.description, reverse=self.reversed_flag)
            elif eng_title_for_sort == 'employer_name':
                data.sort(key=lambda x: x.employer_name, reverse=self.reversed_flag)
            elif eng_title_for_sort == 'salary_currency':
                data.sort(key=lambda x: x.salary.salary_currency, reverse=self.reversed_flag)
            elif eng_title_for_sort == 'key_skills':
                data.sort(key=lambda x: x.key_skills.count('\n'), reverse=self.reversed_flag)
            elif eng_title_for_sort == 'area_name':
                data.sort(key=lambda x: x.area_name, reverse=self.reversed_flag)
            elif eng_title_for_sort == 'salary':
                data.sort(key=cmp_to_key(InputConnect.compare_by_sal), reverse=self.reversed_flag)
            elif eng_title_for_sort == 'published_at':
                data.sort(key=lambda x: x.published_at, reverse=self.reversed_flag)
            else:
                pass

        form_data = [formatter(d, eng_rus_work_experience) for d in data]

        print_vacancies_table(form_data, self.indexes, self.params)


def csv_reader(file_name):
    """
    Осуществляет чтение csv файла с данными о вакансиях
    Args:
        file_name (str): Название файла

    Returns:
        list: Заголовки таблицы с вакансиями
        list: Список вакансий
    """
    file_csv = csv.reader(open(file_name, encoding='utf_8_sig'))
    list_data = [x for x in file_csv]
    check_valid_file(list_data)
    titles = list_data[0]
    values = [x for x in list_data[1:] if x.count('') == 0 and len(x) == len(titles)]
    return titles, values


def check_valid_file(list_data):
    """
    Проверяет корректность файла
    Args:
        list_data (list): Список вакансий
    """
    if len(list_data) == 1:
        print('Нет данных')
        exit()
    if len(list_data) == 0:
        print('Пустой файл')
        exit()


def print_vacancies_table(data_vacancies, indexes, parameters):
    """
    Печатает информацию о вакансиях в виде таблицы
    Args:
        data_vacancies (list): Информация о вакансиях
        indexes (list): Диапозон вывода
        parameters (list): Требуемые столбцы
    """
    table = create_table(data_vacancies)
    actual_range = make_range(indexes, data_vacancies)
    print(table.get_string(fields=['№', *parameters] if parameters.count('') == 0 else table.field_names,
                           start=actual_range[0],
                           end=actual_range[1]))


def make_range(indexes, data_vacancies):
    """
    Создает корректный диапозон
    Args:
        indexes (list): Диапозон вывода
        data_vacancies (list): Информация о вакансиях

    Returns:
        int: корректный диапозон вывода
    """
    if len(indexes) == 0:
        return 0, len(data_vacancies)
    elif len(indexes) == 1:
        return indexes[0] - 1, len(data_vacancies)
    else:
        return indexes[0] - 1, indexes[1] - 1


def clean_string(string, is_skills):
    """
    Очищает строку с информацией о вакансии от лишних пробелов и html тегов, превращает список в единую строку
    Args:
        string (str): Значение одного из полей вакансии
        is_skills (bool): Флаг, сигнализирущий о том, что передана строка с навыками

    Returns:
        str: "Чистая" строка

    >>> clean_string('<p><strong>Ключевые требования:</strong>', False)
    'Ключевые требования:'
    >>> clean_string('<p><strong>Responsibilities:</strong><br />', False)
    'Responsibilities:'
    >>> clean_string('<li>Запуск в работу и ПГР для нового производственного оборудования;</li>', False)
    'Запуск в работу и ПГР для нового производственного оборудования;'
    """
    string = re.sub(r'<[^>]*>', '', string)
    string = ' '.join(string.split(' ')) if is_skills else ' '.join(string.split())
    return string


# def convert_datetime_to_dmy(dt):
#     return dt.strftime('%d.%m.%Y')


def convert_datetime_to_dmy_v2(dt: datetime.datetime):
    return f'{dt.day:02}.{dt.month:02}.{dt.year}'


# days = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14',
#         '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']
#
# months = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


# def convert_datetime_to_dmy_v3(dt: datetime.datetime):
#     return days[dt.day] + '.' + months[dt.month] + '.' + str(dt.year)


def formatter(vac, eng_rus_work_experience):
    """
    Форматирует информацию о вакансии, переводит все значения на русский язык
    Args:
        vac (Vacancy):
        eng_rus_work_experience (dict): Словарь с анг/рус опытом работы

    Returns:
        dict: отформатированную информацию о вакансии
    """

    result_dic = {}
    result_dic[eng_rus_title['name']] = vac.name
    result_dic[eng_rus_title['description']] = vac.description
    result_dic[eng_rus_title['key_skills']] = vac.key_skills
    result_dic[eng_rus_title['experience_id']] = eng_rus_work_experience[vac.experience_id]
    result_dic[eng_rus_title['premium']] = 'Да' if vac.premium == 'True' else 'Нет'
    result_dic[eng_rus_title['employer_name']] = vac.employer_name
    result_dic['Оклад'] = str(vac.salary)
    result_dic[eng_rus_title['area_name']] = vac.area_name
    result_dic[eng_rus_title['published_at']] = convert_datetime_to_dmy_v2(vac.published_at)
    return result_dic


def format_for_table(vacancy):
    """
    Форматирует данные о вакансии, чтобы они корректно отображались в таблице
    Args:
        vacancy (dict): словарь с информацией  о вакансии

    Returns:
        list: отформатированный список значений вакансии
    """
    result_list = []
    for key, value in vacancy.items():
        formatted_str = str(value)
        if len(formatted_str) > 100:
            formatted_str = value[:100] + '...'
        result_list.append(formatted_str)
    return result_list


def create_table(data):
    """
    Создает таблицу для печати
    Args:
        data (list): Список словарей с информацией о вакансиях

    Returns:
       PrettyTable: результирующая таблица
    """
    result_table = PrettyTable()
    result_table.field_names = ['№', *data[0].keys()]
    for i in range(len(data)):
        result_table.add_row([str(i + 1), *format_for_table(data[i])])
    result_table.align = 'l'
    result_table.hrules = 1
    result_table.max_width = 20
    return result_table


def all_are_pos(user_range):
    """
    Проверяет, что пользователь указал не отрицательный диапозон вывода
    Args:
        user_range (list): диапозон вывода

    Returns:
        bool: False если указан отрицательный диапозон, иначе True

    >>> all_are_pos([-1, 5])
    False
    >>> all_are_pos([2, 15])
    True
    """
    for x in user_range:
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

columns_for_range_match = {'Оклад'}
columns_for_prem_match = {'Премиум-вакансия'}

columns_for_lexi_sort = {'Название', 'Описание', 'Компания', 'Идентификатор валюты оклада', 'Название региона'}
columns_for_date_sort = {'Дата публикации вакансии'}
columns_for_line_count_sort = {'Навыки'}
columns_for_salary_sort = {'Оклад'}
columns_for_work_experience_sort = {'Опыт работы'}

rus_eng_title = {}
rus_eng_currency = {}
rus_eng_work_experience = {}



def main_5_2():
    """
    Запускает работу программы, если в пользовательском вводе не обнаружено ошибок
    """
    user_input = InputConnect()
    user_input.read_user_input()

    if not user_input.full_check_error_not_found():
        exit()
    else:
        user_input.standard_process()


if __name__ == '__main__':
    main_5_2()
    p = pstats.Stats('standard_process.prof')
    p.sort_stats('calls').print_stats()


# test input
# vacancies_medium.csv
# Оклад: 100000
# Оклад
# Нет
# 1
# Название, Навыки, Опыт работы, Компания, Оклад
