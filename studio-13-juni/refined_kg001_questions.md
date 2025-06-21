# Targeted Research Questions for KG-001: Core ISA Application Architecture and Design (Firebase Focus)

## Targeted Question 1.1 (Firestore Data Modeling for GS1)

*   What are the optimal Firestore data structures (specific collection names, subcollection strategies, document ID hashing approaches for potentially sequential GS1 IDs like GTINs) for key GS1 entities, including but not limited to:
    *   Products (identified by GTINs)
    *   Locations (identified by GLNs)
    *   Logistic/Shipment Units (identified by SSCCs)
    *   GS1 Application Identifiers (AIs) associated with these entities
    *   GS1 Digital Link components and their relationships to primary identifiers?
*   How should relationships between these GS1 entities (e.g., a product GTIN and its associated manufacturer GLN, a shipment SSCC and its contained GTINs, a GTIN and its various packaging levels, a Digital Link URI and its target resources) be modeled in Firestore to optimize for ISA's anticipated common query patterns, such as:
    *   "Retrieve all information for a given GTIN (including its AIs and Digital Link data)."
    *   "Find all products manufactured at or shipped from a specific GLN."
    *   "List all GTINs contained within a specific SSCC."
    *   "Resolve all target URLs associated with a given GS1 Digital Link URI."?
*   What specific composite indexes will be critical for these common GS1 query patterns in Firestore? Conversely, which fields within the GS1 data models should be explicitly exempted from indexing to optimize write latency, reduce storage costs, and stay within Firestore indexing limits, assuming they are not used for direct querying or ordering?
*   What are the detailed best practices and recommended strategies for batch ingesting and managing potentially high-volume GS1 data streams into Firestore? This should include:
    *   Specific batching techniques (e.g., using Firestore batched writes or bulk writer operations).
    *   Strategies for gradual traffic ramp-up to new collections to avoid hotspotting, considering Firestore's 500 operations/second initial limit and 50% increase every 5 minutes.
    *   Error handling and retry mechanisms for batch ingestion processes.

## Targeted Question 1.2 (Next.js & Genkit API Layer with Firebase)

*   What are the precise conventions and best practices for structuring Next.js API routes (e.g., file naming, directory structure within `src/app/api/`, dynamic route parameters) to effectively expose Genkit flows, considering these flows will be deployed as Firebase Cloud Functions using the `onCallGenkit` helper? How should versioning of these API routes/Genkit flows be handled?
*   What are the most effective and maintainable patterns for sharing and managing Zod schemas between the Next.js frontend (TypeScript) and the Genkit backend (TypeScript, deployed on Firebase Cloud Functions) to ensure robust, type-safe data exchange for API requests and responses? This includes considerations for schema evolution and potential code generation.
*   When using React Server Components (RSCs) in the Next.js frontend (hosted on Firebase Hosting or Cloud Run), what are the optimal data fetching patterns to interact with these Genkit-backed API routes (Firebase Cloud Functions)? Specifically:
    *   How should data be fetched securely and efficiently from RSCs to these backend flows?
    *   What are the implications for caching, state management, and minimizing latency in this server-centric model where both the Next.js backend (for RSCs) and Genkit flows reside within the Firebase/Google Cloud ecosystem?
    *   How does Firebase Authentication context propagate from the Next.js frontend (RSCs) to the Genkit flows on Cloud Functions in this scenario?

## Targeted Question 1.3 (Scalable `src/` Structure for Roo & Firebase)

*   Given the proposed `src/` directory structure for the Next.js application (including `src/app`, `src/components/features/`, `src/lib/firebase.ts`, `src/models/types/`, and `src/genkit/`), what specific, granular naming conventions, module boundary definitions, and file/folder organization principles will make this structure unambiguously machine-interpretable for Roo? This is particularly important for Roo to map UDM directives to specific code artifacts related to Firebase, such as:
    *   Genkit flows located in `src/genkit/` that are intended for deployment as Firebase Cloud Functions.
    *   Firebase SDK initializations, configurations, or core utility functions (e.g., in `src/lib/firebase.ts` or dedicated Firebase service modules).
    *   Frontend components in `src/components/features/` that directly or indirectly consume data from or interact with Firebase services (Firestore, Firebase Auth).
    *   TypeScript type definitions or Zod schemas in `src/models/types/` that define data structures stored in or retrieved from Firestore.
*   Beyond naming conventions and structural organization, are there specific types of metadata annotations, structured comments (e.g., JSDoc-like tags with specific semantics for Roo), or manifest files that should be embedded within the codebase (particularly within the Firebase-related parts of the `src/` structure) to explicitly assist Roo's autonomous development processes, such as code generation, modification, or UDM mapping? How can these be designed to be both human-readable and machine-parsable?
