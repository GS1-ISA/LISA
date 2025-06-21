# APP-URL-LIST-V1: Curated External Documentation Resources

This document contains a curated list of URLs relevant to the ISA project, categorized for ease of use.

## I. GS1 Standards and Data

*   **GS1 General Specifications:**
    *   URL: https://documents.gs1us.org/adobe/assets/deliver/urn:aaid:aem:afbf55ad-0151-4a0c-8454-d494c0dc9527/GS1-General-Specifications.pdf [1]
    *   Description: The foundational GS1 standard defining how identification keys, data attributes, and barcodes must be used. Contains detailed sections on GS1 system basics, application standards, Application Identifier definitions, and rules. Essential for understanding the core GS1 data model.
*   **GS1 US Data Hub APIs:**
    *   URL: https://www.gs1us.org/tools/gs1-us-data-hub/gs1-us-apis [2]
    *   Description: Information on GS1 US APIs for accessing product data, including the Data Hub Developer Portal User Guide. Useful for understanding programmatic access to GS1 data.
*   **GS1 Digital Link Standard:**
    *   URL: https://www.gs1.org/standards/digital-link [3]
    *   Description: Overview of the GS1 Digital Link standard, which extends the power of GS1 identifiers by making them web-addressable. Key for modern product identification and consumer engagement.
*   **GS1 Digital Link Resolver Implementation (GS1 GitHub):**
    *   URL: https://github.com/gs1/GS1_DigitalLink_Resolver_CE [4]
    *   Description: Community Edition of a GS1 Digital Link Resolver. Provides insights into how these resolvers work and potential for self-hosting or understanding the ecosystem.
*   **GS1 Digital Link Syntax:**
    *   URL: https://www.gs1.org/services/gs1-digital-link-online-tool/digital-link-syntax-validator-tool [5]
    *   Description: Online tool for validating GS1 Digital Link URI syntax. Helpful for ensuring correctly formed Digital Links.

## II. Firebase (Backend Platform & Services)

*   **Official Firebase Documentation:**
    *   URL: https://firebase.google.com/docs [6]
    *   Description: Comprehensive documentation for all Firebase services, including Firestore, Firebase Authentication, Cloud Functions for Firebase, Hosting, etc. The primary resource for Firebase development.
*   **Firebase YouTube Channel:**
    *   URL: https://www.youtube.com/user/Firebase [7]
    *   Description: Contains tutorials, best practices, and updates on Firebase features. Good for visual learning and staying up-to-date.
*   **Firebase Blog:**
    *   URL: https://firebase.blog/ [8]
    *   Description: Articles on new features, use cases, and tips for Firebase development.
*   **Firebase Admin SDK for Node.js:**
    *   URL: https://firebase.google.com/docs/admin/setup [9]
    *   Description: Documentation for the Firebase Admin SDK, essential for backend operations like custom authentication token minting, interacting with Firestore with elevated privileges (within Cloud Functions).
*   **Firestore Documentation:**
    *   URL: https://firebase.google.com/docs/firestore [10]
    *   Description: Detailed documentation on Cloud Firestore, covering data modeling, querying, security rules, indexing, and performance. Critical for ISA's data storage.

## III. Genkit (AI Framework)

*   **Official Genkit Documentation Entry (Firebase):**
    *   URL: https://firebase.google.com/docs/genkit [11]
    *   Description: A high-level introduction and links to more detailed Genkit resources, focusing on its integration within the Firebase ecosystem.
*   **Genkit GitHub Repository:**
    *   URL: https://github.com/firebase/genkit [12]
    *   Description: The source code, examples, and issue tracker for Genkit. Essential for understanding its architecture, available plugins, and contributing or finding solutions to specific problems.
*   **Genkit Samples (GitHub):**
    *   URL: https://github.com/firebase/genkit/tree/main/samples [13]
    *   Description: Practical examples demonstrating how to use Genkit for various AI tasks, including different models, flows, and tools.
*   **Configuring Genkit (Firebase Docs):**
    *   URL: https://firebase.google.com/docs/genkit/configure-genkit [N/A - This specific sub-URL might not exist, main Genkit docs are better]
    *   Description: (Assumed) Details on the `configureGenkit()` API, setting up plugins, models, and other core framework options. (Refer to main Genkit docs or GitHub for this).
*   **Genkit Plugins Overview (Conceptual - find on GitHub or main docs):**
    *   URL: (Search on Genkit GitHub or main documentation)
    *   Description: Information on available Genkit plugins for models (Google AI, Vertex AI, Ollama), vector stores (Firestore, Pinecone), caching (Redis), etc.

## IV. Node.js (Runtime Environment)

*   **Official Node.js Documentation:**
    *   URL: https://nodejs.org/en/docs/ [14]
    *   Description: Comprehensive documentation for the Node.js runtime, including its `fs` module for file system access, `path` module, and other core APIs.
*   **Node.js `fs` Module (File System):**
    *   URL: https://nodejs.org/api/fs.html [15]
    *   Description: Detailed API documentation for the Node.js file system module. Essential for understanding secure and efficient file operations if direct `fs` access is ever needed (though abstracted via MCP for Roo).
*   **Node.js `path` Module:**
    *   URL: https://nodejs.org/api/path.html [16]
    *   Description: API documentation for the Node.js path module, useful for constructing and manipulating file paths safely.

## V. TypeScript (Programming Language)

*   **Official TypeScript Documentation:**
    *   URL: https://www.typescriptlang.org/docs/ [17]
    *   Description: Comprehensive documentation for the TypeScript language, including its type system, compiler options, and best practices.
*   **TypeScript Handbook:**
    *   URL: https://www.typescriptlang.org/docs/handbook/intro.html [18]
    *   Description: A guided introduction to TypeScript's features and concepts.

## VI. Next.js (Frontend Framework)

*   **Official Next.js Documentation:**
    *   URL: https://nextjs.org/docs [19]
    *   Description: Comprehensive documentation for the Next.js framework, covering routing (App Router), components (React Server Components), data fetching, API routes, deployment, etc.
*   **Learn Next.js Tutorial:**
    *   URL: https://nextjs.org/learn [20]
    *   Description: Interactive tutorials for learning Next.js concepts.

## VII. Other Useful Libraries & Tools

*   **Zod (Schema Validation):**
    *   URL: https://zod.dev/ [21]
    *   URL: https://github.com/colinhacks/zod [22]
    *   Description: TypeScript-first schema declaration and validation library. Used by Genkit for defining input/output schemas for flows and tools.
*   **Unified / Remark (Markdown Processing):**
    *   URL: https://unifiedjs.com/ [23]
    *   URL: https://github.com/remarkjs/remark [24]
    *   Description: Powerful ecosystem for parsing and manipulating Markdown using Abstract Syntax Trees (AST). Recommended for UDM manipulation.
*   **YAML (YAML Parser - by Eemeli Aro):**
    *   URL: https://eemeli.org/yaml/ [25]
    *   URL: https://github.com/eemeli/yaml [26]
    *   Description: A robust YAML parser and stringifier for JavaScript, recommended for its comment preservation features, crucial for UDM.
*   **Puppeteer (Browser Automation):**
    *   URL: https://pptr.dev/ [27]
    *   URL: https://github.com/puppeteer/puppeteer [28]
    *   Description: Node.js library for controlling headless Chrome or Chromium. A candidate for implementing `ClaudeBrowserMode` actions.
*   **Playwright (Browser Automation):**
    *   URL: https://playwright.dev/ [29]
    *   URL: https://github.com/microsoft/playwright [30]
    *   Description: Alternative Node.js library for browser automation across multiple browsers (Chromium, Firefox, WebKit). Also a candidate for `ClaudeBrowserMode`.

## VIII. Google Cloud & AI

*   **Google Cloud Console:**
    *   URL: https://console.cloud.google.com/ [31]
    *   Description: Central console for managing Google Cloud Platform resources, including Firebase projects, Vertex AI, Secret Manager, etc.
*   **Vertex AI Documentation:**
    *   URL: https://cloud.google.com/vertex-ai/docs [32]
    *   Description: Documentation for Google Cloud's Vertex AI platform, for managing and deploying ML models, including Gemini models that can be used with Genkit.
*   **Google Cloud Secret Manager:**
    *   URL: https://cloud.google.com/secret-manager/docs [33]
    *   Description: Service for securely storing API keys, passwords, certificates, and other sensitive data. Recommended for managing secrets for Genkit flows deployed on Firebase/GCP.
*   **Anthropic Documentation (for Claude models):**
    *   URL: https://docs.anthropic.com/claude/reference/messages_post [34] (Example API reference)
    *   Description: API documentation for Claude models, relevant for `ClaudeBrowserMode` if interacting directly or understanding its tool-use capabilities.

## IX. Web Development & API Design

*   **MDN Web Docs (Mozilla):**
    *   URL: https://developer.mozilla.org/ [35]
    *   Description: Comprehensive resource for web standards (HTML, CSS, JavaScript), browser APIs, and web development best practices.
*   **OpenAPI Specification:**
    *   URL: https://swagger.io/specification/ [36]
    *   Description: Standard for designing, building, and documenting RESTful APIs. Relevant if ISA exposes its own external APIs.

*(Note: The bracketed numbers like [1], [2] are from the original user input and can be removed if not needed for internal cross-referencing, or kept if they correspond to an existing bibliography system not provided in the snippet.)*
