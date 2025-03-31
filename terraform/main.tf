provider "google" {
  project = "de-zoomcamp-2025--id"
  region  = "asia-southeast2"
}

resource "google_storage_bucket" "hospital_bucket" {
  name     = "hospital_datalake2"
  location = "asia-southeast2"
}

resource "google_bigquery_dataset" "hospital_dataset" {
  dataset_id = "hospital2"
}

