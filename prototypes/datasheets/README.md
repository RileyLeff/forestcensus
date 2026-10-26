# Datasheet Layout Prototypes

This folder is a scratch area for testing portrait Typst datasheets before the
generator is wired into the forest census CLI.

- `fake_plot.json` contains fake-but-plausible plot data with multi-stem cases,
  conflicts, old `dhs` history, recruit rows, and long note prompts.
- `portrait_prototype.typ` renders a portrait US-letter field form using the
  proposed post-`alive` and post-routine-DBH schema: `health = 0` implies dead,
  `pi` is separate, known-tree rows omit DBH, and DBH only appears in the new
  newly tracked tree section. It uses New Computer Modern, inline notes, three crew
  lines, plot metadata, section headings, explicit `dbh`, `hsp.1`, and `hsp.2`
  history columns, and an end-of-sheet difficulty checkbox.

Render with:

```sh
typst compile prototypes/datasheets/portrait_prototype.typ output/datasheet_layout/portrait_prototype.pdf
```
