# Gradle Performance: Commands Reference and Troubleshooting

## Commands Reference

```bash
# === OPTIMIZATION COMMANDS ===

# Full optimized build
./gradlew build --parallel --build-cache --configuration-cache

# Build with profiling report
./gradlew build --profile
# Report: build/reports/profile/profile-<timestamp>.html

# Build with scan
./gradlew build --scan

# === DAEMON MANAGEMENT ===

# Check daemon status
./gradlew --status

# Stop all daemons
./gradlew --stop

# Run without daemon (for debugging)
./gradlew build --no-daemon

# === BUILD CACHE ===

# Disable cache temporarily
./gradlew build --no-build-cache

# Clean local cache
rm -rf ~/.gradle/caches/build-cache-*

# === CONFIGURATION CACHE ===

# Disable configuration cache temporarily
./gradlew build --no-configuration-cache

# View configuration cache report
# build/reports/configuration-cache/<hash>/configuration-cache-report.html

# === DEPENDENCY COMMANDS ===

# Lock dependencies
./gradlew dependencies --write-locks

# Verify locks
./gradlew dependencies --verify-locks

# === DEBUGGING ===

# Run with info logging
./gradlew build --info

# Run with debug logging
./gradlew build --debug

# Run with stack trace
./gradlew build --stacktrace

# Show Java toolchains
./gradlew -q javaToolchains
```

## Troubleshooting

**Build still slow despite optimization?**
1. Generate build scan: `./gradlew build --scan`
2. Check profile report: `./gradlew build --profile`
3. Identify slowest tasks in reports
4. Check for:
   - Network I/O during configuration phase
   - Expensive custom tasks
   - Non-cacheable tasks
   - Insufficient memory (OOM errors)

**Configuration cache problems?**
```bash
./gradlew build --configuration-cache-problems=warn
# Check: build/reports/configuration-cache/*/configuration-cache-report.html
```

**Out of memory?**
```bash
./gradlew --stop
# Increase in gradle.properties
# org.gradle.jvmargs=-Xmx8g -XX:MaxMetaspaceSize=2g
./gradlew build
```

## Performance Optimization Checklist

- [ ] Enable build cache: `org.gradle.caching=true`
- [ ] Enable configuration cache: `org.gradle.configuration-cache=true`
- [ ] Enable parallel execution: `org.gradle.parallel=true`
- [ ] Configure adequate heap (4-8 GB for most projects)
- [ ] Use Gradle daemon (enabled by default)
- [ ] Lock dependencies for reproducible builds
- [ ] Generate build scans to identify bottlenecks
- [ ] Cache in CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
- [ ] Enable incremental compilation
- [ ] Consider remote build cache for teams
