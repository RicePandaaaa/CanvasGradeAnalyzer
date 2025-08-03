import csv

input_file = "sample_data.csv"

with open(input_file, "r") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
        break