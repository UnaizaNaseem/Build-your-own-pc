import csv
file_name="Products-Data-14-08-2026.csv"

with open(file_name, "r", encoding="utf-8-sig") as file:
    reader=csv.DictReader(file)
    products = list(reader)

print("Total products:", len(products))

print("\nColumns:")
for column in reader.fieldnames:
    print("-", column)

print("\nFirst product:")
for key, value in products[0].items():
    print(f"{key}: {value}")
