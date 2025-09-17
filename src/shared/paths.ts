// Centralized path constants for ISA_D project
// This file contains commonly used paths to avoid hard-coding

export const DATABASE_URLS = {
  AUTH: "sqlite:///./isa_auth.db",
  AUDIT: "sqlite:///./isa_audit.db",
  MAIN: "sqlite:///./isa.db"
} as const;

export type DatabaseKey = keyof typeof DATABASE_URLS;

export function path(key: DatabaseKey): string {
  return DATABASE_URLS[key];
}

// Default database URL for backward compatibility
export const DEFAULT_DATABASE_URL = DATABASE_URLS.AUTH;