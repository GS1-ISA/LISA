"""
Comprehensive Benchmarking Suite for ISA_D
Advanced benchmarking framework with automated performance testing and optimization validation.
"""

import json
import logging
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .docs_provider.optimized_processor import get_optimized_document_processor
from .optimized_agent_workflow import get_optimized_agent_workflow
from .optimized_graph_analytics import get_optimized_graph_analytics
from .optimized_pipeline import get_optimized_regulatory_pipeline
from .performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Result of a benchmark test."""
    test_name: str
    component: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    metadata: dict[str, Any]


@dataclass
class BenchmarkSuite:
    """Configuration for a benchmark suite."""
    name: str
    description: str
    tests: list[dict[str, Any]]
    warm_up_iterations: int = 5
    measurement_iterations: int = 20
    cooldown_seconds: int = 10


class ISABenchmarkSuite:
    """
    Comprehensive benchmarking suite for ISA_D with:

    - Automated performance regression testing
    - Comparative analysis across components
    - Statistical analysis of results
    - Performance trend tracking
    - Optimization validation
    - Automated report generation
    """

    def __init__(self, results_dir: str = "benchmark_results"):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)

        # Component references
        self.doc_processor = get_optimized_document_processor()
        self.pipeline = get_optimized_regulatory_pipeline()
        self.analytics = get_optimized_graph_analytics()
        self.workflow = get_optimized_agent_workflow()
        self.monitor = get_performance_monitor()

        # Benchmark results storage
        self.results: list[BenchmarkResult] = []
        self.baselines: dict[str, float] = {}

        # Test data
        self.test_documents = self._generate_test_documents()
        self.test_organizations = [
            "TestCorp_Global", "SupplyChain_Inc", "Manufacturing_Ltd",
            "Retail_Group", "Logistics_Pro", "Compliance_Solutions"
        ]

        logger.info("Initialized ISA Benchmark Suite")

    def _generate_test_documents(self) -> list[str]:
        """Generate test documents of various sizes."""
        documents = []

        # Small document
        small_doc = "CSRD compliance requirements for small enterprises. " * 50
        documents.append(("small", small_doc))

        # Medium document
        medium_doc = """
        Comprehensive ESG reporting framework under CSRD Article 8.
        This document outlines the requirements for environmental, social,
        and governance disclosures including climate risk assessment,
        biodiversity impact analysis, and supply chain due diligence.
        """ * 100
        documents.append(("medium", medium_doc))

        # Large document
        large_doc = """
        Detailed regulatory compliance analysis for multinational corporations.
        This comprehensive guide covers all aspects of sustainability reporting
        including greenhouse gas emissions, energy consumption metrics,
        waste management strategies, and stakeholder engagement processes.
        The document includes detailed methodologies for data collection,
        validation procedures, assurance requirements, and reporting frameworks.
        """ * 500
        documents.append(("large", large_doc))

        return documents

    async def run_full_benchmark_suite(self) -> dict[str, Any]:
        """Run the complete benchmark suite."""
        logger.info("Starting full ISA benchmark suite")

        start_time = time.time()
        suite_results = {}

        # Document Processing Benchmarks
        suite_results["document_processing"] = await self._run_document_processing_benchmarks()

        # Pipeline Benchmarks
        suite_results["pipeline"] = await self._run_pipeline_benchmarks()

        # Graph Analytics Benchmarks
        suite_results["graph_analytics"] = await self._run_graph_analytics_benchmarks()

        # Agent Workflow Benchmarks
        suite_results["agent_workflow"] = await self._run_agent_workflow_benchmarks()

        # Cross-Component Benchmarks
        suite_results["integration"] = await self._run_integration_benchmarks()

        total_time = time.time() - start_time

        # Generate comprehensive report
        report = self._generate_benchmark_report(suite_results, total_time)

        # Save results
        self._save_benchmark_results(suite_results, report)

        logger.info(f"Benchmark suite completed in {total_time:.2f} seconds")
        return report

    async def _run_document_processing_benchmarks(self) -> dict[str, Any]:
        """Run document processing performance benchmarks."""
        logger.info("Running document processing benchmarks")

        results = {}

        for doc_name, document in self.test_documents:
            # Benchmark processing time
            times = []
            for _ in range(10):
                start_time = time.time()

                # Create temporary file for testing
                import tempfile
                with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False) as f:
                    # Simulate PDF content (in real scenario, would be actual PDF)
                    f.write(document)
                    temp_path = f.name

                try:
                    result, metrics = await self.doc_processor.process_document_async(temp_path)
                    processing_time = time.time() - start_time
                    times.append(processing_time)
                finally:
                    Path(temp_path).unlink()

            # Calculate statistics
            avg_time = statistics.mean(times)
            p95_time = statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times)

            results[f"{doc_name}_document"] = {
                "avg_processing_time": round(avg_time, 4),
                "p95_processing_time": round(p95_time, 4),
                "throughput": round(len(document) / avg_time, 2),  # chars/second
                "cache_hit_rate": self.doc_processor.get_performance_stats().get("cache_hit_rate", 0)
            }

        return results

    async def _run_pipeline_benchmarks(self) -> dict[str, Any]:
        """Run regulatory pipeline performance benchmarks."""
        logger.info("Running pipeline benchmarks")

        # Create test document paths
        test_paths = []
        import tempfile

        for _i, (_doc_name, document) in enumerate(self.test_documents):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False) as f:
                f.write(document)
                test_paths.append(f.name)

        try:
            # Benchmark batch processing
            start_time = time.time()
            results = await self.pipeline.process_regulatory_documents(test_paths)
            total_time = time.time() - start_time

            pipeline_stats = self.pipeline.get_pipeline_stats()

            benchmark_results = {
                "total_processing_time": round(total_time, 2),
                "documents_processed": results.get("processed_documents", 0),
                "throughput": round(results.get("processed_documents", 0) / total_time, 2),
                "cache_hit_rate": results.get("cache_hit_rate", 0),
                "avg_batch_throughput": pipeline_stats.get("avg_throughput", 0),
                "circuit_breaker_status": pipeline_stats.get("circuit_breaker_status", "unknown")
            }

        finally:
            # Cleanup temp files
            for path in test_paths:
                Path(path).unlink()

        return benchmark_results

    async def _run_graph_analytics_benchmarks(self) -> dict[str, Any]:
        """Run graph analytics performance benchmarks."""
        logger.info("Running graph analytics benchmarks")

        results = {}

        # Benchmark organization risk analysis
        for org in self.test_organizations[:3]:  # Test first 3 organizations
            times = []

            for _ in range(5):
                start_time = time.time()
                risk_metrics, query_metrics = await self.analytics.analyze_organization_risks_async(org)
                processing_time = time.time() - start_time
                times.append(processing_time)

            avg_time = statistics.mean(times)
            results[f"{org}_risk_analysis"] = {
                "avg_query_time": round(avg_time, 4),
                "cache_hit_rate": self.analytics.get_performance_stats().get("cache_hit_rate", 0),
                "risk_score": risk_metrics.overall_risk_score if hasattr(risk_metrics, "overall_risk_score") else 0.5
            }

        # Benchmark batch analysis
        start_time = time.time()
        batch_results = await self.analytics.batch_analyze_organizations(self.test_organizations[:3])
        batch_time = time.time() - start_time

        results["batch_analysis"] = {
            "total_time": round(batch_time, 2),
            "organizations_processed": len(batch_results),
            "avg_time_per_org": round(batch_time / len(batch_results), 4),
            "throughput": round(len(batch_results) / batch_time, 2)
        }

        return results

    async def _run_agent_workflow_benchmarks(self) -> dict[str, Any]:
        """Run agent workflow performance benchmarks."""
        logger.info("Running agent workflow benchmarks")

        from .optimized_agent_workflow import AgentRole, AgentTask

        # Create test tasks
        test_tasks = [
            AgentTask(
                task_id=f"task_{i}",
                role=AgentRole(list(AgentRole)[i % len(AgentRole)]),
                content=f"Analyze regulatory compliance requirement {i} for ESG reporting standards.",
                priority=1
            )
            for i in range(10)
        ]

        # Benchmark workflow execution
        start_time = time.time()
        workflow_results = await self.workflow.execute_workflow(test_tasks)
        total_time = time.time() - start_time

        workflow_stats = self.workflow.get_workflow_stats()

        results = {
            "total_execution_time": round(total_time, 2),
            "tasks_completed": workflow_results.get("completed_tasks", 0),
            "tasks_failed": workflow_results.get("failed_tasks", 0),
            "throughput": workflow_results.get("throughput", 0),
            "cache_hit_rate": workflow_results.get("cache_hit_rate", 0),
            "avg_agent_throughput": workflow_stats.get("avg_throughput", 0),
            "agent_utilization": workflow_results.get("agent_utilization", {})
        }

        return results

    async def _run_integration_benchmarks(self) -> dict[str, Any]:
        """Run cross-component integration benchmarks."""
        logger.info("Running integration benchmarks")

        # End-to-end benchmark: Document -> Pipeline -> Analytics -> Workflow
        start_time = time.time()

        # Phase 1: Process documents
        doc_results = []
        for _doc_name, document in self.test_documents[:2]:  # Use smaller set
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".pdf", delete=False) as f:
                f.write(document)
                temp_path = f.name

            try:
                result, metrics = await self.doc_processor.process_document_async(temp_path)
                doc_results.append((temp_path, result))
            finally:
                Path(temp_path).unlink()

        # Phase 2: Pipeline processing
        doc_paths = [path for path, _ in doc_results]
        pipeline_results = await self.pipeline.process_regulatory_documents(doc_paths)

        # Phase 3: Analytics
        analytics_results = await self.analytics.batch_analyze_organizations(self.test_organizations[:2])

        # Phase 4: Workflow
        from .optimized_agent_workflow import AgentRole, AgentTask
        workflow_tasks = [
            AgentTask(
                task_id="integration_task_1",
                role=AgentRole.SYNTHESIZER,
                content="Synthesize findings from document processing and risk analysis.",
                priority=2
            )
        ]
        workflow_results = await self.workflow.execute_workflow(workflow_tasks)

        total_integration_time = time.time() - start_time

        results = {
            "total_integration_time": round(total_integration_time, 2),
            "documents_processed": len(doc_results),
            "pipeline_success": pipeline_results.get("success", False),
            "analytics_completed": len(analytics_results),
            "workflow_completed": workflow_results.get("completed_tasks", 0),
            "end_to_end_throughput": round(
                (len(doc_results) + len(analytics_results) + workflow_results.get("completed_tasks", 0))
                / total_integration_time, 2
            )
        }

        return results

    def _generate_benchmark_report(self, suite_results: dict[str, Any], total_time: float) -> dict[str, Any]:
        """Generate comprehensive benchmark report."""
        report = {
            "suite_name": "ISA_D Performance Benchmark Suite",
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": round(total_time, 2),
            "results": suite_results,
            "performance_summary": self._calculate_performance_summary(suite_results),
            "recommendations": self._generate_optimization_recommendations(suite_results),
            "regression_analysis": self._analyze_performance_regression(suite_results)
        }

        return report

    def _calculate_performance_summary(self, suite_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall performance summary."""
        summary = {
            "overall_health_score": 0.0,
            "bottlenecks": [],
            "strengths": [],
            "avg_cache_hit_rate": 0.0,
            "avg_throughput": 0.0,
            "total_tests_run": 0
        }

        cache_rates = []
        throughputs = []
        test_count = 0

        # Analyze each component
        for component, results in suite_results.items():
            if component == "integration":
                continue

            for test_name, metrics in results.items():
                test_count += 1

                # Collect cache hit rates
                if "cache_hit_rate" in metrics:
                    cache_rates.append(metrics["cache_hit_rate"])

                # Collect throughputs
                if "throughput" in metrics:
                    throughputs.append(metrics["throughput"])

                # Identify bottlenecks (slow performance)
                if "avg_processing_time" in metrics and metrics["avg_processing_time"] > 1.0:
                    summary["bottlenecks"].append(f"{component}.{test_name}: slow processing")
                elif "avg_query_time" in metrics and metrics["avg_query_time"] > 0.5:
                    summary["bottlenecks"].append(f"{component}.{test_name}: slow queries")

        # Calculate averages
        if cache_rates:
            summary["avg_cache_hit_rate"] = round(statistics.mean(cache_rates), 2)
        if throughputs:
            summary["avg_throughput"] = round(statistics.mean(throughputs), 2)

        summary["total_tests_run"] = test_count

        # Calculate health score
        health_factors = []
        if summary["avg_cache_hit_rate"] > 0.7:
            health_factors.append(0.3)
            summary["strengths"].append("Good cache performance")
        if summary["avg_throughput"] > 10:
            health_factors.append(0.3)
            summary["strengths"].append("High throughput")
        if len(summary["bottlenecks"]) == 0:
            health_factors.append(0.4)
            summary["strengths"].append("No performance bottlenecks")

        summary["overall_health_score"] = round(sum(health_factors), 2)

        return summary

    def _generate_optimization_recommendations(self, suite_results: dict[str, Any]) -> list[str]:
        """Generate optimization recommendations based on benchmark results."""
        recommendations = []

        # Analyze cache performance
        cache_rates = []
        for component_results in suite_results.values():
            if isinstance(component_results, dict):
                for metrics in component_results.values():
                    if isinstance(metrics, dict) and "cache_hit_rate" in metrics:
                        cache_rates.append(metrics["cache_hit_rate"])

        if cache_rates and statistics.mean(cache_rates) < 0.6:
            recommendations.append("Improve cache hit rates by increasing cache sizes or optimizing cache keys")
            recommendations.append("Implement cache warming strategies for frequently accessed data")

        # Analyze throughput
        throughputs = []
        for component_results in suite_results.values():
            if isinstance(component_results, dict):
                for metrics in component_results.values():
                    if isinstance(metrics, dict) and "throughput" in metrics:
                        throughputs.append(metrics["throughput"])

        if throughputs and statistics.mean(throughputs) < 5:
            recommendations.append("Increase parallel processing capacity for better throughput")
            recommendations.append("Optimize batch sizes and concurrent operation limits")

        # Component-specific recommendations
        if "document_processing" in suite_results:
            doc_results = suite_results["document_processing"]
            slow_docs = [name for name, metrics in doc_results.items()
                        if isinstance(metrics, dict) and metrics.get("avg_processing_time", 0) > 2.0]
            if slow_docs:
                recommendations.append(f"Optimize processing for large documents: {', '.join(slow_docs)}")

        if "graph_analytics" in suite_results:
            analytics_results = suite_results["graph_analytics"]
            slow_queries = [name for name, metrics in analytics_results.items()
                           if isinstance(metrics, dict) and metrics.get("avg_query_time", 0) > 1.0]
            if slow_queries:
                recommendations.append(f"Optimize slow graph queries: {', '.join(slow_queries)}")

        return recommendations

    def _analyze_performance_regression(self, suite_results: dict[str, Any]) -> dict[str, Any]:
        """Analyze performance regression compared to baselines."""
        regression_analysis = {
            "regressions_detected": [],
            "improvements_detected": [],
            "baseline_comparison": {}
        }

        # Compare with stored baselines (if available)
        baseline_file = self.results_dir / "baselines.json"
        if baseline_file.exists():
            with open(baseline_file) as f:
                stored_baselines = json.load(f)

            for component, results in suite_results.items():
                if component in stored_baselines:
                    baseline_metrics = stored_baselines[component]

                    # Compare key metrics
                    for metric_name, current_value in results.items():
                        if isinstance(current_value, dict) and metric_name in baseline_metrics:
                            baseline_value = baseline_metrics[metric_name]

                            # Check for regression (performance degradation)
                            if "processing_time" in metric_name or "query_time" in metric_name:
                                if current_value > baseline_value * 1.1:  # 10% degradation
                                    regression_analysis["regressions_detected"].append(
                                        f"{component}.{metric_name}: {current_value:.2f} vs {baseline_value:.2f} baseline"
                                    )
                                elif current_value < baseline_value * 0.9:  # 10% improvement
                                    regression_analysis["improvements_detected"].append(
                                        f"{component}.{metric_name}: {current_value:.2f} vs {baseline_value:.2f} baseline"
                                    )

        return regression_analysis

    def _save_benchmark_results(self, suite_results: dict[str, Any], report: dict[str, Any]):
        """Save benchmark results to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        results_file = self.results_dir / f"benchmark_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(suite_results, f, indent=2, default=str)

        # Save report
        report_file = self.results_dir / f"benchmark_report_{timestamp}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Update baselines
        baseline_file = self.results_dir / "baselines.json"
        with open(baseline_file, "w") as f:
            json.dump(suite_results, f, indent=2, default=str)

        logger.info(f"Benchmark results saved to {self.results_dir}")

    async def run_quick_benchmark(self, component: str) -> dict[str, Any]:
        """Run a quick benchmark for a specific component."""
        logger.info(f"Running quick benchmark for {component}")

        if component == "document_processing":
            return await self._run_document_processing_benchmarks()
        elif component == "pipeline":
            return await self._run_pipeline_benchmarks()
        elif component == "graph_analytics":
            return await self._run_graph_analytics_benchmarks()
        elif component == "agent_workflow":
            return await self._run_agent_workflow_benchmarks()
        else:
            raise ValueError(f"Unknown component: {component}")

    def get_benchmark_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get historical benchmark results."""
        result_files = sorted(self.results_dir.glob("benchmark_report_*.json"))

        history = []
        for result_file in result_files[-limit:]:
            try:
                with open(result_file) as f:
                    data = json.load(f)
                    history.append({
                        "timestamp": data.get("timestamp"),
                        "execution_time": data.get("total_execution_time"),
                        "health_score": data.get("performance_summary", {}).get("overall_health_score", 0),
                        "cache_hit_rate": data.get("performance_summary", {}).get("avg_cache_hit_rate", 0),
                        "throughput": data.get("performance_summary", {}).get("avg_throughput", 0)
                    })
            except Exception as e:
                logger.warning(f"Failed to load historical result {result_file}: {e}")

        return history


# Global instance
_benchmark_suite: ISABenchmarkSuite | None = None


def get_benchmark_suite() -> ISABenchmarkSuite:
    """Get or create global benchmark suite instance."""
    global _benchmark_suite
    if _benchmark_suite is None:
        _benchmark_suite = ISABenchmarkSuite()
    return _benchmark_suite


async def run_full_benchmark_suite() -> dict[str, Any]:
    """Run the complete benchmark suite."""
    suite = get_benchmark_suite()
    return await suite.run_full_benchmark_suite()


async def run_component_benchmark(component: str) -> dict[str, Any]:
    """Run benchmark for a specific component."""
    suite = get_benchmark_suite()
    return await suite.run_quick_benchmark(component)


def get_benchmark_history(limit: int = 10) -> list[dict[str, Any]]:
    """Get historical benchmark results."""
    suite = get_benchmark_suite()
    return suite.get_benchmark_history(limit)
