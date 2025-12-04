import csv
import json


def export_to_csv(filename, headers, rows):
    """Экспорт данных в CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def export_to_json(filename, headers, rows):
    """Экспорт данных в JSON"""
    data = []
    for row in rows:
        # Собираем словарь zip-ом заголовков и значений строки
        item = dict(zip(headers, row))
        data.append(item)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
