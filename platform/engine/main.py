"""
This script is the brain. It reads the developer's intent, validates it, and renders the templates.
This is also the Phase 2: The Integration Plane (The Engine & CLI) for the Canvas platform.

Let's go over all the four steps of planes to understand Canvas platform end to end.

Phase 1: The Developer Experience Plane (The Interface)
We start by defining the "Contract." This is what your developers (and you) will interact with daily. 
We are replacing complex Kubernetes YAMLs with intention-based configuration.

Action: Create/Update these files in services/text-service/
- canvas.yaml (Extensive Runtime Definition). This file tells Canvas what the app needs to run.
- pipeline.yaml (The Assembly Line). This file tells Canvas how to verify and build the app.


Phase 2: The Integration Plane (The Engine & CLI)
Now we build the "brain." This Python CLI (platform/engine/main.py) will do two things:
1. Local Dev: Validate the yaml and run the app locally (canvas up).
2. CI/CD: Render Kubernetes manifests (canvas generate).

Prerequisites: Ensure you have the engine dependencies installed (typer, jinja2, pyyaml, rich).

1. The Universal Templates (Helm/Jinja2)
We need a robust template that translates the simple canvas.yaml into complex Kubernetes resources.

Action: Create platform/engine/templates/deployment.yaml.j2.

2. The Canvas CLI (canvas)
This is the tool your developers will love. It standardizes how they work.

Action: Update platform/engine/main.py.

Phase 3: The Artifact (Dockerfile)
The text-service needs a robust Dockerfile. This is what the CI pipeline will build.

Action: Create services/text-service/Dockerfile.

Phase 4: The CI/CD Pipeline (GitHub Actions)
This acts as the Integration & Delivery Plane. It ties everything together.

Action: Create .github/workflows/ci-cd.yml.

Summary of what you just built:
1. The Contract: canvas.yaml defines the service simply.
2. The Tooling: canvas up lets you run the service locally in Docker instantly using that contract.
3. The Automation: The GitHub Action runs tests, builds the Docker image, and then uses the Canvas Engine to write the Kubernetes files to ops/.
4. The Deployment: ArgoCD (conceptually) sees the new file in ops/ and updates your cluster.

You now have a Platform Engineering foundation that is scalable for the next 50 services.

"""


import os
import sys
import yaml
import typer
import subprocess
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(help="Canvas Platform Engine CLI")
console = Console()

# Configuration constants
TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_REGISTRY = "123456789.dkr.ecr.us-east-1.amazonaws.com/immersive"

def load_blueprint(path: Path) -> dict:
    """Helper: Loads and validates the canvas.yaml file."""
    blueprint_path = path / "canvas.yaml"
    
    if not blueprint_path.exists():
        console.print(f"[bold red]Error:[/bold red] Blueprint not found at {blueprint_path}")
        raise typer.Exit(code=1)
        
    try:
        with open(blueprint_path, "r") as f:
            data = yaml.safe_load(f)
        if data.get("kind") != "CanvasService":
            console.print("[bold red]Invalid Blueprint:[/bold red] 'kind' must be 'CanvasService'")
            raise typer.Exit(code=1)
        return data
    except yaml.YAMLError as e:
        console.print(f"[bold red]YAML Parsing Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(service_path: Path = typer.Argument(..., help="Path to service folder")):
    """✅ Check if a service's canvas.yaml is valid."""
    blueprint = load_blueprint(service_path)
    name = blueprint['metadata']['name']
    console.print(Panel(f"[bold green]Valid Canvas Blueprint found for service: {name}[/bold green]"))

@app.command()
def up(service_path: Path = typer.Argument(..., help="Path to service folder")):
    """🚀 Run the service locally using Docker."""
    blueprint = load_blueprint(service_path)
    name = blueprint['metadata']['name']
    port = blueprint['spec']['networking']['port']
    
    console.print(f"[blue]Canvas Up: Bootstrapping {name}...[/blue]")
    
    # 1. Build
    subprocess.run(["docker", "build", "-t", f"{name}:local", "."], cwd=service_path, check=True)
    
    # 2. Prepare Env
    docker_env_args = []
    if 'spec' in blueprint and 'env' in blueprint['spec']:
        for key, value in blueprint['spec']['env'].items():
            docker_env_args.extend(["-e", f"{key}={value}"])
    
    # 3. Load Secrets
    local_env_file = service_path / ".env"
    if local_env_file.exists():
        docker_env_args.extend(["--env-file", str(local_env_file)])

    # 4. Run
    console.print(f"[green]Starting on http://localhost:{port}[/green]")
    cmd = ["docker", "run", "--rm", "-p", f"{port}:{port}", "--name", f"{name}-local"] + docker_env_args + [f"{name}:local"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping...[/yellow]")

@app.command()
def generate(
    service_path: Path = typer.Argument(..., help="Path to service folder"),
    image_tag: str = typer.Option("latest", help="Docker image tag to deploy"),
    output_dir: Path = typer.Option(None, help="Custom output directory for manifests")
):
    """⚙️ CI/CD: Render Kubernetes manifests from the blueprint."""
    blueprint = load_blueprint(service_path)
    service_name = blueprint['metadata']['name']
    
    console.print(f"Hydrating manifests for [cyan]{service_name}[/cyan]...")
    
    if not TEMPLATE_DIR.exists():
        console.print(f"[bold red]Template directory not found at {TEMPLATE_DIR}[/bold red]")
        raise typer.Exit(code=1)
        
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)
    
    # Prepare Context
    context = {
        **blueprint, 
        "image_repo": f"{DEFAULT_REGISTRY}/{service_name}",
        "image_tag": image_tag
    }
    
    # Determine Output Directory
    if not output_dir:
        output_dir = Path("ops/production") / service_name
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generated_files = []

    try:
        # --- 1. Render Deployment ---
        dep_tpl = env.get_template("deployment.yaml.j2")
        dep_content = dep_tpl.render(**context)
        dep_path = output_dir / "01-deployment.yaml"
        with open(dep_path, "w") as f:
            f.write(dep_content)
        generated_files.append(str(dep_path))

        # --- 2. Render Service (NEW) ---
        svc_tpl = env.get_template("service.yaml.j2")
        svc_content = svc_tpl.render(**context)
        svc_path = output_dir / "02-service.yaml"
        with open(svc_path, "w") as f:
            f.write(svc_content)
        generated_files.append(str(svc_path))
            
    except Exception as e:
        console.print(f"[bold red]Rendering Failed:[/bold red] {e}")
        raise typer.Exit(code=1)

    # Summary Output
    table = Table(title="Canvas Manifest Generation")
    table.add_column("Manifest", style="cyan")
    table.add_column("Path", style="green")
    
    for file_path in generated_files:
        table.add_row(Path(file_path).name, file_path)
    
    console.print(table)
    console.print(f"[bold green]✔ Successfully generated GitOps artifacts in {output_dir}[/bold green]")

if __name__ == "__main__":
    app()

# run the engine
# CI/CD: Render Kubernetes manifests (canvas generate).
# From project root /immersive
#./platform/engine/.venv/bin/python platform/engine/main.py generate services/text-service

# Local Dev: Validate the yaml and run the app locally (canvas up).

