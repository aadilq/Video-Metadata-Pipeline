resource "google_project_iam_member" "cloudsql_client" {
    project = var.project_id
    role    = "roles/cloudsql.client"
    member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}