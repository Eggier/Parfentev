import cProfile
import concurrent.futures
import pandas as pd
import os


class DataSet:
    """Класс DataSet работает с информацией из csv-файлов
	Attributes:
		directory (str): Название директории с csv-файлами (чанками)
		profession (str): Название выбранной профессии
		raw_data list[tuple]: Список кортежей с необработанными данными
	"""

    def __init__(self, directory, profession):
        """Инициализирует объект DataSet
		Attributes:
			directory (str): Название директории с csv-файлами (чанками)
			profession (str): Название выбранной профессии
		"""
        self.directory = directory
        self.profession = profession
        self.raw_data = []

    def get_analytics(self):
        """Достает все файлы из директории, анализирует и складывает в поле raw_data"""
        with concurrent.futures.ProcessPoolExecutor() as ex:
            for res_chunk in ex.map(self.get_data_from_chunk, os.listdir(self.directory)):
                self.raw_data.append(res_chunk)

        def get_converted_data(self):
            """Берет сырые данные из поля analyzed_data и разбивает их на словари, выводит их на экран
    		В словаре ключ - год, значение параметр аналитики (средняя зарплата, количество вакансий и т.д.)"""
            dct_years_salary, dct_years_count, dct_years_salary_filt, dct_years_count_filt = {}, {}, {}, {}
            for year, average_salary, count_by_year, average_salary_filt, count_by_year_filt in self.raw_data:
                dct_years_salary[year] = average_salary
                dct_years_count[year] = count_by_year
                dct_years_salary_filt[year] = average_salary_filt
                dct_years_count_filt[year] = count_by_year_filt
            print(f'Динамика уровня зарплат по годам: {dct_years_salary}')
            print(f'Динамика количества вакансий по годам: {dct_years_count}')
            print(f'Динамика уровня зарплат по годам для выбранной профессии: {dct_years_salary_filt}')
            print(f'Динамика количества вакансий по годам для выбранной профессии: {dct_years_count_filt}')


    def get_data_from_chunk(self, file_name):
        """Возвращает параметры аналитики одного файла
		Attributes:
			file_name (str): Название csv-файла
		Returns:
			year (int): Год публикации вакансии
			average_salary (int): Средняя зарплата
			count (int): Количество вакансий
			average_salary_profession (int): Cредняя зарплата для выбранной профессии
			count_profession (int): Количество вакансий для выбранной профессии
		"""
        data = pd.read_csv(f'{self.directory}/{file_name}')
        vac = data['name'].str.contains(self.profession)
        vacancy_data = data[vac]
        average_salary = round(self.get_average(data))
        average_salary_profession = round(self.get_average(vacancy_data))
        count = data.shape[0]
        count_profession = vacancy_data.shape[0]
        year = data['published_at'].apply(lambda x: x[:4]).unique()[0]
        return year, average_salary, count, average_salary_profession, count_profession

    def get_average(self, data):
        return data.apply(lambda x: (x['salary_from'] + x['salary_to']) * 0.5, axis=1).mean()


if __name__ == '__main__':
    directory = 'split_files'
    profession = 'Аналитик'
    profile = cProfile.Profile()
    profile.enable()
    data_analitics = DataSet(directory, profession)
    data_analitics.get_analytics()
    data_analitics.get_converted_data()
    profile.disable()
    profile.print_stats(1)