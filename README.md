# ShopSphere — AWS DevOps E-Commerce Project

Production-style architecture | Amazon EKS | Amazon RDS PostgreSQL | Linux | Jenkins | Terraform | GitOps

Updated database: RDS PostgreSQL

Full-stack

Interview portfolio

This is the consolidated project document, replacing the earlier CloudTask design. ShopSphere will be a modern e-commerce platform with a React storefront, FastAPI backend and Amazon RDS PostgreSQL database, deployed on Amazon EKS using a complete DevSecOps pipeline.

The implementation will be divided into a working application, AWS infrastructure, automated delivery and production operations. The initial release will use a modular monolith to keep development straightforward while providing substantial DevOps experience.

# 1. Project objectives

The goal is to demonstrate the complete lifecycle of a cloud-native application: development, automated testing, infrastructure provisioning, containerization, deployment, security, monitoring, scaling and recovery.

The finished application will support customer registration, product browsing, shopping carts, simulated checkout, order tracking and an administrator dashboard.

![IsoTech - Electronics Store Shopify Theme OS 2.0](https://images.openai.com/static-rsc-4/YKb6TnllF9r3QEKvVYF9LVdl-v9rkmdmqke3F_ZJBzsK4xTy9G666jd5sraPQa88BoB8vN1ARbVvaJQNTl23TALRAEGNbEJ0dsOtImjqOUHNh1KOUQjpptZt7VNmgKAs8m4UHARmDQwj9sSggg9JAH2nSW9Bz3ZSQBqHt6nJGYY?purpose=inline)

# ShopSphere

Modern e-commerce platform for demonstrating real-world AWS DevOps workflows.

Customer storefront

Admin dashboard

Secure checkout

Order management

# 2. Final technology stack

|
Component

|

Technology

|
| --- | --- |
|

Frontend

|

React, TypeScript, Tailwind CSS

|
|

Backend

|

Python FastAPI

|
|

ORM and migrations

|

SQLAlchemy, Alembic

|
|

Primary database

|

Amazon RDS PostgreSQL

|
|

Local database

|

PostgreSQL in Docker

|
|

Database connections

|

SQLAlchemy pool; RDS Proxy if needed

|
|

Operating system

|

Amazon Linux 2023

|
|

CI

|

Jenkins

|
|

Code analysis

|

SonarQube

|
|

Security scanning

|

Trivy

|
|

Containerization

|

Docker

|
|

Container registry

|

Amazon ECR

|
|

Orchestration

|

Amazon EKS

|
|

Deployment packaging

|

Helm

|
|

Continuous delivery

|

Argo CD

|
|

Infrastructure as Code

|

Terraform

|
|

Load balancing

|

AWS ALB

|
|

DNS and TLS

|

Route 53, ACM

|
|

Secrets

|

AWS Secrets Manager

|
|

Autoscaling

|

Kubernetes HPA, Karpenter

|
|

Monitoring

|

CloudWatch, Prometheus, Grafana

|
|

Asynchronous processing

|

Amazon SQS, advanced phase

|
|

Object storage

|

Amazon S3 for product images

|

# 3. Complete AWS architecture

GitHub

Application + Terraform + Helm

Jenkins on Linux

Test → Scan → Build

Amazon ECR

Immutable container images

GitOps repository

Approved image digests

# Amazon EKS

Private worker nodes in two Availability Zones

Argo CD + Helm

GitOps deployment

AWS ALB Ingress

HTTPS • Route 53 • ACM

React

Frontend pods

2 replicas

FastAPI

Backend pods

2 replicas

HPA + Karpenter

Pod and node autoscaling

## Amazon RDS PostgreSQL

Private database subnets

Primary

Availability Zone A

Standby

Availability Zone B

Multi-AZ production target • Automated backups

Secrets Manager

CloudWatch

Amazon S3

Traffic flow: Users connect to the HTTPS ALB, which routes storefront traffic to React and API requests to FastAPI. The backend connects privately to RDS PostgreSQL. Jenkins builds approved images and updates GitOps configuration; Argo CD deploys those images to EKS.

# 4. Application functionality

|
Module

|

Features

|
| --- | --- |
|

Authentication

|

Registration, login, logout, customer/admin roles

|
|

Product catalog

|

Categories, search, filtering, product details

|
|

Shopping cart

|

Add, update and remove items

|
|

Checkout

|

Shipping address, inventory validation, simulated payment

|
|

Orders

|

Order creation, history and tracking

|
|

Inventory

|

Stock quantities and reservations

|
|

Admin portal

|

Product, category, inventory and order management

|
|

Dashboard

|

Orders, simulated revenue, inventory alerts

|
|

Product images

|

Upload and retrieve images from S3

|

Start with simulated payments. Do not collect real payment card data for this training project.

# 5. PostgreSQL database design

Amazon RDS PostgreSQL is the primary transactional database. It will store users, products, inventory, carts, orders and payment records.

## Core entity relationships

Users

Customer and administrator accounts

Carts

Cart items and quantities

Orders

Order items and payments

Products and categories

Catalog data, pricing and product details

Inventory

Available and reserved stock

The initial database will contain ten core tables: `users`, `addresses`, `categories`, `products`, `inventory`, `carts`, `cart_items`, `orders`, `order_items` and `payments`.

Use `NUMERIC(12,2)` for monetary amounts, foreign keys for relational integrity, unique constraints for email and product SKU, and indexes on frequently queried order and product fields. Store order-item prices at purchase time so historical orders remain accurate when catalog prices change.

For checkout, use PostgreSQL transactions and appropriate row locking to prevent overselling. Add idempotency keys to avoid duplicate orders when a customer retries a request.


# 6. Repository structure

```
shopsphere/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── auth/
│   │   ├── products/
│   │   ├── cart/
│   │   ├── orders/
│   │   └── payments/
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── infrastructure/
│   └── terraform/
│       ├── environments/
│       │   ├── dev/
│       │   ├── staging/
│       │   └── production/
│       └── modules/
│           ├── vpc/
│           ├── eks/
│           ├── rds/
│           ├── ecr/
│           └── iam/
│
├── helm/
│   └── shopsphere/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── gitops/
│   ├── staging/
│   └── production/
│
├── monitoring/
├── scripts/
├── Jenkinsfile
├── docker-compose.yml
└── README.md
```

# 7. Local development

Develop and test the complete application locally before deploying to AWS.

Use Docker Compose to run three services:

|
Container

|

Port

|

Purpose

|
| --- | --- | --- |
|

React + Nginx

|

8080

|

Storefront

|
|

FastAPI

|

8000

|

REST API

|
|

PostgreSQL

|

5432, internal only

|

Database

|

Basic commands:

Bash

```
git clone YOUR_REPOSITORY_URL
cd shopsphere

docker compose up -d --build

docker compose ps

docker compose logs -f backend
```

After implementing the application, initialize the database using Alembic and load sample products. Test customer registration, cart operations, checkout and order history.

The PostgreSQL container is intended for local development. Production uses Amazon RDS.

# 8. AWS infrastructure implementation

## Phase A: Linux and networking

Use Amazon Linux 2023 for Jenkins and EKS managed worker nodes.

Provision a VPC with two public subnets, two private application subnets and two private database subnets across two Availability Zones.

## VPC network design

VPC: 10.0.0.0/16

AZ A

Public: 10.0.0.0/24

App: 10.0.10.0/24

DB: 10.0.20.0/24

AZ B

Public: 10.0.1.0/24

App: 10.0.11.0/24

DB: 10.0.21.0/24

Illustrative CIDR allocation. Public subnets host the ALB; application and database workloads remain private.

Use security groups to restrict traffic. The ALB accepts HTTPS, the backend accepts traffic through the designated application path, and RDS accepts PostgreSQL connections only from authorized application workloads.

## Phase B: Amazon EKS

For the initial lab, create the cluster with `eksctl`:

Bash

```
eksctl create cluster \
  --name shopsphere-eks \
  --region us-east-1 \
  --nodegroup-name linux-nodes \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 4 \
  --managed
```

Configure access:

Bash

```
aws eks update-kubeconfig \
  --name shopsphere-eks \
  --region us-east-1

kubectl get nodes -o wide
kubectl get pods -A
```

This is a learning-cluster command. The production environment should use Terraform, private networking, explicit Amazon Linux 2023 node configuration, scoped cluster access and workload IAM roles.

## Phase C: Amazon RDS PostgreSQL

Provision RDS with Terraform using the following target configuration:

|
Setting

|

Configuration

|
| --- | --- |
|

Engine

|

PostgreSQL

|
|

Deployment

|

Multi-AZ for production

|
|

Connectivity

|

Private

|
|

Public access

|

Disabled

|
|

Storage

|

Encrypted gp3

|
|

Credentials

|

Secrets Manager

|
|

Backups

|

Automated with defined retention

|
|

Recovery

|

Point-in-time recovery

|
|

Deletion protection

|

Enabled in production

|
|

Monitoring

|

CloudWatch and Enhanced Monitoring

|

For a cost-controlled development environment, use Single-AZ RDS. Test Multi-AZ failover separately in a production-like environment.

The database should not be deployed as an ordinary EKS application pod.

# 9. Containerization and ECR

Create separate Docker images for the React frontend and FastAPI backend.

Use multi-stage builds for React and a minimal Python image for FastAPI. Run containers as non-root users, exclude secrets from build contexts and pin dependencies.

Create two ECR repositories:

Bash

```
aws ecr create-repository \
  --repository-name shopsphere-frontend \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true

aws ecr create-repository \
  --repository-name shopsphere-backend \
  --region us-east-1 \
  --image-scanning-configuration scanOnPush=true
```

Use immutable image tags derived from Git commits. Enable lifecycle policies to remove obsolete images while retaining known-good rollback versions.

# 10. Jenkins CI/CD and GitOps

## End-to-end release pipeline

1. GitHub

   Developer opens a pull request. Branch protection requires successful checks before merging.

2. Jenkins testing

   Run frontend unit tests, FastAPI tests and PostgreSQL integration tests.

3. Security and quality

   Run SonarQube, dependency checks and Trivy image scanning. Block releases on configured critical failures.

4. Container publishing

   Build frontend and backend images and publish them to Amazon ECR using immutable tags and recorded digests.

5. GitOps promotion

   Update the approved image digests in the staging GitOps configuration. Require approval before production promotion.

6. Argo CD

   Synchronize Helm manifests to EKS, perform rolling updates and monitor deployment health.

7. Release verification

   Run API smoke tests, verify storefront availability and monitor application metrics.

Jenkins handles continuous integration and image publication. Argo CD owns Kubernetes deployment. Avoid having Jenkins and Argo CD independently modify the same Kubernetes resources.

Use separate namespaces for staging and production, with separate configuration and appropriately isolated database environments.

# 11. Kubernetes deployment

The Helm chart should include frontend and backend Deployments, ClusterIP Services, an ALB Ingress, HPAs, PodDisruptionBudgets and workload security settings.

Recommended starting values:

|
Setting

|

Frontend

|

Backend

|
| --- | --- | --- |
|

Minimum replicas

|

2

|

2

|
|

Maximum HPA replicas

|

5

|

5

|
|

CPU request

|

100m

|

200m

|
|

Memory request

|

128 MiB

|

256 MiB

|
|

Container port

|

8080

|

8000

|
|

Health endpoint

|

`/`

|

`/health/ready`

|

Tune resource requests and limits after load testing rather than treating these starting values as production capacity requirements.

Configure readiness and liveness probes separately. Use rolling updates with `maxUnavailable: 0` where capacity permits, and spread replicas across Availability Zones.

For database migrations, use a controlled release job that runs once, not a migration command in every backend pod.


# 12. Monitoring, security and recovery

Monitoring

CloudWatch collects infrastructure and application logs. Prometheus monitors Kubernetes and application metrics. Grafana visualizes latency, errors, pod health, CPU, memory and database performance.

Security

Use least-privilege IAM, EKS Pod Identity or IRSA, Secrets Manager, encrypted storage, HTTPS, non-root containers, Kubernetes RBAC and vulnerability scanning.

Recovery

Test application rollback, RDS restoration, node failure, unhealthy pods and database connection failures. Document recovery procedures and their measured duration.

Autoscaling

Use HPA for application pods and Karpenter for node capacity. Test realistic traffic increases with a load-testing tool such as k6.

# 13. Interview demonstration scenarios

These scenarios turn the project into a practical portfolio demonstration.

|
Scenario

|

Demonstration

|
| --- | --- |
|

Black Friday sale

|

Generate traffic and observe HPA and Karpenter

|
|

Failed deployment

|

Diagnose failed readiness checks and restore the previous release

|
|

Inventory race condition

|

Run concurrent checkout requests and verify stock consistency

|
|

Database outage

|

Inspect backend logs, database connections and recovery

|
|

Vulnerable image

|

Show Trivy blocking an unsafe build

|
|

Node failure

|

Verify workload rescheduling across nodes

|
|

Expired or invalid secret

|

Diagnose authentication and connectivity errors

|
|

Infrastructure drift

|

Detect unauthorized configuration changes with Terraform

|
|

Failed asynchronous order

|

Demonstrate SQS retries and a dead-letter queue in the advanced phase

|
|

Slow application

|

Trace latency through the ALB, backend and database

|

For each scenario, save screenshots, relevant commands, logs, root-cause findings and recovery evidence. These provide concrete material for explaining your engineering decisions in interviews.

# 14. Implementation schedule

## 60-hour project plan

|
Phase

|

Deliverable

|

Hours

|
| --- | --- | --- |
|

1

|

React storefront and FastAPI API

|

12

|
|

2

|

PostgreSQL schema, authentication and checkout

|

8

|
|

3

|

Docker and local integration testing

|

5

|
|

4

|

Terraform, VPC, EKS, RDS and ECR

|

10

|
|

5

|

Jenkins, SonarQube and Trivy

|

6

|
|

6

|

Helm, Argo CD and HTTPS

|

6

|
|

7

|

Autoscaling, monitoring and recovery

|

8

|
|

8

|

Load testing and documentation

|

5

|

Estimated total: 60 hours. The complete application and production hardening may require additional time.

# 15. Final deliverables

## Project completion tracker

0/16

Responsive React storefront and admin dashboard

FastAPI backend with authenticated REST APIs

PostgreSQL schema and Alembic migrations

Working local Docker Compose environment

Frontend and backend Docker images

Terraform infrastructure for VPC, EKS and RDS

ECR repositories and secure image publishing

Jenkins CI pipeline with automated tests

SonarQube and Trivy quality gates

Helm chart and Argo CD GitOps deployment

HTTPS ingress and DNS configuration

HPA and Karpenter scaling demonstration

CloudWatch and Grafana dashboards

RDS backup and recovery demonstration

Load testing and incident runbooks

GitHub README, architecture and demonstration evidence

Reset tracker

Implementation priority: Complete the application and PostgreSQL integration locally first. Next, deploy it to EKS with RDS, automate delivery through Jenkins and Argo CD, and finally add monitoring, scaling and recovery exercises.

This document defines the complete project scope and architecture. The source code, full Terraform modules, Helm chart and end-to-end tests remain implementation deliverables, rather than completed or validated artifacts.
