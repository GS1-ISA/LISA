# Long Functions and Classes

## Classes longer than 300 lines:

- `src/benchmark_suite.py:ISABenchmarkSuite` (516 lines) - Benchmark suite for ISA components performance testing.
- `src/neo4j_gds_analytics.py:SupplyChainRiskAnalyzer` (644 lines) - Analyzer for supply chain risks using graph analytics.
- `src/performance_monitor.py:PerformanceMonitor` (558 lines) - Monitor for system performance metrics and alerts.
- `src/neo4j_gds_ingestion.py:Neo4jGDSDataIngestion` (343 lines) - Ingestion service for EPCIS data into Neo4j graph.
- `src/optimized_agent_workflow.py:OptimizedAgentWorkflow` (397 lines) - Optimized workflow for agent task execution.
- `src/optimized_graph_analytics.py:OptimizedGraphAnalytics` (341 lines) - Optimized analytics for graph data.
- `src/optimized_pipeline.py:OptimizedRegulatoryPipeline` (517 lines) - Optimized pipeline for regulatory document processing.
- `src/vc_supply_chain_integration.py:VCSupplyChainIntegrator` (372 lines) - Integrator for VC attestations in supply chain.

## Functions longer than 40 lines:

- `src/api_server.py:research` (72 lines) - Run the multi-agent research flow and return the final Markdown report.
- `src/benchmark_suite.py:_run_integration_benchmarks` (55 lines) - Run integration benchmarks for ISA components.
- `src/benchmark_suite.py:_generate_benchmark_report` (74 lines) - Generate comprehensive benchmark report with metrics.
- `src/benchmark_suite.py:_calculate_performance_summary` (60 lines) - Calculate performance summary from benchmark results.
- `src/benchmark_suite.py:_generate_optimization_recommendations` (44 lines) - Generate optimization recommendations based on benchmark data.
- `src/neo4j_gds_analytics.py:SupplyChainRiskAnalyzer.__init__` (79 lines) - Initialize the supply chain risk analyzer with GDS client.
- `src/neo4j_gds_analytics.py:analyze_supply_chain_risks` (89 lines) - Analyze supply chain risks for an organization.
- `src/neo4j_gds_analytics.py:_analyze_supply_paths` (44 lines) - Analyze supply chain paths for the organization.
- `src/neo4j_gds_analytics.py:_count_alternative_paths` (31 lines) - Count alternative paths between source and target.
- `src/neo4j_gds_analytics.py:predict_disruption_scenarios` (42 lines) - Predict disruption scenarios for organization.
- `src/performance_monitor.py:PerformanceMonitor.__init__` (49 lines) - Initialize the performance monitor with configuration.
- `src/performance_monitor.py:_monitoring_loop` (28 lines) - Main monitoring loop for collecting metrics.
- `src/performance_monitor.py:_collect_metrics` (20 lines) - Collect current performance metrics.
- `src/performance_monitor.py:_check_alerts` (35 lines) - Check for performance alerts based on metrics.
- `src/performance_monitor.py:_check_latency_alert` (35 lines) - Check for latency alerts.
- `src/performance_monitor.py:_check_throughput_alert` (35 lines) - Check for throughput alerts.
- `src/performance_monitor.py:_check_cache_hit_rate_alert` (35 lines) - Check for cache hit rate alerts.
- `src/performance_monitor.py:_check_memory_alert` (35 lines) - Check for memory alerts.
- `src/performance_monitor.py:_check_error_rate_alert` (35 lines) - Check for error rate alerts.
- `src/performance_monitor.py:_create_alert` (41 lines) - Create a performance alert.
- `src/performance_monitor.py:get_performance_summary` (35 lines) - Get comprehensive performance summary.
- `src/performance_monitor.py:export_metrics_report` (49 lines) - Export metrics report to file.
- `src/neo4j_gds_ingestion.py:ingest_epcis_events` (38 lines) - Ingest EPCIS events into the graph database.
- `src/neo4j_gds_ingestion.py:_process_batch` (56 lines) - Process a batch of EPCIS events.
- `src/neo4j_gds_ingestion.py:_batch_insert_graph_data` (29 lines) - Insert batch of graph data.
- `src/neo4j_gds_ingestion.py:validate_ingestion_data` (34 lines) - Validate ingestion data.
- `src/optimized_agent_workflow.py:execute_workflow` (75 lines) - Execute the optimized agent workflow.
- `src/optimized_agent_workflow.py:_execute_tasks_with_dependencies` (29 lines) - Execute tasks with dependencies.
- `src/optimized_agent_workflow.py:_execute_task_batch` (37 lines) - Execute a batch of tasks.
- `src/optimized_agent_workflow.py:_execute_single_task` (47 lines) - Execute a single agent task.
- `src/optimized_agent_workflow.py:_execute_agent_task` (35 lines) - Execute agent task with caching.
- `src/optimized_graph_analytics.py:analyze_organization_risks_async` (81 lines) - Analyze organization risks asynchronously.
- `src/optimized_graph_analytics.py:batch_analyze_organizations` (51 lines) - Batch analyze multiple organizations.
- `src/optimized_graph_analytics.py:predict_disruption_scenarios_batch` (28 lines) - Predict disruption scenarios in batch.
- `src/optimized_graph_analytics.py:analyze_supply_chain_network` (27 lines) - Analyze supply chain network.
- `src/optimized_graph_analytics.py:get_performance_stats` (43 lines) - Get performance statistics.
- `src/optimized_pipeline.py:process_regulatory_documents` (84 lines) - Process regulatory documents through pipeline.
- `src/optimized_pipeline.py:_process_single_document` (50 lines) - Process a single document.
- `src/optimized_pipeline.py:_validate_extracted_data` (30 lines) - Validate extracted data.
- `src/optimized_pipeline.py:_perform_semantic_validation` (50 lines) - Perform semantic validation.
- `src/vc_supply_chain_integration.py:integrate_supplier_attestations` (67 lines) - Integrate supplier attestations with supply chain.
- `src/vc_supply_chain_integration.py:verify_supply_chain_attestations` (64 lines) - Verify supply chain attestations.
- `src/vc_supply_chain_integration.py:link_vc_to_traceability` (34 lines) - Link VC to traceability data.
- `src/vc_supply_chain_integration.py:get_supply_chain_compliance_dashboard` (46 lines) - Get compliance dashboard data.