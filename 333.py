import pandas as pd
import grequests


class RequestsHH:
    def __init__(self, head):
        self.head = head

    @staticmethod
    def makeRequests():
        urls = []
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T00:00:00&date_to=2022-12-12T08:00:00'
            for page in range(20)]
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T08:00:00&date_to=2022-12-12T16:00:00'
            for page in range(20)]
        urls += [
            f'https://api.hh.ru/vacancies?specialization=1&per_page=100&page={page}&date_from=2022-12-12T16:00:00&date_to=2022-12-13T00:00:00'
            for page in range(20)]
        requests = (grequests.get(url) for url in urls)
        return requests

    def make_csv(self):
        vac_list = []
        for req in grequests.map(self.makeRequests()):
            for vac in req.json()['items']:
                vac_list.append(self.parse_vac_for_csv(vac))
        pd.DataFrame(data=vac_list, columns=self.head).to_csv('vacancies_from_hh.csv', index=False)

    @staticmethod
    def parse_vac_for_csv(vac):
        name, area_name, published_at, salary = vac['name'], vac['area']['name'], vac['published_at'], vac['salary']
        salary_from = salary['from'] if salary else None
        salary_to = salary['to'] if salary else None
        salary_currency = salary['currency'] if salary else None
        return name, salary_from, salary_to, salary_currency, area_name, published_at



head = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
result = RequestsHH(head)
result.make_csv()