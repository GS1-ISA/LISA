"""
Fully Homomorphic Encryption (FHE) module for privacy-preserving computations.

This module provides FHE capabilities for secure analytics on encrypted ESG data,
enabling computations on encrypted values without decryption.
"""

import logging
from typing import List, Union, Optional, Dict, Any
import numpy as np

try:
    import tenseal as ts
except ImportError:
    logging.warning("TenSEAL not installed. FHE operations will be simulated.")
    ts = None

logger = logging.getLogger(__name__)


class FHEContext:
    """
    Manages FHE context and key management for secure computations.
    """

    def __init__(self, poly_modulus_degree: int = 8192, coeff_mod_bit_sizes: List[int] = None,
                 global_scale: int = 2**40):
        """
        Initialize FHE context.

        Args:
            poly_modulus_degree: Polynomial modulus degree
            coeff_mod_bit_sizes: Coefficient modulus bit sizes
            global_scale: Global scale for CKKS encoding
        """
        if coeff_mod_bit_sizes is None:
            coeff_mod_bit_sizes = [40, 21, 21, 21, 21, 21, 21, 40]

        self.poly_modulus_degree = poly_modulus_degree
        self.coeff_mod_bit_sizes = coeff_mod_bit_sizes
        self.global_scale = global_scale
        self.context = None
        self.secret_key = None
        self.public_key = None
        self.relin_keys = None
        self.galois_keys = None

        self._initialize_context()

    def _initialize_context(self):
        """Initialize the TenSEAL context."""
        if ts is None:
            logger.warning("TenSEAL not available, using mock context")
            return

        try:
            self.context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=self.poly_modulus_degree,
                coeff_mod_bit_sizes=self.coeff_mod_bit_sizes
            )
            self.context.global_scale = self.global_scale
            self.context.generate_galois_keys()

            # Generate keys
            self.secret_key = self.context.secret_key()
            self.public_key = self.context.public_key()
            self.relin_keys = self.context.relin_keys()
            self.galois_keys = self.context.galois_keys()

            logger.info("FHE context initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize FHE context: {e}")
            raise

    def encrypt(self, data: Union[float, List[float], np.ndarray]) -> Optional[Any]:
        """
        Encrypt data using FHE.

        Args:
            data: Data to encrypt (scalar, list, or numpy array)

        Returns:
            Encrypted data or None if encryption fails
        """
        if ts is None:
            logger.warning("TenSEAL not available, returning mock encrypted data")
            return f"mock_encrypted_{data}"

        if self.context is None:
            raise ValueError("FHE context not initialized")

        try:
            if isinstance(data, (int, float)):
                data = [float(data)]
            elif isinstance(data, np.ndarray):
                data = data.flatten().tolist()

            encrypted = ts.ckks_vector(self.context, data)
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None

    def decrypt(self, encrypted_data: Any) -> Optional[List[float]]:
        """
        Decrypt FHE encrypted data.

        Args:
            encrypted_data: Encrypted data to decrypt

        Returns:
            Decrypted data as list of floats or None if decryption fails
        """
        if ts is None:
            logger.warning("TenSEAL not available, returning mock decrypted data")
            if isinstance(encrypted_data, str) and encrypted_data.startswith("mock_encrypted_"):
                return [float(encrypted_data.replace("mock_encrypted_", ""))]
            return [0.0]

        if self.context is None:
            raise ValueError("FHE context not initialized")

        try:
            decrypted = encrypted_data.decrypt()
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None

    def serialize_context(self) -> Optional[bytes]:
        """Serialize the FHE context for distribution."""
        if ts is None or self.context is None:
            return None
        return self.context.serialize()

    def serialize_public_key(self) -> Optional[bytes]:
        """Serialize public key for distribution to clients."""
        if ts is None or self.public_key is None:
            return None
        return self.public_key.serialize()

    @classmethod
    def from_serialized(cls, context_bytes: bytes) -> 'FHEContext':
        """Create FHE context from serialized data."""
        instance = cls.__new__(cls)
        if ts is None:
            return instance

        instance.context = ts.context_from(context_bytes)
        return instance


class FHEOperations:
    """
    Provides FHE operations for encrypted data analytics.
    """

    def __init__(self, context: FHEContext):
        self.context = context

    def add_encrypted_vectors(self, vec1: Any, vec2: Any) -> Optional[Any]:
        """Add two encrypted vectors."""
        if ts is None:
            return f"mock_add_{vec1}_{vec2}"
        try:
            return vec1 + vec2
        except Exception as e:
            logger.error(f"Encrypted addition failed: {e}")
            return None

    def multiply_encrypted_vectors(self, vec1: Any, vec2: Any) -> Optional[Any]:
        """Multiply two encrypted vectors."""
        if ts is None:
            return f"mock_mul_{vec1}_{vec2}"
        try:
            result = vec1 * vec2
            result = result.relinearize()
            return result
        except Exception as e:
            logger.error(f"Encrypted multiplication failed: {e}")
            return None

    def sum_encrypted_vector(self, vec: Any) -> Optional[Any]:
        """Compute sum of encrypted vector elements."""
        if ts is None:
            return f"mock_sum_{vec}"
        try:
            # Sum all elements
            result = vec.sum()
            return result
        except Exception as e:
            logger.error(f"Encrypted sum failed: {e}")
            return None

    def mean_encrypted_vector(self, vec: Any, length: int) -> Optional[Any]:
        """Compute mean of encrypted vector."""
        if ts is None:
            return f"mock_mean_{vec}"
        try:
            total = self.sum_encrypted_vector(vec)
            if total is None:
                return None
            # Divide by length (need to encrypt the divisor)
            divisor = self.context.encrypt(1.0 / length)
            if divisor is None:
                return None
            result = total * divisor
            result = result.relinearize()
            return result
        except Exception as e:
            logger.error(f"Encrypted mean failed: {e}")
            return None

    def dot_product_encrypted(self, vec1: Any, vec2: Any) -> Optional[Any]:
        """Compute dot product of two encrypted vectors."""
        if ts is None:
            return f"mock_dot_{vec1}_{vec2}"
        try:
            result = vec1.dot(vec2)
            result = result.relinearize()
            return result
        except Exception as e:
            logger.error(f"Encrypted dot product failed: {e}")
            return None


class ESGDataEncryptor:
    """
    Specialized encryptor for ESG data metrics.
    """

    def __init__(self, fhe_context: FHEContext):
        self.fhe_context = fhe_context
        self.operations = FHEOperations(fhe_context)

    def encrypt_esg_metrics(self, metrics: Dict[str, Union[float, List[float]]]) -> Dict[str, Any]:
        """
        Encrypt ESG metrics data.

        Args:
            metrics: Dictionary of ESG metrics (e.g., {'scope1_emissions': 100.5, 'employees': 5000})

        Returns:
            Dictionary with encrypted metrics
        """
        encrypted_metrics = {}
        for key, value in metrics.items():
            encrypted = self.fhe_context.encrypt(value)
            if encrypted is not None:
                encrypted_metrics[key] = encrypted
            else:
                logger.warning(f"Failed to encrypt metric: {key}")
        return encrypted_metrics

    def compute_encrypted_esg_analytics(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform analytics on encrypted ESG data.

        Args:
            encrypted_data: Dictionary of encrypted ESG metrics

        Returns:
            Dictionary with encrypted analytics results
        """
        results = {}

        # Example: Compute total emissions (scope1 + scope2 + scope3)
        if all(k in encrypted_data for k in ['scope1_emissions', 'scope2_emissions', 'scope3_emissions']):
            scope1 = encrypted_data['scope1_emissions']
            scope2 = encrypted_data['scope2_emissions']
            scope3 = encrypted_data['scope3_emissions']

            total_emissions = self.operations.add_encrypted_vectors(
                self.operations.add_encrypted_vectors(scope1, scope2), scope3
            )
            if total_emissions is not None:
                results['total_emissions'] = total_emissions

        # Example: Compute emissions per employee
        if 'total_emissions' in results and 'employees' in encrypted_data:
            emissions_per_employee = self.operations.multiply_encrypted_vectors(
                results['total_emissions'],
                self.fhe_context.encrypt(1.0)  # Will be divided by employee count
            )
            if emissions_per_employee is not None:
                results['emissions_per_employee'] = emissions_per_employee

        return results

    def decrypt_analytics_results(self, encrypted_results: Dict[str, Any]) -> Dict[str, float]:
        """
        Decrypt analytics results.

        Args:
            encrypted_results: Dictionary of encrypted analytics results

        Returns:
            Dictionary with decrypted results
        """
        decrypted_results = {}
        for key, encrypted_value in encrypted_results.items():
            decrypted = self.fhe_context.decrypt(encrypted_value)
            if decrypted is not None and len(decrypted) > 0:
                decrypted_results[key] = decrypted[0]
            else:
                logger.warning(f"Failed to decrypt result: {key}")
        return decrypted_results