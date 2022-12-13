import csv
import numpy as np

filename = 'input_example.csv'

def unique(list):
    x = np.array(list)
    indexes = np.unique(x, return_index=True)[1]
    return [x[index] for index in sorted(indexes)]

clusters = []
keywords = []
questions = []
with open(filename, newline='') as csvfile:
    data = csv.reader(csvfile)
    for row in data:
        clusters.append(row[0])
        keywords.append(row[1])
        questions.append(row[2])

clusters_unique = unique(clusters)
keywords_unique = unique(keywords)

data_new = []

for cluster in clusters_unique:
    data_new.append([cluster, cluster])
    with open(filename, newline='') as csvfile:
        data = csv.reader(csvfile)
        for row in data:
            if row[0] == cluster:
                if [cluster, row[1]] not in data_new:
                    data_new.append([cluster, row[1]])
                    current_keyword = row[1]

                    with open(filename, newline='') as csvfile:
                        data = csv.reader(csvfile)
                        for row in data:
                            if row[1] == current_keyword:
                                data_new.append([cluster, row[2]])
                            else:
                                continue
                else:
                    continue

with open('result.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(data_new)

print("Done")