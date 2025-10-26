/**
 * Secure Storage Utility
 * Provides encrypted storage for sensitive data using Web Crypto API
 * Addresses HIGH priority security issue: localStorage without encryption
 */

import { logger } from '@/lib/logger';

interface EncryptedData {
  iv: string;
  data: string;
}

class SecureStorage {
  private static instance: SecureStorage;
  private encryptionKey: CryptoKey | null = null;
  private readonly STORAGE_KEY_PREFIX = 'paiid_secure_';
  private readonly ENCRYPTION_ALGORITHM = 'AES-GCM';
  private readonly KEY_LENGTH = 256;

  private constructor() {
    this.initializeEncryptionKey();
  }

  public static getInstance(): SecureStorage {
    if (!SecureStorage.instance) {
      SecureStorage.instance = new SecureStorage();
    }
    return SecureStorage.instance;
  }

  /**
   * Initialize or retrieve encryption key from secure storage
   */
  private async initializeEncryptionKey(): Promise<void> {
    try {
      // Try to get existing key material from sessionStorage (temporary per-session)
      const keyMaterial = sessionStorage.getItem('__key_material__');
      
      if (keyMaterial) {
        // Import existing key
        this.encryptionKey = await this.importKey(keyMaterial);
      } else {
        // Generate new key for this session
        this.encryptionKey = await window.crypto.subtle.generateKey(
          {
            name: this.ENCRYPTION_ALGORITHM,
            length: this.KEY_LENGTH,
          },
          true,
          ['encrypt', 'decrypt']
        );

        // Export and store key material for session
        const exported = await window.crypto.subtle.exportKey('jwk', this.encryptionKey);
        sessionStorage.setItem('__key_material__', JSON.stringify(exported));
      }
    } catch (error) {
      logger.error('Failed to initialize encryption key', error);
      throw new Error('Secure storage initialization failed');
    }
  }

  /**
   * Import cryptographic key from JWK format
   */
  private async importKey(keyMaterialJson: string): Promise<CryptoKey> {
    const keyMaterial = JSON.parse(keyMaterialJson);
    return await window.crypto.subtle.importKey(
      'jwk',
      keyMaterial,
      {
        name: this.ENCRYPTION_ALGORITHM,
        length: this.KEY_LENGTH,
      },
      true,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encrypt data using AES-GCM
   */
  private async encrypt(data: string): Promise<EncryptedData> {
    if (!this.encryptionKey) {
      await this.initializeEncryptionKey();
    }

    if (!this.encryptionKey) {
      throw new Error('Encryption key not available');
    }

    // Generate random IV (Initialization Vector)
    const iv = window.crypto.getRandomValues(new Uint8Array(12));

    // Encode data to bytes
    const encoder = new TextEncoder();
    const dataBytes = encoder.encode(data);

    // Encrypt
    const encryptedBytes = await window.crypto.subtle.encrypt(
      {
        name: this.ENCRYPTION_ALGORITHM,
        iv: iv,
      },
      this.encryptionKey,
      dataBytes
    );

    // Convert to base64 for storage
    const encryptedBase64 = this.arrayBufferToBase64(encryptedBytes);
    const ivBase64 = this.arrayBufferToBase64(iv);

    return {
      iv: ivBase64,
      data: encryptedBase64,
    };
  }

  /**
   * Decrypt data using AES-GCM
   */
  private async decrypt(encryptedData: EncryptedData): Promise<string> {
    if (!this.encryptionKey) {
      await this.initializeEncryptionKey();
    }

    if (!this.encryptionKey) {
      throw new Error('Encryption key not available');
    }

    // Convert from base64
    const iv = this.base64ToArrayBuffer(encryptedData.iv);
    const data = this.base64ToArrayBuffer(encryptedData.data);

    // Decrypt
    const decryptedBytes = await window.crypto.subtle.decrypt(
      {
        name: this.ENCRYPTION_ALGORITHM,
        iv: iv,
      },
      this.encryptionKey,
      data
    );

    // Decode bytes to string
    const decoder = new TextDecoder();
    return decoder.decode(decryptedBytes);
  }

  /**
   * Store encrypted data in localStorage
   */
  public async setItem(key: string, value: string): Promise<void> {
    try {
      const encrypted = await this.encrypt(value);
      const storageKey = this.STORAGE_KEY_PREFIX + key;
      localStorage.setItem(storageKey, JSON.stringify(encrypted));
    } catch (error) {
      logger.error('Failed to store encrypted data', error);
      throw error;
    }
  }

  /**
   * Retrieve and decrypt data from localStorage
   */
  public async getItem(key: string): Promise<string | null> {
    try {
      const storageKey = this.STORAGE_KEY_PREFIX + key;
      const storedData = localStorage.getItem(storageKey);

      if (!storedData) {
        return null;
      }

      const encryptedData: EncryptedData = JSON.parse(storedData);
      return await this.decrypt(encryptedData);
    } catch (error) {
      logger.error('Failed to retrieve encrypted data', error);
      return null;
    }
  }

  /**
   * Remove item from secure storage
   */
  public removeItem(key: string): void {
    const storageKey = this.STORAGE_KEY_PREFIX + key;
    localStorage.removeItem(storageKey);
  }

  /**
   * Clear all secure storage items
   */
  public clear(): void {
    const keysToRemove: string[] = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.STORAGE_KEY_PREFIX)) {
        keysToRemove.push(key);
      }
    }

    keysToRemove.forEach(key => localStorage.removeItem(key));
  }

  /**
   * Check if secure storage is available
   */
  public static isAvailable(): boolean {
    try {
      return (
        typeof window !== 'undefined' &&
        !!window.crypto &&
        !!window.crypto.subtle &&
        !!localStorage
      );
    } catch {
      return false;
    }
  }

  /**
   * Convert ArrayBuffer to Base64 string
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Convert Base64 string to ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
}

// Export singleton instance
export const secureStorage = SecureStorage.getInstance();

// Export helper functions for common use cases
export const secureStorageHelpers = {
  /**
   * Store authentication token securely
   */
  async storeAuthToken(token: string): Promise<void> {
    await secureStorage.setItem('auth_token', token);
  },

  /**
   * Retrieve authentication token
   */
  async getAuthToken(): Promise<string | null> {
    return await secureStorage.getItem('auth_token');
  },

  /**
   * Remove authentication token
   */
  removeAuthToken(): void {
    secureStorage.removeItem('auth_token');
  },

  /**
   * Store API keys securely
   */
  async storeApiKey(service: string, apiKey: string): Promise<void> {
    await secureStorage.setItem(`api_key_${service}`, apiKey);
  },

  /**
   * Retrieve API key
   */
  async getApiKey(service: string): Promise<string | null> {
    return await secureStorage.getItem(`api_key_${service}`);
  },

  /**
   * Store user preferences securely
   */
  async storeUserPreferences(preferences: Record<string, unknown>): Promise<void> {
    await secureStorage.setItem('user_preferences', JSON.stringify(preferences));
  },

  /**
   * Retrieve user preferences
   */
  async getUserPreferences(): Promise<Record<string, unknown> | null> {
    const data = await secureStorage.getItem('user_preferences');
    return data ? JSON.parse(data) : null;
  },

  /**
   * Clear all secure data (on logout)
   */
  clearAll(): void {
    secureStorage.clear();
    sessionStorage.clear();
  },
};

export default secureStorage;

