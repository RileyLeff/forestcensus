export type Box = {
  x: number;
  y: number;
  width: number;
  height: number;
  skew_y?: number;
};

export type ReviewRow = {
  key: string;
  source_run_dir: string;
  survey_id: string;
  date: string;
  site: string;
  zone: string;
  plot: string;
  tree_number: string;
  trunk_number: string;
  genus: string;
  spp: string;
  dbh_mm: string;
  health: string;
  standing: string;
  poison_ivy: string;
  notes: string;
  section: string;
  species_update: string;
  identity_source: string;
  field_date: string;
  source_page: number;
  source_row: number;
  source_row_label: string;
  source_id_text: string;
  source_page_title: string;
  source_image: string;
  source_json: string;
  transcription_flags: string;
  review_flags: string;
  row_crop_path: string;
  page_image_width: number;
  page_image_height: number;
  row_box: Box | null;
  page_columns: Array<{
    index: number;
    name: string;
    box: Box;
  }>;
};

export type ReviewPage = {
  source_page: number;
  source_run_dir: string;
  source_image: string;
  page_image_width: number;
  page_image_height: number;
  source_page_title: string;
  plot: string;
  field_date: string;
  crew: string;
  problems_and_info: string;
  difficulty: string;
  page_flags: string;
  observer: string;
  recorder: string;
  bonus_person: string;
  recheck_answers: Array<{ question_number: number; question?: string; tags?: string[]; answer: string; flags: string[] }>;
  field_note_feedback: Array<{ note_number: number; text?: string; helpful: boolean | null; confusing: boolean | null; incorrect: boolean | null; handwritten_notes: string; flags: string[] }>;
  other_handwriting: string;
};

export type ReviewDecision = {
  key: string;
  source_run_dir?: string;
  action: 'accept' | 'edit' | 'skip';
  chosen_field?: string;
  chosen_value?: string;
  note?: string;
  decided_at: string;
};
