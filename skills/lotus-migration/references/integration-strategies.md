# Integration Replacement Strategies

## Direct Database Writes (Highest Priority)

### Why This Matters

Direct DB writes represent the tightest coupling and are highest priority for migration because they:
- Create schema dependencies
- Make testing difficult
- Provide poor error visibility
- Create change coordination challenges

### Option A: REST API Integration ⭐ Recommended for most cases

**Characteristics:**
- Source app calls API endpoint instead of writing database
- Target system owns database changes
- Clear error handling and versioning
- Easier to monitor and debug
- Overhead: Requires API development, network latency

**When to Use:**
- Synchronous operations requiring immediate feedback
- Low to medium volume (<1000 requests/min)
- Clear request/response semantics
- Need for retry and idempotency

### Option B: Message Queue Integration ⭐ Best for asynchronous, high-volume

**Characteristics:**
- Source app publishes message (incident/charge data)
- Target system subscribes and processes
- Decoupled, scalable, replay capability
- Better for high-volume scenarios
- Overhead: Queue infrastructure, eventual consistency, monitoring

**When to Use:**
- Asynchronous operations where immediate response not required
- High volume (>1000 messages/min)
- Need for replay/reprocessing capability
- Multiple consumers of same event

### Option C: Shared Staging Table - Transitional approach

**Characteristics:**
- Source app writes to staging table
- Target system polls and processes
- Maintains existing database connectivity
- Simple atomic transactions
- Downside: Maintains coupling, less modern

**When to Use:**
- Short-term migration step
- Cannot deploy API infrastructure immediately
- Need to maintain transactional consistency
- Stepping stone to eventual API/message queue

### Option D: Event Sourcing - Strategic long-term

**Characteristics:**
- Apps emit domain events (IncidentCreated, ViolationDetected)
- Event store captures all changes
- Subscribers react to events
- Full audit trail, replay capability
- Overhead: Complex, requires event infrastructure

**When to Use:**
- Long-term strategic architecture
- Need complete audit trail
- Multiple systems reacting to same events
- Complex event-driven workflows

## Decision Matrix

| Integration Type          | Volume | Latency | Best Fit     | Alternative   |
|---------------------------|--------|---------|--------------|---------------|
| Direct DB Write (sync)    | Low    | <1s     | API          | Staging Table |
| Direct DB Write (batch)   | High   | Hours   | API+Queue    | Batch API     |
| ODBC Read (reference)     | Low    | Seconds | API          | Cache Layer   |
| ODBC Read (transactional) | Medium | <1s     | API/Query    | Cached API    |
| File Export               | Medium | Minutes | Scheduled Job| Event Stream  |
| Email Notification        | Low    | Minutes | Message/Event| Direct Service|

## ODBC Connections

### Replacement Strategy

1. **If reading reference data:**
   - Create API endpoint for reference data
   - Implement caching (Redis/in-memory)
   - Sunset ODBC connection
   - Monitor cache hit rate

2. **If reading transactional data:**
   - Refactor to direct SQL connection (if same database)
   - Or create service API with proper connection pooling
   - Remove ODBC driver dependency

3. **If writing data:**
   - Replace with REST API (preferred)
   - Or message queue for high volume
   - Never write via ODBC in new systems

4. **Mainframe dependencies:**
   - Prioritize API layer to abstract mainframe
   - Enables future mainframe retirement
   - Centralizes mainframe access patterns
   - Improves monitoring and troubleshooting

### Example: Mainframe DB2 ODBC queries in VRS validation

**Current:**
VRS agents query DB2 via ODBC for product validation

**Problem:**
- Tight coupling to mainframe
- Network latency (200ms per query)
- Hard to troubleshoot ODBC errors
- No caching capability

**Solution:**
1. Create product validation API
2. API queries mainframe DB2
3. API caches results in Redis (5-minute TTL)
4. VRS calls API instead of ODBC
5. Decommission ODBC driver

**Benefits:**
- 90% reduction in mainframe queries (caching)
- <50ms response time (vs 200ms)
- Clear error messages
- Monitoring and alerting
- Path to mainframe retirement

## File-Based Integrations

### Current Usage in B&O
- Oracle Finance exports
- PDP (Product Data Platform) feeds
- Data warehouse imports
- Regulatory reporting

### Replacement Strategy

**For exports (outbound):**
- Keep file-based as intermediary format
- Add API-first capability for new consumers
- Standardize file formats (CSV with headers, JSON)
- Add schema validation (JSON Schema, XSD)
- Improve error detection and notification

**For imports (inbound):**
- Prefer file over API for batch imports (compatibility)
- Add validation before processing
- Implement retry and recovery
- Create staging area for problematic files

**For both:**
- Use file staging as transitional approach
- Move to API for new integrations
- Document file formats and validation rules
- Implement automated testing

**Improvements:**
- Standardize formats across all file integrations
- Add schema validation (reject invalid files early)
- Improve error handling (detailed error reports)
- Add monitoring and alerting
- Create reconciliation reports

## Reference Data Integrations

### Critical Issue in B&O: BDL feeds being decommissioned

**Current State:**
Four reference databases (Assortment, Supplier Info, Buying Groups, Lookups) fed by BDL

**Problem:**
BDL decommissioning creates immediate risk - all B&O transactions depend on reference data

**Action Required:**
Identify alternative sources urgently (2-week deadline)

### Replacement Strategy

**1. Map data lineage:**
- Where does BDL data originate?
- Which systems are authoritative sources?
- What transformations does BDL perform?
- What data quality rules exist?

**2. Identify alternatives:**
- Which systems own supplier information?
- Where does product assortment data live?
- Who maintains buying group mappings?
- What's the fallback if primary source unavailable?

**3. Design sync mechanism:**
- **Periodic file-based:** Nightly batch, full refresh or incremental
- **Real-time API:** On-demand lookup with caching
- **Hybrid:** Initial load via file, updates via API
- **Event-driven:** Subscribe to master data change events

**4. Create migration path:**
- Batch initial load (full data set)
- Incremental updates ongoing (changes only)
- Reconciliation reports (validate data accuracy)
- Rollback plan (keep BDL active for 2 weeks)

### Data Quality Considerations

**Validation Rules:**
- Supplier ID format and existence checks
- Product code validation against catalog
- Buying group hierarchy consistency
- Date range validation (effective/expiry dates)

**Error Handling:**
- Invalid records logged separately
- Partial success accepted (process valid records)
- Notification on data quality issues
- Manual reconciliation for exceptions

**Monitoring:**
- Data freshness (time since last update)
- Record counts (compare to previous load)
- Rejection rates (invalid records)
- API availability (if real-time)

## API Design Best Practices

### REST API Essentials

**Required Elements:**
- Clear resource endpoints (/api/v1/products/{id})
- HTTP methods aligned with operations (GET, POST, PUT, DELETE)
- Error codes with clear messages (400, 404, 409, 500)
- Idempotency support (Idempotency-Key header)
- Versioning strategy (/api/v1/, /api/v2/)

**Authentication:**
- API keys for service-to-service
- OAuth 2.0 for user-facing
- Never embed credentials in code

**Rate Limiting:**
- Per-API-key limits (e.g., 1000 req/min)
- 429 Too Many Requests response
- Retry-After header
- Exponential backoff guidance

**Monitoring:**
- Request count and rate
- Latency percentiles (p50, p95, p99)
- Error rates by status code
- Top consumers by API key

### Message Queue Best Practices

**Message Design:**
- Self-contained (all data needed to process)
- Idempotent (safe to process multiple times)
- Include timestamp and correlation ID
- Version field for schema evolution

**Queue Configuration:**
- Dead letter queue for poison messages
- Message retention (7-30 days typical)
- Visibility timeout aligned with processing time
- Batch size tuned for throughput

**Error Handling:**
- Retry with exponential backoff
- Move to DLQ after max retries
- Alert on DLQ accumulation
- Manual intervention process for DLQ

**Monitoring:**
- Message backlog size
- Processing latency
- DLQ depth
- Consumer lag

## Migration Patterns

### Strangler Fig Pattern

**Concept:**
Gradually replace old system by intercepting calls and routing to new system

**Steps:**
1. Create routing layer (API gateway, proxy)
2. Route 10% of traffic to new system
3. Validate correctness, monitor errors
4. Increase routing percentage gradually
5. Decommission old system when 100% migrated

**Benefits:**
- Low risk (gradual cutover)
- Easy rollback (adjust routing)
- Parallel validation
- No "big bang" migration

### Parallel Run Pattern

**Concept:**
Run old and new systems in parallel, compare results

**Steps:**
1. Deploy new system
2. Send requests to both old and new
3. Compare responses, log differences
4. Fix data mapping issues
5. Switch traffic to new system
6. Keep old system as backup for 2 weeks

**Benefits:**
- Catch data mapping issues early
- Users unaffected during validation
- High confidence before cutover
- Easy rollback if issues found

### Blue-Green Deployment

**Concept:**
Maintain two production environments, switch traffic instantly

**Steps:**
1. Blue environment (current production)
2. Deploy to Green environment (new version)
3. Test Green thoroughly
4. Switch routing from Blue to Green
5. Monitor closely
6. Rollback to Blue if issues
7. Keep Blue as standby for 1 week

**Benefits:**
- Instant rollback capability
- Zero downtime cutover
- Full production testing before switch
- Clear separation of versions
