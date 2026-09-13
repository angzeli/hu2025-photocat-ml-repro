#!/usr/bin/env python3
"""Summarize candidate aggregation operations on validation arrays, not MD ensembles."""
import csv
from pathlib import Path

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[2]


def main():
    book = openpyxl.load_workbook(ROOT / 'orginal/41929_2025_1291_MOESM2_ESM.xlsx',
                                 read_only=True, data_only=True)
    rows = list(book['Supplementary Fig. 9'].values)[2:]
    output = []
    for name, column in [('J_calculated', 0), ('J_predicted', 1),
                         ('Jstar_calculated', 3), ('Jstar_predicted', 4)]:
        a = np.array([row[column] for row in rows], dtype=float)
        assert a.shape == (1000,) and np.isfinite(a).all()
        output.append(dict(channel=name, n=len(a), signed_mean=float(a.mean()),
                           mean_absolute=float(np.abs(a).mean()), absolute_signed_mean=float(abs(a.mean())),
                           rms=float(np.sqrt(np.mean(a*a))),
                           source='MOESM2 Supplementary Fig. 9 rows3:1002',
                           interpretation='validation rows with unknown pair grouping; not a recovered pair average'))
    book.close()
    path = ROOT / 'data/derived/aggregation_probes.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(output[0]))
        writer.writeheader(); writer.writerows(output)
    for row in output:
        print(row)


if __name__ == '__main__':
    main()
