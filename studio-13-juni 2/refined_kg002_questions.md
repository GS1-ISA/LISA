# Targeted Research Questions for KG-002: Genkit and Firebase Integration Strategy (Firebase Focus)

## Targeted Question 2.1 (Genkit Flow Modularity & Firebase Deployment)

*   What are concrete examples of specific domain-driven Genkit flow designs for ISA's core tasks that exemplify modularity and employ strict Zod input/output schemas? Examples should cover:
    *   A simple validation flow (e.g., "validate GTIN structure against GS1 rules").
    *   A content generation flow (e.g., "generate UDM section summary based on provided keywords").
    *   A more complex conversational handling flow (e.g., a segment of "RooConversationHandler" managing a specific intent).
*   What is the detailed, step-by-step process for packaging and deploying these modular Genkit flows as Firebase Cloud Functions (2nd gen) using the `onCallGenkit` helper? This should address:
    *   Managing shared code and dependencies between multiple Genkit flows intended for different Cloud Functions.
    *   Handling any native dependencies that might be required by underlying libraries used in Genkit flows.
    *   Best practices for managing environment-specific configurations for deployed Cloud Functions (e.g., API keys for LLMs, database connection strings), specifically leveraging Cloud Secret Manager and accessing these secrets securely from within the Genkit flow/Cloud Function.
    *   Strategies for optimizing cold start times for these Genkit-based Cloud Functions.
*   How should the versioning of Genkit flows be managed in relation to the versioning of Firebase Cloud Functions? What strategies ensure that updates to flows are deployed controllably and that breaking changes are handled gracefully (e.g., using multiple function versions, traffic splitting)?

## Targeted Question 2.2 (Unified Security with Firebase Auth & Genkit)

*   What is the detailed implementation plan for securely passing Firebase ID tokens from various Next.js frontend contexts (client-side components, React Server Components, API routes acting as BFFs) to Genkit flows deployed as Firebase Cloud Functions? This should include code snippets or pseudo-code for token retrieval and inclusion in requests.
*   How should the `authPolicy` parameter of the `onCallGenkit` wrapper be configured to enforce different levels of access control for various Genkit flows? Provide specific examples, including:
    *   Ensuring only authenticated users can invoke any flow.
    *   Restricting access to specific flows based on Firebase Authentication custom claims (e.g., a user role like `admin` or `udm_editor`).
    *   Handling unauthorized access attempts gracefully and providing appropriate error responses.
*   What are comprehensive example Firestore security rules that effectively use `request.auth.uid` (obtained from the verified Firebase ID token in the calling Genkit flow/Cloud Function) to control access to diverse ISA-related data structures? Examples should cover:
    *   User-specific data (e.g., user profiles, user-uploaded GS1 data subsets).
    *   Shared UDM content (e.g., allowing read access to all authenticated users but write access only to specific roles).
    *   Collaborative data (e.g., scenarios where multiple users might have defined permissions on the same GS1 data entities).
    *   Rules that prevent unauthorized data exfiltration or modification through carefully crafted queries.

## Targeted Question 2.3 (Asynchronous Orchestration with Cloud Functions)

*   For which specific ISA processes is an event-driven, asynchronous architecture using standard Firebase Cloud Functions (i.e., not directly `onCallGenkit` wrapped flows, but potentially invoking them) most appropriate and beneficial? Identify at least 3-5 candidate processes, such as:
    *   Post-modification validation of UDM content after Roo makes a change (triggered by a Firestore write to the UDM collection).
    *   Re-indexing UDM content in a vector database (e.g., Firestore Vector Search) whenever relevant UDM sections are updated.
    *   Sending notifications (e.g., via Firebase Cloud Messaging or email) upon critical system events or when specific UDM milestones are reached.
    *   Aggregating audit logs from various ISA operations.
*   When these standard Firebase Cloud Functions (event-triggered) need to invoke Genkit flows for subsequent AI processing (e.g., a Firestore trigger on a UDM document write then calls a Genkit flow to summarize the changes or check for ethical implications), what are the best practices for such chained invocations? This should cover:
    *   Securely calling the Genkit flow (another Cloud Function) from the trigger function (e.g., service-to-service authentication if applicable, or passing necessary context).
    *   Managing data flow and error handling between the trigger function and the invoked Genkit flow.
    *   Avoiding cascading failures and ensuring idempotency if the processes involve multiple steps.
