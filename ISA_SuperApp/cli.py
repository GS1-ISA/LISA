"""
ISA SuperApp Command Line Interface.

This module provides a comprehensive CLI for the ISA SuperApp,
including commands for running the application, managing data,
and interacting with various components.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from .core.app import ISASuperApp, create_app
from .core.config import create_default_config_file, get_config
from .core.exceptions import ISAError
from .core.models import Document, SearchQuery, Task, TaskType


@click.group()
@click.option("--config", "-c", help="Path to configuration file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """ISA SuperApp Command Line Interface."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose

    # Setup logging based on verbosity
    if verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option("--host", "-h", default="localhost", help="Host to bind to")
@click.option("--port", "-p", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.pass_context
def serve(ctx, host: str, port: int, reload: bool):
    """Start the ISA SuperApp server."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(_run_server(config_path, host, port, reload))
    except KeyboardInterrupt:
        click.echo("\nServer stopped by user")
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        sys.exit(1)


async def _run_server(config_path: Optional[str], host: str, port: int, reload: bool):
    """Run the server."""
    app = await create_app(config_path)

    # Override API configuration if provided
    if host != "localhost" or port != 8000:
        app.config.api.host = host
        app.config.api.port = port

    click.echo(f"Starting ISA SuperApp server on {host}:{port}")
    await app.start()


@cli.command()
@click.option("--output", "-o", help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format",
)
def create_config(output: str, format: str):
    """Create a default configuration file."""
    if not output:
        output = f"isa_config.{format}"

    try:
        create_default_config_file(output, format)
        click.echo(f"Configuration file created: {output}")
    except Exception as e:
        click.echo(f"Error creating configuration file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument(
    "task_type", type=click.Choice(["research", "analysis", "document", "search"])
)
@click.option("--query", "-q", required=True, help="Task query or description")
@click.option("--context", "-c", help="Additional context for the task")
@click.option(
    "--priority",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    help="Task priority",
)
@click.option("--timeout", type=int, help="Task timeout in seconds")
@click.pass_context
def task(
    ctx,
    task_type: str,
    query: str,
    context: Optional[str],
    priority: str,
    timeout: Optional[int],
):
    """Execute a task using the agent system."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(
            _execute_task(config_path, task_type, query, context, priority, timeout)
        )
    except Exception as e:
        click.echo(f"Error executing task: {e}", err=True)
        sys.exit(1)


async def _execute_task(
    config_path: Optional[str],
    task_type: str,
    query: str,
    context: Optional[str],
    priority: str,
    timeout: Optional[int],
):
    """Execute a task."""
    app = await create_app(config_path)

    task = Task(
        type=TaskType(task_type),
        query=query,
        context=context or "",
        priority=priority,
        timeout=timeout,
    )

    click.echo(f"Executing {task_type} task: {query}")
    task_id = await app.execute_task(task)
    click.echo(f"Task submitted with ID: {task_id}")


@cli.command()
@click.argument("workflow_name")
@click.option("--input", "-i", help="Input data as JSON string")
@click.option(
    "--input-file", "-f", type=click.Path(exists=True), help="Input data file (JSON)"
)
@click.pass_context
def workflow(ctx, workflow_name: str, input: Optional[str], input_file: Optional[str]):
    """Execute a workflow."""
    config_path = ctx.obj.get("config_path")

    # Parse input data
    input_data = {}
    if input:
        try:
            input_data = json.loads(input)
        except json.JSONDecodeError as e:
            click.echo(f"Invalid JSON input: {e}", err=True)
            sys.exit(1)
    elif input_file:
        try:
            with open(input_file, "r") as f:
                input_data = json.load(f)
        except Exception as e:
            click.echo(f"Error reading input file: {e}", err=True)
            sys.exit(1)

    try:
        asyncio.run(_execute_workflow(config_path, workflow_name, input_data))
    except Exception as e:
        click.echo(f"Error executing workflow: {e}", err=True)
        sys.exit(1)


async def _execute_workflow(
    config_path: Optional[str], workflow_name: str, input_data: Dict[str, Any]
):
    """Execute a workflow."""
    app = await create_app(config_path)

    click.echo(f"Executing workflow: {workflow_name}")
    workflow_id = await app.execute_workflow(workflow_name, input_data)
    click.echo(f"Workflow submitted with ID: {workflow_id}")


@cli.command()
@click.argument("query")
@click.option("--limit", "-l", type=int, default=10, help="Maximum number of results")
@click.option("--threshold", "-t", type=float, help="Similarity threshold")
@click.option("--collection", "-c", help="Vector store collection name")
@click.pass_context
def search(
    ctx, query: str, limit: int, threshold: Optional[float], collection: Optional[str]
):
    """Search documents in the vector store."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(_search_documents(config_path, query, limit, threshold, collection))
    except Exception as e:
        click.echo(f"Error searching documents: {e}", err=True)
        sys.exit(1)


async def _search_documents(
    config_path: Optional[str],
    query: str,
    limit: int,
    threshold: Optional[float],
    collection: Optional[str],
):
    """Search documents."""
    app = await create_app(config_path)

    search_query = SearchQuery(
        query=query, limit=limit, threshold=threshold, collection=collection
    )

    click.echo(f"Searching for: {query}")
    results = await app.search_documents(search_query)

    if not results:
        click.echo("No documents found")
        return

    click.echo(f"\nFound {len(results)} documents:")
    for i, doc in enumerate(results, 1):
        click.echo(f"\n{i}. {doc.title}")
        click.echo(f"   ID: {doc.id}")
        click.echo(f"   Score: {doc.score:.3f}")
        click.echo(f"   Content: {doc.content[:200]}...")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--title", "-t", help="Document title")
@click.option("--collection", "-c", help="Vector store collection name")
@click.option("--metadata", "-m", help="Additional metadata as JSON")
@click.pass_context
def index(
    ctx,
    file_path: str,
    title: Optional[str],
    collection: Optional[str],
    metadata: Optional[str],
):
    """Index a document in the vector store."""
    config_path = ctx.obj.get("config_path")

    # Parse metadata
    meta_dict = {}
    if metadata:
        try:
            meta_dict = json.loads(metadata)
        except json.JSONDecodeError as e:
            click.echo(f"Invalid JSON metadata: {e}", err=True)
            sys.exit(1)

    try:
        asyncio.run(
            _index_document(config_path, file_path, title, collection, meta_dict)
        )
    except Exception as e:
        click.echo(f"Error indexing document: {e}", err=True)
        sys.exit(1)


async def _index_document(
    config_path: Optional[str],
    file_path: str,
    title: Optional[str],
    collection: Optional[str],
    metadata: Dict[str, Any],
):
    """Index a document."""
    app = await create_app(config_path)

    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise ISAError(f"Failed to read file: {e}")

    document = Document(
        title=title or Path(file_path).name,
        content=content,
        source=file_path,
        collection=collection,
        metadata=metadata,
    )

    click.echo(f"Indexing document: {file_path}")
    doc_id = await app.index_document(document)
    click.echo(f"Document indexed with ID: {doc_id}")


@cli.command()
@click.pass_context
def status(ctx):
    """Show application status."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(_show_status(config_path))
    except Exception as e:
        click.echo(f"Error getting status: {e}", err=True)
        sys.exit(1)


async def _show_status(config_path: Optional[str]):
    """Show application status."""
    app = await create_app(config_path)
    status = app.get_status()

    click.echo("ISA SuperApp Status")
    click.echo("=" * 50)
    click.echo(f"Version: {status['version']}")
    click.echo(f"Environment: {status['environment']}")
    click.echo(f"Initialized: {status['initialized']}")
    click.echo(f"Running: {status['running']}")

    if "components" in status:
        click.echo("\nComponents:")
        for component, comp_status in status["components"].items():
            click.echo(f"  {component}: {comp_status.get('status', 'unknown')}")


@cli.command()
@click.pass_context
def health(ctx):
    """Perform health check."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(_health_check(config_path))
    except Exception as e:
        click.echo(f"Error performing health check: {e}", err=True)
        sys.exit(1)


async def _health_check(config_path: Optional[str]):
    """Perform health check."""
    app = await create_app(config_path)
    health = await app.health_check()

    click.echo("Health Check Results")
    click.echo("=" * 50)
    click.echo(f"Overall Status: {health['status']}")
    click.echo(f"Timestamp: {datetime.fromtimestamp(health['timestamp'])}")

    if "checks" in health:
        click.echo("\nComponent Checks:")
        for component, check_result in health["checks"].items():
            status = check_result.get("status", "unknown")
            click.echo(f"  {component}: {status}")
            if status == "unhealthy" and "error" in check_result:
                click.echo(f"    Error: {check_result['error']}")


@cli.command()
@click.argument("config_key")
@click.option("--value", "-v", help="New value for the configuration key")
@click.pass_context
def config(ctx, config_key: str, value: Optional[str]):
    """Get or set configuration values."""
    config_path = ctx.obj.get("config_path")

    try:
        config_manager = get_config(config_path)

        if value:
            # Set configuration value
            config_manager.set(config_key, value)
            click.echo(f"Configuration updated: {config_key} = {value}")
        else:
            # Get configuration value
            current_value = config_manager.get(config_key)
            click.echo(f"{config_key}: {current_value}")

    except Exception as e:
        click.echo(f"Error accessing configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--pattern", "-p", default="**/*.md", help="File pattern to match")
@click.option("--collection", "-c", help="Vector store collection name")
@click.option("--recursive", "-r", is_flag=True, help="Process directories recursively")
@click.pass_context
def batch_index(
    ctx, directory: str, pattern: str, collection: Optional[str], recursive: bool
):
    """Batch index documents from a directory."""
    config_path = ctx.obj.get("config_path")

    try:
        asyncio.run(
            _batch_index(config_path, directory, pattern, collection, recursive)
        )
    except Exception as e:
        click.echo(f"Error during batch indexing: {e}", err=True)
        sys.exit(1)


async def _batch_index(
    config_path: Optional[str],
    directory: str,
    pattern: str,
    collection: Optional[str],
    recursive: bool,
):
    """Batch index documents."""
    app = await create_app(config_path)

    from pathlib import Path

    dir_path = Path(directory)

    if recursive:
        files = list(dir_path.rglob(pattern))
    else:
        files = list(dir_path.glob(pattern))

    if not files:
        click.echo(f"No files found matching pattern: {pattern}")
        return

    click.echo(f"Found {len(files)} files to index")

    indexed_count = 0
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            document = Document(
                title=file_path.name,
                content=content,
                source=str(file_path),
                collection=collection,
            )

            await app.index_document(document)
            indexed_count += 1
            click.echo(f"Indexed: {file_path}")

        except Exception as e:
            click.echo(f"Error indexing {file_path}: {e}", err=True)

    click.echo(
        f"\nBatch indexing completed: {indexed_count}/{len(files)} files indexed"
    )


def main():
    """Main CLI entry point."""
    cli()


if __name__ == "__main__":
    main()
