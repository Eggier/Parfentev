import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit


class Report:
    def __init__(self, file_name, profession, area):
        self.file = pd.read_csv(file_name)
        self.profession = profession
        self.area = area

    def get_data_for_all_city(self):
        cities_count = self.file['area_name'].value_counts().to_dict()
        city_part = dict(filter(lambda x: x[-1] > 0.01, [(k, round(v / self.file.shape[0], 4))
                                                         for k, v in cities_count.items()]))
        dict_part_city = dict(list(city_part.items())[:10])

        city_vac = self.file.groupby(['area_name'])
        salary_by_city = {city: round(data['salary'].mean()) for city, data in city_vac if city in city_part}
        dict_sal_city = dict(sorted(salary_by_city.items(), key=lambda x: x[-1], reverse=True)[:10])
        return dict_sal_city, dict_part_city

    def get_data_for_one(self):
        data = self.file[
            (self.file['name'].str.contains(self.profession, case=False)) & (self.file['area_name'] == self.area)]
        data['year'] = data['published_at'].apply(lambda x: x[:4])
        years_vac = data.groupby(['year'])
        salary_prof = {}
        count = {}
        for year, data in years_vac:
            salary_prof[year] = round(data['salary'].mean())
            count[year] = data.shape[0]
        return salary_prof, count

    def make_pdf(self):
        salary_prof, count = self.get_data_for_one()
        dict_sal_city, dict_part_city = self.get_data_for_all_city()
        template = Environment(loader=FileSystemLoader('other')).get_template('template_upd.html')
        years_and_area = [[year, salary_prof[year], count[year]] for year in count]
        pdf_template = template.render({'name': self.profession, 'area': self.area, 'years_and_area': years_and_area,
                                        'salary_by_city': dict_sal_city.items(),
                                        'parts_city': dict_part_city.items()})
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report_city.pdf', configuration=config, options={"enable-local-file-access": ""})


file_name = input('Введите название файла: ')
profession = input('Введите название профессии: ').lower()
area = input('Введите название региона: ')
result = Report(file_name, profession, area)
result.make_pdf()