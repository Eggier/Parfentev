import pandas as pd


class ConvertVacancy:
    def __init__(self, file_name, convert_file):
        self.file_name = pd.read_csv(file_name)
        self.convert_file = pd.read_csv(convert_file)

    def get_converted_currency_salary(self, currency, date):
        try:
            res_conv = self.convert_file[self.convert_file['date'] == date][currency].values
        except:
            return None
        if len(res_conv) > 0:
            return res_conv[0]
        else:
            return None

    def get_salary_row(self, row):
        salary_from = row['salary_from']
        salary_to = row['salary_to']
        salary_currency = row['salary_currency']
        date = row['published_at'][:7]
        if pd.isnull(salary_currency) or (pd.isnull(salary_to) and pd.isnull(salary_from)):
            return None
        if salary_currency == 'RUR':
            conv = 1
        else:
            conv = self.get_converted_currency_salary(salary_currency, date)
        if not conv:
            return None
        salary_from = 0 if pd.isnull(salary_from) else salary_from
        salary_to = 0 if pd.isnull(salary_to) else salary_to
        average_salary = 0
        if salary_to == 0 or salary_from == 0:
            average_salary = max(salary_to, salary_from)
        else:
            average_salary = 0.5 * (salary_to + salary_from)
        salary = round(average_salary * conv, 0)
        return salary

    def make_csv_100(self):
        data = self.file_name.copy()
        data = data.head(100)
        data['salary'] = data.apply(lambda x: self.get_salary_row(x), axis=1)
        data[['name', 'salary', 'area_name', 'published_at']].to_csv('vacancies_with_converted_currency.csv', index=False)


file_name = 'vacancies_dif_currencies.csv'
convert_file = 'currency_from_2003_to_2022.csv'
result = ConvertVacancy(file_name, convert_file)
result.make_csv_100()