"""
VC Storage and Retrieval System

This module provides persistent storage for Verifiable Credentials
with efficient retrieval mechanisms and indexing.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from dataclasses import asdict

from .supplier_attestation_vc import SupplierAttestationCredential

logger = logging.getLogger(__name__)

class VCStorage:
    """Storage system for Verifiable Credentials."""

    def __init__(self, storage_path: str = "vc_storage.db"):
        self.storage_path = Path(storage_path)
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.storage_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id TEXT PRIMARY KEY,
                    issuer TEXT,
                    subject_id TEXT,
                    type TEXT,
                    issuance_date TEXT,
                    expiration_date TEXT,
                    status TEXT DEFAULT 'active',
                    credential_data TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')

            # Create indexes for efficient queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_issuer ON credentials(issuer)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_subject ON credentials(subject_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_type ON credentials(type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status ON credentials(status)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_expiration ON credentials(expiration_date)')

            # Revocation table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS revocations (
                    credential_id TEXT PRIMARY KEY,
                    revocation_date TEXT,
                    revocation_reason TEXT,
                    revoked_by TEXT,
                    FOREIGN KEY (credential_id) REFERENCES credentials(id)
                )
            ''')

    def store_credential(self, credential: SupplierAttestationCredential) -> bool:
        """Store a VC in the database."""
        try:
            credential_data = json.dumps(credential.to_dict(), default=str)

            with sqlite3.connect(self.storage_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO credentials
                    (id, issuer, subject_id, type, issuance_date, expiration_date,
                     credential_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    credential.id,
                    credential.issuer,
                    credential.credential_subject.get("id", ""),
                    json.dumps(credential.type),
                    credential.issuance_date,
                    credential.expiration_date,
                    credential_data,
                    datetime.now(timezone.utc).isoformat(),
                    datetime.now(timezone.utc).isoformat()
                ))

            logger.info(f"Stored VC: {credential.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store VC {credential.id}: {e}")
            return False

    def retrieve_credential(self, credential_id: str) -> Optional[SupplierAttestationCredential]:
        """Retrieve a VC by ID."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT credential_data FROM credentials
                    WHERE id = ? AND status = 'active'
                ''', (credential_id,))

                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    return SupplierAttestationCredential.from_dict(data)

        except Exception as e:
            logger.error(f"Failed to retrieve VC {credential_id}: {e}")

        return None

    def retrieve_credentials_by_subject(self, subject_id: str) -> List[SupplierAttestationCredential]:
        """Retrieve all VCs for a subject."""
        credentials = []
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT credential_data FROM credentials
                    WHERE subject_id = ? AND status = 'active'
                    ORDER BY issuance_date DESC
                ''', (subject_id,))

                for row in cursor.fetchall():
                    data = json.loads(row[0])
                    credentials.append(SupplierAttestationCredential.from_dict(data))

        except Exception as e:
            logger.error(f"Failed to retrieve VCs for subject {subject_id}: {e}")

        return credentials

    def retrieve_credentials_by_issuer(self, issuer: str) -> List[SupplierAttestationCredential]:
        """Retrieve all VCs issued by an issuer."""
        credentials = []
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT credential_data FROM credentials
                    WHERE issuer = ? AND status = 'active'
                    ORDER BY issuance_date DESC
                ''', (issuer,))

                for row in cursor.fetchall():
                    data = json.loads(row[0])
                    credentials.append(SupplierAttestationCredential.from_dict(data))

        except Exception as e:
            logger.error(f"Failed to retrieve VCs for issuer {issuer}: {e}")

        return credentials

    def retrieve_credentials_by_type(self, credential_type: str) -> List[SupplierAttestationCredential]:
        """Retrieve VCs by type."""
        credentials = []
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT credential_data FROM credentials
                    WHERE type LIKE ? AND status = 'active'
                    ORDER BY issuance_date DESC
                ''', (f'%{credential_type}%',))

                for row in cursor.fetchall():
                    data = json.loads(row[0])
                    credentials.append(SupplierAttestationCredential.from_dict(data))

        except Exception as e:
            logger.error(f"Failed to retrieve VCs by type {credential_type}: {e}")

        return credentials

    def revoke_credential(self, credential_id: str, reason: str, revoked_by: str) -> bool:
        """Revoke a VC."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                # Update credential status
                conn.execute('''
                    UPDATE credentials SET status = 'revoked', updated_at = ?
                    WHERE id = ?
                ''', (datetime.now(timezone.utc).isoformat(), credential_id))

                # Add revocation record
                conn.execute('''
                    INSERT INTO revocations
                    (credential_id, revocation_date, revocation_reason, revoked_by)
                    VALUES (?, ?, ?, ?)
                ''', (
                    credential_id,
                    datetime.now(timezone.utc).isoformat(),
                    reason,
                    revoked_by
                ))

            logger.info(f"Revoked VC: {credential_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to revoke VC {credential_id}: {e}")
            return False

    def check_revocation_status(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Check if a VC is revoked."""
        try:
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT revocation_date, revocation_reason, revoked_by
                    FROM revocations WHERE credential_id = ?
                ''', (credential_id,))

                row = cursor.fetchone()
                if row:
                    return {
                        "revoked": True,
                        "revocation_date": row[0],
                        "reason": row[1],
                        "revoked_by": row[2]
                    }

                # Check if credential exists and is active
                cursor = conn.execute('SELECT status FROM credentials WHERE id = ?', (credential_id,))
                row = cursor.fetchone()
                if row and row[0] == 'revoked':
                    return {"revoked": True, "reason": "Credential revoked"}

        except Exception as e:
            logger.error(f"Failed to check revocation status for {credential_id}: {e}")

        return {"revoked": False}

    def get_expired_credentials(self) -> List[str]:
        """Get list of expired credential IDs."""
        expired = []
        try:
            now = datetime.now(timezone.utc).isoformat()
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    SELECT id FROM credentials
                    WHERE expiration_date < ? AND status = 'active'
                ''', (now,))

                expired = [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Failed to get expired credentials: {e}")

        return expired

    def cleanup_expired_credentials(self) -> int:
        """Mark expired credentials as inactive. Returns count of cleaned up credentials."""
        try:
            now = datetime.now(timezone.utc).isoformat()
            with sqlite3.connect(self.storage_path) as conn:
                cursor = conn.execute('''
                    UPDATE credentials SET status = 'expired', updated_at = ?
                    WHERE expiration_date < ? AND status = 'active'
                ''', (now, now))

                count = cursor.rowcount

            logger.info(f"Cleaned up {count} expired credentials")
            return count

        except Exception as e:
            logger.error(f"Failed to cleanup expired credentials: {e}")
            return 0

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            "total_credentials": 0,
            "active_credentials": 0,
            "revoked_credentials": 0,
            "expired_credentials": 0,
            "total_revocations": 0
        }

        try:
            with sqlite3.connect(self.storage_path) as conn:
                # Count credentials by status
                cursor = conn.execute('SELECT status, COUNT(*) FROM credentials GROUP BY status')
                for row in cursor.fetchall():
                    status, count = row
                    stats[f"{status}_credentials"] = count
                    stats["total_credentials"] += count

                # Count revocations
                cursor = conn.execute('SELECT COUNT(*) FROM revocations')
                stats["total_revocations"] = cursor.fetchone()[0]

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")

        return stats

class VCRegistry:
    """Registry for managing VC metadata and status."""

    def __init__(self, storage: VCStorage):
        self.storage = storage
        self.registry: Dict[str, Dict[str, Any]] = {}

    def register_credential(self, credential: SupplierAttestationCredential) -> bool:
        """Register a VC in the registry."""
        try:
            self.registry[credential.id] = {
                "issuer": credential.issuer,
                "subject_id": credential.credential_subject.get("id"),
                "type": credential.type,
                "issuance_date": credential.issuance_date,
                "expiration_date": credential.expiration_date,
                "status": "active",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            return True

        except Exception as e:
            logger.error(f"Failed to register VC {credential.id}: {e}")
            return False

    def get_credential_status(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a VC."""
        # Check registry first
        if credential_id in self.registry:
            return self.registry[credential_id]

        # Check storage
        revocation_status = self.storage.check_revocation_status(credential_id)
        if revocation_status["revoked"]:
            return {
                "status": "revoked",
                "revocation_info": revocation_status
            }

        # Check if credential exists
        credential = self.storage.retrieve_credential(credential_id)
        if credential:
            return {
                "status": "active",
                "issuer": credential.issuer,
                "subject_id": credential.credential_subject.get("id"),
                "type": credential.type
            }

        return None

    def update_credential_status(self, credential_id: str, status: str) -> bool:
        """Update the status of a VC."""
        try:
            if credential_id in self.registry:
                self.registry[credential_id]["status"] = status
                self.registry[credential_id]["last_updated"] = datetime.now(timezone.utc).isoformat()
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update VC status {credential_id}: {e}")
            return False

    def list_credentials_by_status(self, status: str) -> List[str]:
        """List credential IDs by status."""
        return [
            cred_id for cred_id, info in self.registry.items()
            if info.get("status") == status
        ]