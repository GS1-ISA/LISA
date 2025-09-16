"""
Federated Analytics Coordinator for Privacy-Preserving ESG Analysis.

This module coordinates federated analytics across multiple parties,
enabling secure computation of ESG metrics and insights without
sharing sensitive raw data.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json

from .fhe import FHEContext, ESGDataEncryptor
from .fl_server import create_fl_server, FederatedLearningServer
from .fl_client import create_fl_client, FederatedLearningClient
from .training_pipeline import EncryptedTrainingPipeline, TrainingConfig, ESGModel

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsQuery:
    """Represents an analytics query for federated computation."""
    query_id: str
    query_type: str  # 'aggregation', 'prediction', 'correlation'
    parameters: Dict[str, Any]
    created_at: datetime
    status: str  # 'pending', 'processing', 'completed', 'failed'


@dataclass
class AnalyticsResult:
    """Result of a federated analytics computation."""
    query_id: str
    result_type: str
    encrypted_result: Any
    decrypted_result: Optional[Dict[str, float]]
    participating_clients: int
    computation_time: float
    completed_at: datetime


class FederatedAnalyticsCoordinator:
    """
    Coordinator for federated analytics on encrypted ESG data.
    """

    def __init__(self, server_url: str = 'http://localhost:8080',
                 fhe_context: Optional[FHEContext] = None):
        self.server_url = server_url
        self.fhe_context = fhe_context or FHEContext()
        self.esg_encryptor = ESGDataEncryptor(self.fhe_context)

        # Analytics state
        self.pending_queries: Dict[str, AnalyticsQuery] = {}
        self.completed_results: Dict[str, AnalyticsResult] = {}
        self.active_clients: Dict[str, FederatedLearningClient] = {}

        # Training pipeline
        self.training_config = TrainingConfig()
        self.training_pipeline = EncryptedTrainingPipeline(
            self.training_config, self.fhe_context
        )

        logger.info("Federated Analytics Coordinator initialized")

    async def register_client(self, client_id: str, local_data: List[Dict[str, Any]]) -> bool:
        """
        Register a new client for federated analytics.

        Args:
            client_id: Unique client identifier
            local_data: Client's local ESG data

        Returns:
            True if registration successful
        """
        try:
            client = create_fl_client(client_id, self.server_url, self.fhe_context)
            self.active_clients[client_id] = client

            async with client:
                success = await client.register_with_server(len(local_data))
                if success:
                    client.load_local_esg_data(local_data)
                    logger.info(f"Client {client_id} registered with {len(local_data)} data points")
                    return True
                else:
                    logger.error(f"Failed to register client {client_id}")
                    return False

        except Exception as e:
            logger.error(f"Client registration error: {e}")
            return False

    async def submit_analytics_query(self, query_type: str,
                                   parameters: Dict[str, Any]) -> str:
        """
        Submit a new analytics query for federated computation.

        Args:
            query_type: Type of analytics query
            parameters: Query parameters

        Returns:
            Query ID for tracking
        """
        query_id = f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(parameters))}"

        query = AnalyticsQuery(
            query_id=query_id,
            query_type=query_type,
            parameters=parameters,
            created_at=datetime.now(),
            status='pending'
        )

        self.pending_queries[query_id] = query
        logger.info(f"Submitted analytics query {query_id} of type {query_type}")

        # Start processing the query
        asyncio.create_task(self._process_query(query))

        return query_id

    async def _process_query(self, query: AnalyticsQuery):
        """Process an analytics query."""
        try:
            query.status = 'processing'
            start_time = datetime.now()

            if query.query_type == 'train_esg_model':
                result = await self._train_federated_esg_model(query.parameters)
            elif query.query_type == 'compute_emissions_aggregate':
                result = await self._compute_encrypted_emissions_aggregate(query.parameters)
            elif query.query_type == 'predict_company_emissions':
                result = await self._predict_company_emissions(query.parameters)
            else:
                raise ValueError(f"Unknown query type: {query.query_type}")

            computation_time = (datetime.now() - start_time).total_seconds()

            analytics_result = AnalyticsResult(
                query_id=query.query_id,
                result_type=query.query_type,
                encrypted_result=result.get('encrypted'),
                decrypted_result=result.get('decrypted'),
                participating_clients=len(self.active_clients),
                computation_time=computation_time,
                completed_at=datetime.now()
            )

            self.completed_results[query.query_id] = analytics_result
            query.status = 'completed'

            logger.info(f"Query {query.query_id} completed in {computation_time:.2f}s")

        except Exception as e:
            logger.error(f"Query {query.query_id} failed: {e}")
            query.status = 'failed'

    async def _train_federated_esg_model(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Train ESG model using federated learning."""
        num_rounds = parameters.get('num_rounds', 5)

        # Collect client datasets
        client_datasets = []
        for client in self.active_clients.values():
            # In practice, clients would provide their data through secure channels
            # For simulation, use mock data
            mock_data = self._generate_mock_esg_data()
            client_datasets.append(mock_data)

        # Train federated model
        trained_model = self.training_pipeline.train_federated_model(client_datasets)

        return {
            'encrypted': trained_model,  # Model is not encrypted, but updates were
            'decrypted': {
                'model_version': trained_model.version,
                'training_rounds': trained_model.training_round,
                'weights': trained_model.weights,
                'bias': trained_model.bias
            }
        }

    async def _compute_encrypted_emissions_aggregate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Compute aggregated emissions statistics across clients."""
        scope = parameters.get('scope', 'total')  # 'scope1', 'scope2', 'scope3', 'total'

        # Collect encrypted emissions data from all clients
        encrypted_emissions = []

        for client_id, client in self.active_clients.items():
            # In practice, clients would encrypt and send their data
            # For simulation, generate mock encrypted data
            mock_emissions = self._generate_mock_encrypted_emissions(scope)
            encrypted_emissions.append(mock_emissions)

        # Compute encrypted aggregate
        total_encrypted = encrypted_emissions[0]
        for encrypted_em in encrypted_emissions[1:]:
            total_encrypted = self.esg_encryptor.fhe_ops.add_encrypted_vectors(
                total_encrypted, encrypted_em
            )

        # Compute mean
        num_clients = len(encrypted_emissions)
        mean_encrypted = self.esg_encryptor.fhe_ops.multiply_encrypted_vectors(
            total_encrypted, self.fhe_context.encrypt(1.0 / num_clients)
        )

        # Decrypt results
        total_decrypted = self.fhe_context.decrypt(total_encrypted)
        mean_decrypted = self.fhe_context.decrypt(mean_encrypted)

        return {
            'encrypted': {
                'total_emissions': total_encrypted,
                'mean_emissions': mean_encrypted
            },
            'decrypted': {
                'total_emissions': total_decrypted[0] if total_decrypted else 0,
                'mean_emissions': mean_decrypted[0] if mean_decrypted else 0,
                'num_companies': num_clients
            }
        }

    async def _predict_company_emissions(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Predict emissions for a company using federated model."""
        company_features = parameters.get('features', {})

        if not self.training_pipeline.global_model:
            raise ValueError("No trained model available for prediction")

        # Encrypt company features
        encrypted_features = self.esg_encryptor.encrypt_esg_metrics(company_features)

        # Make encrypted prediction
        encrypted_prediction = self.training_pipeline.predict_encrypted(encrypted_features)

        # Decrypt prediction
        decrypted_prediction = self.fhe_context.decrypt(encrypted_prediction)

        return {
            'encrypted': encrypted_prediction,
            'decrypted': {
                'predicted_emissions': decrypted_prediction[0] if decrypted_prediction else 0,
                'model_version': self.training_pipeline.global_model.version
            }
        }

    def _generate_mock_esg_data(self) -> List[Dict[str, Any]]:
        """Generate mock ESG data for testing."""
        import random
        data = []
        for _ in range(10):
            record = {
                'lei': f'LEI{random.randint(100000, 999999)}',
                'social_totalEmployees': random.randint(100, 10000),
                'financial_revenue': random.randint(1000000, 100000000),
                'sector_energy_intensity': random.uniform(0.5, 2.0),
                'environmental_scope1Emissions': random.uniform(100, 10000),
                'environmental_scope2Emissions': random.uniform(50, 5000),
                'environmental_scope3Emissions': random.uniform(200, 20000),
                'timestamp': datetime.now().isoformat()
            }
            data.append(record)
        return data

    def _generate_mock_encrypted_emissions(self, scope: str) -> Any:
        """Generate mock encrypted emissions data."""
        if scope == 'total':
            emissions = sum([
                self._generate_mock_encrypted_emissions('scope1'),
                self._generate_mock_encrypted_emissions('scope2'),
                self._generate_mock_encrypted_emissions('scope3')
            ])
        else:
            base_value = {'scope1': 1000, 'scope2': 500, 'scope3': 2000}[scope]
            import random
            value = base_value * random.uniform(0.5, 1.5)
            emissions = self.fhe_context.encrypt(value)

        return emissions

    def get_query_status(self, query_id: str) -> Optional[str]:
        """Get the status of an analytics query."""
        if query_id in self.pending_queries:
            return self.pending_queries[query_id].status
        elif query_id in self.completed_results:
            return 'completed'
        return None

    def get_query_result(self, query_id: str) -> Optional[AnalyticsResult]:
        """Get the result of a completed analytics query."""
        return self.completed_results.get(query_id)

    async def run_federated_learning_round(self) -> bool:
        """
        Run a single round of federated learning with all active clients.

        Returns:
            True if round completed successfully
        """
        if not self.active_clients:
            logger.warning("No active clients for federated learning")
            return False

        try:
            # Have each client participate in the round
            tasks = []
            for client in self.active_clients.values():
                async with client:
                    task = asyncio.create_task(client.participate_in_round())
                    tasks.append(task)

            # Wait for all clients to complete
            results = await asyncio.gather(*tasks)

            success_count = sum(1 for r in results if r)
            logger.info(f"Federated learning round completed: {success_count}/{len(results)} clients successful")

            return success_count > 0

        except Exception as e:
            logger.error(f"Federated learning round failed: {e}")
            return False

    async def start_server_and_clients(self):
        """Start the FL server and initialize clients."""
        # Start FL server
        server = create_fl_server(host='localhost', port=8080, fhe_context=self.fhe_context)
        server_task = asyncio.create_task(server.start_server())

        # Wait a moment for server to start
        await asyncio.sleep(1)

        # Register some mock clients
        mock_clients_data = [
            self._generate_mock_esg_data() for _ in range(3)
        ]

        for i, client_data in enumerate(mock_clients_data):
            client_id = f'client_{i+1}'
            await self.register_client(client_id, client_data)

        logger.info("Federated analytics system started with server and clients")

        return server_task

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            'active_clients': len(self.active_clients),
            'pending_queries': len(self.pending_queries),
            'completed_queries': len(self.completed_results),
            'trained_model_available': self.training_pipeline.global_model is not None,
            'model_version': self.training_pipeline.global_model.version if self.training_pipeline.global_model else 0
        }