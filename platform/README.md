# 🎨 Canvas: The Engineering Platform

> **"Don't build clusters. Paint the vision."**

Canvas is the Internal Developer Platform (IDP) powering the Immersive Craft AI startup. It provides a "Golden Path" for engineering, abstracting the complexities of Kubernetes, Security, and Observability into simple, developer-centric blueprints.

## 🎯 Mission

The core mission of Canvas is to enable developers to ship production-ready microservices without managing infrastructure. We enforce a strict separation of concerns:

* **Developers** define **"What"** they need (CPU, Memory, Ports).
* **Canvas** defines **"How"** it happens (Ingress, HPA, Sidecars, Security Contexts).

## 🏗️ Architecture: The Four Planes

Canvas operates across four distinct planes, ensuring speed, security, and stability from code commit to production runtime.

### 1. Developer Experience Plane (The Interface)
The entry point for all engineering work. Developers interact solely with high-level configuration files in their service repositories.

* **Interface:** `canvas.yaml` and `pipeline.yaml`.
* **The Canvas CLI:** A local tool for developers to validate and bootstrap their services (e.g., `canvas validate`, `canvas up` for local Docker Compose environments).

### 2. Integration & Delivery Plane (The Engine)
This is the automation layer that converts developer intent (`canvas.yaml`) into deployable infrastructure (`Deployment.yaml`).

* **The Canvas Engine:** A Python-based orchestrator that reads the high-level blueprints and uses **Universal Helm Charts** to generate security-hardened Kubernetes manifests.
* **GitOps (ArgoCD):** Automatically watches the generated manifests in the `ops/` directory and syncs them to the production EKS cluster in real-time.

### 3. Observability Plane (Built-in Monitoring)
Canvas provides visibility by default, requiring zero configuration from the application developer.

* **Standardization:** The Canvas Engine automatically injects **OpenTelemetry (OTEL)** sidecars into every pod.
* **Logs:** Automatically collected by OTEL and routed to the **EFK Stack** (Elasticsearch, Fluentd, Kibana).
* **Metrics & APM:** Traces and metrics are automatically sent to **Datadog**.
* **Dashboarding:** All services adhere to a single data contract, enabling the use of universal Grafana dashboards.

### 4. Security Plane (Guardrails & Secrets)
Security is treated as a foundational requirement, not an optional step.

* **Guardrails:** The Engine rejects `canvas.yaml` configurations that request unsafe permissions (e.g., `root` access or excessive K8s capabilities).
* **Secrets:** Developers reference secrets by name (e.g., `GEMINI_API_KEY`). The Engine configures the **External Secrets Operator** to fetch the actual value from **AWS Secrets Manager** at runtime.
* **Scanning:** **SonarQube (SAST)** and **Trivy (Container)** scans are mandatory steps in the build pipeline (`pipeline.yaml`).

---

## 📝 The Canvas Contract (Blueprints)

Developers define their service requirements using two primary YAML files and a local environment file.

### A. `canvas.yaml` (The Runtime Spec)
Describes the service's runtime environment, compute, and networking needs.

```yaml
version: "v1"
kind: "CanvasService"
metadata:
  name: "text-service"
  domain: "immersive.ai"
  owner: "backend-team"

spec:
  runtime: "python:3.10"
  tier: "backend-api" # Defines preset security/network policies
  
  compute:
    cpu: "1"
    memory: "1Gi"
    gpu: false # Set to 'true' for GPU-accelerated services (e.g., Image Service)
    autoscaling:
      min: 2
      max: 10
      target_cpu_utilization: 75

  networking:
    port: 8000
    ingress:
      enabled: true
      path: "/v1/text"
    health_check: "/health"

  dependencies:
    # Canvas automatically provisions and links this resource
    - type: "redis" 
      name: "task-queue"
```

### B. `pipeline.yaml` (The Build Spec)
Defines how raw code is tested, built, and registered.

```yaml
pipeline:
  type: "python-fastapi" # Loads a standardized CI/CD workflow template
  security:
    sast_scan: true      # Mandatory SAST scan before merging
    container_scan: true # Mandatory container vulnerability check
  artifacts:
    registry: "ecr"      # AWS ECR
    retention: "90days"
```

### C. `.env` (The Local Context)
Used exclusively for local development and testing. This file is never committed or deployed. Production secrets are handled by the Security Plane.

# 📂 Repository Structure
The Canvas platform enforces this standard Monorepo structure:

```
/immersive-monorepo
├── apps/                       # 🏗️ Developer Experience Plane (Where developers work)
│   └── text-service/           
│       ├── canvas.yaml         # Service Runtime Definition
│       └── pipeline.yaml       # Service Build Definition
│
├── platform/                   # ⚙️ The Canvas Engine (Platform Code)
│   ├── README.md               # You are here
│   ├── engine/                 # Python CLI, Jinja2 templates
│   └── charts/                 # Universal Helm Charts
│
└── ops/                        # 🚀 GitOps State (The Output)
    └── production/         
        └── text-service/
            ├── 01-deployment.yaml  # Generated by Canvas
            └── 02-service.yaml     # Generated by Canvas
```

