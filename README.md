
# EnBW assesment

## Overview

This project is a FastAPI application that includes automated testing and coverage reports using `pytest`. The application can be run inside a Docker container, and you can also run tests or generate test coverage reports inside the Docker environment using the provided scripts.

## Prerequisites

- Docker
- Docker Compose

## Setup

Before running the application or tests, ensure you have Docker installed on your machine.

### 1. Permissions

To run the scripts, you need to give them execution permissions. Run the following command for each script:

```bash
chmod +x run_docker_app.sh
chmod +x run_docker_coverage.sh
chmod +x run_docker_test.sh.sh
```

## Running the Application

To run the FastAPI application inside a Docker container, execute the following script:

```bash
./run_docker_app.sh
```

This will build and run the application in a Docker container.

## Running Tests

To run the tests for the application inside a Docker container, use:

```bash
./run_docker_test.sh.sh
```

This will execute the `pytest` test suite.

## Running Test Coverage

To generate a test coverage report in HTML format, run:

```bash
./run_docker_coverage.sh
```

This will run `pytest` with coverage options and save the HTML report to the `htmlcov` directory.

## Accessing the Coverage Report

After running `./run_docker_coverage.sh`, the coverage report will be available in the `htmlcov/index.html` file. Open this file in your browser to view the test coverage.

---

### Notes

- Ensure you have given the necessary execution permissions (`+x`) to the scripts before running them.
- Modify the `docker-compose.yml` and `Dockerfile` as needed for your environment.