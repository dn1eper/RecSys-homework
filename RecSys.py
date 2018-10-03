import csv
import math
import json
import sys

# Загрузка данных из csv файла
def load_file_int(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(reader)    #skip first row
        return [[int(item) for item in row[1:]] for row in reader]

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

# Подсчет всех комбинаций метрик сходства и их сортировка по сходству
def sim_all(data) -> dict:
    sims = {i: { j: sim(data[j], data[i]) for j in range(len(data)) if i != j} for i in range(len(data))}   #TODO: оптимизировать повторные вычисления
    for i in range(len(data)):
        sims[i] = sorted(sims[i].items(), key = lambda x: x[1], reverse = True)
        sims[i] = { i: j for i, j in sims[i]}
    return sims

# Подсчет среднего арифметического кортежа (исключая -1)
def avg(u) -> float:
    i = sum = 0
    for item in u:
        if item != -1:
            sum += item
            i += 1
    return round(sum / i, 3)

# Вычисление недостающих оценок подхом user-based коллаборативной фильтрации
def marks(user_id = None, K = 7) -> dict:
    res = {}
    data = load_file_int("data.csv")

    # Подсчет всех средних оценок
    avgs = [avg(row) for row in data]
    # Подсчет всех метрик сходства
    sims = sim_all(data)
    
    # Перебираем пользователей
    for u in range(len(data)):
        # Перебираем оценки за фильмы
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

                if not (u+1 in res):
                    res[u+1] = {}
                res[u+1]["movie " + str(i+1)]= round(avgs[u] + nominator / denominator, 3)
    if user_id: #TODO: убрать лишние вычисления если нужны оценки для одного пользователя
        return { user_id: res[int(user_id)]}
    else: return res

def recomendation(user_id = None) -> dict:
    res = {}
    data = load_file_int("data.csv")
    context_day = load_file("context_day.csv")
    context_place = load_file("context_place.csv")
    
    # Подсчет всех метрик сходства
    sims = sim_all(data)

    # Перебираем пользователей
    for u in range(len(data)):
        # Перебираем наиболее схожих пользователей с выбранным
        for v in sims[u].keys():
            if u+1 in res:
                break
            # Перебираем фильмы
            for i in range(len(data[u])):
                # Находим фильм который:
                # - пользователь не видел (не стоит оценка)
                # - схожий пользователь видел дома в выходные и поставил оценку > 2
                if data[u][i] == -1 and context_place[v][i] == " h" and \
                (context_day[v][i] == " Thu" or context_day[v][i] == " Sun") and data[v][i] > 2:
                    res[u+1] =  "movie " + str(i+1)
                    break

    if user_id: #TODO: убрать лишние вычисления если нужна рекомендация для одного пользователя
        return { user_id: res[int(user_id)]}
    else: return res

def print_help():
    print("""usage: 
        marks [user_id] 
        recomendation [user_id]""")
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) > 1 and len(sys.argv) < 4:
        user_id = None
        if len(sys.argv) == 3: 
            user_id = sys.argv[2]

        if 'marks' == sys.argv[1]:
            jsn = json.dumps(marks(user_id), indent=4)
            with open("marks.json", "w") as f:
                f.write(jsn)
            
        elif 'recomendation' == sys.argv[1]:
            jsn = json.dumps(recomendation(user_id), indent=4)
            with open("recomendation.json", "w") as f:
                f.write(jsn)

        else: print_help()
    else: print_help()
    


