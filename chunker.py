import csv


def creat_csv_chunks(file_name):
    """
    Разбивает большой csv файл на несколько csv файлов меньшего размера
    Args:
        file_name (str): Название файла, который нужно разделить
    """
    data = {}
    titles = []

    with open(f'work_files/{file_name}', encoding="utf-8-sig") as File:
        reader = csv.reader(File)
        k = 0
        count_years = 2007
        for row in reader:
            if k == 0:
                titles = row
                k += 1
                continue
            year = row[len(row) - 1][0:4]
            if int(year) == count_years:
                if data.keys().__contains__(year):
                    data[year].append(row)
                else:
                    data[year] = [row]
            else:
                count_years += 1
                data[str(count_years)] = [row]

    for k in data.keys():
        my_file = open(f'csv_chunks/{k}_year.csv', 'w', encoding="utf-8-sig")
        with my_file:
            writer = csv.writer(my_file, delimiter=",", lineterminator="\r")
            writer.writerow(titles)
            writer.writerows(data[k])


file_name = input('Введите название файла: ')
creat_csv_chunks(file_name)
