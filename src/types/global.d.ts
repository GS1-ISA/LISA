declare module 'minimatch';
declare module '@google-cloud/local-auth';
declare module 'googleapis';
declare module 'universal-user-agent';
declare module 'puppeteer';
declare module 'redis';
declare module 'pg';
declare module 'shell-quote';
declare module 'fzf';
declare module 'i18next';
declare module 'shiki';
declare module 'posthog-js';
declare module 'p-map';
declare module 'vite';
declare module '@vitejs/plugin-react';
declare module '@tailwindcss/vite';

// For import.meta.glob
interface ImportMeta {
  readonly glob: (pattern: string, options?: { eager?: boolean }) => Record<string, () => Promise<unknown>>;
}

// For test globals if @types/jest or @types/mocha are not picked up correctly
declare const suite: any;
declare const test: any;
declare const expect: any;
declare const beforeEach: any;
declare const jest: any;
declare const it: any;
declare const suiteSetup: any;
declare const suiteTeardown: any;
declare const setup: any;
declare const teardown: any;