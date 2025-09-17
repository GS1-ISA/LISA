"""
Federated Learning Server for coordinating privacy-preserving model training.

This module implements a federated learning coordinator that manages encrypted
model updates from multiple clients without accessing their raw data.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

try:
    import aiohttp
    from aiohttp import web
except ImportError:
    logging.warning("aiohttp not installed. FL server will use mock implementation.")
    aiohttp = None
    web = None

from .fhe import FHEContext, FHEOperations

logger = logging.getLogger(__name__)


@dataclass
class ClientInfo:
    """Information about a connected FL client."""
    client_id: str
    last_seen: datetime
    status: str  # 'active', 'training', 'idle'
    model_version: int
    data_size: int


@dataclass
class TrainingRound:
    """Information about a training round."""
    round_id: int
    start_time: datetime
    end_time: datetime | None
    participating_clients: set[str]
    aggregated_updates: Any | None
    status: str  # 'active', 'completed', 'failed'


class FederatedLearningServer:
    """
    Server for coordinating federated learning with encrypted model updates.
    """

    def __init__(self, host: str = "localhost", port: int = 8080,
                 fhe_context: FHEContext | None = None):
        self.host = host
        self.port = port
        self.fhe_context = fhe_context or FHEContext()
        self.fhe_ops = FHEOperations(self.fhe_context)

        # Server state
        self.clients: dict[str, ClientInfo] = {}
        self.training_rounds: list[TrainingRound] = []
        self.current_round: TrainingRound | None = None
        self.global_model: Any | None = None
        self.min_clients_per_round = 3
        self.max_rounds = 100

        # HTTP server
        self.app = None
        self.runner = None
        self.site = None

        self._setup_routes()

    def _setup_routes(self):
        """Set up HTTP routes for the FL server."""
        if web is None:
            logger.warning("aiohttp not available, routes not set up")
            return

        self.app = web.Application()
        self.app.router.add_post("/register", self.register_client)
        self.app.router.add_post("/update", self.receive_model_update)
        self.app.router.add_get("/model", self.get_global_model)
        self.app.router.add_get("/status", self.get_server_status)
        self.app.router.add_post("/start_round", self.start_training_round)

    async def register_client(self, request: web.Request) -> web.Response:
        """
        Register a new client for federated learning.

        Expected JSON payload:
        {
            "client_id": "client_123",
            "data_size": 1000
        }
        """
        try:
            data = await request.json()
            client_id = data.get("client_id")
            data_size = data.get("data_size", 0)

            if not client_id:
                return web.json_response({"error": "client_id required"}, status=400)

            client_info = ClientInfo(
                client_id=client_id,
                last_seen=datetime.now(),
                status="idle",
                model_version=0,
                data_size=data_size
            )

            self.clients[client_id] = client_info
            logger.info(f"Client {client_id} registered with {data_size} data points")

            return web.json_response({
                "status": "registered",
                "client_id": client_id,
                "fhe_public_key": self.fhe_context.serialize_public_key().decode("latin-1") if self.fhe_context.serialize_public_key() else None
            })

        except Exception as e:
            logger.error(f"Client registration failed: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def receive_model_update(self, request: web.Request) -> web.Response:
        """
        Receive encrypted model update from a client.

        Expected JSON payload:
        {
            "client_id": "client_123",
            "round_id": 1,
            "encrypted_update": "...",
            "model_version": 1
        }
        """
        try:
            data = await request.json()
            client_id = data.get("client_id")
            round_id = data.get("round_id")
            encrypted_update = data.get("encrypted_update")
            model_version = data.get("model_version", 0)

            if not all([client_id, round_id is not None]):
                return web.json_response({"error": "client_id and round_id required"}, status=400)

            if client_id not in self.clients:
                return web.json_response({"error": "client not registered"}, status=404)

            # Update client status
            self.clients[client_id].last_seen = datetime.now()
            self.clients[client_id].status = "idle"
            self.clients[client_id].model_version = model_version

            # Add to current round if active
            if self.current_round and self.current_round.round_id == round_id:
                self.current_round.participating_clients.add(client_id)

                # Store encrypted update (in real implementation, would aggregate)
                if self.current_round.aggregated_updates is None:
                    self.current_round.aggregated_updates = encrypted_update
                else:
                    # Aggregate encrypted updates
                    self.current_round.aggregated_updates = self._aggregate_encrypted_updates(
                        self.current_round.aggregated_updates, encrypted_update
                    )

                # Check if round is complete
                if len(self.current_round.participating_clients) >= self.min_clients_per_round:
                    await self._complete_round()

            logger.info(f"Received model update from {client_id} for round {round_id}")

            return web.json_response({"status": "update_received"})

        except Exception as e:
            logger.error(f"Model update reception failed: {e}")
            return web.json_response({"error": str(e)}, status=500)

    def _aggregate_encrypted_updates(self, update1: Any, update2: Any) -> Any:
        """
        Aggregate two encrypted model updates.

        In a real implementation, this would perform federated averaging
        on encrypted model parameters.
        """
        # Mock aggregation - in practice, this would be complex FHE operations
        if isinstance(update1, str) and isinstance(update2, str):
            return f"aggregated_{update1}_{update2}"
        return update1  # Placeholder

    async def _complete_round(self):
        """Complete the current training round."""
        if not self.current_round:
            return

        self.current_round.end_time = datetime.now()
        self.current_round.status = "completed"

        # Update global model with aggregated updates
        self.global_model = self.current_round.aggregated_updates

        logger.info(f"Training round {self.current_round.round_id} completed with "
                   f"{len(self.current_round.participating_clients)} clients")

        # Start next round if under max_rounds
        if len(self.training_rounds) < self.max_rounds:
            await self._start_new_round()

    async def start_training_round(self, request: web.Request) -> web.Response:
        """Manually start a new training round."""
        try:
            await self._start_new_round()
            return web.json_response({"status": "round_started"})
        except Exception as e:
            logger.error(f"Failed to start round: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def _start_new_round(self):
        """Start a new training round."""
        round_id = len(self.training_rounds) + 1

        new_round = TrainingRound(
            round_id=round_id,
            start_time=datetime.now(),
            end_time=None,
            participating_clients=set(),
            aggregated_updates=None,
            status="active"
        )

        self.training_rounds.append(new_round)
        self.current_round = new_round

        # Notify clients to start training (in real implementation)
        logger.info(f"Started training round {round_id}")

    async def get_global_model(self, request: web.Request) -> web.Response:
        """Get the current global model."""
        return web.json_response({
            "model": self.global_model,
            "round_id": self.current_round.round_id if self.current_round else None
        })

    async def get_server_status(self, request: web.Request) -> web.Response:
        """Get server status information."""
        return web.json_response({
            "active_clients": len([c for c in self.clients.values() if c.status == "active"]),
            "total_clients": len(self.clients),
            "current_round": self.current_round.round_id if self.current_round else None,
            "round_status": self.current_round.status if self.current_round else None,
            "total_rounds": len(self.training_rounds)
        })

    async def start_server(self):
        """Start the FL server."""
        if self.app is None:
            logger.warning("HTTP server not available (aiohttp not installed)")
            return

        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()

        logger.info(f"Federated Learning Server started on {self.host}:{self.port}")

        # Start initial round
        await self._start_new_round()

    async def stop_server(self):
        """Stop the FL server."""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Federated Learning Server stopped")


class MockFederatedLearningServer:
    """
    Mock implementation for testing when aiohttp is not available.
    """

    def __init__(self, *args, **kwargs):
        self.clients = {}
        self.rounds = []
        logger.info("Using mock FL server")

    async def start_server(self):
        logger.info("Mock FL server started")

    async def stop_server(self):
        logger.info("Mock FL server stopped")


# Factory function to get appropriate server implementation
def create_fl_server(*args, **kwargs) -> FederatedLearningServer:
    """Create FL server instance."""
    if aiohttp is None:
        return MockFederatedLearningServer(*args, **kwargs)
    return FederatedLearningServer(*args, **kwargs)
