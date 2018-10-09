from csv import reader
from math import sqrt
from json import dumps
from sys import argv

def load_file(filename) -> list:
    """
    Чтение csv файла в двухмерный список
    """
    with open(filename, newline='') as csvfile:
        rdr = reader(csvfile, delimiter=',', quotechar='|')
        next(rdr)
        return [[item for item in row[1:]] for row in rdr]

def sim(u, v) -> float:
    """
    Подсчет метрики сходства для двух кортежей
    """
    nominator = denominator1 = denominator2 = 0
    for i in range(len(v)):
        if u[i] != -1 and v[i] != -1:
            nominator += v[i] * u[i]
            denominator1 += v[i] ** 2
            denominator2 += u[i] ** 2
    return nominator / sqrt(denominator1) / sqrt(denominator2)

def avg(u) -> float:
    """
    Подсчет среднего арифметического кортежа (исключая -1)
    """
    i = sum = 0
    for item in u:
        if item != -1:
            sum += item
            i += 1
    return sum / i

def RecSys(user_id = None, K = 7) -> dict:
    """
    Подсчет всех оценок и рекомендаций, или при указании user_id только для данного пользователя
    """
    # Чтение данных из файлов
    context_day = load_file("context_day.csv")
    context_place = load_file("context_place.csv")
    data = [[int(item) for item in user] for user in load_file("data.csv")]
    # Подсчет всех средних оценок
    avgs = [avg(row) for row in data]
    # Подсчет всех комбинаций метрик сходства и их сортировка по сходству
    sims = {i: { j: sim(data[j], data[i]) for j in range(len(data)) if i != j} for i in range(len(data))}   #TODO: оптимизировать повторные вычисления
    for i in range(len(data)):
        sims[i] = sorted(sims[i].items(), key = lambda x: x[1], reverse = True)
        sims[i] = { i: j for i, j in sims[i]}

    mrks = {}
    rec = {}
    rng = range(len(data))
    if user_id: rng = range(user_id-1, user_id)
    # Перебираем пользователей
    for u in rng:
        # Для расчета оценкок - перебираем оценки за фильмы
        for i in range(len(data[u])):
            # Если оценка не указана считаем ее
            if data[u][i] == -1:
                nominator = denominator = count = 0
                # Перебираем наиболее схожих пользователей с выбранным
                for v in sims[u].keys():
                    # Оценка за этот фильм у схожего пользователя должна стоять
                    if data[v][i] != -1:
                        nominator += sims[v][u] * (data[v][i] - avgs[v])
                        denominator += abs(sims[v][u])
                        if count < K-1:
                            count += 1
                        else: 
                            break
                if not (u+1 in mrks):
                    mrks[u+1] = {}
                mrks[u+1]["movie " + str(i+1)] = round(avgs[u] + nominator / denominator, 3)
    
        # Для расчета рекомендации - перебираем наиболее схожих пользователей с выбранным
        for v in sims[u].keys():
            if u+1 in rec: break
            # Перебираем фильмыы
            for i in range(len(data[u])):
                # Находим фильм который пользователь не видел (не стоит оценка)
                # а схожий пользователь видел дома в выходные и поставил оценку > чем в среднем 
                if data[u][i] == -1 and context_place[v][i] == " h" and \
                (context_day[v][i] == " Thu" or context_day[v][i] == " Sun") and data[v][i] > avgs[v]:
                    rec[u+1] =  "movie " + str(i+1)
                    break
        
    if user_id:
        mrks = mrks.popitem()[1]
        rec = rec.popitem()[1]
        return { "user": user_id,  "1": mrks, "2": { rec: mrks[rec] } }
    else: 
        return { "marks": mrks, "recomedtations": rec } 

if __name__ == '__main__':
    user_id = None if len(argv) == 1 else int(argv[1])
    res = RecSys(user_id)
    print(dumps( res, indent=4))
