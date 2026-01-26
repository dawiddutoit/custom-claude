# Spring Boot Gradle Integration: Commands and Troubleshooting

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
