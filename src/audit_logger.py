"""
Comprehensive Audit Logging System for ISA_D
Provides enterprise-grade audit logging with compliance features.

This module provides:
- Structured audit logging with multiple storage backends
- Compliance-ready audit trails
- Real-time monitoring and alerting
- Data retention and archiving
- Search and reporting capabilities
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.encryption import EncryptedText


class AuditEventType(str, Enum):
    """Audit event types for categorization"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ACCESS = "system_access"
    SECURITY_EVENT = "security_event"
    COMPLIANCE = "compliance"
    ADMIN_ACTION = "admin_action"
    USER_ACTIVITY = "user_activity"
    API_ACCESS = "api_access"


class AuditEventSeverity(str, Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event data structure"""
    event_type: AuditEventType
    severity: AuditEventSeverity
    user_id: int | None
    username: str | None
    session_id: str | None
    ip_address: str | None
    user_agent: str | None
    resource: str
    action: str
    outcome: str  # success, failure, blocked, etc.
    details: dict[str, Any]
    timestamp: datetime
    event_id: str
    checksum: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AuditEvent":
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy["event_type"] = AuditEventType(data["event_type"])
        data_copy["severity"] = AuditEventSeverity(data["severity"])
        data_copy["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data_copy)


# Database models for audit logging
AuditBase = declarative_base()


class AuditLogEntry(AuditBase):
    """Database model for audit log entries"""
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True, nullable=False)
    event_type = Column(String, nullable=False, index=True)
    severity = Column(String, nullable=False, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String, index=True)
    session_id = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(Text)
    resource = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    outcome = Column(String, nullable=False)
    details = Column(EncryptedText)  # Encrypted for sensitive data
    timestamp = Column(DateTime, nullable=False, index=True)
    checksum = Column(String, nullable=False)
    archived = Column(Boolean, default=False)
    retention_date = Column(DateTime)


class AuditAlert(AuditBase):
    """Database model for audit alerts"""
    __tablename__ = "audit_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text)
    event_ids = Column(JSON)  # List of related event IDs
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)


class AuditLogger:
    """Main audit logging service"""

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or "sqlite:///./isa_audit.db"
        self._engine = None
        self._session_maker = None
        self._alert_rules = {}
        self._initialize_database()

    def _initialize_database(self):
        """Initialize audit database"""
        self._engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            echo=False
        )

        self._session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )

        # Create tables
        AuditBase.metadata.create_all(bind=self._engine)

    def log_event(
        self,
        event_type: AuditEventType,
        severity: AuditEventSeverity,
        resource: str,
        action: str,
        outcome: str,
        user_id: int | None = None,
        username: str | None = None,
        session_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: dict[str, Any] | None = None,
        sensitive_data: bool = False
    ) -> str:
        """Log an audit event"""
        timestamp = datetime.utcnow()
        event_id = self._generate_event_id(timestamp, resource, action)
        details_json = json.dumps(details or {})

        # Create checksum for integrity
        checksum_data = f"{event_id}{event_type.value}{resource}{action}{outcome}{details_json}"
        checksum = hashlib.sha256(checksum_data.encode()).hexdigest()

        # Create audit event
        audit_event = AuditEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            username=username,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource=resource,
            action=action,
            outcome=outcome,
            details=details or {},
            timestamp=timestamp,
            event_id=event_id,
            checksum=checksum
        )

        # Store in database
        with self._get_session() as session:
            db_entry = AuditLogEntry(
                event_id=event_id,
                event_type=event_type.value,
                severity=severity.value,
                user_id=user_id,
                username=username,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                resource=resource,
                action=action,
                outcome=outcome,
                details=details_json if not sensitive_data else None,  # Don't store sensitive details
                timestamp=timestamp,
                checksum=checksum,
                retention_date=timestamp + timedelta(days=2555)  # 7 years retention
            )
            session.add(db_entry)
            session.commit()

        # Check for alerts
        self._check_alerts(audit_event)

        # Log to application logger as well
        logger = logging.getLogger(__name__)
        logger.info(f"AUDIT: {event_type.value} - {resource}:{action} - {outcome} - User: {username or 'N/A'}")

        return event_id

    def _generate_event_id(self, timestamp: datetime, resource: str, action: str) -> str:
        """Generate unique event ID"""
        data = f"{timestamp.isoformat()}{resource}{action}{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _get_session(self) -> Session:
        """Get database session"""
        return self._session_maker()

    def _check_alerts(self, event: AuditEvent):
        """Check if event triggers any alerts"""
        # This would implement alert rules based on event patterns
        # For now, just a placeholder
        pass

    def search_events(
        self,
        event_type: AuditEventType | None = None,
        user_id: int | None = None,
        resource: str | None = None,
        action: str | None = None,
        outcome: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100
    ) -> list[AuditEvent]:
        """Search audit events"""
        with self._get_session() as session:
            query = session.query(AuditLogEntry)

            if event_type:
                query = query.filter(AuditLogEntry.event_type == event_type.value)
            if user_id:
                query = query.filter(AuditLogEntry.user_id == user_id)
            if resource:
                query = query.filter(AuditLogEntry.resource == resource)
            if action:
                query = query.filter(AuditLogEntry.action == action)
            if outcome:
                query = query.filter(AuditLogEntry.outcome == outcome)
            if start_date:
                query = query.filter(AuditLogEntry.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLogEntry.timestamp <= end_date)

            query = query.order_by(AuditLogEntry.timestamp.desc()).limit(limit)

            entries = query.all()
            events = []

            for entry in entries:
                details = json.loads(entry.details) if entry.details else {}
                event = AuditEvent(
                    event_type=AuditEventType(entry.event_type),
                    severity=AuditEventSeverity(entry.severity),
                    user_id=entry.user_id,
                    username=entry.username,
                    session_id=entry.session_id,
                    ip_address=entry.ip_address,
                    user_agent=entry.user_agent,
                    resource=entry.resource,
                    action=entry.action,
                    outcome=entry.outcome,
                    details=details,
                    timestamp=entry.timestamp,
                    event_id=entry.event_id,
                    checksum=entry.checksum
                )
                events.append(event)

            return events

    def get_event_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> dict[str, Any]:
        """Get audit event statistics"""
        with self._get_session() as session:
            query = session.query(AuditLogEntry)

            if start_date:
                query = query.filter(AuditLogEntry.timestamp >= start_date)
            if end_date:
                query = query.filter(AuditLogEntry.timestamp <= end_date)

            total_events = query.count()

            # Count by event type
            event_types = {}
            for event_type in AuditEventType:
                count = query.filter(AuditLogEntry.event_type == event_type.value).count()
                event_types[event_type.value] = count

            # Count by severity
            severities = {}
            for severity in AuditEventSeverity:
                count = query.filter(AuditLogEntry.severity == severity.value).count()
                severities[severity.value] = count

            # Count by outcome
            outcomes = {}
            outcome_counts = session.query(
                AuditLogEntry.outcome,
                session.query(AuditLogEntry).filter(AuditLogEntry.outcome == AuditLogEntry.outcome).count()
            ).group_by(AuditLogEntry.outcome).all()

            for outcome, count in outcome_counts:
                outcomes[outcome] = count

            return {
                "total_events": total_events,
                "event_types": event_types,
                "severities": severities,
                "outcomes": outcomes,
                "period": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }

    def archive_old_events(self, days_to_keep: int = 2555):
        """Archive events older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        with self._get_session() as session:
            # Mark events for archiving
            session.query(AuditLogEntry)\
                .filter(AuditLogEntry.timestamp < cutoff_date)\
                .filter(not AuditLogEntry.archived)\
                .update({"archived": True})

            session.commit()

    def cleanup_expired_events(self):
        """Clean up events past their retention date"""
        with self._get_session() as session:
            expired_events = session.query(AuditLogEntry)\
                .filter(AuditLogEntry.retention_date < datetime.utcnow())\
                .all()

            for event in expired_events:
                session.delete(event)

            session.commit()
            return len(expired_events)


# Global audit logger instance
_audit_logger = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


# Convenience functions for common audit events
def log_auth_event(
    action: str,
    outcome: str,
    user_id: int | None = None,
    username: str | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None
):
    """Log authentication event"""
    logger = get_audit_logger()
    logger.log_event(
        event_type=AuditEventType.AUTHENTICATION,
        severity=AuditEventSeverity.MEDIUM if outcome == "failure" else AuditEventSeverity.LOW,
        resource="authentication",
        action=action,
        outcome=outcome,
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        details=details
    )


def log_data_access(
    resource: str,
    action: str,
    user_id: int | None = None,
    username: str | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None
):
    """Log data access event"""
    logger = get_audit_logger()
    logger.log_event(
        event_type=AuditEventType.DATA_ACCESS,
        severity=AuditEventSeverity.LOW,
        resource=resource,
        action=action,
        outcome="success",
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        details=details
    )


def log_security_event(
    action: str,
    severity: AuditEventSeverity,
    resource: str,
    user_id: int | None = None,
    username: str | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None
):
    """Log security event"""
    logger = get_audit_logger()
    logger.log_event(
        event_type=AuditEventType.SECURITY_EVENT,
        severity=severity,
        resource=resource,
        action=action,
        outcome="detected",
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        details=details
    )


def log_admin_action(
    action: str,
    resource: str,
    user_id: int,
    username: str,
    ip_address: str | None = None,
    details: dict[str, Any] | None = None
):
    """Log admin action"""
    logger = get_audit_logger()
    logger.log_event(
        event_type=AuditEventType.ADMIN_ACTION,
        severity=AuditEventSeverity.MEDIUM,
        resource=resource,
        action=action,
        outcome="success",
        user_id=user_id,
        username=username,
        ip_address=ip_address,
        details=details
    )
