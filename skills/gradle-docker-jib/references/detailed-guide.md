# Gradle Docker Jib - Detailed Reference

This document provides comprehensive examples, commands, troubleshooting, and best practices for building Docker images with Jib.

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


