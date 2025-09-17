"""
Federated Learning Client for encrypted model training on ESG data.

This module implements a client that performs local model training on encrypted
ESG data and sends encrypted updates to the federated learning server.
"""

import asyncio
import json
import logging
from typing import Any

try:
    import aiohttp
except ImportError:
    logging.warning("aiohttp not installed. FL client will use mock implementation.")
    aiohttp = None

from .fhe import ESGDataEncryptor, FHEContext

logger = logging.getLogger(__name__)


class FederatedLearningClient:
    """
    Client for federated learning that trains models on encrypted local ESG data.
    """

    def __init__(self, client_id: str, server_url: str = "http://localhost:8080",
                 fhe_context: FHEContext | None = None):
        self.client_id = client_id
        self.server_url = server_url.rstrip("/")
        self.fhe_context = fhe_context or FHEContext()
        self.esg_encryptor = ESGDataEncryptor(self.fhe_context)

        # Local data and model state
        self.local_esg_data: list[dict[str, float | int]] = []
        self.local_model: dict[str, Any] | None = None
        self.model_version = 0
        self.current_round = 0

        # Training parameters
        self.learning_rate = 0.01
        self.epochs = 5
        self.batch_size = 32

        # HTTP client session
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        if aiohttp:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def register_with_server(self, data_size: int = 0) -> bool:
        """
        Register this client with the FL server.

        Args:
            data_size: Number of data points this client has

        Returns:
            True if registration successful
        """
        if not self.session:
            logger.warning("HTTP session not available")
            return False

        try:
            payload = {
                "client_id": self.client_id,
                "data_size": data_size
            }

            async with self.session.post(f"{self.server_url}/register",
                                       json=payload) as response:
                if response.status == 200:
                    await response.json()
                    logger.info(f"Client {self.client_id} registered successfully")
                    return True
                else:
                    logger.error(f"Registration failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False

    def load_local_esg_data(self, esg_data: list[dict[str, float | int]]):
        """
        Load local ESG data for training.

        Args:
            esg_data: List of ESG data records
        """
        self.local_esg_data = esg_data
        logger.info(f"Loaded {len(esg_data)} ESG data records for client {self.client_id}")

    async def download_global_model(self) -> dict[str, Any] | None:
        """
        Download the current global model from the server.

        Returns:
            Global model parameters or None if download fails
        """
        if not self.session:
            logger.warning("HTTP session not available")
            return None

        try:
            async with self.session.get(f"{self.server_url}/model") as response:
                if response.status == 200:
                    data = await response.json()
                    self.local_model = data.get("model")
                    self.current_round = data.get("round_id", 0)
                    logger.info(f"Downloaded global model for round {self.current_round}")
                    return self.local_model
                else:
                    logger.error(f"Model download failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Model download error: {e}")
            return None

    def train_local_model(self) -> dict[str, Any] | None:
        """
        Train local model on encrypted ESG data.

        Returns:
            Encrypted model update or None if training fails
        """
        if not self.local_esg_data:
            logger.warning("No local ESG data available for training")
            return None

        if not self.local_model:
            # Initialize local model if none exists
            self.local_model = self._initialize_model()

        try:
            # Encrypt local ESG data
            encrypted_data = []
            for record in self.local_esg_data:
                encrypted_record = self.esg_encryptor.encrypt_esg_metrics(record)
                encrypted_data.append(encrypted_record)

            # Perform encrypted training (simplified for demonstration)
            model_update = self._perform_encrypted_training(encrypted_data)

            self.model_version += 1
            logger.info(f"Local training completed for client {self.client_id}")

            return model_update

        except Exception as e:
            logger.error(f"Local training failed: {e}")
            return None

    def _initialize_model(self) -> dict[str, Any]:
        """
        Initialize a simple linear model for ESG analytics.

        Returns:
            Initial model parameters
        """
        # Simple model: predict total emissions from company size and sector
        return {
            "weights": {
                "employees": 0.1,
                "sector_coefficient": 0.05,
                "bias": 10.0
            },
            "version": 0
        }

    def _perform_encrypted_training(self, encrypted_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Perform training on encrypted data.

        In a real implementation, this would use FHE-compatible training algorithms.
        For demonstration, we simulate encrypted gradient computation.

        Args:
            encrypted_data: List of encrypted ESG data records

        Returns:
            Encrypted model update
        """
        # Mock encrypted training - in practice, this would be complex FHE operations
        # Compute gradients on encrypted data without decryption

        total_samples = len(encrypted_data)
        learning_rate = self.learning_rate

        # Simulate gradient computation (would be encrypted in real implementation)
        gradient_updates = {
            "employees": f"encrypted_grad_employees_{total_samples}",
            "sector_coefficient": f"encrypted_grad_sector_{total_samples}",
            "bias": f"encrypted_grad_bias_{total_samples}"
        }

        # Apply learning rate (encrypted multiplication)
        for param in gradient_updates:
            gradient_updates[param] = f"scaled_{gradient_updates[param]}_{learning_rate}"

        model_update = {
            "client_id": self.client_id,
            "round_id": self.current_round,
            "model_version": self.model_version,
            "encrypted_gradients": gradient_updates,
            "num_samples": total_samples
        }

        return model_update

    async def send_model_update(self, model_update: dict[str, Any]) -> bool:
        """
        Send encrypted model update to the FL server.

        Args:
            model_update: Encrypted model update to send

        Returns:
            True if update sent successfully
        """
        if not self.session:
            logger.warning("HTTP session not available")
            return False

        try:
            payload = {
                "client_id": self.client_id,
                "round_id": self.current_round,
                "encrypted_update": json.dumps(model_update),
                "model_version": self.model_version
            }

            async with self.session.post(f"{self.server_url}/update",
                                       json=payload) as response:
                if response.status == 200:
                    logger.info(f"Model update sent successfully for round {self.current_round}")
                    return True
                else:
                    logger.error(f"Update send failed: {response.status}")
                    return False

        except Exception as e:
            logger.error(f"Update send error: {e}")
            return False

    async def participate_in_round(self) -> bool:
        """
        Complete participation in one FL round.

        Returns:
            True if round participation successful
        """
        try:
            # Download global model
            global_model = await self.download_global_model()
            if global_model is None:
                return False

            # Train local model
            model_update = self.train_local_model()
            if model_update is None:
                return False

            # Send update to server
            success = await self.send_model_update(model_update)
            return success

        except Exception as e:
            logger.error(f"Round participation failed: {e}")
            return False

    async def run_training_loop(self, max_rounds: int = 10):
        """
        Run continuous training loop participating in multiple rounds.

        Args:
            max_rounds: Maximum number of rounds to participate in
        """
        logger.info(f"Starting training loop for client {self.client_id}")

        for round_num in range(max_rounds):
            logger.info(f"Participating in round {round_num + 1}")

            success = await self.participate_in_round()
            if not success:
                logger.warning(f"Failed to participate in round {round_num + 1}")
                continue

            # Wait before next round
            await asyncio.sleep(5)

        logger.info(f"Training loop completed for client {self.client_id}")


class MockFederatedLearningClient:
    """
    Mock implementation for testing when aiohttp is not available.
    """

    def __init__(self, client_id: str, *args, **kwargs):
        self.client_id = client_id
        logger.info(f"Using mock FL client {client_id}")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def register_with_server(self, data_size: int = 0) -> bool:
        logger.info(f"Mock registration for {self.client_id}")
        return True

    def load_local_esg_data(self, esg_data):
        logger.info(f"Mock loaded {len(esg_data)} records for {self.client_id}")

    async def participate_in_round(self) -> bool:
        logger.info(f"Mock participating in round for {self.client_id}")
        return True

    async def run_training_loop(self, max_rounds: int = 10):
        logger.info(f"Mock training loop for {self.client_id}")


# Factory function to get appropriate client implementation
def create_fl_client(client_id: str, *args, **kwargs) -> FederatedLearningClient:
    """Create FL client instance."""
    if aiohttp is None:
        return MockFederatedLearningClient(client_id, *args, **kwargs)
    return FederatedLearningClient(client_id, *args, **kwargs)
