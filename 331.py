import pandas as pd
import xmltodict
import grequests


class AnaliticsCurr:
    def __init__(self, data):
        self.data = data[pd.notnull(data['salary_currency'])]

    def get_count_currency(self):
        return self.data['salary_currency'].value_counts().to_dict()

    def get_frequrency(self):
        amount_data = len(self.data.index)
        freq_currency_dict = {currency: amount / amount_data for currency, amount in self.get_count_currency().items()}
        return freq_currency_dict


    def d_m_y_date(self, date):
        return f'{date[8:]}/{date[5:7]}/{date[:4]}'

    def change_date(self, date):
        return f'{date[6:]}-{date[3:5]}'

    def get_popular_currency(self):
        list_curr = []
        for k, v in self.get_count_currency().items():
            if v > 5000 and k != 'RUR':
                list_curr.append(k)
        return list_curr

    def get_dates(self):
        years_series = pd.to_datetime(self.data['published_at'].apply(lambda x: x[:10]))
        dad, son = self.d_m_y_date(str(years_series.min())[:10]), self.d_m_y_date(str(years_series.max())[:10])
        return pd.date_range(start=dad, end=son, freq='M').strftime('%d/%m/%Y').tolist()


    def make_res_dict(self):
        list_currency = self.get_popular_currency()
        dict_result = {'date': []}
        dict_result.update({currency: [] for currency in list_currency})
        for request in grequests.map(grequests.get(url) for url in self.requests()):
            data = xmltodict.parse(request.text)['ValCurs']
            dict_result['date'] = dict_result['date'] + [self.change_date(data['@Date'])]
            currency_value = {currency: 0 for currency in list_currency}
            for currency in data['Valute']:
                if currency['CharCode'] in list_currency:
                    currency_value[currency['CharCode']] = round(float(currency['Value'].replace(',', '.')) /
                                                                 float(currency['Nominal']), 6)
            for k, v in currency_value.items():
                dict_result[k] = dict_result[k] + [v]
        return dict_result

    def requests(self):
        list_curr = [f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date}' for date in self.get_dates()]
        return list_curr

    def make_csv(self):
        pd.DataFrame(self.make_res_dict()).to_csv(path_or_buf='currency_from_2003_to_2022.csv', index=False, encoding='utf-8-sig')


file_name = 'vacancies_dif_currencies.csv'
currency_count = AnaliticsCurr(pd.read_csv(file_name))
currency_count.make_csv()