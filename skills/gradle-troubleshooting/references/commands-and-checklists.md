# Gradle Troubleshooting: Commands Reference and Checklists

## Commands Reference

### Core Debug Commands

```bash
# === DEBUG OUTPUT ===
./gradlew build --stacktrace        # Stack trace (shows where)
./gradlew build --full-stacktrace   # Full stack (includes cause)
./gradlew build --info              # Info logging (what's happening)
./gradlew build --debug             # Debug logging (very detailed)

# === DEPENDENCY ANALYSIS ===
./gradlew dependencies               # Full dependency tree
./gradlew dependencies --configuration compileClasspath  # Specific config
./gradlew dependencyInsight --dependency spring-core     # Why included
./gradlew buildEnvironment           # Build-level dependencies

# === BUILD CACHE ===
./gradlew build --build-cache        # Enable cache
./gradlew build --no-build-cache     # Disable cache
rm -rf ~/.gradle/caches/build-cache-*  # Clear cache

# === DAEMON ===
./gradlew --status                   # Check daemon
./gradlew --stop                     # Stop daemon
./gradlew build --no-daemon          # Run without daemon

# === CONFIGURATION CACHE ===
./gradlew build --configuration-cache            # Enable
./gradlew build --no-configuration-cache         # Disable
./gradlew build --configuration-cache-problems=warn  # Show problems

# === BUILD SCAN ===
./gradlew build --scan               # Generate scan
./gradlew build --scan --profile     # With profiling

# === CLEANUP ===
./gradlew clean                      # Clean build outputs
rm -rf ~/.gradle/caches              # Clear entire cache
./gradlew --stop && rm -rf ~/.gradle/caches  # Hard reset
```

### Filtering Output

```bash
# Grep for common issues
./gradlew build --info 2>&1 | grep -i error
./gradlew build --info 2>&1 | grep cache
./gradlew build --info 2>&1 | grep "Xmx"
./gradlew build --stacktrace 2>&1 | head -50
```

## Troubleshooting Checklist

When builds fail, work through this checklist:

1. ✅ **Clear and restart**:
   ```bash
   ./gradlew --stop
   ./gradlew clean
   ```

2. ✅ **Check basics**:
   ```bash
   ./gradlew --version           # Verify Gradle version
   java -version                 # Verify Java version
   ```

3. ✅ **Get detailed output**:
   ```bash
   ./gradlew build --stacktrace --info
   ```

4. ✅ **Refresh dependencies**:
   ```bash
   ./gradlew build --refresh-dependencies
   ```

5. ✅ **Disable caching**:
   ```bash
   ./gradlew build --no-build-cache --no-configuration-cache
   ```

6. ✅ **Check environment**:
   ```bash
   env | grep GRADLE
   env | grep JAVA
   ```

7. ✅ **Review recent changes**:
   - Changes to build.gradle.kts?
   - Changes to gradle.properties?
   - Updated plugins?

8. ✅ **Generate build scan**:
   ```bash
   ./gradlew build --scan
   ```

9. ✅ **Run without daemon**:
   ```bash
   ./gradlew build --no-daemon
   ```

10. ✅ **Last resort - Full reset**:
    ```bash
    ./gradlew --stop
    rm -rf ~/.gradle/caches
    rm -rf build/
    ./gradlew clean build
    ```

## Quick Reference: Common Issues

| Issue | Symptoms | Command | Fix |
|-------|----------|---------|-----|
| OutOfMemory | `Java heap space` | `./gradlew build -Xmx8g` | Increase in `gradle.properties` |
| Slow build | Takes 2+ minutes | `./gradlew build --profile` | Enable caching in `gradle.properties` |
| Dependency missing | `Could not resolve` | `./gradlew dependencyInsight` | Check repositories, force version |
| Cache invalid | Failures with cache on | `./gradlew --no-build-cache` | `rm -rf ~/.gradle/caches` |
| Daemon stale | Config not applied | `./gradlew --stop` | Restart daemon |
| Plugin not found | `Plugin not found` | `./gradlew --stacktrace` | Check `pluginManagement` repos |
| Test failures | Tests fail in CI only | `./gradlew test --info` | Check environment variables |
| Docker errors | TestContainers fail | `docker ps` | Verify Docker running |
