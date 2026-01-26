# Gradle Troubleshooting: Advanced Examples

## Slow Build Performance Analysis

```bash
# Build is slow
./gradlew build
# Took 3 minutes

# Profile the build
./gradlew build --profile
# Report: build/reports/profile/profile-2025-11-14-09-30-45.html

# Analysis shows:
# - Configuration phase: 45 seconds (slow!)
# - Compilation: 60 seconds
# - Tests: 90 seconds

# Solution: Enable configuration cache
# In gradle.properties:
echo "org.gradle.configuration-cache=true" >> gradle.properties
echo "org.gradle.caching=true" >> gradle.properties

./gradlew --stop
./gradlew build
# Took 45 seconds (88% faster!)
```

## Configuration Cache Debugging

```bash
# Build fails with configuration cache
./gradlew build --configuration-cache
# ERROR: Unsupported class: MyCustomTask

# Start with warnings
./gradlew build --configuration-cache-problems=warn

# Check report
open build/reports/configuration-cache/report.html
# Shows: Task 'MyCustomTask' is not serializable

# Solution: Update task to be configuration cache compatible
# In build.gradle.kts:
// Before
tasks.register("myTask") {
    // Non-cacheable work
}

// After
tasks.register("myTask") {
    @Input
    val myProperty = "value"
    // Make task properly input/output decorated
}

./gradlew build --configuration-cache
# SUCCESS!
```

## TestContainers Docker Issues

```bash
# Integration tests fail with Docker error
./gradlew integrationTest
# ERROR: Could not connect to Docker daemon

# Check Docker
docker ps
# Cannot connect to Docker daemon

# Solution: Start Docker
# On macOS
open /Applications/Docker.app

# Set environment variables
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
export DOCKER_HOST=unix://${HOME}/.docker/run/docker.sock

# Retry
./gradlew integrationTest
# BUILD SUCCESSFUL
```
