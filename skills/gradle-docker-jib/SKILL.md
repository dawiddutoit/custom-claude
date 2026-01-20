---
name: gradle-docker-jib
description: |
  Build optimized Docker images using Jib without Docker or Dockerfile.
  Use when containerizing Spring Boot microservices, building multi-architecture images,
  or pushing to registries. Includes Jib setup, multi-module configuration,
  and CI/CD integration.
---

# Gradle Docker Jib Integration

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Quick Start](#quick-start)
- [Instructions](#instructions)
- [Examples](#examples)
- [Commands Reference](#commands-reference)
- [Troubleshooting](#troubleshooting)
- [Image Best Practices](#image-best-practices)
- [See Also](#see-also)

## Purpose

Build Docker images efficiently using Google's Jib plugin without requiring Docker installation, Dockerfiles, or any container knowledge. Jib automatically optimizes layers and handles multi-architecture builds for both local and registry deployments.

## When to Use

Use this skill when you need to:
- Build Docker images without Docker daemon or Dockerfiles
- Containerize Spring Boot microservices efficiently
- Create multi-architecture images (amd64, arm64) for cloud deployment
- Optimize Docker layer caching for faster builds
- Push images to GCR, Docker Hub, or private registries
- Integrate Docker image building in CI/CD pipelines
- Configure JVM settings and container runtime parameters

## Quick Start

Add Jib plugin to `build.gradle.kts`:

```kotlin
plugins {
    id("com.google.cloud.tools.jib") version "3.4.4"
}

jib {
    from {
        image = "eclipse-temurin:21-jre-alpine"
    }

    to {
        image = "gcr.io/my-project/my-app"
        tags = setOf("latest", project.version.toString())
    }

    container {
        jvmFlags = listOf("-Xms512m", "-Xmx2048m")
        ports = listOf("8080")
        user = "1000:1000"
    }
}
```

Build and push:

```bash
./gradlew jib                    # Build and push to registry
./gradlew jibDockerBuild         # Build to local Docker daemon
./gradlew jibBuildTar            # Build as tar file
```

## Instructions

### Step 1: Add Jib Plugin

Add to `build.gradle.kts`:

```kotlin
plugins {
    id("com.google.cloud.tools.jib") version "3.4.4"
}
```

Or use version catalog (recommended for multi-module):

```kotlin
plugins {
    alias(libs.plugins.jib)
}
```

### Step 2: Configure Base Image

Choose appropriate base image for your application:

```kotlin
jib {
    from {
        // Lightweight JRE (recommended for Spring Boot)
        image = "eclipse-temurin:21-jre-alpine"

        // Or standard JRE
        image = "eclipse-temurin:21-jre"

        // Or JDK (if needed)
        image = "eclipse-temurin:21-jdk-alpine"

        // Multi-architecture support (amd64, arm64)
        platforms {
            platform {
                architecture = "amd64"
                os = "linux"
            }
            platform {
                architecture = "arm64"
                os = "linux"
            }
        }
    }
}
```

### Step 3: Configure Target Registry

Set up target image location and authentication:

```kotlin
jib {
    to {
        // Google Container Registry (GCR)
        image = "gcr.io/my-project/supplier-charges-hub"

        // Or Docker Hub
        image = "docker.io/mycompany/supplier-charges-hub"

        // Or private registry
        image = "registry.company.com/supplier-charges-hub"

        // Tags (version + latest)
        tags = setOf("latest", project.version.toString())

        // Authentication (from environment variables)
        auth {
            username = System.getenv("DOCKER_USERNAME")
            password = System.getenv("DOCKER_PASSWORD")
        }
    }
}
```

### Step 4: Configure Container Runtime

Set JVM arguments, ports, and environment:

```kotlin
jib {
    container {
        // JVM flags for optimal performance
        jvmFlags = listOf(
            "-Xms512m",                           // Initial heap
            "-Xmx2048m",                          // Max heap
            "-XX:+UseG1GC",                       // Garbage collector
            "-XX:MaxGCPauseMillis=200",           // GC pause time
            "-Djava.security.egd=file:/dev./urandom"  // Entropy
        )

        // Exposed ports
        ports = listOf("8080", "8081")

        // Environment variables
        environment = mapOf(
            "SPRING_PROFILES_ACTIVE" to "production",
            "JAVA_TOOL_OPTIONS" to "-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"
        )

        // Image labels for metadata
        labels = mapOf(
            "maintainer" to "platform-team@company.com",
            "version" to project.version.toString()
        )

        // Non-root user (security best practice)
        user = "1000:1000"

        // Reproducible builds (EPOCH = timestamp 0)
        creationTime = "EPOCH"  // Or "USE_CURRENT_TIMESTAMP"
    }
}
```

### Step 5: Configure Extra Files (Optional)

Add configuration files to the container:

```kotlin
jib {
    extraDirectories {
        paths {
            path {
                from = file("src/main/jib")
                into = "/app/config"
            }
        }
    }
}
```

Create files in `src/main/jib/app/config/`:

```
src/main/jib/
└── app/
    └── config/
        ├── application-prod.yml
        └── logback.xml
```

### Step 6: Handle Authentication

**Environment variables** (recommended):

```kotlin
jib {
    to {
        auth {
            username = System.getenv("DOCKER_USERNAME")
            password = System.getenv("DOCKER_PASSWORD")
        }
    }
}
```

**Docker config** (from `~/.docker/config.json`):

```bash
# Login once
docker login -u username -p password gcr.io

# Jib will automatically use stored credentials
./gradlew jib
```

**Gradle properties** (fallback):

```properties
# gradle.properties
jibTo.username=myuser
jibTo.password=mytoken
```

### Step 7: Multi-Module Configuration

Configure common Jib settings in root `build.gradle.kts`:

```kotlin
// Root build.gradle.kts
subprojects {
    plugins.withId("com.google.cloud.tools.jib") {
        configure<com.google.cloud.tools.jib.gradle.JibExtension> {
            from {
                image = "eclipse-temurin:21-jre-alpine"
            }

            to {
                image = "gcr.io/my-project/${project.name}"
                tags = setOf("latest", rootProject.version.toString())

                auth {
                    username = System.getenv("DOCKER_USERNAME")
                    password = System.getenv("DOCKER_PASSWORD")
                }
            }

            container {
                jvmFlags = listOf(
                    "-Xms512m",
                    "-Xmx2048m",
                    "-XX:+UseContainerSupport"
                )

                ports = listOf("8080")
                user = "1000:1000"
                creationTime = "EPOCH"
            }
        }
    }
}
```

Each module can override with specific settings:

```kotlin
// supplier-charges-hub/build.gradle.kts
configure<com.google.cloud.tools.jib.gradle.JibExtension> {
    container {
        ports = listOf("8080", "8081")  // Additional port
        jvmFlags = listOf(
            "-Xms512m",
            "-Xmx3048m"  // More memory for this service
        )
    }
}
```

## Examples

### Example 1: Complete Jib Configuration

```kotlin
// build.gradle.kts
plugins {
    id("java")
    id("org.springframework.boot") version "3.5.5"
    id("io.spring.dependency-management") version "1.1.7"
    id("com.google.cloud.tools.jib") version "3.4.4"
}

group = "com.waitrose"
version = "1.0.0"

jib {
    // Base image
    from {
        image = "eclipse-temurin:21-jre-alpine"
        platforms {
            platform { architecture = "amd64"; os = "linux" }
            platform { architecture = "arm64"; os = "linux" }
        }
    }

    // Target registry
    to {
        image = "gcr.io/supplier-charges/supplier-charges-hub"
        tags = setOf("latest", "v${project.version}", "stable")

        auth {
            username = System.getenv("DOCKER_USERNAME")
            password = System.getenv("DOCKER_PASSWORD")
        }
    }

    // Container configuration
    container {
        jvmFlags = listOf(
            "-Xms512m",
            "-Xmx2048m",
            "-XX:+UseG1GC",
            "-XX:MaxGCPauseMillis=200",
            "-Djava.security.egd=file:/dev./urandom",
            "-XX:+UseContainerSupport",
            "-XX:MaxRAMPercentage=75.0"
        )

        ports = listOf("8080", "8081")  // 8080: app, 8081: actuator

        environment = mapOf(
            "SPRING_PROFILES_ACTIVE" to "production",
            "LOG_LEVEL" to "INFO",
            "TZ" to "UTC"
        )

        labels = mapOf(
            "maintainer" to "platform-team@waitrose.com",
            "app.version" to "${project.version}",
            "app.name" to "${project.name}",
            "build.date" to System.currentTimeMillis().toString()
        )

        // Non-root user
        user = "1000:1000"

        // Reproducible builds
        creationTime = "EPOCH"
    }

    // Extra files
    extraDirectories {
        paths {
            path {
                from = file("src/main/jib")
                into = "/app/config"
            }
        }
    }
}
```

### Example 2: Multi-Architecture Build

```kotlin
jib {
    from {
        image = "eclipse-temurin:21-jre-alpine"
        platforms {
            // Build for both AMD64 and ARM64
            platform {
                architecture = "amd64"
                os = "linux"
            }
            platform {
                architecture = "arm64"  // Apple Silicon, AWS Graviton2
                os = "linux"
            }
        }
    }

    to {
        image = "gcr.io/my-project/my-app"
        tags = setOf("latest", "${project.version}")
    }
}
```

Build:

```bash
# Builds both architectures and pushes
./gradlew jib

# For local testing
./gradlew jibDockerBuild
# Then check available architectures
docker image inspect my-app:latest | grep -A 5 Architecture
```

### Example 3: CI/CD Integration with GitHub Actions

```yaml
# .github/workflows/docker-build.yml
name: Build and Push Docker Image

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 21
      uses: actions/setup-java@v4
      with:
        java-version: '21'
        distribution: 'temurin'

    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v4

    - name: Build Docker Image with Jib
      run: ./gradlew jib
      if: github.ref == 'refs/heads/main'
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build Local Docker Image (PR)
      run: ./gradlew jibDockerBuild
      if: github.ref != 'refs/heads/main'
```

### Example 4: GitLab CI/CD Integration

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

variables:
  GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.caching=true"

build-image:
  stage: deploy
  image: gradle:8.11-jdk21-alpine
  only:
    - main
  script:
    - chmod +x ./gradlew
    - ./gradlew jib
      -Djib.to.auth.username=$DOCKER_USERNAME
      -Djib.to.auth.password=$DOCKER_PASSWORD
  environment:
    name: production
```

### Example 5: Local Testing Before Push

```bash
# Build to local Docker daemon (requires Docker)
./gradlew jibDockerBuild

# Test locally
docker run -p 8080:8080 supplier-charges-hub:latest

# Access application
curl http://localhost:8080/actuator/health

# Check image size
docker images supplier-charges-hub
# REPOSITORY                SIZE
# supplier-charges-hub:latest  250MB
```

### Example 6: Debugging Image Contents

```bash
# Build as tar file
./gradlew jibBuildTar --image=supplier-charges-hub:latest

# Extract and inspect
mkdir image-contents
cd image-contents
tar xf ../build/jib-image.tar

# Browse layers
ls -la
# app/
# config/
# layers/
```

### Example 7: Multi-Module with Shared Configuration

```kotlin
// Root build.gradle.kts
subprojects {
    plugins.withId("com.google.cloud.tools.jib") {
        configure<com.google.cloud.tools.jib.gradle.JibExtension> {
            from {
                image = "eclipse-temurin:21-jre-alpine"
                platforms {
                    platform { architecture = "amd64"; os = "linux" }
                    platform { architecture = "arm64"; os = "linux" }
                }
            }

            to {
                image = "gcr.io/my-company/${project.name}"
                tags = setOf("latest", rootProject.version.toString())

                auth {
                    username = System.getenv("DOCKER_USERNAME")
                    password = System.getenv("DOCKER_PASSWORD")
                }
            }

            container {
                jvmFlags = listOf(
                    "-Xms512m",
                    "-Xmx2048m",
                    "-XX:+UseContainerSupport",
                    "-XX:MaxRAMPercentage=75.0"
                )

                user = "1000:1000"
                creationTime = "EPOCH"
            }
        }
    }
}
```

## Commands Reference

```bash
# === BUILDING ===

# Build and push to registry
./gradlew jib

# Build to local Docker daemon (requires Docker)
./gradlew jibDockerBuild

# Build as tar file (no Docker needed)
./gradlew jibBuildTar

# Dry run (show what would be done)
./gradlew jib --dry-run

# === CONFIGURATION ===

# Override base image via command line
./gradlew jib -Djib.from.image=eclipse-temurin:21-jdk-alpine

# Override target image
./gradlew jib -Djib.to.image=gcr.io/my-project/my-app

# Override tags
./gradlew jib -Djib.to.tags=latest,v1.0.0

# === DEBUGGING ===

# Verbose output
./gradlew jib --info

# Very verbose output
./gradlew jib --debug

# Show what would be built
./gradlew jib --dry-run --info
```

## Troubleshooting

**Authentication failures**:
- Ensure credentials are set: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- Test with `docker login`: `docker login -u $DOCKER_USERNAME gcr.io`
- Check credentials haven't expired

**Image too large**:
- Use `-alpine` base images (much smaller)
- Verify only needed dependencies in build
- Check layering in `container { jvmFlags }` config

**Multi-architecture build fails**:
- Ensure registry supports multi-arch (GCR, Docker Hub do)
- Check `platforms` configuration includes both amd64 and arm64
- Use `./gradlew jibDockerBuild` first for single-arch testing

**Permission denied - non-root user**:
- Verify `user = "1000:1000"` is set
- Ensure application can write to needed directories
- Run as numeric UID (not username) for Kubernetes compatibility

**Slow builds**:
- Enable Gradle build cache: `org.gradle.caching=true`
- Use configuration cache: `org.gradle.configuration-cache=true`
- Run with `--parallel`

## Image Best Practices

- Use `-jre-alpine` base images (smallest, recommended)
- Set `creationTime = "EPOCH"` for reproducible builds
- Use non-root user: `user = "1000:1000"`
- Configure container memory for Kubernetes: `-XX:MaxRAMPercentage=75.0`
- Tag with version AND commit SHA for traceability
- Keep JVM flags minimal (only production-critical ones)
- Add labels for monitoring and debugging

## See Also

- [gradle-spring-boot-integration](../gradle-spring-boot-integration/SKILL.md) - Create Spring Boot JARs for Jib
- [gradle-performance-optimization](../gradle-performance-optimization/SKILL.md) - Speed up builds before containerizing
- [gradle-ci-cd-integration](../gradle-ci-cd-integration/SKILL.md) - Integrate with GitHub Actions, GitLab CI
- [Jib Documentation](https://github.com/GoogleContainerTools/jib)
- [Google Container Registry Documentation](https://cloud.google.com/container-registry/docs)
