provider "google" {
    project = var.project_id
    region = "us-south1"
}

resource "google_bigquery_dataset" "my_dataset" {
  dataset_id                  = "climbing_weather"
  description                 = "This dataset contains weather related data"
}

resource "google_storage_bucket" "raw_weather_bucket" {
 name          = "${var.project_id}-raw-weather"
 location = "US"
 storage_class = "STANDARD"

 uniform_bucket_level_access = true
}