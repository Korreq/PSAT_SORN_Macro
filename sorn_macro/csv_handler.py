import csv

class CsvFile:

    def __init__(self, filename, header, rows):
        self.filename = filename

        with open(self.filename, 'w') as file:

            writer = csv.writer(file, dialect="excel")

            writer.writerow(header)

            writer.writerows(rows)