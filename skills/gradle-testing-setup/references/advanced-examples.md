# Gradle Testing: Advanced Examples

## Complete Testing Configuration

```kotlin
// build.gradle.kts
plugins {
    id("java")
    id("org.springframework.boot") version "3.5.5"
    id("jacoco")
    id("com.adarshr.test-logger") version "4.0.0"
}

// === DEPENDENCIES ===
dependencies {
    // Unit testing
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.0")

    // Integration testing with containers
    testImplementation("org.testcontainers:testcontainers:1.21.0")
    testImplementation("org.testcontainers:junit-jupiter:1.21.0")
    testImplementation("org.testcontainers:postgresql:1.21.0")
    testImplementation("org.testcontainers:gcloud:1.21.0")

    testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.11.0")
}

// === SOURCE SETS ===
sourceSets {
    create("integrationTest") {
        java {
            srcDir("src/integrationTest/java")
            compileClasspath += sourceSets.main.get().output + sourceSets.test.get().output
            runtimeClasspath += sourceSets.main.get().output + sourceSets.test.get().output
        }
        resources {
            srcDir("src/integrationTest/resources")
        }
    }
}

// === UNIT TESTS ===
tasks.test {
    useJUnitPlatform {
        excludeTags("integration", "slow")
    }

    filter {
        excludeTestsMatching("*IntegrationTest")
    }

    maxParallelForks = Runtime.getRuntime().availableProcessors() / 2

    testLogging {
        events("passed", "skipped", "failed")
        showExceptions = true
        showStackTraces = true
    }

    finalizedBy(tasks.jacocoTestReport)
}

// === INTEGRATION TESTS ===
val integrationTest = tasks.register<Test>("integrationTest") {
    description = "Run integration tests"
    group = "verification"

    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath

    useJUnitPlatform {
        includeTags("integration")
    }

    shouldRunAfter(tasks.test)

    systemProperty("testcontainers.reuse.enable", "true")

    testLogging {
        events("passed", "skipped", "failed")
        showExceptions = true
    }
}

// === CODE COVERAGE ===
jacoco {
    toolVersion = "0.8.12"
}

tasks.jacocoTestReport {
    dependsOn(tasks.test)

    reports {
        xml.required = true
        html.required = true
    }

    finalizedBy(tasks.jacocoTestCoverageVerification)
}

tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            element = "BUNDLE"
            limit {
                minimum = BigDecimal("0.60")
            }
        }

        rule {
            element = "CLASS"
            excludes = listOf("**/config/*", "**/dto/*")
            limit {
                counter = "LINE"
                value = "COVEREDRATIO"
                minimum = BigDecimal("0.50")
            }
        }
    }
}

// === TEST LOGGER ===
testlogger {
    theme = "mocha"
    showExceptions = true
    slowThreshold = 2000
}

// === INCLUDE IN OVERALL CHECK ===
tasks.check {
    dependsOn(integrationTest)
    dependsOn(tasks.jacocoTestReport)
}
```

## TestContainers Integration Test

```java
// src/integrationTest/java/com/example/SupplierServiceIntegrationTest.java
package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@Testcontainers
class SupplierServiceIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
        .withDatabaseName("testdb")
        .withUsername("test")
        .withPassword("test");

    @Autowired
    private SupplierService supplierService;

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Test
    void testCreateSupplier() {
        Supplier supplier = supplierService.create("New Supplier");
        assertThat(supplier).isNotNull();
        assertThat(supplier.getId()).isPositive();
        assertThat(supplier.getName()).isEqualTo("New Supplier");
    }
}
```

## GitHub Actions with Coverage Reports

```yaml
# .github/workflows/test.yml
name: Tests and Coverage

on: [push, pull_request]

jobs:
  test:
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

    - name: Run unit tests
      run: ./gradlew test

    - name: Run integration tests
      run: ./gradlew integrationTest

    - name: Generate coverage report
      run: ./gradlew jacocoTestReport

    - name: Upload to Codecov
      uses: codecov/codecov-action@v5
      with:
        files: ./build/reports/jacoco/test/jacocoTestReport.xml

    - name: Publish test results
      uses: mikepenz/action-junit-report@v4
      if: always()
      with:
        report_paths: '**/build/test-results/test/TEST-*.xml'
```

## Coverage Report Verification in CI

```properties
# gradle.properties
org.gradle.logging.level=info
org.gradle.parallel=true

# Fail CI if coverage below threshold
jacoco.coverage.minimum=0.60
```

```kotlin
// build.gradle.kts
tasks.jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = BigDecimal(project.property("jacoco.coverage.minimum") as String)
            }
        }
    }
}
```

Run:

```bash
# Local testing
./gradlew jacocoTestReport

# View report
open build/reports/jacoco/test/html/index.html

# CI will automatically fail if coverage < 0.60
```
