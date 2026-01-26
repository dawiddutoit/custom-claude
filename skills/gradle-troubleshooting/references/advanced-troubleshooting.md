# Gradle Troubleshooting: Advanced Techniques

## Performance Troubleshooting

### Diagnose Slow Builds

Use profiling to identify bottlenecks:

```bash
# Generate profile report
./gradlew build --profile

# Report location
# build/reports/profile/profile-<timestamp>.html
open build/reports/profile/profile-*.html

# Or use build scan (cloud-based analysis)
./gradlew build --scan
```

**Common slow build causes**:

**Configuration phase slow**:
```bash
# Check what's slow in configuration
./gradlew build --info 2>&1 | grep -E "Evaluating|Processing"

# Enable configuration cache
./gradlew build --configuration-cache
```

**Compilation slow**:
```bash
# Enable incremental compilation (should be default)
# Check for full recompilation
./gradlew build --info 2>&1 | grep -i "incremental\|full"

# Clean and rebuild
./gradlew clean build
```

**Tests slow**:
```bash
# Run unit tests only (exclude integration tests)
./gradlew test -x integrationTest

# Enable parallel test execution
# In build.gradle.kts:
# tasks.test { maxParallelForks = Runtime.getRuntime().availableProcessors() / 2 }
```

**Network slow**:
```bash
# Check network dependency resolution
./gradlew build --info 2>&1 | grep "Downloading\|Uploading"

# Use offline mode if dependencies are cached
./gradlew build --offline

# Check repositories configuration
./gradlew build --info 2>&1 | grep repositories
```

## Daemon Management Issues

Handle daemon-related problems:

```bash
# Check daemon status
./gradlew --status

# Stop all daemons
./gradlew --stop

# Run without daemon (if daemon is problematic)
./gradlew build --no-daemon

# Run with new daemon (fresh start)
./gradlew --stop && ./gradlew build
```

**Issue: Daemon using old gradle.properties**:

```bash
# Stop daemon
./gradlew --stop

# Update gradle.properties
# org.gradle.jvmargs=-Xmx4g

# Run build (new daemon starts with new settings)
./gradlew build
```

**Issue: Daemon crashed**:

```bash
# Kill daemon process
pkill -f "gradle.*daemon"

# Or use Gradle command
./gradlew --stop

# Verify no daemons running
./gradlew --status

# Run build
./gradlew build
```

## Gradle Wrapper Issues

Fix wrapper script problems:

```bash
# Make wrapper executable
chmod +x gradlew

# Regenerate wrapper
gradle wrapper --gradle-version 9.2

# Validate wrapper
./gradlew wrapper --gradle-version 9.2 --validate-distribution-url

# Check current version
./gradlew --version
```

**Issue: Wrong Gradle version**:

```bash
# Update to specific version
./gradlew wrapper --gradle-version 9.2

# Or latest
./gradlew wrapper --gradle-version latest

# Verify
./gradlew --version
```

## Plugin and Repository Issues

Resolve plugin loading problems:

```bash
# Check plugin resolution
./gradlew build --stacktrace 2>&1 | grep -i plugin

# Add plugin repositories (settings.gradle.kts)
# pluginManagement {
#     repositories {
#         gradlePluginPortal()
#         mavenCentral()
#     }
# }

# Force refresh plugin resolution
./gradlew build --refresh-dependencies
```

## TestContainers and Docker Troubleshooting

When integration tests with TestContainers fail:

**Check Docker is running**:
```bash
docker ps
docker info
```

**Set Docker socket (macOS)**:
```bash
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
export DOCKER_HOST=unix://${HOME}/.docker/run/docker.sock
```

**Enable container reuse**:
```properties
# gradle.properties
testcontainers.reuse.enable=true
```

**Debug TestContainers**:
```bash
# Run with TestContainers debug logging
./gradlew test --info 2>&1 | grep -i testcontainers

# Check Docker logs
docker logs <container-id>
```

## CI/CD-Specific Issues

When tests pass locally but fail in CI:

**Environment differences**:
```bash
# Check CI environment
./gradlew build --info | grep -E "Java|Gradle|OS"

# Check CI timezone
./gradlew test -Duser.timezone=UTC

# Check CI locale
./gradlew test -Duser.language=en -Duser.country=US
```

**Parallel execution issues**:
```bash
# Disable parallel execution in CI
./gradlew test -Dorg.gradle.parallel=false

# Or in gradle.properties:
# org.gradle.parallel=false
```

**Memory constraints**:
```bash
# Reduce memory for CI
./gradlew build -Dorg.gradle.jvmargs="-Xmx2g"
```

## Build Scan Analysis

Generate and analyze detailed build scans:

```bash
# Generate build scan
./gradlew build --scan

# Scan shows:
# - Timeline of tasks
# - Configuration time
# - Task execution time
# - Test results
# - Dependency resolution
# - Plugin application
# - Build environment
```

Key areas to check in build scan:
- **Performance tab**: Identify slow tasks
- **Timeline**: Find serial vs parallel execution gaps
- **Dependencies**: Identify resolution issues
- **Tests**: Find flaky or slow tests
- **Configuration**: Check configuration cache eligibility
