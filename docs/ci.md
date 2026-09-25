# Continuous Integration

## Overview

The project uses GitHub Actions for continuous integration.

The CI workflow validates application changes through automated tests, Docker image builds, and container health validation.

## Workflow Triggers

The workflow runs for:

- Pull requests targeting `main`
- Pushes to `main`

## CI Workflow

```text
GitHub event
     │
     ├── Pull Request → main
     │
     └── Push → main
             │
             ▼
      GitHub Actions
             │
             ├── Checkout repository
             ├── Set up Python 3.10
             ├── Install dependencies
             ├── Run automated tests
             ├── Build Docker image
             ├── Tag image using Git SHA
             └── Validate container health
```

### Automated Tests

The workflow installs dependencies from:

> app/requirements.txt

and runs:

> python -m pytest -q app/tests

The application test suite currently contains 19 tests.

### Docker Build

The CI workflow builds the application image from:

> app/Dockerfile

The image is tagged using the first seven characters of GITHUB_SHA:

> thumbnail-service:<git-sha>

This provides a traceable image tag for each CI execution.

### Docker Validation

After the image is built, CI:

1. Inspects the image. 
2. Starts a test container. 
3. Waits for application startup. 
4. Checks the Docker health status. 
5. Requires the health status to be `healthy`. 
6. Stops and removes the test container.

A failed health assertion causes the CI job to fail.

### Pull Request Validation

Pull requests targeting main are validated before merging.

This was verified using Pull Request #1.

The pull request successfully executed:

> CI / ci (pull_request)

and passed.

### Push Validation

Pushes to `main` also trigger the CI workflow.

This was verified using commits pushed directly to main.

The resulting:

> CI / ci (push)

workflow completed successfully.

### Failure Handling

CI failure handling was deliberately tested by changing the expected Docker health status from:

> healthy

to:

> broken

The workflow correctly failed with exit code 1.

The validation was then restored to `healthy`, and CI passed again.

### Current Scope

The CI pipeline currently provides:

1. Python environment setup 
2. Dependency installation 
3. Automated application tests 
4. Docker image building 
5. Git **SHA** image tagging 
6. Docker runtime health validation 
7. Pull request validation 
8. Push-to-main validation

**Container registry publishing and GitOps deployment are not part of the current CI workflow.**
