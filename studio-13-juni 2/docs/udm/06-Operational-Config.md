# Section 06: Operational Configuration

This section defines the operational configurations for the Intelligent Standards Assistant (ISA) across various environments (development, staging, production). It also includes best practices, security guidelines, and performance optimizations related to configuration management.

## 6.1 Genkit Configuration and Deployment

### 6.1.1 Core Genkit Setup
Details on initializing Genkit are typically managed in a `genkit.config.ts` file (or equivalent JavaScript). The `configureGenkit({...})` function is central to this setup. Key aspects include:
- **Plugin Registration:** This is where plugins for various services are registered. Based on `APP-GENKIT-RESEARCH-REPORT-V1.md`, essential plugin categories for ISA include:
    - **Model Providers:** For integrating LLMs like Gemini. Examples: `@genkit-ai/google-ai` (for Google AI Studio) or `@genkit-ai/vertex-ai` (for Vertex AI). The choice impacts API key and project configuration.
    - **Vector Stores (for RAG):** Examples: `@genkit-ai/firebase` or `@genkit-ai/firestore` (for Firestore Vector Search), `@genkit-ai/pinecone`.
    - **Caching:** Example: `@genkit-ai/redis` for services like Redis, potentially for Context7's Fast-Access Pool.
    - **Firebase Integration:** The `@genkit-ai/firebase` plugin often provides helpers for Firestore-backed flow state (`flowStateStore`) and trace storage (`traceStore`).
- **Core Settings:**
    - `flowStateStore`: Defines where flow state is persisted (e.g., 'firebase' if using Firestore via the Firebase plugin).
    - `traceStore`: Defines where execution traces are stored (e.g., 'firebase').
    - `enableTracingAndMetrics`: Should be set to `true` for production to leverage Google Cloud Operations Suite for monitoring.
    - `logLevel`: Configurable for desired verbosity (e.g., 'debug' during development, 'info' for production).

### 6.1.2 Genkit Flow Deployment to Firebase Cloud Functions
- **Method:** Genkit flows are primarily deployed as HTTPS callable functions using Firebase Cloud Functions (2nd gen recommended).
- **Mechanism:** This is achieved using the `onCallGenkit` helper provided by `@google-cloud/functions-genkit` (or equivalent Firebase Functions v2 Genkit integration). This wrapper handles request/response marshalling, streaming, and integration with Firebase Authentication.
- **Configuration:** Each flow intended for deployment will be exported as a Cloud Function in the project's `index.ts` (or relevant Firebase Functions entry point).
- **Example (Conceptual for Firebase Functions `index.ts`):**
  ```typescript
  // import { https } from 'firebase-functions/v2'; // Or from 'firebase-functions/v2/https'
  // import { onCallGenkit } from '@google-cloud/functions-genkit'; // Or from a firebase-functions genkit helper
  // import { mySampleFlow } from './flows/sampleFlow'; // Assuming flow is defined elsewhere
  //
  // exports.mySampleFlowEndpoint = https.onCall(
  //   onCallGenkit(
  //     {
  //       flow: mySampleFlow,
  //       // Zod schemas for request and response can be specified here for type safety
  //       // inputSchema: MySampleFlowInputSchema,
  //       // outputSchema: MySampleFlowOutputSchema,
  //       // authPolicy: (auth, request) => { ... } // For Firebase Authentication
  //     }
  //   )
  // );
  ```

### 6.1.3 Secret Management for Genkit Flows
- **Requirement:** Genkit flows, especially those interacting with external services or LLMs (like Gemini via Google AI or Vertex AI), require secure management of API keys and other secrets.
- **Method:** Secrets (e.g., Google AI API keys, API keys for other integrated services) must NOT be hardcoded in source files. They should be stored securely using Google Cloud Secret Manager.
- **Access in Firebase Cloud Functions:** Deployed Genkit flows (as Cloud Functions) will be granted appropriate IAM permissions to access specific secrets from Secret Manager at runtime. The Genkit initialization code (e.g., within `configureGenkit` plugins) or individual flows can then retrieve these secrets.
- **Best Practice:** Use environment variables within the Cloud Function runtime (set via Secret Manager bindings) to pass secrets to Genkit configurations or tools.

## 6.2 Current Project Configuration Audit (TASK-P0-M0.1-T001)

This subsection documents the initial audit findings for key project configuration files as part of Milestone M0.1, Task T001.

### 6.2.1 `apphosting.yaml`

**Current State (Placeholder):**
```yaml
# This is a placeholder for Google Cloud App Hosting configuration.
# Further configuration will be added based on audit findings and deployment needs.
# Example minimal configuration:
# service: default
# regions:
#   - us-central1
#   - us-east1
# memoryMiB: 512 # This is a known discrepancy from initial human review, will be audited.
```

**Findings:**
- **Issue:** File is a placeholder with no active configuration.
- **Risk Level:** Informational
- **Recommendation:** Populate with actual Google Cloud App Hosting configuration based on project requirements. Review `memoryMiB` value against actual application needs and cost optimization.

### 6.2.2 `firebase.json`

**Current State (Minimal Hosting):**
```json
{
  "hosting": {
    "public": "public",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  }
}
```

**Findings:**
- **Issue:** Minimal configuration, lacks definitions for other Firebase services (Functions, Firestore, Storage, etc.) that might be used by ISA.
- **Risk Level:** Low
- **Recommendation:** Expand `firebase.json` to include configurations for all Firebase services utilized by the ISA project, ensuring security rules and deployment settings are optimized.

### 6.2.3 `next.config.ts`

**Current State (Basic Next.js with ESLint override):**
```typescript
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  eslint: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
```

**Findings:**
- **Issue:** `eslint.ignoreBuildErrors` is set to `true`, which allows production builds to complete even with ESLint errors. This compromises code quality and consistency.
- **UDM Reference Violated:** Master Prompt: 'obsessively driven to eliminate all forms of ambiguity, inconsistency, and sub-optimality'
- **Risk Level:** High
- **Recommendation:** Set `eslint.ignoreBuildErrors` to `false` once initial setup is complete and all ESLint errors are resolved. Implement a robust linting process to ensure code quality.

### 6.2.4 `package.json`

**Current State (Basic Next.js dependencies):**
```json
{
  "name": "isa-project",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.2.3",
    "react": "^18",
    "react-dom": "^18"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "eslint": "^8",
    "eslint-config-next": "14.2.3",
    "typescript": "^5"
  }
}
```

**Findings:**
- **Issue:** Dependencies are minimal and may not reflect all actual project needs (e.g., Genkit, Firebase SDKs).
- **Risk Level:** Informational
- **Recommendation:** Review and update dependencies to include all necessary libraries for ISA's functionality (e.g., Genkit, Firebase Admin/Client SDKs, Zod for schema validation, etc.). Ensure dependency versions are managed to prevent conflicts and security vulnerabilities.

### 6.2.5 `tsconfig.json`

**Current State (Standard TypeScript config):**
```json
{
  "compilerOptions": {
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Findings:**
- **Issue:** No immediate issues identified. Configuration aligns with best practices.
- **Risk Level:** None
- **Recommendation:** Maintain `strict: true` and other quality-focused compiler options. Ensure `include` and `exclude` paths accurately reflect the project structure as it evolves.

## 6.3 AI Model Configuration

### 6.3.1 Gemini 2.5 Flash Preview 20-5 Configuration

The primary AI model used by Roo and ISA is Gemini 2.5 Flash Preview 20-5. Its configuration within the Genkit framework is managed as part of the `configureGenkit()` setup, typically in a `genkit.config.ts` file.

**Conceptual Genkit Configuration for Gemini Model (within `configureGenkit`):**
```typescript
// genkit.config.ts (Conceptual)
import { configureGenkit } from '@genkit-ai/core';
import { googleAI } from '@genkit-ai/google-ai'; // For Google AI Studio (requires API Key)
// OR
// import { vertexAI } from '@genkit-ai/vertex-ai'; // For Vertex AI (uses application default credentials or service account)

// Example using googleAI plugin:
// Ensure GOOGLE_GENAI_API_KEY is set as an environment variable, sourced from Secret Manager.
// plugins: [googleAI({ apiKey: process.env.GOOGLE_GENAI_API_KEY })],

// Example using vertexAI plugin:
// Ensure GCP_PROJECT_ID and GCP_LOCATION are set as environment variables if not using ADC defaults.
// plugins: [vertexAI({ projectId: process.env.GCP_PROJECT_ID, location: process.env.GCP_LOCATION })],

// Models can be explicitly defined and registered if needed, or used by default by the plugin.
// For example, if 'gemini-1.5-flash-preview-0514' is the target:
// const geminiFlash = defineModel(
//   { name: 'google-ai/gemini-1.5-flash-preview-0514', ...options }, // if using googleAI plugin
//   // OR { name: 'vertex-ai/gemini-1.5-flash-preview-0514', ...options } // if using vertexAI
//   async (request) => { /* ... call to model via client ... */ }
// );
// modelProviders: [{ name: 'gemini-flash', model: geminiFlash}], // Registering a custom defined model

// More commonly, models from a plugin are used directly in flows by referencing their string ID, e.g.,
// `generate({ model: 'gemini-1.5-flash-preview-0514', ... })`
// or by importing a pre-defined model object from the plugin.
```

**Key Configuration Points & Implications from `APP-GENKIT-RESEARCH-REPORT-V1.md`:**
- **Model Choice:** Gemini 2.5 Flash Preview 20-5 remains the selected model for its balance of speed and cost-effectiveness.
- **Plugin Selection:** The choice between `@genkit-ai/google-ai` (for Google AI Studio API) and `@genkit-ai/vertex-ai` (for Vertex AI managed models) is critical:
    - `@google-ai`: Requires an API key, typically managed via Secret Manager and passed as an environment variable (e.g., `GOOGLE_GENAI_API_KEY`).
    - `@vertex-ai`: Can use Application Default Credentials (ADC) if the runtime environment (e.g., Cloud Function) has appropriate IAM permissions, or requires project ID and location. Vertex AI is generally preferred for production workloads on Google Cloud for its integration and IAM controls.
- **Secure Configuration:** All sensitive information (API keys, GCP Project IDs if not ADC) MUST be sourced from environment variables linked to Google Cloud Secret Manager, as detailed in Section 6.1.3.
- **Observability:** As noted in Section 6.1.1, `enableTracingAndMetrics: true`, `flowStateStore`, and `traceStore` (e.g., configured to use Firestore via `@genkit-ai/firebase`) are essential for production monitoring.
- **Recommendation:**
    1.  Finalize the choice of Genkit plugin for accessing Gemini (prefer `@genkit-ai/vertex-ai` for better GCP integration if possible).
    2.  Ensure all necessary configurations (API keys, project IDs, locations) are securely managed via Secret Manager and accessed as environment variables by the Genkit configuration.
    3.  Verify that `flowStateStore` and `traceStore` are configured (e.g., using `@genkit-ai/firebase`) for robust state management and observability.

### 6.3.2 Claude Sonnet 3.5 Configuration (for ClaudeBrowserMode)

The `ClaudeBrowserMode` utilizes Claude Sonnet 3.5 (or latest approved equivalent) for its specialized web interaction and tool-use capabilities. Its configuration within Genkit is as follows:

**Conceptual Genkit Configuration for Claude Model (within `configureGenkit`):**
```typescript
// genkit.config.ts (Conceptual Addition for Claude)
// import { vertexAI } from '@genkit-ai/vertex-ai'; // If Claude is available via Vertex AI & this plugin
// OR
// import { anthropic } from '@genkit-ai/anthropic'; // Assuming a hypothetical Anthropic plugin for Genkit

// Example if using Claude via Vertex AI:
// plugins: [
//   vertexAI({ projectId: process.env.GCP_PROJECT_ID, location: process.env.GCP_LOCATION }),
//   // ... other plugins
// ],

// Example if using a dedicated Anthropic plugin:
// plugins: [
//   anthropic({ apiKey: process.env.ANTHROPIC_API_KEY }),
//   // ... other plugins
// ],

// The Claude model would then be referenced in the ClaudeBrowserMode Genkit flow, e.g.,
// `generate({ model: 'vertex-ai/claude-3-5-sonnet-via-vertex', ... })` or
// `generate({ model: 'anthropic/claude-3-5-sonnet', ... })`
```

**Key Configuration Points & Implications:**
- **Model Access:** Claude Sonnet 3.5 is accessed via a suitable Genkit plugin. If it's available on Vertex AI and supported by the `@genkit-ai/vertex-ai` plugin, this would be the preferred integration route for consistency within GCP. Otherwise, a dedicated Anthropic Genkit plugin (`@genkit-ai/anthropic` or similar, if available/developed) would be used.
- **Secure Configuration:** Any API keys (e.g., `ANTHROPIC_API_KEY`) or specific endpoint configurations for accessing Claude must be managed via Google Cloud Secret Manager and exposed to the Genkit runtime as environment variables (see Section 6.1.3).
- **Genkit Flow Integration:** The `ClaudeBrowserMode` (defined in UDM Section 04) is a Genkit flow that will specify the configured Claude model for its `generate` calls, and will provide the 8 browser sub-action tools (defined in UDM Section 02.5) to Claude for tool calling.
- **Recommendation:**
    1.  Determine and confirm the exact Genkit plugin (e.g., `@genkit-ai/vertex-ai`) and model identifier for accessing Claude Sonnet 3.5, preferably via Vertex AI for streamlined GCP integration.
    2.  Ensure secure management of any associated API keys or service account credentials via Secret Manager, exposing them as environment variables (e.g., `GCP_PROJECT_ID`, `GCP_LOCATION` if not covered by Application Default Credentials for Vertex AI).
    3.  Refer to `docs/research_appendix/APP-GENKIT-RESEARCH-REPORT-V1.md` for general Genkit setup best practices, which are applicable to configuring model access and plugins.