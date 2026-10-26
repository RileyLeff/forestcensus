# Mini Report: Original Forest Census Source Records

Date prepared: 2026-05-06

## Summary

I searched the Gedan Lab Google Drive under:

`Gedan Lab > Major Projects > CZN > Forest disturbance project > Annual Surveys`

I found and downloaded a small source-record bundle to:

`data/raw/forest_census/original_drive_records/`

The strongest original/source evidence is for 2020, 2022, and especially 2023. I did not find clearly tree-specific original 2019 or 2021 field/data-entry sheets in the Drive search path. The local bundle therefore includes derived all-years workbooks for those years as supporting evidence, but those should be treated as secondary sources rather than original datasheets.

## What Was Found

### Strong Source Records

The most useful files for resolving record-level conflicts are:

| Year | Local files | Why they matter |
| --- | --- | --- |
| 2020 | `2020/UpperPhillipsTreeData2020.csv` | Appears to be a direct uploaded 2020 tree data export. |
| 2022 | `2022/UPC_Forest_Disturbance_Trees_2022_1.xlsx` | Appears to be the main 2022 tree workbook. |
| 2023 | `2023/dated_reu_tree_entries/*.xlsx` | Dated REU tree-entry workbooks from June 8 through July 7, 2023. These are likely the closest thing to original 2023 entry sheets. |
| 2023 | `2023/templates/tree_data_entry_2023.xlsx` | Native Google Sheet export, likely a 2023 data-entry template or live entry sheet. |

The 2023 dated workbooks are especially valuable because they preserve the progression of data entry across field dates. If a conflict concerns a 2023 value, I would check the dated workbook for the relevant plot/date first, then compare against the RAW and QAQC merged files.

### Merge and QAQC Trail

Several files look like intermediate or downstream merge products:

| Local file | Likely role |
| --- | --- |
| `2023/merged_exports/UPC_Forest_Disturbance_tree_data_entry_2023_RAW.xlsx` | 2023 raw merged/export candidate. Useful for seeing how dated entry sheets were assembled before cleanup. |
| `2023/merged_exports/UPC_Forest_Disturbance_tree_data_entry_2023_QAQC_In_Progress.xlsx` | QAQC in-progress version. Useful for seeing intentional corrections or unresolved flags. |
| `2023/merged_exports/Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx` | All-years in-progress workbook. It appears to include 2023 uploaded data, tag-change notes, and cleanup notes. |
| `2023/merged_exports/2023_Forest_Disturbance_Plot_Trees_All_Years_Cleaned.xlsx` | Later cleaned all-years export from a native Google Sheet. Useful as downstream comparison, not as original evidence. |

The all-years in-progress workbook is notable because its preview showed a `tag_changes`-style sheet with explicit 2023 tag mappings, such as old tree codes mapped to new tree codes. That is probably a key source for conflicts involving newly tagged or renamed trees.

### Older All-Years Reference Files

These files are included because they may help reconstruct 2019-2022 context, but they are not original field sheets:

| Local file | Interpretation |
| --- | --- |
| `all_years/outdated_UPC_Forest_Disturbance_Trees_All_Years.xlsx` | Older all-years compilation. Useful for historical comparison, but marked outdated. |
| `all_years/UPC_Forest_Disturbance_Trees_All_Years_1.xlsx` | Another all-years workbook. Useful secondary reference. |
| `all_years/Forest_Disturbance_Plot_Trees_All_Years_Cleaned.xlsx` | Cleaned all-years workbook. Useful for downstream/current expectations. |

## What Was Not Found

I did not find clear original tree-specific field/data-entry sheets for:

- 2019
- 2021

Those years do appear inside all-years compilations, but I would avoid treating those all-years records as original evidence where a conflict depends on exact source provenance. They are still useful for triangulation.

## Suggested Conflict-Resolution Order

For 2023 conflicts:

1. Check the dated REU entry workbook closest to the survey date or plot.
2. Compare against `UPC_Forest_Disturbance_tree_data_entry_2023_RAW.xlsx`.
3. Check `UPC_Forest_Disturbance_tree_data_entry_2023_QAQC_In_Progress.xlsx` for possible manual corrections.
4. Use `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx` for tag-change context.
5. Use cleaned all-years files only as downstream comparison.

For 2022 conflicts:

1. Start with `2022/UPC_Forest_Disturbance_Trees_2022_1.xlsx`.
2. Compare to the all-years in-progress workbook if the issue involves a 2022-to-2023 carry-forward, tag replacement, or apparent back-from-dead case.

For 2020 conflicts:

1. Start with `2020/UpperPhillipsTreeData2020.csv`.
2. Use older all-years compilations only if the CSV lacks needed context.

For 2019 or 2021 conflicts:

1. Treat the all-years files as secondary evidence.
2. Look for corroboration across multiple all-years workbooks.
3. Be cautious about accepting a derived cleaned value as original truth without another source.

## Practical Notes

- The local bundle contains 19 downloaded data files plus README/report files.
- The Drive source path and Drive IDs are recorded in `README.md`.
- Google Drive was only read/exported; no Drive files were edited.
- The downloaded files are reference copies for provenance and conflict resolution, not canonical pipeline inputs.

## Bottom Line

The best source trail is for 2023, where the dated REU files plus RAW/QAQC/all-years workbooks give a plausible full path from entry to cleanup. The 2022 and 2020 sources are also solid. The weak point is 2019/2021: those years are represented in derived all-years files, but I did not locate original tree-specific datasheets for them in the searched Drive area.
