# Targeted Research Questions for KG-003: Advanced Knowledge & Data Management ('Context7') (Firebase Focus)

## Targeted Question 3.1 (Context7 Hybrid Storage Design on Firebase)

*   What is the optimal schema and data flow design for implementing the `/memory_bank/` using a hybrid approach primarily leveraging Firebase services and compatible extensions? Specifically:
    *   **Firestore for Structured LTM:**
        *   What specific Firestore collection and document structures are best suited for storing Roo's Episodic LTM (e.g., logs of interactions, decisions, outcomes, tagged with user, timestamp, task type)?
        *   How should User Context (profiles, preferences, interaction history) be modeled in Firestore for efficient retrieval by Context7?
        *   How can Procedural LTM (links to or configurations of reusable Genkit flows representing learned skills) be effectively stored and managed within Firestore?
    *   **Firestore Vector Search for Semantic LTM (RAG):**
        *   What are the best practices for generating, storing, and managing vector embeddings within Firestore Vector Search for UDM sections, GS1 standard documentation, and other general knowledge sources intended for Retrieval Augmented Generation?
        *   How will these embeddings be updated or invalidated when the source documents in Firestore (or elsewhere) change? What is the process for keeping embeddings fresh?
        *   What are the query strategies for Firestore Vector Search to retrieve the most relevant semantic context for a given input?
    *   **In-Memory Cache (e.g., Redis via Genkit Plugin) for Fast-Access Pool:**
        *   Which specific data items from Firestore (structured LTM like recent episodic memories, user context) and Firestore Vector Search (frequently accessed semantic chunks) are prime candidates for caching in Redis to serve as the Fast-Access Pool?
        *   What are the detailed cache invalidation and update strategies to ensure consistency between Redis and the persistent Firestore/Vector Search stores, considering data volatility and access patterns?
        *   How will Genkit flows interact with the Redis cache (via the plugin) for both STM (e.g., current conversation turns) and LTM caching?
*   How will data consistency, relationships, and referential integrity be managed across these different Firebase-centric storage layers (Firestore documents for structured data, Firestore Vector Search for embeddings, and the Redis cache)? For example, if an episodic memory in Firestore refers to a semantic concept whose embedding is in Vector Search, how is this link maintained and resolved?

## Targeted Question 3.2 (Context7 Orchestration & Learning with Genkit on Firebase)

*   What specific Genkit flow architectures, designed to run on Firebase Cloud Functions, are required to implement the core Context7 orchestration logic? This should detail:
    *   Flows for input analysis and query formulation for the `/memory_bank/`.
    *   Flows implementing the Hierarchical Memory Retrieval (HMR) strategy, including multi-stage retrieval logic (checking Redis cache first, then Firestore/Vector Search).
    *   Flows responsible for context fusion (combining information from different memory types and real-time inputs) and preparing the synthesized context for other cognitive Genkit flows.
    *   How these orchestration flows will be triggered and how they will pass context to subsequent Genkit flows responsible for Roo's reasoning or response generation.
*   How can Genkit flows, operating within Firebase Cloud Functions, effectively implement the Task-Category Oriented Experience Learning (TOEL) principle for continuous improvement of the `/memory_bank/`? Specifically:
    *   How will experiences (data points, decisions, outcomes) from Roo's tasks (which are themselves Genkit flows) be captured and classified by category?
    *   What Genkit flow logic will be responsible for writing these classified experiences back to the appropriate storage layers within the Firebase ecosystem (e.g., new documents in Firestore for episodic logs, updates to semantic embeddings in Firestore Vector Search if learning refines understanding, updates to cached items in Redis)?
    *   How will this learning process be triggered (e.g., at the end of every task flow, or asynchronously via a Pub/Sub message processed by a dedicated learning flow)?
*   What are the anticipated performance implications (latency, Firebase resource consumption, and associated costs) of these potentially complex Context7 orchestration and TOEL learning flows running on Firebase Cloud Functions and interacting heavily with Firestore, Firestore Vector Search, and Redis?
    *   What strategies can be employed to optimize these flows for both speed and cost-efficiency within the Firebase environment (e.g., batching Firestore operations, optimizing queries, selective data retrieval, efficient cache utilization)?
    *   How can Firebase Genkit Monitoring be used to track the performance of these specific Context7-related flows and identify bottlenecks?
