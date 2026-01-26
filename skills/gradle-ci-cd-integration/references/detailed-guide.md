# Gradle CI/CD Integration - Detailed Reference

This document provides comprehensive examples, commands, best practices, and troubleshooting for Gradle CI/CD integration.

## Examples

### Example 1: GitHub Actions Complete Pipeline

```yaml
# .github/workflows/build.yml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        java-version: [21]

    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK
      uses: actions/setup-java@v4
      with:
        java-version: ${{ matrix.java-version }}
        distribution: 'temurin'

    - name: Setup Gradle (with caching)
      uses: gradle/actions/setup-gradle@v4
      with:
        cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}

    - name: Build with Gradle
      run: ./gradlew build --parallel --build-cache --scan
      env:
        CI: true

    - name: Run Tests
      run: ./gradlew test jacocoTestReport
      if: always()

    - name: Publish Test Results
      uses: mikepenz/action-junit-report@v4
      if: always()
      with:
        report_paths: '**/build/test-results/test/TEST-*.xml'

    - name: Upload Coverage to Codecov
      uses: codecov/codecov-action@v5
      with:
        files: ./build/reports/jacoco/test/jacocoTestReport.xml
        fail_ci_if_error: false

    - name: Build Docker Image (PR)
      if: github.event_name == 'pull_request'
      run: ./gradlew jibDockerBuild

    - name: Build and Push Docker Image (Main)
      if: github.ref == 'refs/heads/main'
      run: ./gradlew jib
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    - name: Upload Build Artifacts
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: build-artifacts
        path: |
          build/libs/
          build/reports/
```

### Example 2: GitLab CI Complete Pipeline

```yaml
# .gitlab-ci.yml
image: gradle:8.11-jdk21-alpine

variables:
  GRADLE_OPTS: "-Dorg.gradle.daemon=false"
  GRADLE_USER_HOME: "$CI_PROJECT_DIR/.gradle"

cache:
  key: "$CI_COMMIT_REF_SLUG"
  paths:
    - .gradle/wrapper
    - .gradle/caches

stages:
  - build
  - test
  - quality
  - deploy

before_script:
  - export GRADLE_USER_HOME=`pwd`/.gradle
  - chmod +x ./gradlew

build:
  stage: build
  script:
    - ./gradlew assemble --parallel --build-cache
  artifacts:
    paths:
      - build/libs/
    expire_in: 1 day

test:
  stage: test
  script:
    - ./gradlew test --parallel --build-cache
  artifacts:
    when: always
    paths:
      - build/reports/tests/
      - build/test-results/
    reports:
      junit: build/test-results/test/TEST-*.xml

coverage:
  stage: quality
  script:
    - ./gradlew jacocoTestReport
  coverage: '/Total.*?([0-9]{1,3})%/'
  artifacts:
    paths:
      - build/reports/jacoco/

security:
  stage: quality
  script:
    - ./gradlew dependencyCheckAnalyze
  artifacts:
    paths:
      - build/reports/dependency-check-report.html
  allow_failure: true

docker-build:
  stage: deploy
  only:
    - main
  script:
    - ./gradlew jib
  environment:
    name: production
```

### Example 3: Jenkins Pipeline (Scripted)

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'gradle:8.11-jdk21'
            args '-v $HOME/.gradle:/home/gradle/.gradle'
        }
    }

    environment {
        GRADLE_OPTS = '-Dorg.gradle.daemon=false -Dorg.gradle.caching=true'
        CI = 'true'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }

    stages {
        stage('Build') {
            steps {
                sh './gradlew clean build --parallel --build-cache'
            }
        }

        stage('Test') {
            steps {
                sh './gradlew test jacocoTestReport'
            }
            post {
                always {
                    junit '**/build/test-results/test/TEST-*.xml'
                    publishHTML([
                        reportDir: 'build/reports/tests/test',
                        reportFiles: 'index.html',
                        reportName: 'Test Report'
                    ])
                    publishHTML([
                        reportDir: 'build/reports/jacoco/test/html',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
            }
        }

        stage('Security') {
            steps {
                sh './gradlew dependencyCheckAnalyze'
            }
            post {
                always {
                    publishHTML([
                        reportDir: 'build/reports/',
                        reportFiles: 'dependency-check-report.html',
                        reportName: 'Security Report'
                    ])
                }
            }
        }

        stage('Docker Build') {
            when {
                branch 'main'
            }
            steps {
                script {
                    withCredentials([
                        usernamePassword(
                            credentialsId: 'docker-registry',
                            usernameVariable: 'DOCKER_USERNAME',
                            passwordVariable: 'DOCKER_PASSWORD'
                        )
                    ]) {
                        sh './gradlew jib'
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            emailext(
                subject: "Build Failed: ${env.JOB_NAME}",
                body: "Check console output at ${env.BUILD_URL}",
                to: 'team@company.com'
            )
        }
    }
}
```

### Example 4: CircleCI Configuration

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  gradle: circleci/gradle@3.0.0

executors:
  gradle-executor:
    docker:
      - image: cimg/openjdk:21.0
    resource_class: large

jobs:
  build:
    executor: gradle-executor
    steps:
      - checkout
      - restore_cache:
          keys:
            - gradle-{{ checksum "build.gradle.kts" }}-{{ checksum "gradle/wrapper/gradle-wrapper.properties" }}
            - gradle-
      - run:
          name: Build
          command: ./gradlew build --parallel --build-cache
      - save_cache:
          paths:
            - ~/.gradle
          key: gradle-{{ checksum "build.gradle.kts" }}-{{ checksum "gradle/wrapper/gradle-wrapper.properties" }}
      - store_test_results:
          path: build/test-results/test
      - store_artifacts:
          path: build/reports
      - store_artifacts:
          path: build/libs

workflows:
  build-and-deploy:
    jobs:
      - build
```

### Example 5: Performance-Optimized CI Configuration

```yaml
# .github/workflows/optimized-build.yml
name: Optimized Build

on: [push, pull_request]

env:
  JAVA_VERSION: '21'
  GRADLE_BUILD_ACTION_CACHE_DEBUG_ENABLED: false

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-java@v4
      with:
        java-version: ${{ env.JAVA_VERSION }}
        distribution: 'temurin'

    - uses: gradle/actions/setup-gradle@v4
      with:
        cache-encryption-key: ${{ secrets.GRADLE_ENCRYPTION_KEY }}
        cache-read-only: ${{ github.ref != 'refs/heads/main' }}

    # Full optimized build
    - name: Build
      run: ./gradlew build --parallel --build-cache --configuration-cache --scan

    # Tests with parallel execution
    - name: Tests with Coverage
      run: ./gradlew test jacocoTestReport --parallel

    # Only build and push image on main branch
    - name: Docker Push (Main)
      if: github.ref == 'refs/heads/main'
      run: ./gradlew jib
      env:
        DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
        DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}

    # Upload results
    - name: Test Results
      uses: mikepenz/action-junit-report@v4
      if: always()
      with:
        report_paths: '**/build/test-results/test/TEST-*.xml'

    - name: Coverage
      uses: codecov/codecov-action@v5
      with:
        files: ./build/reports/jacoco/test/jacocoTestReport.xml
```



## Commands Reference

```bash
# === CI BUILDS ===

# Full optimized build for CI
./gradlew build --parallel --build-cache --configuration-cache --scan

# Build and test
./gradlew build --parallel --build-cache

# Tests only
./gradlew test --parallel

# With coverage
./gradlew test jacocoTestReport --parallel

# === DOCKER BUILDS ===

# Build and push image
./gradlew jib

# Build to local Docker (for PR testing)
./gradlew jibDockerBuild

# === REPORTS ===

# Generate test report
./gradlew test

# Generate coverage report
./gradlew jacocoTestReport

# Build scan for analysis
./gradlew build --scan

# === DEBUGGING ===

# With info logging
./gradlew build --info

# With debug logging
./gradlew build --debug

# Dry run (show what would happen)
./gradlew build --dry-run
```



## CI/CD Best Practices

1. **Always use Gradle Wrapper**: Ensures consistent Gradle version
2. **Enable build cache**: Use `org.gradle.caching=true`
3. **Parallel execution**: Use `--parallel` for multi-module builds
4. **Cache dependencies**: Cache `~/.gradle` directory
5. **Generate build scans**: Use `--scan` for CI troubleshooting
6. **Test reporting**: Collect JUnit XML results
7. **Coverage tracking**: Upload JaCoCo reports
8. **Fail fast**: Stop on first failure with `--fail-fast`
9. **Docker conditional**: Only push on main/tag branches
10. **Artifact management**: Store build outputs for debugging



## Troubleshooting CI Builds

**Build slower in CI than locally**:
- Check parallel execution: `--parallel`
- Verify build cache enabled: `org.gradle.caching=true`
- Generate build scan: `--scan`

**Dependency resolution timeouts**:
- Increase timeout in settings
- Use dependency locking: `--write-locks`
- Cache dependencies properly

**Tests fail in CI only**:
- Check Java version matches
- Verify environment variables
- Run with `--info` for details
- Check Docker running (for TestContainers)


