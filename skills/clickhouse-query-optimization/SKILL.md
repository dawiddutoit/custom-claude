---
name: clickhouse-query-optimization
description: |
  Optimize ClickHouse queries for speed and efficiency. Helps with primary key design, sparse indexes, data skipping indexes (minmax, set, bloom filter, ngrambf_v1), partitioning strategies, projections, PREWHERE optimization, approximate functions, and query profiling with EXPLAIN.
  Use when writing ClickHouse queries, designing table schemas, analyzing slow queries, or implementing analytical aggregations. Works with columnar OLAP workloads.
allowed-tools: Read, Grep, Bash
---

# ClickHouse Query Optimization

## Table of Contents

1. [Purpose](#purpose) - Understand ClickHouse's columnar architecture and optimization model
2. [Quick Start](#quick-start) - Check your query plan with EXPLAIN
3. **Core Principles for Query Optimization** - Instructions section covering 6 steps:
   - [Primary Key Design](#step-1-design-the-right-primary-key) - Sort order and sparse index behavior
   - [Data Skipping Indexes](#step-2-add-data-skipping-indexes-for-non-primary-key-columns) - Index types and when to use them
   - [Partitioning](#step-3-design-partitions-for-lifecycle-management) - Physical separation for lifecycle management
   - [Projections](#step-4-use-projections-for-multiple-access-patterns) - Different sort orders and pre-aggregation
   - [Query Optimization](#step-5-optimize-query-syntax) - PREWHERE, approximate functions, column selection
   - [Profiling and Debugging](#step-6-profile-and-debug-queries) - EXPLAIN and system.query_log
4. [Common Patterns and Solutions](#common-patterns-and-solutions) - Decision matrix with performance impact
5. [Examples](#examples) - Quick reference with links to detailed scenarios:
   - E-commerce orders table optimization (full before/after)
   - User events with complex multi-column filtering
   - Time-series data with retention policies
   - Common pitfalls and how to avoid them
   - Query profiling workflow
   - Projection transparency and automatic selection
   - **See [examples/examples.md](./examples/examples.md) for comprehensive scenarios**
6. [Requirements](#requirements) - ClickHouse version and prerequisites
7. [Integration Tips](#integration-tips) - Practical guidance for Python applications
8. [See Also](#see-also) - Comprehensive documentation with links:
   - **[examples/examples.md](./examples/examples.md)** - 6 real-world scenarios with performance metrics
   - **[references/reference.md](./references/reference.md)** - Technical guides and decision trees

## Purpose

ClickHouse's columnar architecture and sparse indexing model are fundamentally different from traditional SQL databases. This skill guides developers to write fast, efficient queries by understanding ClickHouse's execution model and leveraging its powerful optimization capabilities like data skipping indexes, projections, and approximate functions.

## Quick Start

### Check Your Query Plan

```sql
-- Always start by analyzing the execution plan
EXPLAIN
SELECT user_id, COUNT()
FROM events
WHERE timestamp >= '2024-01-01'
GROUP BY user_id;
```

This shows which parts of the index are used, how many partitions are read, and the aggregation strategy. If you see full table scans, your primary key or indexes need adjustment.

## Instructions

### Step 1: Design the Right Primary Key

The primary key defines data **sort order** (not uniqueness). ClickHouse uses a sparse index that stores min/max values per granule (default: 8,192 rows).

**Rule**: Order columns by **low cardinality → high cardinality**.

```sql
-- Good: country (low cardinality) → user_id (higher) → timestamp (high)
CREATE TABLE events (
    user_id UInt32,
    timestamp DateTime,
    country String,
    event_type String
)
ENGINE = MergeTree()
ORDER BY (country, user_id, timestamp);
```

**Key principle**: Queries must filter on the **primary key prefix** to use the index.

```sql
-- ✅ Fast: Uses index (country is first)
SELECT * FROM events WHERE country = 'US';

-- ✅ Fast: Uses index (country + user_id prefix)
SELECT * FROM events WHERE country = 'US' AND user_id = 12345;

-- ❌ Slow: Skips index (missing country prefix)
SELECT * FROM events WHERE user_id = 12345;
```

**When to use explicit PRIMARY KEY**: Separate the index from the full sort order to save memory:

```sql
CREATE TABLE events (
    user_id UInt32,
    timestamp DateTime,
    event_id UInt64
)
ENGINE = MergeTree()
ORDER BY (user_id, timestamp, event_id)
PRIMARY KEY (user_id, timestamp);
-- Index only includes (user_id, timestamp)
-- But data is fully sorted for optimal cache locality
```

### Step 2: Add Data Skipping Indexes for Non-Primary-Key Columns

When you filter on columns outside the primary key prefix, use data skipping indexes to skip entire blocks without reading them.

**Types of indexes**:

1. **MinMax Index** (numeric/date ranges):
```sql
ALTER TABLE events ADD INDEX idx_duration session_duration TYPE minmax GRANULARITY 4;
-- Stores min/max per 4 granules (32,768 rows each block)
-- Query: WHERE session_duration > 300 skips blocks where max < 300
```

2. **Set Index** (categorical, low cardinality):
```sql
ALTER TABLE events ADD INDEX idx_event_type event_type TYPE set(100) GRANULARITY 4;
-- Stores unique values per block (up to 100)
-- Query: WHERE event_type = 'purchase' skips blocks without 'purchase'
```

3. **Bloom Filter** (string equality):
```sql
ALTER TABLE events ADD INDEX idx_url url TYPE bloom_filter(0.01) GRANULARITY 4;
-- 0.01 = 1% false positive rate
-- Query: WHERE url = 'https://...' skips blocks that definitely don't contain it
```

4. **ngrambf_v1** (substring search):
```sql
ALTER TABLE logs ADD INDEX idx_message message TYPE ngrambf_v1(4, 512, 3, 0) GRANULARITY 1;
-- Query: WHERE message LIKE '%error%' skips blocks without 'error' n-grams
```

**When NOT to add indexes**:
- Column is already in primary key
- Column has low selectivity (filter doesn't eliminate much)
- Rarely queried

### Step 3: Design Partitions for Lifecycle Management

Partitioning physically separates data into directories, enabling fast deletion and TTL management.

**Monthly partitions** (most common):
```sql
CREATE TABLE events (
    user_id UInt32,
    timestamp DateTime,
    event_type String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (user_id, timestamp);

-- Drop old data instantly (no mutations)
ALTER TABLE events DROP PARTITION '202401';

-- Or use TTL
ALTER TABLE events MODIFY TTL timestamp + INTERVAL 90 DAY;
```

**When to partition**:
- Time-series data with predictable retention (e.g., 90 days of data)
- Need to delete old data frequently
- Query patterns align with time ranges

**Avoid**:
- Daily partitions for high-volume data (creates 365+ partitions/year)
- Partitioning by high-cardinality columns (user_id, product_id)
- Over-partitioning (> 1,000 partitions total)

### Step 4: Use Projections for Multiple Access Patterns

Projections are hidden tables with different sort orders, automatically kept in sync. ClickHouse transparently chooses which to use per query.

```sql
-- Main table sorted by (user_id, timestamp)
CREATE TABLE events (
    user_id UInt32,
    timestamp DateTime,
    product_id UInt32,
    revenue Decimal(10, 2)
)
ENGINE = MergeTree()
ORDER BY (user_id, timestamp);

-- Add projection for product-first queries
ALTER TABLE events ADD PROJECTION proj_by_product (
    SELECT *
    ORDER BY (product_id, timestamp)
);

-- Materialize (backfill) projection
ALTER TABLE events MATERIALIZE PROJECTION proj_by_product;

-- Now both queries are fast:
SELECT * FROM events WHERE user_id = 12345;    -- Uses main table
SELECT * FROM events WHERE product_id = 789;   -- Uses projection
```

**Aggregating projections** (pre-compute results):
```sql
ALTER TABLE events ADD PROJECTION proj_hourly_stats (
    SELECT
        toStartOfHour(timestamp) as hour,
        product_id,
        COUNT() as event_count,
        SUM(revenue) as total_revenue
    GROUP BY hour, product_id
);

ALTER TABLE events MATERIALIZE PROJECTION proj_hourly_stats;

-- Queries automatically use the pre-aggregated projection
SELECT
    hour,
    product_id,
    SUM(total_revenue)
FROM events
WHERE hour >= '2024-01-01'
GROUP BY hour, product_id;
```

**Trade-offs**: More storage, slower inserts, but dramatically faster reads for certain patterns.

### Step 5: Optimize Query Syntax

#### Use PREWHERE for Early Filtering

PREWHERE filters on small columns first, then reads remaining columns only for matches.

```sql
-- Standard WHERE (reads all columns, then filters)
SELECT user_id, event_type, properties
FROM events
WHERE timestamp >= '2024-01-01' AND country = 'US' AND event_type IN ('purchase', 'signup');

-- Better: PREWHERE for filtering, WHERE for remaining logic
SELECT user_id, event_type, properties
FROM events
PREWHERE timestamp >= '2024-01-01' AND country = 'US'  -- Small columns, read first
WHERE event_type IN ('purchase', 'signup');            -- Large columns or complex logic
```

**When to use PREWHERE**: Filtering on small columns (dates, enums) before reading large ones (strings, JSON).

#### Use Approximate Functions

```sql
-- Exact (slow on billions of rows)
SELECT COUNT(DISTINCT user_id) FROM events;
-- ~10 seconds on 1B rows

-- Approximate (10-100x faster, ~2% error)
SELECT uniq(user_id) FROM events;
-- ~100ms on 1B rows

-- Other approximate functions
SELECT
    uniq(user_id) as unique_users,              -- vs COUNT(DISTINCT)
    topK(10)(product_id) as top_10_products,    -- Approximate top-K
    quantile(0.95)(response_time) as p95        -- Approximate percentile
FROM events;
```

#### Use SAMPLE for Quick Exploration

```sql
-- Read 10% of data for approximate results (10x faster)
SELECT COUNT()
FROM events SAMPLE 0.1
WHERE timestamp >= '2024-01-01';

-- Deterministic sampling (same rows on repeated queries)
SELECT user_id, COUNT()
FROM events SAMPLE 1/10
GROUP BY user_id;
```

#### Select Only Needed Columns

```sql
-- Bad: Reads all columns from disk
SELECT * FROM events WHERE user_id = 12345;

-- Good: Reads only needed columns (columnar advantage)
SELECT user_id, timestamp, event_type FROM events WHERE user_id = 12345;
```

#### Optimize GROUP BY Column Order

```sql
-- Good: Low cardinality first
GROUP BY country, user_id
-- ClickHouse processes low-cardinality columns more efficiently

-- Bad: High cardinality first
GROUP BY user_id, country
-- Less efficient aggregation
```

### Step 6: Profile and Debug Queries

#### Use EXPLAIN to Verify Index Usage

```sql
-- View the execution plan
EXPLAIN
SELECT user_id, COUNT()
FROM events
WHERE country = 'US' AND session_duration > 300
GROUP BY user_id;

-- Output shows:
-- - Partitions/granules to read
-- - Index usage
-- - Aggregation type
```

#### Use Query Log for Performance Analysis

```sql
-- Enable detailed logging
SET send_logs_level = 'trace';

-- Run your query
SELECT COUNT() FROM events WHERE user_id = 12345;

-- Check performance metrics
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    memory_usage
FROM system.query_log
WHERE query LIKE '%events%'
ORDER BY event_time DESC
LIMIT 1;

-- Look for:
-- - read_rows vs table size (should be small fraction)
-- - query_duration_ms (baseline performance)
-- - memory_usage (avoid exceeding available RAM)
```

#### Find Slow Queries

```sql
-- Queries slower than 1 second
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE query_duration_ms > 1000
ORDER BY query_duration_ms DESC
LIMIT 10;
```

## Common Patterns and Solutions

This skill teaches six core optimization techniques. Each addresses a specific performance challenge:

| Technique | Problem Solved | Impact | When to Use |
|-----------|----------------|--------|------------|
| **Primary Key Design** | Index doesn't cover all queries | Foundation | Always - design first |
| **Data Skipping Indexes** | Filtering on non-primary columns is slow | 10-100x | After primary key, for selective filters |
| **Partitioning** | Need to delete old data quickly | Instant deletion | Time-series with retention policies |
| **Projections** | Multiple different query patterns | 100-1000x for pre-aggregation | Different sort orders or repeated aggregations |
| **Query Syntax** | Large columns read unnecessarily | 2-10x | Per-query optimization |
| **Profiling** | Don't know why query is slow | Insight | When optimization isn't obvious |

**Key Insight**: Optimization is cumulative. A table with good primary key + selective indexes + projections can be 1000x faster than unoptimized.

For real-world scenarios applying these techniques, see [examples/examples.md](./examples/examples.md):
- E-commerce orders: From 8000ms to 50ms with data skipping + projections
- User events: Complex filtering across 5+ dimensions
- Time-series: Automatic data retention with TTL
- Profiling workflow: Step-by-step optimization process
- Common pitfalls: SELECT *, GROUP BY high-cardinality, missing primary key prefix

## Examples

Quick reference examples are below. For comprehensive real-world scenarios with performance comparisons and detailed explanations, see **[examples/examples.md](./examples/examples.md)**.

### Quick Reference: E-Commerce Product Analytics

```sql
-- Basic optimized schema
CREATE TABLE orders (
    order_id String,
    customer_id UInt32,
    product_id UInt32,
    created_at DateTime,
    status String,
    total_amount Decimal(10, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (customer_id, created_at, order_id);

-- Add skipping indexes
ALTER TABLE orders ADD INDEX idx_status status TYPE set(10) GRANULARITY 4;
ALTER TABLE orders ADD INDEX idx_product product_id TYPE minmax GRANULARITY 4;

-- Add projection for product queries
ALTER TABLE orders ADD PROJECTION proj_by_product (
    SELECT * ORDER BY (product_id, created_at)
);
ALTER TABLE orders MATERIALIZE PROJECTION proj_by_product;
```

### Quick Reference: Data Skipping Indexes

```sql
-- Numeric range filtering
ALTER TABLE events ADD INDEX idx_duration session_duration TYPE minmax GRANULARITY 4;

-- Categorical filtering (low cardinality)
ALTER TABLE events ADD INDEX idx_country country TYPE set(250) GRANULARITY 4;

-- High-cardinality string equality
ALTER TABLE events ADD INDEX idx_url url TYPE bloom_filter(0.01) GRANULARITY 4;

-- Substring search
ALTER TABLE logs ADD INDEX idx_message message TYPE ngrambf_v1(4, 512, 3, 0) GRANULARITY 1;
```

### Quick Reference: PREWHERE and Approximate Functions

```sql
-- Filter small columns first, then read large columns
SELECT user_id, COUNT()
FROM events
PREWHERE timestamp >= '2024-01-01' AND country = 'US'
WHERE CAST(properties AS String) LIKE '%premium%'
GROUP BY user_id;

-- Use approximate functions for speed
SELECT
    uniq(user_id) as unique_users,              -- vs COUNT(DISTINCT)
    topK(10)(product_id) as top_products,       -- approximate top-K
    quantile(0.95)(response_time) as p95        -- approximate percentile
FROM events
WHERE timestamp >= '2024-01-01';
```

## Requirements

- ClickHouse 21.4+ (for stable sparse index behavior)
- Understanding of SQL and aggregation concepts
- Knowledge of your workload's query patterns (what columns are filtered most?)

## Integration Tips

When working with ClickHouse in your Python application:

1. **Design tables first**: Use EXPLAIN before and after adding indexes to verify improvements
2. **Monitor query_log**: Set up alerts for queries reading > 100M rows
3. **Profile inserts**: More indexes = slower writes; balance for your workload
4. **Test projections**: Use `EXPLAIN` to confirm optimizer chose your projection
5. **Materialized columns**: Add for frequently filtered columns to avoid computation

## See Also

### Supporting Documentation

- **[examples/examples.md](./examples/examples.md)** - Real-world optimization scenarios with performance metrics:
  - E-commerce orders: Full before/after analysis (8000ms → 50ms)
  - User events: Complex multi-dimensional filtering
  - Time-series: IoT data with retention policies
  - Common pitfalls: SELECT *, GROUP BY high-cardinality, missing keys
  - Profiling workflow: Step-by-step optimization process
  - Projection transparency: Query optimizer behavior

- **[references/reference.md](./references/reference.md)** - Technical reference and decision trees:
  - Index selection matrix: Choose the right index by column type and filter pattern
  - EXPLAIN output reference: Interpret execution plans
  - Data skipping index granularity guide: Balance precision and size
  - Primary key design patterns: Time-series, product analytics, multi-dimensional
  - Query optimization checklist: Pre/post optimization verification
  - Performance metrics to monitor: Track in system.query_log
  - Bloom filter and ngrambf_v1 parameters: Fine-tune string indexes
  - TTL configuration: Automatic data lifecycle management
  - Query rewrite patterns: GROUP BY, JOIN, filtering optimizations
