/**
 * GS1 Digital Link Toolkit wrapper for ISA frontend
 *
 * Provides TypeScript interface to GS1DigitalLinkToolkit.js for web-based GS1 processing
 */

// Declare the global GS1DigitalLinkToolkit object
declare const window: any;

export interface GS1DigitalLink {
  primaryKey: string;
  qualifierPath: string[];
  dataAttributes: Record<string, string>;
  aiData: Record<string, string>;
}

export interface GS1ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
}

export class GS1Toolkit {
  private toolkit: any;

  constructor() {
    if (typeof window !== 'undefined' && window.GS1DigitalLinkToolkit) {
      this.toolkit = window.GS1DigitalLinkToolkit;
    } else {
      throw new Error('GS1DigitalLinkToolkit not loaded. Make sure to include the script.');
    }
  }

  /**
   * Parse a GS1 Digital Link URI
   */
  parseDigitalLink(uri: string): GS1DigitalLink | null {
    try {
      return this.toolkit.parseDigitalLink(uri);
    } catch (error) {
      console.error('Error parsing GS1 Digital Link:', error);
      return null;
    }
  }

  /**
   * Build a GS1 Digital Link URI from components
   */
  buildDigitalLink(
    primaryKey: string,
    qualifiers?: Record<string, string>,
    dataAttributes?: Record<string, string>
  ): string {
    try {
      return this.toolkit.buildDigitalLink(primaryKey, qualifiers, dataAttributes);
    } catch (error) {
      console.error('Error building GS1 Digital Link:', error);
      return '';
    }
  }

  /**
   * Validate GS1 data
   */
  validateGS1Data(data: string): GS1ValidationResult {
    try {
      const result = this.toolkit.validateGS1Data(data);
      return {
        isValid: result.isValid,
        errors: result.errors || [],
        warnings: result.warnings || []
      };
    } catch (error) {
      console.error('Error validating GS1 data:', error);
      return {
        isValid: false,
        errors: ['Validation failed'],
        warnings: []
      };
    }
  }

  /**
   * Extract AI data from GS1 string
   */
  extractAIData(gs1String: string): Record<string, string> {
    try {
      return this.toolkit.extractAIData(gs1String);
    } catch (error) {
      console.error('Error extracting AI data:', error);
      return {};
    }
  }

  /**
   * Compress a GS1 Digital Link
   */
  compressDigitalLink(uri: string): string {
    try {
      return this.toolkit.compressDigitalLink(uri);
    } catch (error) {
      console.error('Error compressing GS1 Digital Link:', error);
      return uri;
    }
  }

  /**
   * Decompress a compressed GS1 Digital Link
   */
  decompressDigitalLink(compressedUri: string): string {
    try {
      return this.toolkit.decompressDigitalLink(compressedUri);
    } catch (error) {
      console.error('Error decompressing GS1 Digital Link:', error);
      return compressedUri;
    }
  }
}

// Export a singleton instance
let gs1ToolkitInstance: GS1Toolkit | null = null;

export function getGS1Toolkit(): GS1Toolkit {
  if (!gs1ToolkitInstance) {
    gs1ToolkitInstance = new GS1Toolkit();
  }
  return gs1ToolkitInstance;
}

// Utility functions
export function loadGS1Toolkit(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof window === 'undefined') {
      reject(new Error('GS1 Toolkit can only be loaded in browser environment'));
      return;
    }

    if (window.GS1DigitalLinkToolkit) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = '/lib/GS1DigitalLinkToolkit.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load GS1DigitalLinkToolkit.js'));
    document.head.appendChild(script);
  });
}

export default GS1Toolkit;