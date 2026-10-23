import requests
import csv
import numpy as np
import matplotlib.pyplot as plt

def infodata():
    indicator = "FP.CPI.TOTL.ZG"
    countries = {"UKR": "Ukraine", "POL": "Poland"}
    all_data = []

    for code, name in countries.items():
        url = (
            f"https://api.worldbank.org/v2/country/{code}/"
            f"indicator/{indicator}?format=json&per_page=2000"
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print("Дані відсутні:", name)
            else:
                for item in data[1]:
                    if item["value"] is not None:
                        all_data.append([name, int(item["date"]), float(item["value"])])

        except (requests.exceptions.RequestException, ValueError, TypeError, KeyError) as error:
            print("Помилка отримання даних:", error)
            return

    if len(all_data) == 0:
        print("Дані не отримано.")
    else:
        try:
            with open("inflation_data.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Country", "Year", "Inflation"])
                writer.writerows(all_data)

            print("CSV файл створено.")

        except (OSError, csv.Error) as error:
            print("Помилка створення CSV файлу:", error)

def read_csv():
    data = []

    try:
        with open("inflation_data.csv", "r", newline="", encoding="utf-8") as file: 
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    data.append([row["Country"], int(row["Year"]), float(row["Inflation"])
                    ])
                except (ValueError, TypeError, KeyError):
                    print("Некоректний рядок.")

    except (OSError, csv.Error, UnicodeError) as error:
        print("Помилка читання CSV файлу:", error)

    if len(data) == 0:
        print("Дані відсутні або файл порожній.")
    else:
        return data

def visualization(data):
    countries = ["Ukraine", "Poland"]
    years_ukraine = []
    values_ukraine = []
    years_poland = []
    values_poland = []

    for row in data:
        if row[0] == "Ukraine":
            years_ukraine.append(row[1])
            values_ukraine.append(row[2])

        elif row[0] == "Poland":
            years_poland.append(row[1])
            values_poland.append(row[2])

    ukraine = sorted(zip(years_ukraine, values_ukraine))
    poland = sorted(zip(years_poland, values_poland))

    years_ukraine = np.array([row[0] for row in ukraine])
    values_ukraine = np.array([row[1] for row in ukraine])
    years_poland = np.array([row[0] for row in poland])
    values_poland = np.array([row[1] for row in poland])

    if len(years_ukraine) == 0 or len(years_poland) == 0:
        print("Не знайдено дані обох країн.")

    plt.figure(figsize=(8, 5))

    plt.plot(years_ukraine, values_ukraine, label="Ukraine")
    plt.plot(years_poland, values_poland, label="Poland")

    plt.title("Inflation in Ukraine and Poland")
    plt.xlabel("Year")
    plt.ylabel("Inflation (%)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    while True:
        country = input(
            "Введіть країну Ukraine або Poland: "
        ).strip().lower()

        if country == "ukraine" or country == "poland":
            break

        print("Неправильна назва країни.")

    if country == "ukraine":
        years = years_ukraine
        values = values_ukraine
        name = "Ukraine"
    else:
        years = years_poland
        values = values_poland
        name = "Poland"

    plt.figure(figsize=(8, 5))
    plt.bar(years, values, width=0.7)

    plt.title("Inflation in " + name)
    plt.xlabel("Year")
    plt.ylabel("Inflation (%)")
    plt.xticks(years[::3], rotation=45)
    plt.grid(axis="y")
    plt.tight_layout()

    ukraine = dict(zip(years_ukraine, values_ukraine))
    poland = dict(zip(years_poland, values_poland))

    common_years = []

    for year in ukraine:
        if year in poland:
            if ukraine[year] > 0 and poland[year] > 0:
                common_years.append(year)

    if len(common_years) == 0:
        print("Немає років для кругової діаграми.")
        plt.show()
        return

    print("Доступні роки:", sorted(common_years))

    while True:
        try:
            year = int(input("Введіть рік: "))
            if year in common_years:
                break
            print("Такого року немає у списку.")

        except ValueError:
            print("Введіть рік числом.")

    values = np.array([ukraine[year], poland[year]])

    def func(pct, all_values):
        absolute = pct / 100 * np.sum(all_values)
        return f"{pct:.1f}%\n({absolute:.2f})"

    plt.figure(figsize=(6, 6))
    plt.pie(values, labels=["Ukraine", "Poland"], autopct=lambda pct: func(pct, values))
    plt.title("Inflation comparison (" + str(year) + ")")
    plt.tight_layout()
    plt.show()

def main():
    infodata()
    data = read_csv()

    if data is not None:
        visualization(data)

main()