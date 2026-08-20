# Journal API — Cloud-Native DevOps Project

## Project Overview

Journal API is an end-to-end cloud and DevOps engineering project demonstrating the evolution of a Python FastAPI application from local application development through traditional cloud deployment and ultimately into a containerized, Kubernetes-based platform on AWS.

The project covers the full application and infrastructure lifecycle, including application development, automated testing, containerization, Infrastructure as Code, CI/CD, Kubernetes orchestration, managed databases, networking, and observability.

The final architecture uses Docker, Amazon ECR, Amazon EKS, Amazon RDS, Terraform, GitHub Actions, and the LGTM observability stack with OpenTelemetry.

---

## Project Attribution

This project is based on the [Learn to Cloud Journal Starter](https://github.com/learntocloud/journal-starter) repository.

The starter repository provided the foundation for the FastAPI journal application. I extended the application itself before using it as the workload for a broader cloud and DevOps engineering project.

My work on the project can be divided into two main areas: **application development** and **cloud/platform engineering**.

### Application Development

I extended the starter application with additional API functionality and improvements to validation, logging, testing, and external service integration.

Key additions include:

* Added retrieval of individual journal entries by ID.
* Added deletion of individual journal entries with appropriate HTTP responses and error handling.
* Introduced reusable Pydantic validation models with shared string constraints, whitespace handling, empty-input prevention, and maximum-length validation.
* Added separate request models for create and update operations.
* Replaced print-based debugging with structured Python application logging.
* Added AI-powered journal analysis for generating structured summaries and sentiment analysis.
* Implemented the AI integration asynchronously and used dependency injection to keep external services testable.
* Expanded automated test coverage with `pytest`, including mocked AI clients to avoid external API dependencies during testing.
* Used Ruff and Pyright for linting and static type checking.
* Developed and validated application changes through a pull-request-based workflow.

### Cloud & Platform Engineering

After extending the application, I evolved its deployment and operational model through several stages:

```text
FastAPI Application
        |
        v
Application Feature Development
        |
        v
EC2 Two-Tier Deployment
        |
        v
Docker Containerization
        |
        v
Amazon ECR
        |
        v
Amazon EKS + Amazon RDS
        |
        v
GitHub Actions CI/CD
        |
        v
Terraform Infrastructure as Code
        |
        v
Observability
Prometheus + Grafana + Loki + Tempo + OpenTelemetry
```

The platform engineering work includes:

* Containerizing the FastAPI application with Docker.
* Building AWS networking using public and private subnets across multiple Availability Zones.
* Provisioning AWS infrastructure using Terraform.
* Migrating the application from an EC2-based deployment to Amazon EKS.
* Using Amazon RDS for managed PostgreSQL.
* Publishing application container images to Amazon ECR.
* Deploying and managing the application using Kubernetes.
* Implementing liveness and readiness health probes.
* Building CI/CD automation using GitHub Actions.
* Using GitHub Actions OIDC for AWS authentication instead of long-lived access keys.
* Automating testing, container builds, ECR publishing, and Kubernetes deployments.
* Implementing metrics with Prometheus.
* Building dashboards and alerting with Grafana.
* Centralizing application logs with Loki.
* Implementing distributed tracing with Tempo.
* Instrumenting the application and telemetry pipeline with OpenTelemetry.

---

# Architecture

<br>

<p align="center">
  <img src="docs/Architecture.png" alt="AWS Two-Tier Architecture" width="1000">
</p>

<br>

The production architecture runs the Journal API as a containerized workload on Amazon EKS.

The EKS environment spans multiple Availability Zones and uses private subnets for application workloads and database resources.

### Why EKS?

Amazon EKS is intentionally more infrastructure than this application's current workload requires.

A small CRUD API like Journal API could be deployed more simply and cost-effectively using a service such as Amazon ECS with Fargate or AWS App Runner. EKS was chosen because one of the primary goals of this project was to gain hands-on experience building and operating a Kubernetes-based platform on AWS.

Using EKS provided practical experience with Kubernetes deployments, services, health probes, rolling deployments, container scheduling, networking, CI/CD integration, and Kubernetes-native observability.

The architecture therefore represents a **learning and platform-engineering environment rather than the minimum infrastructure required to run the application**.

For a low-traffic production workload where cost and operational simplicity were the primary requirements, I would evaluate a simpler managed compute platform before choosing Kubernetes.

---

# DevOps Workflow

The application follows an automated CI/CD workflow using GitHub Actions.

When application changes are pushed through the development workflow, GitHub Actions performs the following stages:

1. Runs automated tests and code-quality checks.
2. Builds the Journal API Docker image.
3. Authenticates to AWS using GitHub Actions OIDC.
4. Pushes the container image to Amazon ECR.
5. Connects to the Amazon EKS cluster.
6. Updates the Kubernetes deployment.
7. Kubernetes performs a rolling deployment of the new application version.

This creates an automated path from source code to the Kubernetes environment.

```text
Code Change
     |
     v
   GitHub
     |
     v
GitHub Actions
     |
     +--> Test
     |
     +--> Docker Build
     |
     +--> Amazon ECR
     |
     +--> Amazon EKS
              |
              v
       Kubernetes Deployment
              |
              v
        Journal API Pods
```

---

# Kubernetes Deployment

The Journal API is deployed to Amazon Elastic Kubernetes Service (EKS).

The application is packaged as a Docker image and stored in Amazon Elastic Container Registry (ECR). Kubernetes worker nodes pull the image from ECR and run the application inside Kubernetes pods.

The Kubernetes deployment includes:

* Application Deployment
* Multiple application pods
* Kubernetes Service
* AWS Load Balancer integration
* Liveness probes
* Readiness probes
* Environment configuration
* Rolling deployments

The application exposes:

```text
/health
/metrics
```

The `/health` endpoint is used by Kubernetes health probes, while `/metrics` exposes application metrics for Prometheus.

---

# CI/CD Pipeline

GitHub Actions provides the project's continuous integration and continuous deployment pipeline.

### Continuous Integration

The CI stage validates application changes using:

* pytest
* Ruff
* Pyright
* PostgreSQL test database

### Container Build

After validation, GitHub Actions:

```text
Dockerfile
    |
    v
Docker Build
    |
    v
Docker Image
    |
    v
Amazon ECR
```

### Continuous Deployment

After the image is pushed to ECR, the deployment stage authenticates with AWS, connects to Amazon EKS, and applies the Kubernetes manifests.

Kubernetes then performs the application rollout across the EKS worker nodes.

AWS authentication from GitHub Actions uses **OpenID Connect (OIDC)** rather than long-lived AWS access keys.

---

# Observability

The project includes a Kubernetes-native observability stack for monitoring application and cluster health.

## Prometheus

Prometheus collects application and Kubernetes metrics.

The Journal API exposes Prometheus-compatible metrics through:

```text
/metrics
```

Metrics include application request activity and infrastructure telemetry.

---

## Grafana

<br>

<p align="center">
  <img src="docs/grafana - Kubernetes API server.png" alt="Grafana Kubernetes API Server" width="49%">
  <img src="docs/grafana - Journal API.png" alt="Journal API" width="49%">
</p>

<br>

Grafana provides dashboards for visualizing application and Kubernetes performance.

Dashboards monitor areas such as:

* HTTP request volume
* Application error rate
* Request latency
* Kubernetes CPU usage
* Kubernetes memory usage
* Application exceptions

Grafana alerting is also configured to detect application issues such as elevated error rates or latency.

---

## Loki

Loki provides centralized log aggregation for the Kubernetes environment.

Application logs can be queried and analyzed through Grafana, allowing application failures to be correlated with metrics and traces.

---

## Tempo

Tempo provides distributed tracing.

Application requests are instrumented using OpenTelemetry and traces can be inspected through Grafana to understand request execution across application components.

---

## OpenTelemetry

The OpenTelemetry Collector provides the telemetry pipeline between the application and observability services.

```text
Journal API
    |
    v
OpenTelemetry
    |
    +------> Prometheus
    |
    +------> Loki
    |
    +------> Tempo
                 |
                 v
               Grafana
```

Together, these tools provide visibility across the three major observability signals:

```text
Metrics  -> Prometheus
Logs     -> Loki
Traces   -> Tempo
             |
             v
           Grafana
```

---

# AWS Infrastructure

The project uses several AWS services to provide compute, networking, container hosting, database services, security, and traffic management.

| AWS Service            | Purpose                             |
| ---------------------- | ----------------------------------- |
| Amazon EKS             | Managed Kubernetes cluster          |
| Amazon ECR             | Docker container image registry     |
| Amazon RDS             | Managed PostgreSQL database         |
| Amazon EC2             | EKS worker node compute             |
| Amazon VPC             | Network isolation                   |
| Elastic Load Balancing | External application traffic        |
| Route 53               | DNS                                 |
| IAM                    | AWS permissions and workload access |
| Security Groups        | Network access control              |

The environment uses multiple Availability Zones with public and private networking to provide workload isolation and improved availability.

---

# Technology Stack

| Category               | Technology     |
| ---------------------- | -------------- |
| Backend                | FastAPI        |
| Application Server     | Uvicorn        |
| Language               | Python         |
| Database               | PostgreSQL     |
| Cloud Platform         | AWS            |
| Containers             | Docker         |
| Container Registry     | Amazon ECR     |
| Orchestration          | Kubernetes     |
| Kubernetes             | Amazon EKS     |
| Infrastructure as Code | Terraform      |
| CI/CD                  | GitHub Actions |
| Metrics                | Prometheus     |
| Visualization          | Grafana        |
| Logging                | Loki           |
| Tracing                | Tempo          |
| Telemetry              | OpenTelemetry  |
| Version Control        | Git & GitHub   |

---

# Infrastructure as Code

Terraform is used to define and provision AWS infrastructure.

Infrastructure as Code allows cloud resources to be managed through version-controlled configuration rather than manual console changes.

The Terraform configuration includes infrastructure such as:

* VPC networking
* Public and private subnets
* Route tables
* Internet connectivity
* Security groups
* Amazon EKS
* EKS managed node groups
* IAM roles and permissions
* Amazon RDS

This makes the infrastructure repeatable, reviewable, and easier to reproduce.

## Terraform State Management

Terraform state is stored remotely in Amazon S3 rather than being maintained locally.

The backend infrastructure is separated from the main application infrastructure because the S3 state bucket must exist before Terraform can initialize and use it as a remote backend.

A dedicated `bootstrap/` Terraform configuration provisions the state bucket with:

* S3 versioning for state recovery
* Server-side encryption
* Public access blocking

The main Terraform configuration in `infra/` uses this bucket through an S3 backend defined in `backend.tf`.

S3-native state locking is enabled to prevent concurrent Terraform operations from modifying the state at the same time.

Separating the backend infrastructure from the application infrastructure provides a reliable foundation for managing Terraform state while keeping the main AWS infrastructure reproducible and version controlled.

---

# Application Features

The Journal API provides REST API functionality for creating and managing journal entries.

Application functionality includes:

* Create journal entries
* Retrieve journal entries
* Retrieve individual entries
* Update journal entries
* Delete journal entries
* Input validation
* AI-assisted journal analysis
* Application logging
* Health monitoring
* Prometheus metrics
* OpenTelemetry instrumentation

---

# Repository Structure

```text
journal-starter/
|
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
│
├── api/                    # FastAPI application
│
├── k8s/                    # Kubernetes manifests
│
├── bootstrap/              # Terraform remote-state infrastructure
│           
├── infra/                  # Infrastructure as Code
│
├── tests/                  # Automated application tests
│
├── scripts/                # Deployment/support scripts
│
├── Dockerfile              # Application container image
│
├── database_setup.sql      # PostgreSQL initialization
│
├── pyproject.toml          # Python project configuration
│
└── README.md
```

---

# Original EC2 Deployment

Before migrating the application to Kubernetes, the Journal API was deployed using a traditional AWS two-tier architecture.

The original environment consisted of:

```text
Internet
   |
   v
Public EC2
FastAPI + Uvicorn + Nginx
   |
   v
Private EC2
PostgreSQL
```

This initial deployment established the networking and infrastructure foundation before the application was containerized and migrated to Amazon EKS.

---

# Key DevOps Concepts Demonstrated

This project demonstrates hands-on implementation of:

**Cloud Infrastructure**

* AWS networking and VPC design
* Public/private subnet architecture
* Security groups
* IAM
* Managed AWS services

**Containers & Kubernetes**

* Docker image creation
* Container registries
* Kubernetes Deployments and Services
* Pod scheduling
* Health checks
* Rolling deployments
* Amazon EKS

**CI/CD**

* Automated testing
* Docker image builds
* Amazon ECR publishing
* Automated Kubernetes deployments
* GitHub Actions
* AWS OIDC authentication

**Infrastructure as Code**

* Terraform
* Repeatable AWS infrastructure
* Version-controlled infrastructure configuration

**Observability**

* Application metrics
* Kubernetes metrics
* Centralized logging
* Distributed tracing
* Dashboards
* Alerting
* OpenTelemetry

---

# Project Goal

The goal of this project is to demonstrate the complete lifecycle of operating a backend application using modern cloud and DevOps practices, from infrastructure provisioning and containerization to automated deployment, Kubernetes orchestration, monitoring, logging, and distributed tracing.

The project provides hands-on experience with the technologies and operational practices commonly used in Cloud Engineering, DevOps Engineering, Platform Engineering, and Site Reliability Engineering environments.
