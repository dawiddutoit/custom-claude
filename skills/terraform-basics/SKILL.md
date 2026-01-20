---
name: terraform-basics
description: |
  Provision and manage cloud infrastructure using Infrastructure as Code. Use when creating or modifying GCP resources,
  managing Pub/Sub topics and subscriptions, configuring IAM bindings, deploying multi-environment infrastructure,
  or tracking infrastructure state. Works with GCP, Kubernetes, and remote state management.
---

# Terraform Skill

## Table of Contents

**Quick Start** → [What Is This](#purpose) | [When to Use](#when-to-use) | [Simple Example](#quick-start)

**How to Implement** → [Step-by-Step](#instructions) | [Examples](#examples)

**Help** → [Requirements](#requirements) | [See Also](#see-also)

## Purpose

Master Terraform for declarative Infrastructure as Code provisioning. This skill covers state management, resource configuration, module design, variable validation, security best practices, and GCP integration patterns.

## When to Use

Use this skill when you need to:

- **Provision cloud infrastructure** - Create GCP resources (Pub/Sub, GKE, Cloud SQL, etc.)
- **Manage infrastructure as code** - Version control infrastructure configurations
- **Deploy multi-environment setups** - Maintain separate labs, test, and production environments
- **Configure IAM bindings** - Set up secure access permissions for services
- **Track infrastructure state** - Maintain state files and prevent drift
- **Implement security best practices** - Manage secrets, apply least privilege, validate inputs

**Trigger Phrases:**
- "Deploy infrastructure to GCP"
- "Create Pub/Sub topics with Terraform"
- "Set up remote state management"
- "Configure GCP provider"
- "Manage infrastructure variables"

## Quick Start

Deploy Pub/Sub topics to GCP in 3 minutes:

```bash
# 1. Initialize Terraform (downloads providers, sets up backend)
terraform init

# 2. Preview what will be created
terraform plan

# 3. Apply changes to infrastructure
terraform apply -auto-approve
```

Terraform configuration:

```hcl
# main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.26.0"
    }
  }

  backend "gcs" {
    prefix = "supplier-charges-hub"
    bucket = "my-terraform-state"  # Must exist
  }
}

provider "google" {
  project = "ecp-wtr-supplier-charges-${var.environment}"
  region  = var.region
}

# Create Pub/Sub topic
resource "google_pubsub_topic" "incoming" {
  name = "supplier-charges-incoming-${var.environment}"
}

# Create subscription
resource "google_pubsub_subscription" "incoming_sub" {
  name  = "supplier-charges-incoming-sub-${var.environment}"
  topic = google_pubsub_topic.incoming.name
}
```

## Instructions

### Step 1: Understand Infrastructure as Code

**Principle**: Infrastructure is version-controlled, peer-reviewed, and declarative.

```hcl
# You declare WHAT you want
resource "google_pubsub_topic" "charges" {
  name = "supplier-charges-incoming"
  # Terraform figures out HOW to create it
}
```

### Step 2: Set Up Remote State

Always use **remote state** (never commit `.tfstate` to Git):

```hcl
# main.tf
terraform {
  backend "gcs" {
    bucket = "terraform-state-prod"
    prefix = "supplier-charges-hub"  # Organize by project
  }
}

# GCS backend provides automatic locking (prevents concurrent applies)
```

**Why Remote State?**
- ✅ Team collaboration (single source of truth)
- ✅ State locking (prevents concurrent modifications)
- ✅ Backup and encryption
- ✅ Sensitive data (passwords) not in Git

### Step 3: Configure Provider & Authentication

```hcl
# main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.26.0"  # Allows 5.26.x, not 5.27.0
    }
  }
}

provider "google" {
  project = "ecp-wtr-supplier-charges-${var.environment}"
  region  = var.region  # "europe-west2"
}
```

**Authentication** (Terraform will auto-detect):
```bash
# Use application default credentials
gcloud auth application-default login

# Or export service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Step 4: Define Input Variables

Create typed, validated variables:

```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment (labs, test, prod)"
  type        = string
  default     = "labs"

  validation {
    condition     = contains(["labs", "test", "prod"], var.environment)
    error_message = "Environment must be: labs, test, or prod"
  }
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "europe-west2"
}

variable "common_labels" {
  description = "Labels applied to all resources"
  type = map(string)
  default = {
    managed-by  = "terraform"
    application = "supplier-charges-hub"
  }
}

# Mark sensitive values
variable "api_key" {
  description = "External API key"
  type        = string
  sensitive   = true
}
```

### Step 5: Create Resources

Define infrastructure resources:

```hcl
# pubsub.tf
locals {
  app_name        = var.common_labels["application"]
  resource_prefix = "${local.app_name}-${var.environment}"
}

# Pub/Sub topic for incoming charges
resource "google_pubsub_topic" "incoming" {
  name                    = "${local.resource_prefix}-incoming"
  message_retention_duration = "604800s"  # 7 days
  labels                  = var.common_labels
}

# Pub/Sub subscription
resource "google_pubsub_subscription" "incoming_sub" {
  name  = "${local.resource_prefix}-incoming-sub"
  topic = google_pubsub_topic.incoming.name

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s"  # 1 day

  dead_letter_policy {
    dead_letter_topic            = google_pubsub_topic.incoming_dlq.id
    max_delivery_attempts        = 5
  }

  labels = var.common_labels
}

# Dead Letter Queue for failed messages
resource "google_pubsub_topic" "incoming_dlq" {
  name   = "${local.resource_prefix}-incoming-dlq"
  labels = var.common_labels
}
```

### Step 6: Configure IAM Permissions

Grant least-privilege access:

```hcl
# iam.tf
# Get current project
data "google_project" "current" {}

# Service account for application
data "google_service_account" "app_runtime" {
  account_id = "app-runtime"
}

# Grant publisher permission to application
resource "google_pubsub_topic_iam_member" "publisher" {
  topic  = google_pubsub_topic.incoming.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${data.google_service_account.app_runtime.email}"
}

# Grant subscriber permission to application
resource "google_pubsub_subscription_iam_member" "subscriber" {
  subscription = google_pubsub_subscription.incoming_sub.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${data.google_service_account.app_runtime.email}"
}
```

### Step 7: Define Outputs

Export important values:

```hcl
# outputs.tf
output "pubsub_topic_name" {
  description = "Name of the Pub/Sub incoming topic"
  value       = google_pubsub_topic.incoming.name
}

output "pubsub_subscription_name" {
  description = "Name of the Pub/Sub incoming subscription"
  value       = google_pubsub_subscription.incoming_sub.name
}

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}
```

Access outputs after apply:
```bash
terraform output pubsub_topic_name
```

## Examples

### Example 1: Multi-Environment Setup

```hcl
# terraform.tfvars.labs
environment = "labs"
region      = "europe-west2"

# terraform.tfvars.prod
environment = "prod"
region      = "europe-west2"
```

Apply to different environments:
```bash
terraform apply -var-file="terraform.tfvars.labs"   # Deploy to labs
terraform apply -var-file="terraform.tfvars.prod"   # Deploy to prod
```

### Example 2: Using for_each for Multiple Resources

```hcl
# pubsub.tf
locals {
  pubsub_topics = {
    "incoming" = {
      retention_days = 7
      iam_publishers = ["app-runtime"]
    }
    "replies" = {
      retention_days = 3
      iam_publishers = ["notification-service"]
    }
    "dlq" = {
      retention_days = 14
      iam_publishers = []
    }
  }
}

# Create all topics in one block
resource "google_pubsub_topic" "topics" {
  for_each = local.pubsub_topics

  name                    = "${local.app_name}-${each.key}-${var.environment}"
  message_retention_duration = "${each.value.retention_days * 24 * 60 * 60}s"
  labels                  = var.common_labels
}

# Reference specific topic
output "incoming_topic" {
  value = google_pubsub_topic.topics["incoming"].name
}
```

### Example 3: Secure Secrets Management

```hcl
# ❌ NEVER DO THIS
variable "db_password" {
  type    = string
  default = "SuperSecret123"  # Terrible!
}

# ✅ USE GOOGLE SECRET MANAGER INSTEAD
data "google_secret_manager_secret_version" "db_password" {
  secret = "database-password"
}

resource "google_sql_database_instance" "main" {
  # password comes from Secret Manager
  settings {
    database_flags {
      name  = "password"
      value = data.google_secret_manager_secret_version.db_password.secret_data
    }
  }
}

# Mark outputs as sensitive
output "db_connection_string" {
  value     = google_sql_database_instance.main.connection_name
  sensitive = true  # Won't print to console
}
```

### Example 4: Complex Resource with Validation

```hcl
# iam.tf
resource "google_project_iam_member" "app_pubsub_access" {
  project = data.google_project.current.project_id

  # ✅ Least privilege: specific role
  role   = "roles/pubsub.editor"

  # ✅ Specific service account
  member = "serviceAccount:${data.google_service_account.app_runtime.email}"

  # ✅ Condition for additional security
  condition {
    title = "Only in production"
    expression = "resource.matchTag('environment', 'production')"
  }
}
```

### Example 5: Essential Terraform Commands

```bash
# Initialize (first run or after provider changes)
terraform init

# Preview changes (always run before apply!)
terraform plan

# Save plan for review
terraform plan -out=tfplan

# Apply changes
terraform apply

# Apply saved plan
terraform apply tfplan

# View current state
terraform state list
terraform state show google_pubsub_topic.incoming

# Destroy infrastructure (WARNING: deletes resources!)
terraform destroy

# Target specific resource
terraform apply -target=google_pubsub_topic.incoming

# View outputs
terraform output

# Validate syntax
terraform validate

# Format code
terraform fmt -recursive
```

## Requirements

- Terraform 1.x+ installed
- GCP credentials (via `gcloud auth application-default login` or service account key)
- GCS bucket for remote state (pre-created)
- Proper IAM permissions in GCP (Owner or Editor role)

**Installation**:
```bash
# macOS
brew install terraform

# Linux/Mac via tfenv (recommended for version management)
git clone https://github.com/tfutils/tfenv.git ~/.tfenv
~/.tfenv/bin/tfenv install 1.6.0
~/.tfenv/bin/tfenv use 1.6.0

# Verify
terraform version
```

## See Also

- **Core Concepts**: Resources, Data Sources, Providers, Backends, State
- **Best Practices**: Naming Conventions, Variable Validation, Least Privilege
- **Security**: Secrets Management, IAM Bindings, Sensitive Values
- **State Management**: Remote State, Locking, Migration
- **Modules**: Reusable configurations, Module structure, Versioning
- **Workflows**: `init`, `plan`, `apply`, `destroy`, `state` commands
- **Troubleshooting**: State drift, Provider issues, Locking problems
