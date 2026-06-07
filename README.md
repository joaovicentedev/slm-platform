# SLM Platform: Fine-Tuning and Inference on AWS

This project demonstrates a production-oriented pipeline for fine-tuning and serving a Small Language Model (SLM) using modern MLOps practices.
It is designed as a monorepo to keep development velocity high while maintaining clear separation of concerns.

The system is built around:

* Fine-tuning and serving a small Hugging Face model, currently **HuggingFaceTB/SmolLM2-135M-Instruct** for local development
* Serving inference through a scalable API
* Managing infrastructure with Terraform
* Deploying to AWS with Kubernetes (EKS)

## Goals

* Provide a realistic end-to-end ML system
* Separate training and inference concerns
* Use infrastructure-as-code (Terraform)
* Implement production-grade API patterns
* Enable local development and cloud deployment
* Keep the system modular and extensible

---

## Architecture Overview

The system is composed of three main layers:

1. **Training Layer**

   * Dataset preparation
   * Fine-tuning pipeline
   * Evaluation and export

2. **Serving Layer**

   * vLLM OpenAI-compatible inference server
   * Product-side OpenAI client integration
   * Observability and performance tracking

3. **Infrastructure Layer**

   * AWS provisioning (Terraform)
   * Kubernetes deployment (EKS)
   * Networking, IAM, and scaling

### High-level Flow

```
Dataset → Hugging Face + PEFT Fine-Tune → LoRA Adapter → Merged Model → vLLM OpenAI API → Client
```

---

## Repository Structure

```
slm-api/
│
├── training/
│   ├── src/
│   │   ├── data/
│   │   ├── datasets/
│   │   ├── training/
│   │   ├── evaluation/
│   │   └── utils/
│   │
│   ├── configs/
│   ├── scripts/
│   ├── tests/
│   └── README.md
│
├── serving/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── inference/
│   │   ├── schemas/
│   │   └── dependencies/
│   │
│   ├── benchmarks/
│   ├── tests/
│   ├── Dockerfile
│   └── README.md
│
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   └── prod/
│   │
│   ├── k8s/
│   │   ├── base/
│   │   ├── overlays/
│   │   └── helm/
│   │
│   └── README.md
│
├── shared/
│   ├── configs/
│   ├── logging/
│   ├── utils/
│   └── types/
│
├── scripts/
│   ├── local_dev.sh
│   ├── build.sh
│   ├── deploy.sh
│   └── test.sh
│
├── docker-compose.yml
├── pyproject.toml
├── Makefile
└── README.md
```

---

## Model

* Current local base model: **HuggingFaceTB/SmolLM2-135M-Instruct**
* Served model name: **slm**
* Target: efficient fine-tuning and low-latency inference
* Expected deployment:

  * MacBook CPU via vLLM CPU Docker image for local development
  * GPU (optional scaling)

The local model is intentionally small so the vLLM CPU image can run on a MacBook. Set `VLLM_MODEL` to serve a different Hugging Face model or a merged local artifact such as `/artifacts/model`.

---

## Training Pipeline

The training module is responsible for:

* Dataset ingestion and preprocessing
* Fine-tuning configuration
* Evaluation and metrics
* Exporting artifacts

### Responsibilities

* No dependency on serving code
* Outputs versioned model artifacts
* Stores artifacts in S3 (or local during development)

### Outputs

* LoRA adapter
* Merged model weights
* Tokenizer
* Config files
* Evaluation metrics

---

## Inference API

The serving layer exposes the model through vLLM's OpenAI-compatible API.

### Features

* OpenAI-compatible `/v1/chat/completions` API
* Stateless service
* Model loaded by vLLM at startup
* Product code can use the OpenAI SDK against the vLLM base URL
* Ready for horizontal scaling

### Responsibilities

* Load merged model from artifact store (S3/local)
* Handle inference requests
* Log metrics and latency
* Integrate with monitoring tools

### Example Endpoint

```
POST /v1/chat/completions

{
  "model": "slm",
  "messages": [{"role": "user", "content": "Explain Kubernetes in simple terms"}],
  "max_tokens": 100
}
```

---

## Infrastructure (AWS)

Infrastructure is managed with Terraform and deployed to AWS.

### Core Components

* **S3**: model artifacts and datasets
* **ECR**: container registry
* **EKS**: inference deployment
* **IAM**: permissions and roles
* **ALB**: API exposure
* **CloudWatch**: logs and metrics

### Deployment Strategy

* Training runs outside Kubernetes (initially)
* Inference runs inside Kubernetes
* Infrastructure defined declaratively via Terraform

---

## Kubernetes (EKS)

The serving API is deployed to EKS with:

* Deployment (replicas for scaling)
* Service (internal communication)
* Ingress (external access via ALB)
* Autoscaling (HPA)

### Goals

* Enable horizontal scaling
* Isolate inference workloads

---

## Local Development

Local development is designed to be simple and fast.

### Requirements

* Python
* Docker
* Docker Compose

### Run locally

```
make serve
```

or

```
docker-compose up
```

### Local capabilities

* Run small fine-tuning jobs
* Test inference API
* Run unit tests
* Perform basic load testing

---

## CI/CD (Planned)

* GitHub Actions
* Linting (ruff, mypy)
* Tests (pytest)
* Build Docker images
* Deploy to AWS environments

---

## Observability (Planned)

* Structured logging
* Metrics collection
* Latency tracking
* Integration with:

  * CloudWatch
  * Prometheus/Grafana

---

## Design Principles

* Separation of concerns (training vs serving vs infra)
* Stateless inference services
* Infrastructure as code
* Reproducibility of experiments
* Minimal coupling between modules
* Production-first thinking, even in a learning project

---

## Roadmap

### Phase 1

* Local training pipeline
* Basic inference API
* Dockerized services

### Phase 2

* Deploy inference to EKS
* Store artifacts in S3
* Integrate Terraform

### Phase 3

* Add autoscaling
* Add monitoring
* Benchmark performance

### Phase 4

* Optimize inference (GPU / batching)
* Evaluate cost vs latency
* Experiment with alternative runtimes
