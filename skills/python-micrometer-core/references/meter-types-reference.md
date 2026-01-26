# Meter Types Reference

Comprehensive guide to all Micrometer meter types with usage patterns.

## Counter - Monotonically Increasing Values

Counters only go up. Use for counting events, requests, errors.

```java
Counter counter = Counter.builder("api.requests")
    .tag("endpoint", "/charges")
    .tag("method", "POST")
    .description("Total API requests")
    .register(registry);

counter.increment();    // +1
counter.increment(5);   // +5
```

**Best for:**
- Request counts
- Error counts
- Event counts
- Message counts

**Not for:**
- Values that decrease (use Gauge)
- Time measurements (use Timer)

## Gauge - Point-in-Time Values

Gauges track current values that can go up or down.

```java
// Function-based (recommended - no manual updates)
Gauge.builder("queue.size", queue, Queue::size)
    .description("Current queue depth")
    .register(registry);

// AtomicInteger-based (manual updates)
AtomicInteger depth = new AtomicInteger(0);
Gauge.builder("queue.depth", depth, AtomicInteger::get)
    .register(registry);

// Update manually
depth.set(10);
depth.incrementAndGet();
```

**Best for:**
- Queue depths
- Pool sizes
- Active connections
- Memory usage
- Temperature readings

**Not for:**
- Cumulative values (use Counter)
- Duration measurements (use Timer)

## Timer - Duration and Frequency

Timers measure both how long operations take AND how frequently they occur.

```java
Timer timer = Timer.builder("database.query")
    .description("Database query latency")
    .tag("operation", "select")
    .serviceLevelObjectives(
        Duration.ofMillis(100),
        Duration.ofMillis(500),
        Duration.ofSeconds(1)
    )
    .register(registry);

// Method 1: Record a runnable/callable
timer.record(() -> {
    database.executeQuery();
});

// Method 2: Use Sample for complex flows
Timer.Sample sample = Timer.start(registry);
try {
    database.executeQuery();
} finally {
    sample.stop(Timer.builder("api.latency").register(registry));
}

// Method 3: Record explicit duration
timer.record(Duration.ofMillis(250));
```

**Metrics provided:**
- `.count` - Total number of times recorded
- `.sum` - Total time spent
- `.max` - Maximum observed duration
- `.mean` - Average duration

**Best for:**
- HTTP request latency
- Database query duration
- External API calls
- Background job duration

**Not for:**
- Non-time measurements (use DistributionSummary)
- Simple counts (use Counter)

## DistributionSummary - Distribution of Values

Track distribution of non-time values (sizes, amounts, quantities).

```java
DistributionSummary summary = DistributionSummary.builder("request.size")
    .baseUnit("bytes")
    .description("HTTP request payload size")
    .serviceLevelObjectives(1024, 10_240, 102_400)
    .register(registry);

summary.record(fileSize);
summary.record(payloadBytes);
```

**Metrics provided:**
- `.count` - Number of values recorded
- `.sum` - Total of all values
- `.max` - Maximum value
- `.mean` - Average value

**Best for:**
- File sizes
- Payload sizes
- Batch sizes
- Money amounts
- Distances

**Not for:**
- Time measurements (use Timer)
- Current values (use Gauge)

## LongTaskTimer - Track In-Progress Long Operations

Special timer for operations that may take minutes or hours.

```java
LongTaskTimer longTask = LongTaskTimer.builder("video.encoding")
    .description("Long-running video encoding")
    .register(registry);

// Start tracking
LongTaskTimer.Sample task = longTask.start();
try {
    encodeVideo();
} finally {
    task.stop();
}
```

**Metrics provided:**
- `.active.count` - Number of tasks currently running
- `.duration.sum` - Total duration of all active tasks

**Best for:**
- Video/image processing
- Large file uploads
- Batch processing
- Data migrations

## FunctionCounter - Counter Backed by Function

Monitor external counters without manual updates.

```java
FunctionCounter.builder("jmx.thread.count",
        threadMXBean,
        ThreadMXBean::getThreadCount)
    .register(registry);
```

## TimeGauge - Gauge for Time-Based Values

Specialized gauge for time values with automatic unit conversion.

```java
TimeGauge.builder("uptime", this, TimeUnit.MILLISECONDS,
        obj -> System.currentTimeMillis() - obj.startTime)
    .register(registry);
```

## Meter Selection Decision Tree

```
Are you measuring time?
├─ Yes
│  ├─ Operation typically < 1 minute? → Timer
│  ├─ Operation typically > 1 minute? → LongTaskTimer
│  └─ Just tracking current time value? → TimeGauge
│
└─ No
   ├─ Value only increases? → Counter
   ├─ Value goes up and down? → Gauge
   └─ Tracking distribution? → DistributionSummary
```
