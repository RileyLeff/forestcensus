#let data = json("fake_plot.json")

#set document(
  title: "Forest census field datasheet",
  author: "forestcensus",
)

#set text(font: "New Computer Modern", size: 7.4pt)
#set par(leading: 0.46em)

#let hairline = 0.36pt + black
#let faintline = 0.28pt + rgb("#777777")

#let blank-box(width: 9pt, height: 9pt) = box(width: width, height: height, stroke: hairline)
#let check-cell = align(center + horizon, blank-box(width: 9.8pt, height: 9.8pt))
#let observation-check = align(center + horizon, blank-box(width: 12pt, height: 12pt))
#let date-digit = blank-box(width: 18pt, height: 22pt)
#let survey-title = data.at("survey_title", default: data.at("survey_id").replace("_", " ") + " Survey")

#let field-label(body) = text(size: 5.9pt, weight: "bold", fill: rgb("#333333"), body)

#let value(row, key) = {
  let v = row.at(key, default: "")
  if v == none { "" } else { str(v) }
}

#let latest-dbh(row) = {
  let reference = value(row, "reference_dbh")
  if reference != "" {
    reference
  } else {
    let recent = value(row, "dhs_1")
    let prior = value(row, "dhs_2")
    if recent != "" and recent.split("/").at(0) != "NA" {
      recent.split("/").at(0)
    } else if prior != "" and prior.split("/").at(0) != "NA" {
      prior.split("/").at(0)
    } else {
      ""
    }
  }
}

#let hsp-value(row, key) = {
  let hsp-key = key.replace("dhs", "hsp")
  if hsp-key in row {
    value(row, hsp-key)
  } else {
    let parts = value(row, key).split("/")
    if parts.len() >= 3 {
      parts.slice(1, 3).join("/") + if parts.len() >= 4 and parts.at(3) in ("1", "true", "p") { "/p" } else { "" }
    } else {
      ""
    }
  }
}

#let tag-counts = {
  let counts = (:)
  for row in data.at("rows") {
    let tag = row.at("tree_uid", default: value(row, "tag"))
    counts.insert(tag, counts.at(tag, default: 0) + 1)
  }
  counts
}

#let stem-label(row) = {
  let stem = value(row, "stem")
  let count = tag-counts.at(row.at("tree_uid", default: value(row, "tag")), default: 1)
  if count > 1 {
    stem + "/" + str(count)
  } else {
    stem
  }
}

#let check-label(label) = [
  #blank-box(width: 10pt, height: 10pt)
  #h(2pt)
  #text(size: 8pt, label)
]

#let date-boxes = [
  #text(size: 7pt, weight: "bold", "Date")
  #h(4pt)
  #text(size: 7pt, "YYYY / MM / DD")
  #v(4pt)
  #for i in range(4) { date-digit }
  #h(3pt) #text(size: 12pt, "/") #h(3pt)
  #for i in range(2) { date-digit }
  #h(3pt) #text(size: 12pt, "/") #h(3pt)
  #for i in range(2) { date-digit }
]

#let crew-line(i) = [
  #text(size: 7pt, weight: "bold", data.at("crew_roles", default: ("Observer", "Recorder", "Bonus person")).at(i - 1))
  #v(22pt)
  #line(length: 100%, stroke: faintline)
]

#let plot-title = data.at("site") + " " + data.at("plot")
#let plot-meta = (
  str(data.at("tree_count")) + " trees, "
  + str(data.at("living_count")) + " last recorded alive, "
  + str(data.at("species_count")) + " species, rated "
  + data.at("difficulty")
)

#let main-cols = (
  0.25in, // row
  0.44in, // tag
  0.52in, // spp
  0.20in, // stem
  0.38in, // health
  0.28in, // standing
  0.25in, // pi
  0.39in, // latest dbh
  0.52in, // hsp 1
  0.52in, // hsp 2
  0.78in, // species update
  3.32in, // notes
)

#let main-labels = table(
  columns: main-cols,
  stroke: hairline,
  inset: (x: 1.8pt, y: 4.0pt),
  align: center + horizon,
  fill: rgb("#f2f2f2"),
  [#field-label("row")],
  [#field-label("tag")],
  [#field-label("spp")],
  [#field-label("stm")],
  [#field-label("health")],
  [#field-label("std")],
  [#field-label("pi")],
  [#field-label("prev DBH")],
  [#field-label("hsp.1")],
  [#field-label("hsp.2")],
  [#field-label("species update")],
  [#field-label("notes")],
)

#set page(
  paper: "us-letter",
  margin: (left: 0.32in, right: 0.32in, top: 0.82in, bottom: 0.32in),
)

#let sheet-start(page-number) = [
  #grid(
    columns: (1fr, auto, auto),
    column-gutter: 16pt,
    align: (left, right, right),
    text(size: 15pt, weight: "bold", plot-title),
    text(size: 8pt, survey-title),
    text(size: 8pt, "page " + str(page-number) + "/" + str(data.at("total_pages"))),
  )
  #v(4pt)
  #grid(
    columns: (2.6in, 1fr, 1fr, 1fr),
    column-gutter: 10pt,
    align: horizon,
    date-boxes,
    crew-line(1),
    crew-line(2),
    crew-line(3),
  )
  #v(7pt)
  #text(size: 9pt, weight: "bold", "Main")
  #h(8pt)
  #text(size: 7pt, plot-meta)
  #v(1pt)
  #main-labels
  #v(-1.2pt)
]

#let continuation-start(page-number) = [
  #grid(
    columns: (1fr, auto, auto),
    column-gutter: 16pt,
    align: (left, right, right),
    text(size: 15pt, weight: "bold", plot-title),
    text(size: 8pt, survey-title),
    text(size: 8pt, "page " + str(page-number) + "/" + str(data.at("total_pages"))),
  )
  #v(4pt)
  #text(size: 9pt, weight: "bold", "Main")
  #h(8pt)
  #text(size: 7pt, plot-meta)
  #v(1pt)
  #main-labels
  #v(-1.2pt)
]

#let row-block(row) = block(
  breakable: false,
  below: 0.25pt,
  table(
    columns: main-cols,
    stroke: hairline,
    inset: (x: 1.8pt, y: 2.55pt),
    align: center + horizon,
    text(size: 6.7pt, value(row, "row")),
    text(size: 8.0pt, weight: "bold", value(row, "tag")),
    text(size: 7.0pt, value(row, "spp")),
    text(size: 6.8pt, stem-label(row)),
    [],
    check-cell,
    check-cell,
    text(size: 7.0pt, latest-dbh(row)),
    text(size: 6.8pt, hsp-value(row, "dhs_1")),
    text(size: 6.8pt, hsp-value(row, "dhs_2")),
    [],
    text(size: 6.5pt, value(row, "note_hint")),
  )
)

#let recruit-cols = (
  0.30in, // row
  0.56in, // tag
  0.62in, // spp
  0.25in, // stem
  0.52in, // dbh
  0.46in, // health
  0.30in, // standing
  0.28in, // pi
  4.57in, // notes
)

#let recruit-labels = table(
  columns: recruit-cols,
  stroke: hairline,
  inset: (x: 1.8pt, y: 1.8pt),
  align: center + horizon,
  fill: rgb("#f2f2f2"),
  [#field-label("row")],
  [#field-label("tag")],
  [#field-label("spp")],
  [#field-label("stm")],
  [#field-label("dbh")],
  [#field-label("health")],
  [#field-label("std")],
  [#field-label("pi")],
  [#field-label("notes")],
)

#let recruit-row(i) = block(
  breakable: false,
  below: 0.85pt,
  table(
    columns: recruit-cols,
    rows: data.at("writing_row_height_pt", default: 15.3) * 1pt,
    stroke: hairline,
    inset: (x: 1.8pt, y: 2.75pt),
    align: center + horizon,
    text(size: 6.8pt, "N" + str(i)),
    [],
    [],
    [],
    [],
    [],
    observation-check,
    observation-check,
    [],
  )
)

#let supplement-content = [
  #block(breakable: false)[
  #v(6pt)
  #text(size: 9pt, weight: "bold", "Newly Tracked")
  #v(2pt)
  #recruit-labels
  #v(-1.2pt)
  #for i in range(1, data.at("newly_tracked_slots", default: 6) + 1) [
    #recruit-row(i)
  ]
  ]

  #block(breakable: false)[
  #v(8pt)
  #text(size: 9pt, weight: "bold", "Problems and Info")
  #v(6pt)
  #line(length: 96%, stroke: faintline)
  #v(13pt)
  #line(length: 96%, stroke: faintline)
  #v(13pt)
  #line(length: 96%, stroke: faintline)
  ]

  #block(breakable: false)[
  #v(8pt)
  #grid(
    columns: (auto, auto, auto, auto, auto),
    column-gutter: 16pt,
    align: horizon,
    text(size: 9pt, weight: "bold", "Difficulty"),
    check-label("easy"),
    check-label("medium"),
    check-label("hard"),
    check-label("brutal"),
  )

  #v(7pt)
  #text(size: 7pt, weight: "bold", "Existing tags")
  #v(2pt)
  #text(size: 8.2pt, data.at("existing_tags").join(", "))
  ]
]

#let supplement-page(page-number) = block(breakable: false)[
  #grid(
    columns: (1fr, auto, auto),
    column-gutter: 16pt,
    align: (left, right, right),
    text(size: 15pt, weight: "bold", plot-title),
    text(size: 8pt, survey-title),
    text(size: 8pt, "page " + str(page-number) + "/" + str(data.at("total_pages"))),
  )
  #supplement-content
]

#let row-pages = data.at("row_pages", default: ())
#let last-row-page-index = row-pages.len() - 1

#if "field_notes" in data {
  set page(margin: (left: 0.32in, right: 0.32in, top: 0.96in, bottom: 0.32in), header-ascent: 8pt, header: context [
    #grid(columns: (1fr, auto, auto), column-gutter: 16pt, align: horizon,
      text(size: 15pt, weight: "bold", plot-title),
      text(size: 9pt, survey-title),
      text(size: 8pt, "page " + str(counter(page).get().first()) + "/" + str(counter(page).final().first())))
    #v(3pt)
    #let difficulty = data.at("historical_difficulty")
    #let rating = if difficulty.at("mean") == none { "NA" } else { str(calc.round(difficulty.at("mean"), digits: 1)) + "/4" }
    #text(size: 7pt, "Avg. difficulty: " + rating + if difficulty.at("count") > 0 { " (" + str(difficulty.at("count")) + " rated survey" + if difficulty.at("count") == 1 { ")" } else { "s)" } } else { "" })
    #h(5pt)
    #text(size: 6.5pt, "1 easy | 2 medium | 3 hard | 4 brutal")
    #v(2pt)
    #text(size: 6.7pt, "HSP.1: " + data.at("context_surveys").at(0).replace("_", " ")
      + " | HSP.2: " + data.at("context_surveys").at(1).replace("_", " ")
      + " | hsp = health / standing / poison ivy (only if applicable)"
      + " | * = open question below | + = appears in field note")
  ])
  grid(columns: (2.6in, 1fr, 1fr, 1fr), column-gutter: 10pt, align: horizon,
    date-boxes, crew-line(1), crew-line(2), crew-line(3))
  for section in ("main",) {
    let rows = data.at("rows").filter(row => value(row, "roster_section") == section)
    if rows.len() > 0 {
      v(5pt)
      block(sticky: true)[
        #text(size: 9pt, weight: "bold", "Main")
      ]
      let labels = ("row", "tag", "spp", "stm", "health", "std", "pi", "prev DBH", "hsp.1", "hsp.2", "species update", "notes")
      table(columns: main-cols, stroke: hairline,
        rows: (20pt,) + rows.map(_ => data.at("writing_row_height_pt") * 1pt),
        inset: (x: 1.8pt, y: 2.55pt), align: center + horizon,
        table.header(..labels.map(label => table.cell(fill: rgb("#f2f2f2"), field-label(label)))),
        ..rows.map(row => (
          text(size: 6.7pt, value(row, "row")),
          text(size: 8pt, weight: "bold", value(row, "tag")
            + if row.at("recheck_ids", default: ()).len() > 0 { "*" } else { "" }
            + if row.at("field_note_numbers", default: ()).len() > 0 { "+" } else { "" }),
          text(size: 7pt, value(row, "spp")),
          text(size: 6.8pt, stem-label(row)), [], observation-check, observation-check,
          text(size: 7pt, latest-dbh(row)),
          text(size: 6.8pt, hsp-value(row, "dhs_1")),
          text(size: 6.8pt, hsp-value(row, "dhs_2")), [], [],
        )).flatten(),
      )
    }
  }
  if data.at("rechecks", default: ()).len() > 0 {
    v(8pt)
    block(sticky: true)[#text(size: 9pt, weight: "bold", "Recheck Questions")]
    for check in data.at("rechecks") {
      block(breakable: false)[
        #text(size: 8pt, weight: "bold", "Q" + str(check.at("number")) + " | " + check.at("tags").join(", ") + " | " + check.at("question"))
        #v(3pt)
        #text(size: 7pt, check.at("context"))
        #v(18pt)
        #line(length: 100%, stroke: faintline)
        #v(18pt)
        #line(length: 100%, stroke: faintline)
        #v(5pt)
      ]
    }
  }
  if data.at("field_notes").len() > 0 {
  v(8pt)
  table(
    columns: (1fr, 0.62in, 0.72in, 0.66in),
    stroke: none,
    inset: (x: 0pt, y: 5pt),
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      text(size: 9pt, weight: "bold", "Field Notes"),
      text(size: 7pt, weight: "bold", "Helpful"),
      text(size: 7pt, weight: "bold", "Confusing"),
      text(size: 7pt, weight: "bold", "Incorrect"),
    ),
    ..data.at("field_notes").map(note => (
      table.cell(breakable: false, inset: (right: 8pt),
        grid(columns: (8pt, 1fr), text(size: 9pt, "-"), text(size: 8pt, note.at("text")))),
      check-cell,
      check-cell,
      check-cell,
    )).flatten(),
  )
  }
  supplement-content
} else {
for page-index in range(row-pages.len()) [
  #{
    if page-index == 0 {
      sheet-start(page-index + 1)
    } else {
      continuation-start(page-index + 1)
    }
  }
  #for row in row-pages.at(page-index) [
    #row-block(row)
  ]
  #if page-index == last-row-page-index and data.at("supplement_on_last_main_page") [
    #supplement-content
  ] else [
    #pagebreak()
  ]
]

if not data.at("supplement_on_last_main_page") [
  #supplement-page(data.at("total_pages"))
]
}
