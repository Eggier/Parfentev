import pandas as pd
import threading


class DataSet:
    def __init__(self, file_name):
        self.data = pd.read_csv(file_name)

    def makePartsCsv(data: pd.DataFrame, file_name):
        data.to_csv(path_or_buf=file_name, index=False, encoding='utf-8-sig')

    def makeResult(self):
        for year in self.data['published_at'].apply(lambda x: x[:4]).unique():
            filter_parametr = self.data['published_at'].str.contains(year)
            filtered_data = self.data[filter_parametr]
            t = threading.Thread(target=makePartsCsv, args=(filtered_data, f'split_files/vacancies_by_{year}.csv'))
            t.start()



data = DataSet('vacancies_by_year.csv')
data.makeResult()