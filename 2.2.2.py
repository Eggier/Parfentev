from lab_5_2 import main_5_2
from lab_2_1_3 import main_2_1_3


s = input()
if s == 'Вакансии':
    main_5_2()
elif s == 'Статистика':
    main_2_1_3()
else:
    print('Некорректный ввод, попробуйте ещё раз')