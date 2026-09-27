# Knative Serving

Knative Serving adds a request-driven serving and autoscaling capability
to the Cloud-Native Thumbnail Pipeline.

It runs on top of Kubernetes and provides concepts such as revisions,
traffic management, autoscaling, and scale-to-zero.

Knative is an additional platform capability in this project. The core
thumbnail service can also run through the standard Kubernetes
Deployment and Service model.

## Architecture

```text id="8p4c3s"
Client
  |
  v
Knative Service
  |
  v
Revision
  |
  v
Thumbnail Service Container
  |
  v
MinIO
```

A Knative Service manages the desired configuration for a Knative
workload and creates revisions from changes to the service template.

## Implementation

Knative Serving was installed in the local Minikube-based Kubernetes
environment.

The thumbnail application was configured as a Knative Service using the
existing container image and the required MinIO configuration.

The Knative configuration is maintained separately under:

```text id="5h2v8a"
k8s/knative/thumbnail-service.yaml
```

This keeps the Knative serving model separate from the core Kubernetes
Deployment resources.

## Revisions

Knative creates a new revision when the revision-producing service
configuration changes.

Conceptually:

```text id="0s8jra"
Knative Service
      |
      +-- Revision 1
      |
      +-- Revision 2
      |
      +-- Revision 3
```

Revisions provide immutable versions of the deployed workload
configuration and form the basis for revision-aware traffic management.

## Traffic Management

Knative supports routing traffic between revisions.

This enables deployment patterns such as directing traffic to a
specific revision or gradually changing traffic distribution without
changing the application code.

The project used the Knative revision and traffic model to understand
revision-level deployment and routing behavior in the local environment.

This was a local demonstration rather than a production canary or
blue-green deployment.

## Autoscaling and Scale-to-Zero

Knative can adjust the number of running instances according to
incoming request traffic.

A revision can scale down to zero when there is no traffic, depending on
the configured autoscaling behavior.

When a request arrives after the workload has scaled to zero, Knative
can activate the revision and start an application instance.

The demonstrated lifecycle is:

```text id="c9a4qd"
No traffic
   |
   v
Scale to zero
   |
   | request
   v
Activation / cold start
   |
   v
Running instance
   |
   v
Request handled
   |
   v
Scale down when idle
```

## Cold Starts

Scale-to-zero introduces a cold-start trade-off.

The first request after a period with no running instances can take
longer because the application instance must be activated before the
request can be served.

Cold-start behavior was observed during the Knative phase and is an
expected characteristic of scale-to-zero serving.

## Why Knative?

Knative provides serverless-style capabilities while retaining
Kubernetes as the underlying orchestration platform:

* request-driven serving
* revision management
* traffic routing
* autoscaling
* scale-to-zero
* Kubernetes-native integration

These capabilities are useful for workloads where continuously running
application instances are not required.

## Relationship to Kubernetes

Knative does not replace Kubernetes.

Kubernetes provides the underlying orchestration platform, while Knative
adds higher-level serving and autoscaling behavior.

```text id="7y3b1w"
Kubernetes
   |
   +-- scheduling
   +-- containers
   +-- networking
   +-- storage
   |
   +-- Knative Serving
          |
          +-- revisions
          +-- traffic
          +-- autoscaling
          +-- scale-to-zero
```

## Relationship to the Core Deployment

The project maintains both deployment models for demonstration:

```text id="1n2f7m"
Standard Kubernetes
        |
        +-- Deployment
        +-- Service
        |
        v
Thumbnail Service


Knative Serving
        |
        +-- Knative Service
        +-- Revisions
        +-- Autoscaling
        |
        v
Thumbnail Service
```

The standard Kubernetes deployment remains the primary application
deployment model used by the broader project workflow.

Knative demonstrates an additional serverless-style serving model.

## Scope

The implementation uses Knative Serving locally with Minikube.

The phase demonstrates request-driven serving, revisions, traffic
management, autoscaling, scale-to-zero, and cold-start behavior in a
local environment.

It does not claim production-scale cloud infrastructure, managed
Knative, multi-node capacity, or production traffic performance.
