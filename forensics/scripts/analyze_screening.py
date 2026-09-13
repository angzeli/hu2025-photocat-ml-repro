#!/usr/bin/env python3
"""Reconstruct descriptor decisions and audit Fig. 1 without redistributing tables.

Complete numeric extractions go ONLY to ignored forensics/local_only/. Tracked
outputs contain decisions, reconstructed identities, ranks and aggregate metrics.
CAT/PS numbering follows SI Tables 1–2, independently checked against sheet order.
Filtered membership follows SI Table 3 (PDF pp. 77–78), not Fig. 1e row position.
"""
import csv
import json
from pathlib import Path

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'orginal'
DERIVED = ROOT / 'data/derived'
LOCAL = ROOT / 'forensics/local_only'
OUTPUT = ROOT / 'forensics/outputs'
SUPP = '41929_2025_1291_MOESM2_ESM.xlsx'
FIG1 = '41929_2025_1291_MOESM11_ESM.xlsx'


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    for directory in (DERIVED, LOCAL, OUTPUT):
        directory.mkdir(parents=True, exist_ok=True)
    workbook = openpyxl.load_workbook(SOURCE / SUPP, read_only=True, data_only=True)
    retained = {}
    descriptors = []
    stats = {}
    for species, sheet_name, expected, cutoff, units in [
        ('CAT', 'Supplementary Fig. 1', 84, -0.20, 'eV'),
        ('PS', 'Supplementary Fig. 2', 41, 90, 'ns'),
    ]:
        values = list(workbook[sheet_name].values)
        assert len(values) == expected + 1
        assert all(len(row) == 1 and isinstance(row[0], (float, int)) for row in values[1:])
        raw = []
        for number, (value,) in enumerate(values[1:], 1):
            passed = value < cutoff if species == 'CAT' else value > cutoff
            raw.append(dict(species=species, id=number, value=value, units=units,
                            retained=passed, source=SUPP, sheet=sheet_name, cell=f'A{number + 1}'))
        descriptors.extend(raw)
        kept = [row for row in raw if row['retained']]
        retained[species] = [row['id'] for row in kept]
        # IDs and source locators, deliberately omitting original descriptor values.
        write_csv(DERIVED / ('retained_catalysts.csv' if species == 'CAT' else 'retained_photosensitizers.csv'),
                  [dict(id=row['id'], species=species, criterion=f'value {"<" if species == "CAT" else ">"} {cutoff} {units}',
                        source=SUPP, sheet=sheet_name, cell=row['cell'],
                        identity_basis='SI Tables 1–2 corroborate sequential row IDs') for row in kept])
        numbers = np.array([row['value'] for row in raw])
        stats[species] = dict(total=len(raw), retained=len(kept), ids=retained[species],
                              minimum=float(numbers.min()), maximum=float(numbers.max()),
                              mean=float(numbers.mean()), exact_cutoff_count=int(np.sum(numbers == cutoff)),
                              cutoff=cutoff, units=units)
    workbook.close()
    assert len(retained['CAT']) == 18 and len(retained['PS']) == 10
    candidates = [dict(cat_id=cat, ps_id=ps, candidate_id=f'CAT{cat}_PS{ps}',
                       provenance='Cartesian product of independently thresholded descriptor IDs')
                  for cat in retained['CAT'] for ps in retained['PS']]
    assert len(candidates) == len({row['candidate_id'] for row in candidates}) == 180
    write_csv(DERIVED / 'candidate_180.csv', candidates)
    write_csv(LOCAL / 'descriptor_values.csv', descriptors)

    workbook = openpyxl.load_workbook(SOURCE / FIG1, read_only=True, data_only=True)
    points = []
    for row_number, row in enumerate(workbook['Fig.1d'].values, 1):
        if row_number == 1 or all(value is None for value in row):
            continue
        assert len(row) == 2 and all(isinstance(value, (int, float)) for value in row)
        points.append(dict(source_row=row_number, J=row[0], Jstar=row[1]))
    j = np.array([row['J'] for row in points])
    js = np.array([row['Jstar'] for row in points])
    # Explicit sensitivity probe requested by the user; these are not identified author settings.
    j_cut, js_cut = 50.0, 0.01
    selected = (j > j_cut) & (js > js_cut)
    decisions = [dict(source_row=row['source_row'], pass_J_gt_50=bool(j[i] > j_cut),
                      pass_Jstar_gt_0p01=bool(js[i] > js_cut), pass_both=bool(selected[i]),
                      J_rank_descending=int(np.sum(j > j[i]) + 1),
                      Jstar_rank_descending=int(np.sum(js > js[i]) + 1),
                      source=FIG1, sheet='Fig.1d', identity='unresolved')
                 for i, row in enumerate(points)]
    write_csv(LOCAL / 'fig1d_source.csv', points)
    write_csv(DERIVED / 'fig1d_classification.csv', decisions)

    # Direct group labels from SI Table 3; the unsynthesized seventh pair has no Fig.1e measurement.
    filtered = {(1, 1), (37, 41), (49, 1), (61, 4), (49, 18), (49, 33)}
    unsynthesized = (50, 41)
    write_csv(DERIVED / 'selected_systems.csv', [
        dict(cat_id=cat, ps_id=ps, measured=(cat, ps) != unsynthesized,
             confidence='exact/direct membership only', source='SI Table 3 PDF pp77–78')
        for cat, ps in sorted(filtered | {unsynthesized})])
    # Caption/text establish star=CAT1/PS1; its unique plotted position matches row2.
    # This cross-source inference does not label the other six selected points.
    write_csv(DERIVED / 'fig1d_identity_mapping.csv', [
        dict(source_row=row['source_row'], cat_id=1 if row['source_row'] == 2 else '',
             ps_id=1 if row['source_row'] == 2 else '',
             confidence='high-confidence inference' if row['source_row'] == 2 else 'unresolved',
             evidence='Fig1 star caption + best-system text + unique plotted position' if row['source_row'] == 2
             else 'Seven-member selected set known; no per-point identity join',
             source='MOESM11 Fig.1d; article PDF pp2,4; SI Table3')
        for i, row in enumerate(points) if selected[i]])
    experimental = []
    for row_number, row in enumerate(workbook['Fig.1e'].values, 1):
        if row_number == 1:
            continue
        assert len(row) == 4 and all(value is not None for value in row)
        cat, ps = (int(row[i].split()[-1]) for i in (0, 1))
        experimental.append(dict(source_row=row_number, cat_id=cat, ps_id=ps,
                                 TON_CO=row[2], CO_selectivity_percent=row[3],
                                 group='filtered' if (cat, ps) in filtered else 'ruled_out'))
    workbook.close()
    assert len(experimental) == len({(row['cat_id'], row['ps_id']) for row in experimental}) == 43
    assert sum(row['group'] == 'filtered' for row in experimental) == 6
    assert unsynthesized not in {(row['cat_id'], row['ps_id']) for row in experimental}
    write_csv(LOCAL / 'fig1e_source.csv', experimental)
    ton = np.array([row['TON_CO'] for row in experimental])
    sel = np.array([row['CO_selectivity_percent'] for row in experimental])
    predicted = np.array([row['group'] == 'filtered' for row in experimental])
    conditional_good = (ton > 1370) & (sel > 72)
    classifications = [dict(source_row=row['source_row'], cat_id=row['cat_id'], ps_id=row['ps_id'],
                            author_selection_group=row['group'],
                            conditional_good_TON_gt_1370_AND_selectivity_gt_72=bool(conditional_good[i]),
                            classification=('TP' if predicted[i] else 'FN') if conditional_good[i]
                            else ('FP' if predicted[i] else 'TN'),
                            criterion_status='sensitivity assumption; unique author decision rule absent',
                            source=FIG1, sheet='Fig.1e', group_source='SI Table 3 PDF pp77–78')
                       for i, row in enumerate(experimental)]
    write_csv(DERIVED / 'fig1e_validation.csv', classifications)
    sensitivity = []
    for name, good in [('TON_gt_1370_AND_selectivity_gt_72', conditional_good),
                       ('TON_gt_1370_only', ton > 1370), ('selectivity_gt_72_only', sel > 72)]:
        tp = int(np.sum(predicted & good)); fp = int(np.sum(predicted & ~good))
        fn = int(np.sum(~predicted & good)); tn = int(np.sum(~predicted & ~good))
        sensitivity.append(dict(assumed_good_criterion=name, tp=tp, fp=fp, fn=fn, tn=tn,
                                precision=tp / (tp + fp), recall=tp / (tp + fn),
                                status='conditional; not an independently recovered author definition'))
    write_csv(DERIVED / 'validation_sensitivity.csv', sensitivity)
    summary = dict(
        provenance=dict(descriptors=f'{SUPP}: Supplementary Fig.1 A2:A85 / Fig.2 A2:A42',
                        screening=f'{FIG1}: Fig.1d A2:B35', experimental=f'{FIG1}: Fig.1e A2:D44'),
        descriptors=stats, candidate_count=len(candidates),
        fig1d=dict(n=len(points), fraction_of_180=len(points)/180,
                   J_min=float(j.min()), J_max=float(j.max()), Jstar_min=float(js.min()), Jstar_max=float(js.max()),
                   negative_J=int(np.sum(j < 0)), negative_Jstar=int(np.sum(js < 0)),
                   proposed_probe=dict(J_gt=j_cut, Jstar_gt=js_cut, pass_count=int(selected.sum()),
                                       source_rows=[row['source_row'] for i, row in enumerate(points) if selected[i]]),
                   same_selection_threshold_intervals=dict(
                       J_with_Jstar_fixed_0p01=[float(j[(js > js_cut) & ~selected].max()), float(j[selected].min())],
                       Jstar_with_J_fixed_50=[float(js[(j > j_cut) & ~selected].max()), float(js[selected].min())],
                       interval_convention='lower inclusive, upper exclusive for strict > predicates'),
                   identity_status='No pair IDs in numeric table; Fig.1d visual anchor assessed separately'),
        fig1e=dict(n=len(experimental), filtered=6, ruled_out=37, unmeasured_filtered=dict(cat_id=50,ps_id=41),
                   conditional_confusion=sensitivity[0],
                   conditional_good_threshold_intervals=dict(
                       TON_with_selectivity_fixed_72=[float(ton[(sel > 72) & ~conditional_good].max()), float(ton[conditional_good].min())],
                       selectivity_with_TON_fixed_1370=[float(sel[(ton > 1370) & ~conditional_good].max()), float(sel[conditional_good].min())],
                       interval_convention='lower inclusive, upper exclusive'),
                   false_negative_ids=[dict(cat_id=row['cat_id'],ps_id=row['ps_id']) for i,row in enumerate(experimental) if conditional_good[i] and not predicted[i]],
                   numerical_good_definition_status='not uniquely identified',
                   paper_individual_bounds_contradictions=dict(
                       ruled_out_TON_ge_1370=int(np.sum(~predicted & (ton >= 1370))),
                       ruled_out_selectivity_ge_72=int(np.sum(~predicted & (sel >= 72))))))
    (OUTPUT / 'screening_analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
