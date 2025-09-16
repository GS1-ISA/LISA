# High-priority governance & docs

This issue groups the top-priority items from docs/TODO.md and docs/ROADMAP.md.

Deliverables:
- docs/AI_PROJECT_CHARTER.md — owner: eng-lead
- docs/VECTOR_STORE_SCHEMA.md — owner: data-engineer
- docs/model_cards/TEMPLATE.md + docs/model_cards/EXAMPLE.md — owner: data-science
- data/data_catalog.yaml — owner: data-engineer

Acceptance criteria:
- Documents exist and are reviewed by core team
- Example model card committed and linked to experiments
- data/data_catalog.yaml parses and references VECTOR_STORE_SCHEMA.md

Next actions:
- Use .github/ISSUE_TEMPLATE/high-priority-governance.md to create per-item issues
- Assign owners and set milestones in project board

## Server Status Update (2025-09-16)

✅ **Server Issues Resolved**: The FastAPI server is now running successfully on http://localhost:8001
- Fixed HTTPS redirect middleware causing 307 redirects and SSL errors
- Added dotenv loading for environment variables
- Resolved import errors (RateLimiter, Form from FastAPI)
- Fixed FastAPI endpoint parameter issues (change-password endpoint)
- Cleaned up app structure and Socket.io integration
- Server operational and ready for use

### Testing Results Summary
- **Socket.io Chat System**: 100% functional (22/22 tests passed) - production-ready
- **Database Connectivity**: Functional and health monitoring working
- **Basic Authentication**: Registration working, login endpoint has issues
- **Security Headers & CORS**: Properly configured
- **API Endpoints**: Health and basic endpoints operational

### Current Issues Identified
❌ **Authentication Login Endpoint**: Failing due to log_auth_event signature mismatch
❌ **GS1 Integration Endpoints**: Not implemented (imports commented out)
❌ **Compliance Workflow Endpoints**: Not implemented (imports commented out)
❌ **LLM/Agent Backend Integration**: Issues with async/await patterns and JSON serialization
❌ **System Monitoring Permissions**: psutil access denied for health metrics
❌ **Integration Features**: Some features not fully implemented

### Current Server Status
- Server runs successfully on http://localhost:8001
- Socket.io chat is fully operational and production-ready
- Basic API endpoints work (health, registration)
- Backend compliance assistant has integration issues
- Database and monitoring systems functional
