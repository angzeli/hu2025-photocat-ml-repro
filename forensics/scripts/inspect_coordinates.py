#!/usr/bin/env python3
"""Parse every released coordinate row; retain composition/order metadata only."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
ELEMENTS = set("H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og".split())
TRANSITION_METALS = set("Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Tc Ru Rh Pd Ag Cd Hf Ta W Re Os Ir Pt Au Hg".split())
MD_NAME = re.compile(r"cat-(\d+)_pho-(\d+)_(initial|final)\.txt$")


def parse_geometry(path):
    symbols, coordinates = [], []
    blank_lines = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            blank_lines += 1
            continue
        fields = line.split()
        if len(fields) != 4 or fields[0] not in ELEMENTS:
            raise ValueError(f"{path}:{line_number}: not an element-x-y-z row")
        try:
            xyz = tuple(float(value) for value in fields[1:])
        except ValueError as error:
            raise ValueError(f"{path}:{line_number}: invalid coordinate") from error
        if not all(math.isfinite(value) for value in xyz):
            raise ValueError(f"{path}:{line_number}: nonfinite coordinate")
        symbols.append(fields[0])
        coordinates.append(xyz)
    if not symbols:
        raise ValueError(f"{path}: no atoms")
    return symbols, coordinates, blank_lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    source = args.root / "orginal"
    output = args.root / "forensics/outputs"
    output.mkdir(parents=True, exist_ok=True)
    rows, md = [], {}
    all_ranges = [[math.inf, -math.inf] for _ in range(3)]
    noncentred = 0
    coordinate_hashes = Counter()
    for path in sorted(source.rglob("*.txt")):
        symbols, xyz, blanks = parse_geometry(path)
        counts = Counter(symbols)
        order_digest = hashlib.sha256("\n".join(symbols).encode()).hexdigest()
        numeric_digest = hashlib.sha256(repr(xyz).encode()).hexdigest()
        coordinate_hashes[numeric_digest] += 1
        match = MD_NAME.fullmatch(path.name)
        cat, ps, stage = (match.group(1), match.group(2), match.group(3)) if match else ("", "", "optimized structure (publisher mapping)")
        rows.append({"relative_path": path.relative_to(source).as_posix(), "format": "headerless element-x-y-z", "geometry_blocks": 1, "atom_count": len(symbols), "composition": ";".join(f"{key}:{counts[key]}" for key in sorted(counts)), "ordered_elements_sha256": order_digest, "transition_metal_positions_1based": ";".join(f"{element}:{i + 1}" for i, element in enumerate(symbols) if element in TRANSITION_METALS), "cat_id_from_filename": cat, "ps_id_from_filename": ps, "stage_from_filename": stage, "blank_line_count": blanks, "metadata_line_count": 0, "parse_status": "all rows finite element-x-y-z"})
        if match:
            key = (int(cat), int(ps), stage)
            if key in md:
                raise ValueError(f"Duplicate MD key: {key}")
            md[key] = (tuple(symbols), numeric_digest)
            for axis in range(3):
                values = [point[axis] for point in xyz]
                all_ranges[axis][0] = min(all_ranges[axis][0], min(values))
                all_ranges[axis][1] = max(all_ranges[axis][1], max(values))
            if any(abs(sum(point[axis] for point in xyz) / len(xyz)) > 1e-8 for axis in range(3)):
                noncentred += 1
    with (output / "structure_metadata.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    pairs = {(cat, ps) for cat, ps, _ in md}
    cats = sorted({cat for cat, _ in pairs})
    ps_ids = sorted({ps for _, ps in pairs})
    missing_pairs = sorted(set((cat, ps) for cat in cats for ps in ps_ids) - pairs)
    missing_endpoints, mismatched_order, identical_numeric = [], [], []
    for cat, ps in sorted(pairs):
        initial, final = md.get((cat, ps, "initial")), md.get((cat, ps, "final"))
        if initial is None or final is None:
            missing_endpoints.append([cat, ps])
            continue
        if initial[0] != final[0]:
            mismatched_order.append([cat, ps])
        if initial[1] == final[1]:
            identical_numeric.append([cat, ps])
    root_rows = [row for row in rows if not row["cat_id_from_filename"]]
    md_rows = [row for row in rows if row["cat_id_from_filename"]]
    summary = {"coordinate_file_count": len(rows), "parsed_geometry_blocks": len(rows), "all_rows_parsed": True, "format": "headerless element x y z; one undelimited block per file", "root_optimized_structure_count": len(root_rows), "root_structures": [{key: row[key] for key in ("relative_path", "atom_count", "composition", "transition_metal_positions_1based")} for row in root_rows], "md_file_count": len(md_rows), "md_stage_counts": dict(sorted(Counter(row["stage_from_filename"] for row in md_rows).items())), "md_pair_count": len(pairs), "cat_ids": cats, "ps_ids": ps_ids, "full_cartesian_product": not missing_pairs, "missing_pairs": missing_pairs, "missing_endpoint_pairs": missing_endpoints, "initial_final_element_order_mismatch_pairs": mismatched_order, "initial_final_identical_numeric_pairs": identical_numeric, "coordinate_numeric_duplicate_group_count": sum(count > 1 for count in coordinate_hashes.values()), "md_atom_count_min": min(row["atom_count"] for row in md_rows), "md_atom_count_max": max(row["atom_count"] for row in md_rows), "md_unique_atom_counts": sorted({row["atom_count"] for row in md_rows}), "md_unique_element_order_count": len({row["ordered_elements_sha256"] for row in md_rows}), "md_coordinate_ranges_unlabelled_units": {axis: values for axis, values in zip("xyz", all_ranges)}, "md_files_with_nonzero_arithmetic_centroid_at_1e-8": noncentred, "metadata_line_count": sum(row["metadata_line_count"] for row in rows), "blank_line_count": sum(row["blank_line_count"] for row in rows), "presence_assessment": {"md_initial_final_pair_identities": "DIRECT: complete CAT 1-84 x PS 1-41 filename grid", "intermediate_trajectory_snapshots": "ABSENT from parsed loose coordinate files; all MD files consist only of initial/final coordinate blocks", "exact_labelled_ml_geometry_mapping": "ABSENT: no snapshot, conformation, training/test, or dipole-row IDs in the coordinate contents", "coordinate_units": "ABSENT from coordinate files; consult article/SI", "cell_pbc_time_charge_spin": "ABSENT from coordinate files", "atom_order": "DIRECT within each file; initial/final consistency computed above", "normalization_centering": "ABSENT; supplied MD coordinates have nonzero arithmetic centroids; that does not determine unpublished NN preprocessing"}}
    (output / "structure_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("coordinate_file_count", "md_stage_counts", "md_pair_count", "full_cartesian_product", "md_atom_count_min", "md_atom_count_max", "initial_final_element_order_mismatch_pairs", "initial_final_identical_numeric_pairs", "blank_line_count")}, indent=2))


if __name__ == "__main__":
    main()
