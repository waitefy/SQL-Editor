import csv
import json


def export_to_csv(filename, headers, rows):
    """Экспорт данных в CSV файл"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)  # Заголовки
            writer.writerows(rows)  # Данные
        return True, "Файл успешно сохранен"
    except Exception as e:
        return False, f"Ошибка при сохранении CSV: {e}"


def export_to_json(filename, headers, rows):
    """Экспорт данных в JSON файл"""
    try:
        # Преобразуем список списков в список словарей
        data = []
        for row in rows:
            # zip объединяет заголовки и значения строки в пары: (id, 1), (name, 'Bob')
            item = dict(zip(headers, row))
            data.append(item)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True, "Файл успешно сохранен"
    except Exception as e:
        return False, f"Ошибка при сохранении JSON: {e}"