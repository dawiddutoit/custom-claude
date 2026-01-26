# Workload Identity Setup for GKE

Complete guide for setting up Workload Identity to enable GKE pods to write metrics to Cloud Monitoring without managing keys.

## Prerequisites

- GKE cluster with Workload Identity enabled
- GCP Project with Cloud Monitoring API enabled
- Appropriate IAM permissions

## Step 1: Create GCP Service Account

```bash
# Set project variables
export PROJECT_ID="my-project"
export SERVICE_ACCOUNT="supplier-charges-api"
export NAMESPACE="supplier-charges"

# Create Google Service Account
gcloud iam service-accounts create ${SERVICE_ACCOUNT} \
  --display-name="Service Account for Supplier Charges API"

# Grant metric writing permission
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/monitoring.metricWriter"

# Optional: grant Cloud Logging permission for structured logs
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

## Step 2: Create Kubernetes Service Account

```yaml
# kubernetes/service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: supplier-charges-api
  namespace: supplier-charges
  annotations:
    # Link to GCP Service Account
    iam.gke.io/gcp-service-account: supplier-charges-api@PROJECT_ID.iam.gserviceaccount.com
```

## Step 3: Bind Kubernetes SA to GCP SA

```bash
# Allow Kubernetes SA to impersonate GCP SA
gcloud iam service-accounts add-iam-policy-binding \
  ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/${SERVICE_ACCOUNT}]"
```

## Step 4: Use Service Account in Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: supplier-charges-api
  namespace: supplier-charges
spec:
  template:
    metadata:
      annotations:
        # Node pool where Workload Identity is enabled
        workload-identity/enable: "true"

    spec:
      # Reference Kubernetes Service Account
      serviceAccountName: supplier-charges-api

      containers:
      - name: app
        image: gcr.io/my-project/supplier-charges-api:latest
        ports:
        - containerPort: 8080

        env:
        # GCP project configuration
        - name: GCP_PROJECT_ID
          value: "my-project"

        - name: STACKDRIVER_ENABLED
          value: "true"

        # GKE resource labels
        - name: GKE_CLUSTER_NAME
          value: "supplier-charges-gke"

        - name: NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace

        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name

        - name: CONTAINER_NAME
          value: "app"

        - name: ENVIRONMENT
          value: "production"

        - name: GCP_REGION
          value: "europe-west2"
```

## Verification

Test Workload Identity:

```bash
#!/bin/bash
# test-workload-identity.sh

POD=$(kubectl get pod -n supplier-charges \
  -l app=supplier-charges-api \
  -o jsonpath='{.items[0].metadata.name}')

echo "Testing Workload Identity on pod: $POD"

# Check service account annotation
kubectl get sa supplier-charges-api -n supplier-charges -o yaml | \
  grep "iam.gke.io/gcp-service-account"

# Test GCP credentials from pod
kubectl exec -it $POD -n supplier-charges -- \
  gcloud auth list

# Verify Cloud Monitoring access
kubectl exec -it $POD -n supplier-charges -- \
  gcloud monitoring metrics-descriptors list \
    --filter="metric.type:custom.googleapis.com" | head -5

echo "✓ Workload Identity configured correctly"
```

## Troubleshooting

**401 Unauthorized errors:**
- Verify IAM binding exists
- Check service account annotation on K8s SA
- Ensure pod is using correct service account

**No metrics appearing:**
- Check pod logs for export confirmation
- Verify STACKDRIVER_ENABLED=true
- Check Cloud Monitoring API is enabled

**Permission denied:**
- Ensure roles/monitoring.metricWriter is granted
- Verify project ID matches in all configurations
