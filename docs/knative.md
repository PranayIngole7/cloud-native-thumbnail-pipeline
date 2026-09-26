# Knative Serving

Knative Serving adds a request-driven serverless layer to the
Cloud-Native Thumbnail Pipeline.

It runs on Kubernetes and provides traffic management, revisions,
autoscaling, and scale-to-zero behavior for the thumbnail service.

## Architecture

``` text
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

The Knative Service manages the deployed application revision rather
than requiring the application to be exposed only through a traditional
Kubernetes Deployment/Service workflow.

## Implementation

Knative Serving was installed into the local Minikube-based Kubernetes
environment.

The thumbnail application was deployed as a Knative Service using the
existing container image.

The Knative configuration defines the application container and its
required runtime configuration, including the MinIO connection settings.

## Revisions

A Knative Service creates revisions when the service configuration or
application template changes.

Conceptually:

``` text
Knative Service
      |
      +-- Revision 1
      |
      +-- Revision 2
      |
      +-- Revision 3
```

This provides a versioned deployment model and allows traffic to be
associated with specific revisions.

## Traffic

Knative supports routing traffic between revisions.

This makes progressive rollout patterns possible without changing the
application itself.

The project used the Knative revision and traffic model to verify that
the service could be updated while retaining revision-level deployment
information.

## Autoscaling and Scale-to-Zero

Knative can scale the service based on incoming requests.

When there is no traffic, the service can scale down to zero running
application instances.

When a request arrives, Knative can activate a revision and start
application instances to serve the request.

The demonstrated lifecycle is:

``` text
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

The first request after a scale-to-zero period can take longer because
an application instance must be started before serving traffic.

This behavior was observed as part of the Knative phase and is an
expected characteristic of scale-to-zero serving.

## Why Knative?

Knative provides useful serverless capabilities while retaining
Kubernetes as the underlying platform:

- request-driven serving
- revision management
- traffic routing
- autoscaling
- scale-to-zero
- Kubernetes-native deployment

This makes it useful for workloads where keeping an application replica
running continuously is unnecessary.

## Relationship to Kubernetes

Knative does not replace Kubernetes.

The relationship is:

``` text
Kubernetes
   |
   +-- networking
   +-- scheduling
   +-- containers
   +-- storage
   |
   +-- Knative Serving
          |
          +-- revisions
          +-- traffic
          +-- autoscaling
          +-- scale-to-zero
```

## Scope

The implementation uses Knative Serving locally with Minikube.

The phase demonstrates the core request-driven serving model and its
operational behavior. It does not claim production-scale cloud
infrastructure, managed Knative, or production traffic capacity.
