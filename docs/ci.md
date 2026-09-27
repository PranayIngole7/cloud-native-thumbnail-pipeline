# Continuous Integration

## Overview

The project uses GitHub Actions for continuous integration.

The CI workflow validates application changes through automated tests,
Docker image builds, and container runtime health validation.

## Workflow Triggers

The workflow runs for:

* Pull requests targeting `main`
* Pushes to `main`

## CI Workflow

```text id="q6j2wn"
GitHub Event
     |
     +-- Pull Request → main
     |
     +-- Push → main
             |
             v
      GitHub Actions
             |
             +-- Checkout repository
             |
             +-- Set up Python 3.10
             |
             +-- Install dependencies
             |
             +-- Run automated tests
             |
             +-- Build Docker image
             |
             +-- Tag image using Git SHA
             |
             +-- Validate container health
```

## Automated Tests

The workflow installs dependencies from:

```text id="9i6h2k"
app/requirements.txt
```

and executes the application test suite with:

```bash id="c4w7lm"
python -m pytest -q app/tests
```

A test failure causes the CI workflow to fail.

## Docker Build

The CI workflow builds the application image from:

```text id="u2q0ef"
app/Dockerfile
```

The image is tagged using the first seven characters of `GITHUB_SHA`:

```text id="y6b4ra"
thumbnail-service:<git-sha>
```

This provides a traceable relationship between a CI-built image and the
Git commit that produced it.

## Docker Runtime Validation

After the image is built, CI:

1. Inspects the image.
2. Starts a test container.
3. Waits for application startup.
4. Checks the Docker health status.
5. Requires the health status to be `healthy`.
6. Stops and removes the test container.

A failed health assertion causes the CI job to fail.

This verifies not only that the image can be built, but also that the
resulting container can start successfully and report healthy runtime
status.

## Pull Request Validation

Pull requests targeting `main` execute the CI workflow before merging.

This provides automated validation of application tests, image
construction, and container health.

## Push Validation

Pushes to `main` also trigger the CI workflow.

This provides continuous validation of the repository's main branch
after changes are committed.

## Failure Handling

CI failure handling was deliberately tested by changing the expected
Docker health status from:

```text id="1m2qkv"
healthy
```

to an intentionally incorrect value:

```text id="wqg2z9"
broken
```

The workflow correctly failed with a non-zero exit status.

The validation was then restored to the expected `healthy` state and the
workflow passed again.

This demonstrated that the CI pipeline can detect a failed runtime
validation rather than only reporting successful builds.

## Current Scope

The CI pipeline currently provides:

* Python environment setup
* Dependency installation
* Automated application tests
* Docker image building
* Git SHA-based image tagging
* Docker runtime health validation
* Pull request validation
* Push-to-main validation

Container registry publishing is **not** part of the current CI
workflow.

GitOps deployment is also separate from CI. Argo CD is responsible for
reconciling the desired Kubernetes state from Git.
