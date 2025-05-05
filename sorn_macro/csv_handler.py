import csv

class CsvFile:

    # Creates results file when created as instance, adds timestamp and prefix if specifed, 
    # fills file with header data and rows data
    def __init__(self, path, filename, header, rows, timestamp='', prefix=''):
        
        full_name = filename

        if prefix:
            full_name = prefix + '_' + full_name

        if timestamp:
            full_name = timestamp + '_' + full_name 
        
        self.full_path = path + '/' + full_name

        with open(self.full_path, 'w', newline='') as file:

            writer = csv.writer(file, dialect="excel-tab")

            writer.writerow(header)

            writer.writerows(rows)