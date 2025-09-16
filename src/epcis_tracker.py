"""
EPCIS Integration Module for ISA

This module provides integration with EPCIS (Electronic Product Code Information Services)
for supply chain event tracking and GS1-based traceability systems.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
import requests


class EventType(Enum):
    OBJECT_EVENT = "ObjectEvent"
    AGGREGATION_EVENT = "AggregationEvent"
    TRANSACTION_EVENT = "TransactionEvent"
    TRANSFORMATION_EVENT = "TransformationEvent"
    ASSOCIATION_EVENT = "AssociationEvent"


class Action(Enum):
    ADD = "ADD"
    OBSERVE = "OBSERVE"
    DELETE = "DELETE"


class BizStep(Enum):
    COMMISSIONING = "commissioning"
    SHIPPING = "shipping"
    RECEIVING = "receiving"
    HOLDING = "holding"
    STORING = "storing"
    PICKING = "picking"
    PACKING = "packing"
    LOADING = "loading"
    UNLOADING = "unloading"
    ACCEPTING = "accepting"
    REJECTING = "rejecting"
    RETURNING = "returning"
    DESTROYING = "destroying"


class Disposition(Enum):
    ACTIVE = "active"
    CONTAINER_CLOSED = "container_closed"
    DAMAGED = "damaged"
    DESTROYED = "destroyed"
    DISPOSED = "disposed"
    ENCODED = "encoded"
    EXPIRED = "expired"
    IN_PROGRESS = "in_progress"
    IN_TRANSIT = "in_transit"
    NO_PEDIGREE_MATCH = "no_pedigree_match"
    NON_SELLABLE_OTHER = "non_sellable_other"
    NON_SELLABLE_MISSING_COMPONENTS = "non_sellable_missing_components"
    RECALLED = "recalled"
    RESERVED = "reserved"
    RETAIL_SOLD = "retail_sold"
    RETURNED = "returned"
    SELLABLE_ACCESSIBLE = "sellable_accessible"
    SELLABLE_NOT_ACCESSIBLE = "sellable_not_accessible"
    STOLEN = "stolen"
    UNAVAILABLE = "unavailable"


@dataclass
class EPCISLocation:
    """Represents a location in EPCIS events."""
    id: str

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id}


@dataclass
class BizTransaction:
    """Represents a business transaction in EPCIS events."""
    type: str
    bizTransaction: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "bizTransaction": self.bizTransaction}


@dataclass
class EPCISEvent:
    """Base class for EPCIS events."""
    eventID: str
    type: EventType
    action: Action
    bizStep: BizStep
    disposition: Optional[Disposition] = None
    epcList: Optional[List[str]] = None
    eventTime: Optional[str] = None
    eventTimeZoneOffset: Optional[str] = None
    readPoint: Optional[EPCISLocation] = None
    bizLocation: Optional[EPCISLocation] = None
    bizTransactionList: Optional[List[BizTransaction]] = None
    parentID: Optional[str] = None
    childEPCs: Optional[List[str]] = None
    inputEPCList: Optional[List[str]] = None
    outputEPCList: Optional[List[str]] = None
    transformationID: Optional[str] = None
    ilmd: Optional[Dict[str, Any]] = None
    customFields: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.eventTime is None:
            self.eventTime = datetime.now(timezone.utc).isoformat()
        if self.eventTimeZoneOffset is None:
            self.eventTimeZoneOffset = "+00:00"
        if self.eventID is None:
            self.eventID = self._generate_event_id()

    def _generate_event_id(self) -> str:
        """Generate a unique event ID using SHA-256 hash."""
        content = f"{self.type.value}{self.action.value}{self.bizStep.value}{self.eventTime}"
        if self.epcList:
            content += "".join(self.epcList)
        hash_obj = hashlib.sha256(content.encode())
        return f"ni:///sha-256;{hash_obj.hexdigest()}?ver=CBV2.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        data = asdict(self)
        data["type"] = self.type.value
        data["action"] = self.action.value
        data["bizStep"] = self.bizStep.value
        if self.disposition:
            data["disposition"] = self.disposition.value
        if self.readPoint:
            data["readPoint"] = self.readPoint.to_dict()
        if self.bizLocation:
            data["bizLocation"] = self.bizLocation.to_dict()
        if self.bizTransactionList:
            data["bizTransactionList"] = [bt.to_dict() for bt in self.bizTransactionList]
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class EPCISDocument:
    """Represents an EPCIS document containing events."""
    id: str
    schemaVersion: str = "2.0"
    creationDate: Optional[str] = None
    eventList: Optional[List[EPCISEvent]] = None
    context: Optional[List[Any]] = None

    def __post_init__(self):
        if self.creationDate is None:
            self.creationDate = datetime.now(timezone.utc).isoformat()
        if self.context is None:
            self.context = ["https://ref.gs1.org/standards/epcis/2.0.0/epcis-context.jsonld"]

    def to_jsonld(self) -> str:
        """Convert document to JSON-LD format."""
        data = {
            "@context": self.context,
            "id": self.id,
            "type": "EPCISDocument",
            "schemaVersion": self.schemaVersion,
            "creationDate": self.creationDate,
            "epcisBody": {
                "eventList": [event.to_dict() for event in (self.eventList or [])]
            }
        }
        return json.dumps(data, indent=2)

    @classmethod
    def from_jsonld(cls, jsonld_str: str) -> 'EPCISDocument':
        """Create document from JSON-LD string."""
        data = json.loads(jsonld_str)
        event_list = []
        if "epcisBody" in data and "eventList" in data["epcisBody"]:
            for event_data in data["epcisBody"]["eventList"]:
                event = cls._parse_event(event_data)
                event_list.append(event)

        return cls(
            id=data.get("id", ""),
            schemaVersion=data.get("schemaVersion", "2.0"),
            creationDate=data.get("creationDate"),
            eventList=event_list,
            context=data.get("@context")
        )

    @staticmethod
    def _parse_event(event_data: Dict[str, Any]) -> EPCISEvent:
        """Parse event data from dictionary."""
        # Parse nested objects
        read_point = None
        if "readPoint" in event_data:
            read_point = EPCISLocation(id=event_data["readPoint"]["id"])

        biz_location = None
        if "bizLocation" in event_data:
            biz_location = EPCISLocation(id=event_data["bizLocation"]["id"])

        biz_transactions = []
        if "bizTransactionList" in event_data:
            for bt_data in event_data["bizTransactionList"]:
                biz_transactions.append(BizTransaction(
                    type=bt_data["type"],
                    bizTransaction=bt_data["bizTransaction"]
                ))

        return EPCISEvent(
            eventID=event_data.get("eventID", ""),
            type=EventType(event_data["type"]),
            action=Action(event_data["action"]),
            bizStep=BizStep(event_data["bizStep"]),
            disposition=Disposition(event_data["disposition"]) if "disposition" in event_data else None,
            epcList=event_data.get("epcList"),
            eventTime=event_data.get("eventTime"),
            eventTimeZoneOffset=event_data.get("eventTimeZoneOffset"),
            readPoint=read_point,
            bizLocation=biz_location,
            bizTransactionList=biz_transactions if biz_transactions else None,
            parentID=event_data.get("parentID"),
            childEPCs=event_data.get("childEPCs"),
            inputEPCList=event_data.get("inputEPCList"),
            outputEPCList=event_data.get("outputEPCList"),
            transformationID=event_data.get("transformationID"),
            ilmd=event_data.get("ilmd"),
            customFields={k: v for k, v in event_data.items() if k.startswith(('example:', 'vendor:'))}
        )


class EPCISTracker:
    """Main class for EPCIS supply chain event tracking."""

    def __init__(self):
        self.documents: List[EPCISDocument] = []
        self.events: List[EPCISEvent] = []
        self.openeepcis_url = os.getenv("OPENEPCIS_URL", "http://openeepcis:8080")
        self.logger = logging.getLogger(__name__)
    def _send_to_openeepcis(self, event: EPCISEvent) -> None:
        """Send event to OpenEPCIS service."""
        try:
            url = f"{self.openeepcis_url}/epcis/v2/events"
            headers = {"Content-Type": "application/json"}
            data = event.to_dict()
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 201:
                self.logger.info(f"Successfully sent event {event.eventID} to OpenEPCIS")
            else:
                self.logger.warning(f"Failed to send event to OpenEPCIS: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"Error sending event to OpenEPCIS: {e}")

    def create_event(self, event_type: str, action: str, biz_step: str, epc_list: Optional[List[str]] = None, **kwargs) -> EPCISEvent:
        """Create an EPCIS event based on type."""
        event_type_enum = EventType(event_type)
        action_enum = Action(action)
        biz_step_enum = BizStep(biz_step)

        if event_type_enum == EventType.OBJECT_EVENT:
            event = self.create_object_event(
                epc_list=epc_list or [],
                action=action_enum,
                biz_step=biz_step_enum,
                **kwargs
            )
        elif event_type_enum == EventType.AGGREGATION_EVENT:
            event = self.create_aggregation_event(
                parent_id=kwargs.get("parentID", ""),
                child_epcs=kwargs.get("childEPCs", []),
                action=action_enum,
                biz_step=biz_step_enum,
                **kwargs
            )
        elif event_type_enum == EventType.TRANSFORMATION_EVENT:
            event = self.create_transformation_event(
                input_epcs=kwargs.get("inputEPCList", []),
                output_epcs=kwargs.get("outputEPCList", []),
                transformation_id=kwargs.get("transformationID", ""),
                biz_step=biz_step_enum,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported event type: {event_type}")

        # Send to OpenEPCIS
        self._send_to_openeepcis(event)
        return event


    def create_object_event(self, epc_list: List[str], action: Action, biz_step: BizStep,
                          disposition: Optional[Disposition] = None,
                          read_point: Optional[EPCISLocation] = None,
                          biz_location: Optional[EPCISLocation] = None,
                          biz_transactions: Optional[List[BizTransaction]] = None) -> EPCISEvent:
        """Create an Object Event for tracking individual objects."""
        event = EPCISEvent(
            eventID=None,  # Will be auto-generated
            type=EventType.OBJECT_EVENT,
            action=action,
            bizStep=biz_step,
            disposition=disposition,
            epcList=epc_list,
            readPoint=read_point,
            bizLocation=biz_location,
            bizTransactionList=biz_transactions
        )
        self.events.append(event)
        return event

    def create_aggregation_event(self, parent_id: str, child_epcs: List[str], action: Action,
                               biz_step: BizStep, disposition: Optional[Disposition] = None,
                               read_point: Optional[EPCISLocation] = None,
                               biz_location: Optional[EPCISLocation] = None) -> EPCISEvent:
        """Create an Aggregation Event for tracking parent-child relationships."""
        event = EPCISEvent(
            eventID=None,
            type=EventType.AGGREGATION_EVENT,
            action=action,
            bizStep=biz_step,
            disposition=disposition,
            parentID=parent_id,
            childEPCs=child_epcs,
            readPoint=read_point,
            bizLocation=biz_location
        )
        self.events.append(event)
        return event

    def create_transformation_event(self, input_epcs: List[str], output_epcs: List[str],
                                  transformation_id: str, biz_step: BizStep,
                                  disposition: Optional[Disposition] = None,
                                  read_point: Optional[EPCISLocation] = None,
                                  biz_location: Optional[EPCISLocation] = None) -> EPCISEvent:
        """Create a Transformation Event for tracking product transformations."""
        event = EPCISEvent(
            eventID=None,
            type=EventType.TRANSFORMATION_EVENT,
            action=Action.OBSERVE,
            bizStep=biz_step,
            disposition=disposition,
            inputEPCList=input_epcs,
            outputEPCList=output_epcs,
            transformationID=transformation_id,
            readPoint=read_point,
            bizLocation=biz_location
        )
        self.events.append(event)
        return event

    def create_document(self, document_id: str, events: Optional[List[EPCISEvent]] = None) -> EPCISDocument:
        """Create an EPCIS document containing events."""
        if events is None:
            events = self.events[-len(events or []):]  # Use recent events if none specified

        document = EPCISDocument(
            id=document_id,
            eventList=events
        )
        self.documents.append(document)
        return document

    def track_supply_chain(self, epc: str, events: List[EPCISEvent]) -> List[EPCISEvent]:
        """Track the supply chain history for a specific EPC."""
        return [event for event in events if epc in (event.epcList or [])]

    def validate_event(self, event: EPCISEvent) -> bool:
        """Validate an EPCIS event according to GS1 standards."""
        # Basic validation
        if not event.eventID:
            return False
        if not event.type:
            return False
        if not event.action:
            return False
        if not event.bizStep:
            return False

        # Type-specific validation
        if event.type == EventType.OBJECT_EVENT and not event.epcList:
            return False
        if event.type == EventType.AGGREGATION_EVENT and (not event.parentID or not event.childEPCs):
            return False
        if event.type == EventType.TRANSFORMATION_EVENT and (not event.inputEPCList or not event.outputEPCList):
            return False

        return True

    def export_to_jsonld(self, document: EPCISDocument) -> str:
        """Export EPCIS document to JSON-LD format."""
        return document.to_jsonld()

    def import_from_jsonld(self, jsonld_str: str) -> EPCISDocument:
        """Import EPCIS document from JSON-LD format."""
        return EPCISDocument.from_jsonld(jsonld_str)