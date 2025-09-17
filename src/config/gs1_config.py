"""
GS1 Configuration for ISA

This module contains configuration settings for GS1 integration capabilities
including EPCIS, WebVoc, End-to-End Traceability, and VC validation.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GS1Paths:
    """File system paths for GS1 resources."""
    research_dir: Path = Path("gs1_research")
    webvoc_dir: Path = Path("gs1_research/WebVoc")
    vc_data_model_dir: Path = Path("gs1_research/VC-Data-Model")
    epcis_dir: Path = Path("gs1_research/EPCIS")
    end_to_end_dir: Path = Path("gs1_research/EndToEndTraceability")

@dataclass
class GS1Settings:
    """Core GS1 integration settings."""
    enable_epcis: bool = True
    enable_webvoc: bool = True
    enable_traceability: bool = True
    enable_vc_validation: bool = True
    auto_initialize: bool = True

    # EPCIS settings
    default_event_timezone: str = "UTC"
    max_events_per_document: int = 1000

    # WebVoc settings
    webvoc_cache_enabled: bool = True
    webvoc_cache_ttl: int = 3600  # 1 hour

    # Traceability settings
    default_credential_expiry_days: int = 365
    max_credentials_per_proof: int = 50

    # VC Validation settings
    strict_validation: bool = False
    allow_unknown_properties: bool = True

@dataclass
class GS1Issuers:
    """Pre-configured GS1 issuers for testing and development."""
    test_issuer: str = "https://example.com/issuer/test"
    gs1_official_issuer: str = "https://gs1.org/issuer"
    development_issuer: str = "https://dev.gs1.org/issuer"

class GS1Config:
    """Main GS1 configuration class."""

    def __init__(self):
        self.paths = GS1Paths()
        self.settings = GS1Settings()
        self.issuers = GS1Issuers()
        self._load_from_environment()

    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Path settings
        if research_dir := os.getenv("GS1_RESEARCH_DIR"):
            self.paths.research_dir = Path(research_dir)
            self.paths.webvoc_dir = self.paths.research_dir / "WebVoc"
            self.paths.vc_data_model_dir = self.paths.research_dir / "VC-Data-Model"
            self.paths.epcis_dir = self.paths.research_dir / "EPCIS"
            self.paths.end_to_end_dir = self.paths.research_dir / "EndToEndTraceability"

        # Feature flags
        self.settings.enable_epcis = os.getenv("GS1_ENABLE_EPCIS", "true").lower() == "true"
        self.settings.enable_webvoc = os.getenv("GS1_ENABLE_WEBVOC", "true").lower() == "true"
        self.settings.enable_traceability = os.getenv("GS1_ENABLE_TRACEABILITY", "true").lower() == "true"
        self.settings.enable_vc_validation = os.getenv("GS1_ENABLE_VC_VALIDATION", "true").lower() == "true"
        self.settings.auto_initialize = os.getenv("GS1_AUTO_INITIALIZE", "true").lower() == "true"

        # EPCIS settings
        self.settings.default_event_timezone = os.getenv("GS1_DEFAULT_TIMEZONE", "UTC")
        self.settings.max_events_per_document = int(os.getenv("GS1_MAX_EVENTS_PER_DOC", "1000"))

        # WebVoc settings
        self.settings.webvoc_cache_enabled = os.getenv("GS1_WEBVOC_CACHE_ENABLED", "true").lower() == "true"
        self.settings.webvoc_cache_ttl = int(os.getenv("GS1_WEBVOC_CACHE_TTL", "3600"))

        # Traceability settings
        self.settings.default_credential_expiry_days = int(os.getenv("GS1_CREDENTIAL_EXPIRY_DAYS", "365"))
        self.settings.max_credentials_per_proof = int(os.getenv("GS1_MAX_CREDENTIALS_PER_PROOF", "50"))

        # VC Validation settings
        self.settings.strict_validation = os.getenv("GS1_STRICT_VALIDATION", "false").lower() == "true"
        self.settings.allow_unknown_properties = os.getenv("GS1_ALLOW_UNKNOWN_PROPERTIES", "true").lower() == "true"

        # Issuer settings
        self.issuers.test_issuer = os.getenv("GS1_TEST_ISSUER", "https://example.com/issuer/test")
        self.issuers.gs1_official_issuer = os.getenv("GS1_OFFICIAL_ISSUER", "https://gs1.org/issuer")
        self.issuers.development_issuer = os.getenv("GS1_DEV_ISSUER", "https://dev.gs1.org/issuer")

    def get_enabled_capabilities(self) -> list[str]:
        """Get list of enabled GS1 capabilities."""
        capabilities = []
        if self.settings.enable_epcis:
            capabilities.append("epcis")
        if self.settings.enable_webvoc:
            capabilities.append("webvoc")
        if self.settings.enable_traceability:
            capabilities.append("traceability")
        if self.settings.enable_vc_validation:
            capabilities.append("vc_validation")
        return capabilities

    def is_fully_enabled(self) -> bool:
        """Check if all GS1 capabilities are enabled."""
        return all([
            self.settings.enable_epcis,
            self.settings.enable_webvoc,
            self.settings.enable_traceability,
            self.settings.enable_vc_validation
        ])

    def get_config_summary(self) -> dict:
        """Get a summary of the current GS1 configuration."""
        return {
            "paths": {
                "research_dir": str(self.paths.research_dir),
                "webvoc_dir": str(self.paths.webvoc_dir),
                "vc_data_model_dir": str(self.paths.vc_data_model_dir),
                "epcis_dir": str(self.paths.epcis_dir),
                "end_to_end_dir": str(self.paths.end_to_end_dir)
            },
            "enabled_capabilities": self.get_enabled_capabilities(),
            "settings": {
                "auto_initialize": self.settings.auto_initialize,
                "default_event_timezone": self.settings.default_event_timezone,
                "max_events_per_document": self.settings.max_events_per_document,
                "webvoc_cache_enabled": self.settings.webvoc_cache_enabled,
                "webvoc_cache_ttl": self.settings.webvoc_cache_ttl,
                "default_credential_expiry_days": self.settings.default_credential_expiry_days,
                "max_credentials_per_proof": self.settings.max_credentials_per_proof,
                "strict_validation": self.settings.strict_validation,
                "allow_unknown_properties": self.settings.allow_unknown_properties
            },
            "issuers": {
                "test_issuer": self.issuers.test_issuer,
                "gs1_official_issuer": self.issuers.gs1_official_issuer,
                "development_issuer": self.issuers.development_issuer
            }
        }

# Global configuration instance
gs1_config = GS1Config()

def get_gs1_config() -> GS1Config:
    """Get the global GS1 configuration instance."""
    return gs1_config
