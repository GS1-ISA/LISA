#!/usr/bin/env python3
"""
Workflow Configuration Validator

This script validates the unified CI/CD pipeline configuration files
to ensure they are properly structured and contain all required fields.
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class WorkflowConfigValidator:
    """Validates workflow configuration files"""
    
    def __init__(self, config_dir: Path = Path(".github/workflows/config")):
        self.config_dir = config_dir
        self.errors = []
        self.warnings = []
    
    def validate_all_configs(self) -> bool:
        """Validate all configuration files"""
        logger.info("Starting configuration validation...")
        
        # Define configuration files to validate
        config_files = {
            "security-config.yml": self.validate_security_config,
            "deployment-config.yml": self.validate_deployment_config,
            "oidc-config.yml": self.validate_oidc_config
        }
        
        all_valid = True
        
        for config_file, validator_func in config_files.items():
            config_path = self.config_dir / config_file
            if not config_path.exists():
                self.errors.append(f"Configuration file not found: {config_file}")
                all_valid = False
                continue
                
            try:
                logger.info(f"Validating {config_file}...")
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                is_valid = validator_func(config)
                if not is_valid:
                    all_valid = False
                    
            except yaml.YAMLError as e:
                self.errors.append(f"Invalid YAML in {config_file}: {e}")
                all_valid = False
            except Exception as e:
                self.errors.append(f"Error validating {config_file}: {e}")
                all_valid = False
        
        return all_valid
    
    def validate_security_config(self, config: Dict[str, Any]) -> bool:
        """Validate security configuration"""
        is_valid = True
        required_sections = [
            'vulnerability_scanning', 'sast', 'dependency_scanning',
            'container_security', 'secret_scanning', 'compliance'
        ]
        
        # Check required sections
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section in security-config.yml: {section}")
                is_valid = False
        
        # Validate vulnerability scanning
        if 'vulnerability_scanning' in config:
            vuln_config = config['vulnerability_scanning']
            required_vuln_fields = ['enabled', 'tools', 'severity_threshold']
            for field in required_vuln_fields:
                if field not in vuln_config:
                    self.errors.append(f"Missing required field in vulnerability_scanning: {field}")
                    is_valid = False
            
            # Validate tools
            if 'tools' in vuln_config:
                for tool_name, tool_config in vuln_config['tools'].items():
                    if 'enabled' not in tool_config:
                        self.warnings.append(f"Tool '{tool_name}' missing 'enabled' field")
        
        # Validate SAST configuration
        if 'sast' in config:
            sast_config = config['sast']
            if 'tools' not in sast_config:
                self.errors.append("Missing 'tools' section in sast configuration")
                is_valid = False
            else:
                for tool_name, tool_config in sast_config['tools'].items():
                    if 'enabled' not in tool_config:
                        self.warnings.append(f"SAST tool '{tool_name}' missing 'enabled' field")
        
        # Validate compliance
        if 'compliance' in config:
            compliance_config = config['compliance']
            if 'standards' not in compliance_config:
                self.warnings.append("No compliance standards specified")
        
        return is_valid
    
    def validate_deployment_config(self, config: Dict[str, Any]) -> bool:
        """Validate deployment configuration"""
        is_valid = True
        required_sections = [
            'environments', 'deployment_strategies', 'health_checks',
            'rollback_mechanisms', 'monitoring'
        ]
        
        # Check required sections
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section in deployment-config.yml: {section}")
                is_valid = False
        
        # Validate environments
        if 'environments' in config:
            environments = config['environments']
            required_envs = ['development', 'integration', 'staging', 'production']
            for env in required_envs:
                if env not in environments:
                    self.errors.append(f"Missing required environment: {env}")
                    is_valid = False
                else:
                    env_config = environments[env]
                    required_env_fields = ['enabled', 'approval_required', 'deployment_strategy']
                    for field in required_env_fields:
                        if field not in env_config:
                            self.errors.append(f"Missing required field in {env} environment: {field}")
                            is_valid = False
        
        # Validate deployment strategies
        if 'deployment_strategies' in config:
            strategies = config['deployment_strategies']
            valid_strategies = ['rolling', 'blue_green', 'canary', 'emergency']
            for strategy_name, strategy_config in strategies.items():
                if strategy_name not in valid_strategies:
                    self.warnings.append(f"Unknown deployment strategy: {strategy_name}")
                
                if strategy_name == 'canary' and 'stages' in strategy_config:
                    for stage in strategy_config['stages']:
                        required_stage_fields = ['weight', 'duration', 'success_threshold']
                        for field in required_stage_fields:
                            if field not in stage:
                                self.errors.append(f"Missing required field in canary stage: {field}")
                                is_valid = False
        
        # Validate health checks
        if 'health_checks' in config:
            health_config = config['health_checks']
            if 'endpoints' not in health_config:
                self.warnings.append("No health check endpoints specified")
        
        return is_valid
    
    def validate_oidc_config(self, config: Dict[str, Any]) -> bool:
        """Validate OIDC configuration"""
        is_valid = True
        required_sections = ['providers', 'compliance']
        
        # Check required sections
        for section in required_sections:
            if section not in config:
                self.errors.append(f"Missing required section in oidc-config.yml: {section}")
                is_valid = False
        
        # Validate providers
        if 'providers' in config:
            providers = config['providers']
            valid_providers = ['aws', 'azure', 'gcp']
            for provider_name, provider_config in providers.items():
                if provider_name not in valid_providers:
                    self.warnings.append(f"Unknown OIDC provider: {provider_name}")
                
                required_provider_fields = ['enabled', 'provider_url', 'audience']
                for field in required_provider_fields:
                    if field not in provider_config:
                        self.errors.append(f"Missing required field in {provider_name} provider: {field}")
                        is_valid = False
                
                # Validate trust conditions
                if 'trust_conditions' in provider_config:
                    for condition in provider_config['trust_conditions']:
                        if 'key' not in condition or 'values' not in condition:
                            self.errors.append("Invalid trust condition format")
                            is_valid = False
        
        # Validate compliance
        if 'compliance' in config:
            compliance_config = config['compliance']
            if 'audit_requirements' in compliance_config:
                valid_standards = ['SOX', 'PCI-DSS', 'HIPAA', 'SOC2']
                for standard in compliance_config['audit_requirements']:
                    if standard not in valid_standards:
                        self.warnings.append(f"Unknown compliance standard: {standard}")
        
        return is_valid
    
    def validate_workflow_syntax(self, workflow_path: Path) -> bool:
        """Validate GitHub Actions workflow syntax"""
        try:
            with open(workflow_path, 'r') as f:
                workflow_content = f.read()
            
            # Basic YAML syntax validation
            workflow_data = yaml.safe_load(workflow_content)
            
            # Check for required workflow elements
            if 'name' not in workflow_data:
                self.errors.append("Workflow missing 'name' field")
                return False
            
            if 'on' not in workflow_data:
                self.errors.append("Workflow missing 'on' field")
                return False
            
            if 'jobs' not in workflow_data:
                self.errors.append("Workflow missing 'jobs' field")
                return False
            
            # Validate job structure
            jobs = workflow_data['jobs']
            for job_name, job_config in jobs.items():
                if 'runs-on' not in job_config:
                    self.warnings.append(f"Job '{job_name}' missing 'runs-on' field")
                
                if 'steps' not in job_config:
                    self.warnings.append(f"Job '{job_name}' missing 'steps' field")
                
                # Check for potential security issues
                if 'env' in job_config:
                    for env_var, env_value in job_config['env'].items():
                        if isinstance(env_value, str) and len(env_value) > 100:
                            self.warnings.append(f"Job '{job_name}' has suspiciously long environment variable: {env_var}")
            
            return True
            
        except yaml.YAMLError as e:
            self.errors.append(f"Invalid YAML in workflow file: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error validating workflow syntax: {e}")
            return False
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*60)
        print("WORKFLOW CONFIGURATION VALIDATION REPORT")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All configurations are valid!")
        
        print("\n" + "="*60)
        print(f"Total Errors: {len(self.errors)}")
        print(f"Total Warnings: {len(self.warnings)}")
        print("="*60)
    
    def get_exit_code(self) -> int:
        """Get exit code based on validation results"""
        return 1 if self.errors else 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Validate workflow configuration files")
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=Path(".github/workflows/config"),
        help="Directory containing configuration files"
    )
    parser.add_argument(
        "--workflow-file",
        type=Path,
        help="Path to workflow file to validate"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = WorkflowConfigValidator(args.config_dir)
    
    # Validate configuration files
    config_valid = validator.validate_all_configs()
    
    # Validate workflow file if provided
    workflow_valid = True
    if args.workflow_file:
        workflow_valid = validator.validate_workflow_syntax(args.workflow_file)
    
    # Print report
    validator.print_report()
    
    # Exit with appropriate code
    sys.exit(validator.get_exit_code())

if __name__ == "__main__":
    main()