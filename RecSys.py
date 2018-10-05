import csv
import math
import json
import sys

# Загрузка данных из csv файла
def load_file(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)    #skip first row
        return [[item for item in row[1:]] for row in reader]

# Подсчет метрики сходства для двух кортежей
def sim(u, v) -> float:
    nominator = denominator1 = denominator2 = 0
    for i in range(len(v)):
        if u[i] != -1 and v[i] != -1:
            nominator += v[i] * u[i]
            denominator1 += v[i] ** 2
            denominator2 += u[i] ** 2
    return round(nominator / math.sqrt(denominator1) / math.sqrt(denominator2), 3)

# Подсчет среднего арифметического кортежа (исключая -1)
def avg(u) -> float:
    i = sum = 0
    for item in u:
        if item != -1:
            sum += item
            i += 1
    return round(sum / i, 3)

def RecSys(user_id = None, K = 7, min_mark = 3) -> dict:
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
                        if count < K:
                            count += 1
                        else: break
                if not (u+1 in mrks):
                    mrks[u+1] = {}
                mrks[u+1]["movie " + str(i+1)]= round(avgs[u] + nominator / denominator, 3)
    
        # Для расчета рекомендации - перебираем наиболее схожих пользователей с выбранным
        for v in sims[u].keys():
            if u+1 in rec: break
            # Перебираем фильмыы
            for i in range(len(data[u])):
                # Находим фильм который пользователь не видел (не стоит оценка)
                # а схожий пользователь видел дома в выходные и поставил оценку > min_mark
                if data[u][i] == -1 and context_place[v][i] == " h" and \
                (context_day[v][i] == " Thu" or context_day[v][i] == " Sun") and data[v][i] > min_mark:
                    rec[u+1] =  "movie " + str(i+1)
                    break
        
    if user_id:
        return {"marks": mrks.popitem()[1], "recomedtation": rec.popitem()[1] }
    else:
        return {"marks": mrks, "recomedtations": rec } 

if __name__ == '__main__':
    if len(sys.argv) == 1:
        res = RecSys()
        with open("all_results.json", "w") as f:
            f.write(json.dumps( res, indent=4))
    elif len(sys.argv) == 2 and int(sys.argv[1]) > 0:
        user_id = int(sys.argv[1])
        res = RecSys(user_id)
        with open("User_{}.json".format(user_id), "w") as f:
            f.write(json.dumps( res, indent=4))
    else:
        print("Error.")
