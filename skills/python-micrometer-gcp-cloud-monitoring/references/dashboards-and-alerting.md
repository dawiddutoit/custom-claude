# Cloud Monitoring Dashboards and Alerting

Guide for creating dashboards and alert policies based on exported Micrometer metrics.

## Creating Dashboards with Terraform

```yaml
# terraform/cloud_monitoring.tf
resource "google_monitoring_dashboard" "supplier_charges" {
  dashboard_json = jsonencode({
    displayName = "Supplier Charges API - Metrics"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          xyChart = {
            dataSources = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/charge/approved\" resource.type=\"k8s_container\""
                  }
                }
              }
            ]
            timeshiftDuration = "0s"
            yAxis = {
              label = "Charges Approved"
            }
          }
        },
        {
          width  = 6
          height = 4
          xyChart = {
            dataSources = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"custom.googleapis.com/charge/value\" resource.type=\"k8s_container\""
                  }
                }
              }
            ]
          }
        }
      ]
    }
  })
}
```

## Alert Policies

Create alert policies based on exported metrics:

```yaml
# Alert: High charge rejection rate
resource "google_monitoring_alert_policy" "high_rejection_rate" {
  display_name = "Supplier Charges - High Rejection Rate"
  combiner     = "OR"

  conditions {
    display_name = "Rejection rate > 5%"

    condition_threshold {
      filter = <<-EOT
        metric.type="custom.googleapis.com/charge/rejected"
        resource.type="k8s_container"
        resource.label.cluster_name="supplier-charges-gke"
      EOT

      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      duration        = "300s"

      aggregations {
        alignment_period    = "60s"
        per_series_aligner  = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [
    google_monitoring_notification_channel.pagerduty.id
  ]
}
```

## Query Metrics via CLI

```bash
# List all metrics for your project
gcloud monitoring metrics-descriptors list \
  --filter="metric.type:custom.googleapis.com"

# Example output:
# metric.type: custom.googleapis.com/charge/approved
# description: "Charges approved for payment"
# unit: "1" (dimensionless)
```

## Viewing Metrics in Console

1. Open GCP Console → Cloud Monitoring → Metrics
2. Select resource type: "Kubernetes Container"
3. Filter by cluster: supplier-charges-gke
4. View metric type: custom.googleapis.com/charge/...

## Common Dashboard Queries

**Request rate by endpoint:**
```
metric.type="custom.googleapis.com/http/requests"
resource.type="k8s_container"
resource.label.cluster_name="my-cluster"
| group_by [resource.label.endpoint], sum(value.rate)
```

**P95 latency:**
```
metric.type="custom.googleapis.com/http/request/duration"
resource.type="k8s_container"
| align delta(1m)
| group_by [], percentile(value, 95)
```

**Error rate:**
```
metric.type="custom.googleapis.com/http/requests"
resource.type="k8s_container"
metric.label.status_class="5xx"
| group_by [], sum(value.rate)
```
