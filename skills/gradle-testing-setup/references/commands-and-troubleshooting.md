# Gradle Testing: Commands Reference and Troubleshooting

## Commands Reference

```bash
# === UNIT TESTS ===
./gradlew test                                  # Run all unit tests
./gradlew test --tests "com.example.MyTest"    # Run specific class
./gradlew test --tests "*IntegrationTest"      # Pattern matching
./gradlew test -x integrationTest              # Exclude integration tests

# === INTEGRATION TESTS ===
./gradlew integrationTest                      # Run integration tests
./gradlew test integrationTest                 # Both unit and integration

# === CODE COVERAGE ===
./gradlew jacocoTestReport                     # Generate coverage report
./gradlew jacocoTestCoverageVerification       # Verify minimum coverage
./gradlew test jacocoTestReport                # Tests + coverage

# === DEBUGGING ===
./gradlew test --info                          # Detailed logging
./gradlew test --stacktrace                    # Full stack traces
./gradlew test --debug                         # Debug mode

# === CONTINUOUS ===
./gradlew test --continuous                    # Rerun on changes
./gradlew integrationTest --continuous         # Watch integration tests

# === CLEANUP ===
./gradlew cleanTest                            # Clean test outputs
./gradlew clean                                # Clean all outputs
```

## Troubleshooting

**TestContainers connection errors**:
```bash
# Verify Docker
docker ps

# Check Docker socket
ls -la /var/run/docker.sock

# Set Docker environment (macOS)
export TESTCONTAINERS_DOCKER_SOCKET_OVERRIDE=/var/run/docker.sock
export DOCKER_HOST=unix://${HOME}/.docker/run/docker.sock
```

**Coverage report not generated**:
- Ensure `tasks.test { finalizedBy(jacocoTestReport) }`
- Verify JaCoCo plugin is applied
- Check build directory permissions

**Tests fail in CI but pass locally**:
- Verify same Java version in CI
- Check environment variables
- Ensure Docker daemon available in CI (for TestContainers)
