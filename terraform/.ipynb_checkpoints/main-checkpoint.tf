provider "google" {
  project = "your project
  region  = "your region"
}

resource "google_storage_bucket" "hospital_bucket" {
  name     = "hospital_datalake"
  location = "your region"
}

resource "google_bigquery_dataset" "hospital_dataset" {
  dataset_id = "hospital"
}

