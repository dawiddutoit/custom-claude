# Spring Boot Gradle Integration: Advanced Examples

## Multi-Module with Shared Library

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

## Layered JAR with Dockerfile

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

## Application Properties with Build Info

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

## Testing Configuration

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
