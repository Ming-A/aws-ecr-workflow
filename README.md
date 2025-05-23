# Project: Multi-Service Web Application CI/CD Pipeline

This project showcases the design and implementation of a scalable, reusable CI/CD pipeline for a web application composed of multiple microservices. It includes provisioning AWS ECR repositories using Terraform and a GitHub Actions workflow for building, testing, containerizing, and deploying Docker images.

## 1. Project Overview

The goal is to create a CI/CD pipeline that supports build, test, containerization, and deployment workflows for microservices written in different languages (Python and Node.js in this example). This project focuses on provisioning AWS ECR and setting up the CI/CD pipeline using GitHub Actions.

## 2. Prerequisites

*   AWS Account
*   Terraform CLI
*   AWS CLI
*   Docker (for local testing)
*   Git
*   A GitHub account

## 3. Overview Diagram

![CI-CD pipeline for AWS ECR and terraform drawio](https://github.com/user-attachments/assets/e84dd2ca-afe8-4734-b358-2d9e2b8cc8e6)

## 4. Infrastructure Provisioning (AWS ECR with Terraform)

AWS Elastic Container Registry (ECR) is used to store Docker images for the microservices. Terraform is used to provision these ECR repositories as Infrastructure as Code.

[**AWS Resources for Terraform**](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) 

[**ECR (Elastic Container Registry) Refrenced Template from Hashicorp's Wiki**](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository)

### Terraform Code

- **`terraform/main.tf`**: Defines the `aws_ecr_repository` resources. It creates a list of repositories provided in `variables.tf`.
- **`terraform/variables.tf`**: Defines input variables such as `aws_region`, `ecr_repository_names`, `image_tag_mutability`, etc.
- **`terraform/outputs.tf`**: Defines outputs for the created ECR repository URLs and ARNs.
- **`terraform/providers.tf`**: Configures the AWS provider.

### Running Terraform

The ECR repositories is intended to be provisioned manually when new services requiring ECR repositories are added. Was done this way to focus more on the implementation for deployment of different languages and images within the workflow. [Automation](https://github.com/Ming-A/aws-ecr-workflow/edit/main/README.md#10-future-improvements) is a future plan.

1. Navigate to the `terraform/` directory.
2. Ensure the AWS CLI is configured with credentials that have permissions to create ECR repositories and related resources.
3. Run `terraform init` to initialize the Terraform working directory.
4. Run `terraform plan` to review the changes that will be applied.
5. Run `terraform apply` to provision the ECR repositories in AWS.

## 5. CI/CD Pipeline (GitHub Actions)

A reusable CI/CD pipeline is implemented using [GitHub Actions](https://github.com/Ming-A/aws-ecr-workflow/blob/main/.github/workflows/build-deploy-aws-ecr.yaml).

[**GitHub Actions templates refrenced from AWS**](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/build-and-push-docker-images-to-amazon-ecr-using-github-actions-and-terraform.html)

### Workflow Overview

The pipeline is designed to:
1. **Detect Changes:** Identify which microservices have been modified in a push request on the **`main`** branch.
2. **Matrix Execution:** Dynamically create parallel jobs for each changed service.
3. **Language-Specific Setup:** Set up the appropriate runtime environment (Python or Node.js).
4. **Install Dependencies:** Install application and testing dependencies.
5. **Run Unit Tests:** Execute unit tests for the specific microservice.
6. **Build Docker Image:** Build a Docker image for the microservice.
7. **Push to ECR:** Authenticate to AWS ECR securely and push the Docker image.

### Workflow Triggers

It also uses a `paths` filter within the trigger configuration and a `detect-changes` job ([`dorny/paths-filter`](https://github.com/dorny/paths-filter) action) to ensure that pipeline jobs for a specific service only run if files within that service's directory (e.g., `apps/test-python-app_1/**`) have changed.

### Key Workflow Steps (for each changed service)

1. **Checkout Code:** [`actions/checkout@v4`](https://github.com/actions/checkout)
2. **Setup Language Environment:**
    - Python: [`actions/setup-python@v5`](https://github.com/actions/setup-python)
    - Node.js: [`actions/setup-node@v4`](https://github.com/actions/setup-node)
3. **Install Dependencies:** `pip install` for Python, `npm ci` for Node.js.
4. **Run Unit Tests:** `pytest` for Python, `npm test` for Node.js.
5. **Configure AWS Credentials:** [`aws-actions/configure-aws-credentials@v4`](https://github.com/aws-actions/configure-aws-credentials) using OIDC.
6. **Login to Amazon ECR:** [`aws-actions/amazon-ecr-login@v2`](https://github.com/aws-actions/amazon-ecr-login).
7. **Build and Push Docker Image:** Standard `docker build` and `docker push` commands. Images are tagged with `latest` for pushes to the `main` branch.

### Secure AWS Authentication (OIDC)

To securely authenticate with AWS from GitHub Actions without storing long-lived credentials as secrets, OpenID Connect (OIDC) is used:
- IAM OIDC Identity Provider is configured in AWS.
- IAM Role is created with only the required policy allowing GitHub Actions to perform its tasks.
- The GitHub Actions workflow requests temporary credentials by assuming this IAM Role using [`aws-actions/configure-aws-credentials`](https://github.com/aws-actions/configure-aws-credentials).

### Handling Multiple Microservices
*(This section took quite a while for me to figure out, had to use some help from deepseek and gemini as well for better understanding.)*

The pipeline employs a [matrix strategy](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow) to handle different microservices and languages: 

1. A `detect-changes` job uses [`dorny/paths-filter`](https://github.com/dorny/paths-filter) to identify which service directories ([`apps/test-python-app_1/`](https://github.com/Ming-A/aws-ecr-workflow/tree/main/apps/test-python-app_1), [`apps/test-nodejs-app_1/`](https://github.com/Ming-A/aws-ecr-workflow/tree/main/apps/test-nodejs-app_1)) have changes.
2. The main `build-test-and-push` job uses the output of `detect-changes` to generate a `matrix` of services to build.
3. Each job in the matrix then runs the build, test, and push steps for that service, using conditional steps (`if: matrix.language == '...'`) for language-specific tasks.
    - The `matrix.include` section defines service-specific parameters like path, ECR repository name, and language runtime versions.

This approach allows for a single, reusable workflow YAML that can scale to support multiple services with different build and test requirements.

## 6. Sample Microservices

I have gotten two minimal sample microservices which are located in the `apps/` directory:

### `test-python-app_1` (Python/Flask)

- **Location:** `apps/test-python-app_1/`
- **Description:** A simple Flask web application serving a "Hello World" message.
- **Dockerfile:** Defines the image build process, using `python:3.9-slim` as a base.
- **Tests:** Includes basic unit tests using `pytest`.

### `test-nodejs-app_1` (Node.js/Express)

- **Location:** `apps/test-nodejs-app_1/`
- **Description:** A simple Express web application serving a "Hello World" message.
- **Dockerfile:** Defines the image build process, using `node:18-alpine` as a base.
- **Tests:** Includes basic unit tests using `jest` and `supertest`.

## 7. Git Branching Strategy

For this project, a simple branching strategy is assumed and implemented in the CI/CD pipeline:

- **`main` branch:**
    - Finial Production, considered stable and ready for deployment.
    - Pushes to `main` trigger CI/CD pipeline: build, test, and push to ECR with the `latest` tag.
- **`dev` branch (Concept / Not fully implemented in this simple pipeline):**
    -  While a `dev` branch was used during development for testing workflow changes, the current CI/CD pipeline primarily focuses on the `main` branch for pushing the `latest` tag. A more comprehensive strategy would involve:
        - A `develop` branch could be used for integration, pushing images with a `develop` tag or seperate dev image to ECR for staging/QA environments.

## 8. Assumptions and Limitations

- **Terraform Applied Manually:** The Terraform code for ECR provisioning is required to be run manually as a prerequisite. It is not currently automated within the GitHub Actions pipeline.
- **Deployment Not Included:** This pipeline focuses on CI (build, test, containerize) and pushing to ECR. The actual deployment of these images to a runtime environment (e.g., ECS, EKS, Docker host) is outside the scope of this project, but could be implemented in a future date.
- **Simple Tagging Strategy:** Images pushed from the `main` branch are tagged as `latest`. A better versioning strategy could be by using [semantic versioning](https://medium.com/@ushiradineth/automated-semantic-versioning-with-ci-7a331ee4e22f) based on Git tags) is a potential improvement.

## 9. Learnings and Reflections

- **Efficient Multi-Service CI/CD:** Explored and implemented a solution for handling multiple microservices within a single repository using GitHub Actions. Initially considered separate workflows per language, but adopted a more scalable approach using a [`matrix`](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow) strategy combined with [`dorny/paths-filter`](https://github.com/dorny/paths-filter). This allows for targeted builds and tests, improving efficiency by only processing services that have changed.
- **Secure AWS Authentication:** Gained practical experience with setting up and using OIDC for secure, keyless authentication between GitHub Actions and AWS, enhancing security by avoiding long-lived credentials.
- **Terraform for IaC:** Utilized Terraform for provisioning ECR, reinforcing the principles of Infrastructure as Code.

## 10. Future Improvements

- **Cloud-Based Terraform State:** Implement a remote backend for Terraform state management (e.g., AWS S3 with DynamoDB for locking) to improve collaboration and prevent state conflicts.
- **Automated Deployments:** Extend the CI/CD pipeline to include automated deployment of the containerized applications to a target environment (e.g., AWS ECS, EKS, or even a simple Docker host for testing).
- **Semantic Versioning:** Implement a proper image tagging and versioning strategy using semantic versioning (e.g., based on Git tags like `v1.0.0`), especially for production releases.

<a name="terraform-auto"></a>

- **Terraform Automation in Pipeline:** Integrate Terraform `plan` and `apply` into GitHub Actions workflow for managing infrastructure changes to reduce human errors and better efficiency/automation.
- **Enhanced CI/CD Workflow Scalability:** For scenarios with hundreds of services, explore more advanced monorepo build tools to further optimize pipeline generation and performance.
*   **More Branches CI:** Expand CI triggers for different branches (e.g., `develop`, `feature/*`) with appropriate tagging and deployment strategies for non-production environments.
