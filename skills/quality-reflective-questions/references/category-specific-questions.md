### For New Modules/Files

**Questions to ask:**
1. "Where is this module imported in production code?"
   - ✅ Good: "builder.py line 45"
   - ❌ Bad: "It's imported" (where?)

2. "Are any functions from this module called?"
   - ✅ Good: "create_review_node() called in builder.py line 146"
   - ❌ Bad: "Yes, they're called" (where?)

3. "If I grep for this module in src/, do I see imports outside of tests?"
   - ✅ Good: "Yes, see: `grep -r 'architecture_nodes' src/ | grep -v test`"
   - ❌ Bad: "I think so" (prove it)

**Red Flags:**
- Module only imported in test files
- No call-sites found in production code
- Functions defined but never invoked

### For LangGraph Nodes

**Questions to ask:**
1. "Is this node in builder.py's node list?"
   - ✅ Good: "Yes, line 146: graph.add_node('architecture_review', node)"
   - ❌ Bad: "It should be" (check it)

2. "What edges connect to this node?"
   - ✅ Good: "Conditional edge from 'query_claude' when should_review_architecture() is True"
   - ❌ Bad: "It's connected" (how?)

3. "Is this node in test_graph_completeness.py EXPECTED_NODES?"
   - ✅ Good: "Yes, added to list at line 270"
   - ❌ Bad: "I don't think we have that test" (create it)

**Red Flags:**
- Node file exists but not in builder.py
- Node added to graph but no edges connect to it
- Node not in integration test expected list

### For CLI Commands

**Questions to ask:**
1. "Does this command show in `--help` output?"
   - ✅ Good: "Yes, verified with `uv run app --help` - shows 'my-command' description"
   - ❌ Bad: "It should" (verify it)

2. "Can you run this command right now?"
   - ✅ Good: "Yes: `uv run app my-command arg` → Output: success"
   - ❌ Bad: "Probably" (try it)

3. "Where is this command registered?"
   - ✅ Good: "main.py line 12: app.add_command(my_command)"
   - ❌ Bad: "In the CLI file" (which file? which line?)

**Red Flags:**
- Command function exists but not registered
- Command not in --help output
- Command causes errors when invoked

### For Service Classes (with DI)

**Questions to ask:**
1. "Where is this service registered in the container?"
   - ✅ Good: "container.py line 67: container.register(MyService)"
   - ❌ Bad: "It's registered" (where?)

2. "Can you resolve this service from the container?"
   - ✅ Good: "Yes: `container.resolve('MyService')` returns instance"
   - ❌ Bad: "It should work" (try it)

3. "Where is this service injected and used?"
   - ✅ Good: "CoordinatorService line 34: def __init__(self, my_service: MyService)"
   - ❌ Bad: "In a few places" (which places?)

**Red Flags:**
- Service class exists but not registered
- Service registered but never injected
- Service injected but methods never called

### For API Endpoints

**Questions to ask:**
1. "Where is this route registered?"
   - ✅ Good: "router.py line 23: router.add_route('/endpoint', handler)"
   - ❌ Bad: "In the routes file" (which file? which line?)

2. "Can you curl this endpoint right now?"
   - ✅ Good: "Yes: `curl http://localhost:8000/api/endpoint` → HTTP 200"
   - ❌ Bad: "If the server is running" (start it and try)

3. "What does this endpoint return?"
   - ✅ Good: "JSON: {'status': 'success', 'data': {...}}"
   - ❌ Bad: "The expected response" (show me the actual response)

**Red Flags:**
- Endpoint function exists but not registered
- Endpoint returns 404 when called
- Endpoint returns errors or unexpected responses

