---
name: gradle-spring-boot-integration
description: |
  Integrate Gradle with Spring Boot projects, including plugin setup, bootable JAR creation,
  layered JARs for Docker, and multi-module Spring Boot configurations.
  Use when setting up Spring Boot builds, creating executable JARs, or configuring
  microservices with shared libraries.
---

# Gradle Spring Boot Integration

## Table of Contents

- [Purpose](#purpose)
- [When to Use](#when-to-use)
- [Quick Start](#quick-start)
- [Instructions](#instructions)
- [Examples](#examples)
- [Commands Reference](#commands-reference)
- [Troubleshooting](#troubleshooting)
- [See Also](#see-also)

## Purpose

Set up and configure Spring Boot projects in Gradle with proper JAR creation, Docker optimization, and multi-module support. This skill covers bootable JAR setup, layered JARs for optimal Docker caching, and Spring Boot-specific task configuration.

## When to Use

Use this skill when you need to:
- Set up new Spring Boot projects with Gradle
- Create executable JAR files for Spring Boot applications
- Configure layered JARs for optimized Docker builds
- Set up multi-module projects with shared libraries
- Configure Spring Boot DevTools for hot reload
- Inject build information into application.yml
- Set up Spring Boot Actuator for monitoring
- Configure testing with Spring Boot test starters

## Quick Start

Minimal Spring Boot setup in `build.gradle.kts`:

```kotlin
plugins {
    id("java")
    id("org.springframework.boot") version "3.5.5"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "com.example"
version = "0.0.1-SNAPSHOT"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}
```

Run and build:

```bash
./gradlew bootRun                                    # Run locally
./gradlew bootJar                                    # Create executable JAR
./gradlew bootRun --args='--spring.profiles.active=dev'  # Run with profile
```

## Instructions

### Step 1: Apply Spring Boot Plugin

Configure the Spring Boot Gradle plugin for your project type:

```kotlin
// build.gradle.kts - Web Service (creates bootable JAR)
plugins {
    id("java")
    id("org.springframework.boot") version "3.5.5"
    id("io.spring.dependency-management") version "1.1.7"
}
```

**Key plugins**:
- `org.springframework.boot`: Creates executable JARs, provides bootRun task
- `io.spring.dependency-management`: Automatically imports Spring Boot BOM

### Step 2: Configure Java Toolchain

Specify Java version for consistency:

```kotlin
java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}
```

### Step 3: Add Spring Boot Dependencies

Use the BOM automatically imported by the plugin:

```kotlin
dependencies {
    // Spring Boot starter (no version needed - from BOM)
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")

    // Development only (DevTools for hot reload)
    developmentOnly("org.springframework.boot:spring-boot-devtools")

    // Test dependencies
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

// Enable JUnit 5
tasks.test {
    useJUnitPlatform()
}
```

### Step 4: Configure Bootable JAR Creation

**For services (executable JARs)**:

```kotlin
tasks.bootJar {
    enabled = true
    archiveClassifier = ""  // No classifier for main artifact
}

tasks.jar {
    enabled = false  // Disable plain JAR
}
```

**For libraries (plain JARs)**:

```kotlin
tasks.bootJar {
    enabled = false  // Not executable
}

tasks.jar {
    enabled = true  // Create library JAR
}
```

### Step 5: Enable Layered JARs for Docker Optimization

Layered JARs separate dependencies by change frequency for better Docker caching:

```kotlin
tasks.bootJar {
    enabled = true

    layered {
        enabled = true
        application {
            enabled = true
        }
        dependencies {
            enabled = true
        }
        springBootLoader {
            enabled = true
        }
        snapshot {
            enabled = true
        }
    }
}
```

**Layers** (in order):
1. **dependencies**: Rarely-changing external dependencies
2. **spring-boot-loader**: Spring Boot loader classes
3. **snapshot-dependencies**: Snapshot/SNAPSHOT versions (changing)
4. **application**: Application classes (most frequently changing)

**Extract layers in Dockerfile**:

```dockerfile
FROM eclipse-temurin:21-jre-alpine AS builder
WORKDIR /builder
COPY build/libs/app.jar .
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre-alpine
WORKDIR /app
COPY --from=builder /builder/dependencies ./
COPY --from=builder /builder/spring-boot-loader ./
COPY --from=builder /builder/snapshot-dependencies ./
COPY --from=builder /builder/application ./
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

### Step 6: Configure Application Properties

Inject build information into `application.yml`:

```kotlin
tasks.processResources {
    filesMatching("application.yml") {
        expand(
            "version" to project.version,
            "name" to project.name,
            "timestamp" to System.currentTimeMillis()
        )
    }
}
```

In `application.yml`:

```yaml
spring:
  application:
    name: ${name}

info:
  app:
    name: ${name}
    version: ${version}
    build-timestamp: ${timestamp}
```

### Step 7: Set Up Spring Boot DevTools for Local Development

Enable hot reload during development:

```kotlin
dependencies {
    developmentOnly("org.springframework.boot:spring-boot-devtools")
}
```

**Trigger reload**:
- **IntelliJ**: Build Project (Cmd/Ctrl + F9)
- **Eclipse**: Save file
- **CLI**: Run `./gradlew compileJava` in separate terminal

### Step 8: Configure Actuator for Monitoring

Add actuator endpoints and metrics:

```kotlin
dependencies {
    implementation("org.springframework.boot:spring-boot-starter-actuator")
    implementation("io.micrometer:micrometer-registry-prometheus")
}
```

In `application.yml`:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics,env
  metrics:
    export:
      prometheus:
        enabled: true
  endpoint:
    health:
      show-details: always
```

## Examples

### Example 1: Simple Web Service

```kotlin
// build.gradle.kts
plugins {
    id("java")
    id("org.springframework.boot") version "3.5.5"
    id("io.spring.dependency-management") version "1.1.7"
}

group = "com.waitrose"
version = "1.0.0"

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-actuator")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test {
    useJUnitPlatform()
}

tasks.bootJar {
    enabled = true
}

tasks.jar {
    enabled = false
}
```

Build and run:

```bash
./gradlew bootJar              # Create JAR: build/libs/app-1.0.0.jar
java -jar build/libs/app-1.0.0.jar  # Run JAR
```

### Example 2: Multi-Module with Shared Library

```kotlin
// settings.gradle.kts
rootProject.name = "supplier-charges"
include("shared-domain")
include("shared-api")
include("supplier-charges-hub")
```

```kotlin
// Root build.gradle.kts
plugins {
    id("java") apply false
    id("org.springframework.boot") version "3.5.5" apply false
    id("io.spring.dependency-management") version "1.1.7" apply false
}

subprojects {
    apply(plugin = "java")
    apply(plugin = "io.spring.dependency-management")

    group = "com.waitrose"
    version = "1.0.0"

    java {
        toolchain {
            languageVersion = JavaLanguageVersion.of(21)
        }
    }

    repositories {
        mavenCentral()
    }

    dependencies {
        testImplementation("org.springframework.boot:spring-boot-starter-test")
    }

    tasks.test {
        useJUnitPlatform()
    }
}
```

```kotlin
// shared-domain/build.gradle.kts
plugins {
    id("java-library")
}

dependencies {
    api("org.springframework.boot:spring-boot-starter-data-jpa")
}

// Library - create plain JAR
tasks.bootJar {
    enabled = false
}

tasks.jar {
    enabled = true
}
```

```kotlin
// supplier-charges-hub/build.gradle.kts
plugins {
    id("org.springframework.boot")
}

dependencies {
    implementation(project(":shared-domain"))
    implementation(project(":shared-api"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    developmentOnly("org.springframework.boot:spring-boot-devtools")
}

// Service - create bootable JAR
tasks.bootJar {
    enabled = true
    layered {
        enabled = true
    }
}

tasks.jar {
    enabled = false
}
```

Build and test:

```bash
./gradlew clean build          # Build all modules
./gradlew :supplier-charges-hub:bootJar  # Build specific service
java -jar supplier-charges-hub/build/libs/supplier-charges-hub-1.0.0.jar
```

### Example 3: Layered JAR with Dockerfile

`build.gradle.kts`:

```kotlin
tasks.bootJar {
    enabled = true
    layered {
        enabled = true
    }
}
```

`Dockerfile`:

```dockerfile
# Multi-stage build using layered JAR
FROM eclipse-temurin:21-jre-alpine AS builder

WORKDIR /builder
COPY build/libs/supplier-charges-hub-1.0.0.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

# Final image
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Copy layers (most frequently changed last)
COPY --from=builder /builder/dependencies ./
COPY --from=builder /builder/spring-boot-loader ./
COPY --from=builder /builder/snapshot-dependencies ./
COPY --from=builder /builder/application ./

# Non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# JVM configuration for containers
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -Xms256m"

EXPOSE 8080
ENTRYPOINT ["java", "org.springframework.boot.loader.launch.JarLauncher"]
```

Build:

```bash
./gradlew bootJar
docker build -t supplier-charges-hub:1.0.0 .
docker run -p 8080:8080 supplier-charges-hub:1.0.0
```

### Example 4: Application Properties with Build Info

`build.gradle.kts`:

```kotlin
tasks.processResources {
    filesMatching("application.yml") {
        expand(
            "version" to project.version,
            "name" to project.name,
            "build.timestamp" to System.currentTimeMillis(),
            "build.number" to System.getenv("BUILD_NUMBER") ?: "local"
        )
    }
}
```

`src/main/resources/application.yml`:

```yaml
spring:
  application:
    name: ${name}

info:
  app:
    name: ${name}
    version: ${version}
    build-timestamp: ${build.timestamp}
    build-number: ${build.number}
  java:
    version: '@java.version@'
    compiler: '@java.compiler@'
```

Access via actuator:

```bash
curl http://localhost:8080/actuator/info
# {"app":{"name":"supplier-charges-hub","version":"1.0.0",...}}
```

### Example 5: Testing Configuration

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.testcontainers:testcontainers:1.21.0")
    testImplementation("org.testcontainers:junit-jupiter:1.21.0")
    testImplementation("org.testcontainers:postgresql:1.21.0")
}

tasks.test {
    useJUnitPlatform()

    // Test filtering
    filter {
        includeTestsMatching("*Test")
        excludeTestsMatching("*IntegrationTest")
    }

    // Parallel test execution
    maxParallelForks = Runtime.getRuntime().availableProcessors() / 2

    // Test logging
    testLogging {
        events("passed", "skipped", "failed")
        showExceptions = true
        showStackTraces = true
        showCauses = true
        exceptionFormat = org.gradle.api.tasks.testing.logging.TestExceptionFormat.FULL
    }
}
```

## Commands Reference

```bash
# === RUNNING ===
./gradlew bootRun                                     # Run the app
./gradlew bootRun --args='--spring.profiles.active=dev'  # With profile

# === BUILDING ===
./gradlew bootJar                                     # Build executable JAR
./gradlew bootWar                                     # Build executable WAR
./gradlew build                                       # Build everything

# === TESTING ===
./gradlew test                                        # Run unit tests
./gradlew test --tests "*IntegrationTest"             # Run specific tests

# === INFORMATION ===
./gradlew bootRun --args='--help'                     # Show Spring Boot help
./gradlew properties                                  # Show project properties

# === CLEANUP ===
./gradlew clean                                       # Clean build outputs
```

## Troubleshooting

**DevTools hot reload not working**:
- Ensure it's in `developmentOnly` configuration
- Run `./gradlew compileJava` to trigger reload
- Check IDE auto-build settings

**JAR not executable**:
- Verify `bootJar.enabled = true`
- Check `java -jar build/libs/app.jar`
- Ensure main class is detected (usually automatic)

**Missing dependencies in JAR**:
- Check configuration: use `implementation` not `compileOnly`
- Verify BOM is imported correctly
- Run `./gradlew dependencies` to inspect tree

## See Also

- [gradle-dependency-management](../gradle-dependency-management/SKILL.md) - Manage Spring Boot BOMs and versions
- [gradle-docker-jib](../gradle-docker-jib/SKILL.md) - Build Docker images with Jib
- [gradle-testing-setup](../gradle-testing-setup/SKILL.md) - Configure Spring Boot testing
- [Spring Boot Gradle Plugin Documentation](https://docs.spring.io/spring-boot/docs/current/gradle-plugin/reference/)
- [Spring Boot Reference Guide](https://docs.spring.io/spring-boot/docs/)
