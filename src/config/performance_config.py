"""
Performance configuration settings for ISA_D MVP.
Optimized for target performance metrics.
"""

import os
from typing import Dict, Any

# Agent Performance Configuration
AGENT_CONFIG = {
    "max_concurrent_tasks": 3,
    "task_timeout": 300,  # 5 minutes
    "llm_timeout": 60,    # 1 minute per LLM call
    "cache_ttl": 1800,   # 30 minutes
    "max_retries": 3,
    "retry_delay": 1.0,
}

# Memory System Configuration
MEMORY_CONFIG = {
    "chromadb_settings": {
        "anonymized_telemetry": False,
        "allow_reset": True,
        "is_persistent": True,
    },
    "collection_config": {
        "chunk_size": 1000,
        "overlap": 200,
        "max_chunks": 10000,
        "cache_size": 1000,
        "cache_ttl": 300,  # 5 minutes
    },
    "batch_config": {
        "batch_size": 100,
        "max_workers": 4,
        "timeout": 30,
    },
}

# API Performance Configuration
API_CONFIG = {
    "rate_limits": {
        "requests_per_minute": 100,
        "burst_limit": 20,
    },
    "timeouts": {
        "request_timeout": 30,
        "long_operation_timeout": 300,
    },
    "caching": {
        "redis_ttl": 300,  # 5 minutes
        "memory_cache_size": 100,
        "memory_cache_ttl": 300,
    },
    "compression": {
        "minimum_size": 1000,
        "compression_level": 6,
    },
}

# LLM Client Configuration
LLM_CONFIG = {
    "openai": {
        "timeout": 30,
        "max_retries": 3,
        "backoff_factor": 0.3,
        "rate_limit_requests": 50,
        "rate_limit_window": 60,
    },
    "anthropic": {
        "timeout": 30,
        "max_retries": 3,
        "backoff_factor": 0.3,
        "rate_limit_requests": 50,
        "rate_limit_window": 60,
    },
    "connection_pool": {
        "max_connections": 20,
        "max_keepalive": 10,
        "timeout": 30,
    },
    "thread_pool": {
        "max_workers": 8,
        "thread_timeout": 30,
    },
}

# Monitoring Configuration
MONITORING_CONFIG = {
    "metrics": {
        "histogram_buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
        "counter_labels": ["method", "endpoint", "status"],
    },
    "logging": {
        "performance_log_level": "INFO",
        "metrics_interval": 60,  # seconds
    },
}

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section."""
    configs = {
        "agent": AGENT_CONFIG,
        "memory": MEMORY_CONFIG,
        "api": API_CONFIG,
        "llm": LLM_CONFIG,
        "monitoring": MONITORING_CONFIG,
    }
    return configs.get(section, {})

def get_env_override(section: str, key: str, default_value: Any) -> Any:
    """Get environment variable override for config value."""
    env_key = f"ISA_{section.upper()}_{key.upper()}"
    env_value = os.getenv(env_key)
    if env_value is not None:
        # Try to convert to appropriate type
        if isinstance(default_value, bool):
            return env_value.lower() in ('true', '1', 'yes')
        elif isinstance(default_value, int):
            return int(env_value)
        elif isinstance(default_value, float):
            return float(env_value)
        else:
            return env_value
    return default_value

def get_request_timeout() -> int:
    """Get request timeout from configuration."""
    return API_CONFIG["timeouts"]["request_timeout"]

# Performance targets (for monitoring)
PERFORMANCE_TARGETS = {
    "agent_response_time": 30,  # seconds
    "memory_retrieval_time": 2,  # seconds
    "api_response_time": 5,     # seconds
    "cache_hit_rate": 0.7,      # 70%
}