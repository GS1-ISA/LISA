# ADR-001: Use Strategy Pattern for Data Adapters

**Status**: Accepted

**Context**: We need to support multiple data sources with different APIs and formats.

**Decision**: Implement the Strategy pattern with a `BaseAdapter` interface and thin concrete adapters.

**Consequences**
- Pros: extensible, testable, consistent.
- Cons: small upfront boilerplate per adapter.
