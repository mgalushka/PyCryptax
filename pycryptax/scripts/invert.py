import csv
import os
from decimal import Decimal


if __name__ == '__main__':
    file = os.path.dirname(__file__) + '/../../examples/prices/gbp_usd.csv'
    out = os.path.dirname(__file__) + '/../../examples/prices/usd_gbp.csv'
    with open(out, 'w') as outfile:
        with open(file) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] == 'DATE':
                    continue
                rate = Decimal(float(row[1]))
                outfile.write('{},{:.4f}\n'.format(row[0], 1 / rate))
                # print('{},{:.4f}'.format(row[0], 1 / rate))