# Preflight Check

Use this skill to verify that the capstone project is ready for submission.

Run all checks from the repository root. Use Bash commands where possible.

> **Important:** This skill is a dry-run validation only. Do not modify, create, delete, or fix any project files. Report problems and recommend fixes without applying them.

## 1. Check Required Files

Verify that the required project files exist.

```bash
required_files=(
  "README.md"
  "Dockerfile"
)

for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    echo "PASS: $file exists"
  else
    echo "FAIL: $file is missing"
  fi
done
```

Also check for the project infrastructure directories:

```bash
for dir in terraform k8s kubernetes; do
  if [ -d "$dir" ]; then
    echo "FOUND: $dir"
  fi
done
```

Inspect the repository and identify any other files that appear required for the project.

If expected files or directories are missing, report them as issues. Do not create them.

## 2. Verify Docker Build

Attempt to build the application Docker image:

```bash
docker build -t journal-api:preflight .
```

If the build succeeds, report the Docker check as `PASS`.

If the build fails:

* Read the Docker build error.
* Identify the likely root cause.
* Report the problem.
* Recommend how it should be fixed.
* Do not modify any files.

The Docker check passes only when the image builds successfully.

## 3. Validate Terraform

Locate the Terraform configuration.

If Terraform files are in the `terraform` directory:

```bash
cd terraform
terraform init -backend=false
terraform validate
cd ..
```

If Terraform files are somewhere else, run the equivalent validation commands from that directory.

Do not apply Terraform changes or deploy infrastructure.

If Terraform configuration is expected but cannot be found, report the Terraform check as `FAIL`.

The Terraform check passes only when `terraform validate` succeeds.

## 4. Validate Kubernetes YAML

Locate all Kubernetes manifest files.

Check that each Kubernetes YAML file is valid.

If `kubectl` is available, use client-side dry-run validation:

```bash
kubectl apply --dry-run=client -f <manifest>
```

For a directory containing Kubernetes manifests:

```bash
kubectl apply --dry-run=client -f <directory>
```

If `kubectl` validation cannot run because the required Kubernetes API schema or environment is unavailable, perform YAML syntax validation with an available YAML parser instead.

Do not apply or deploy any Kubernetes resources.

If Kubernetes manifests are expected but cannot be found, report the Kubernetes check as `FAIL`.

## 5. Report Problems

If any check fails:

1. Explain which check failed.
2. Identify the likely cause.
3. Recommend the smallest appropriate fix.
4. Do not make the fix.
5. Continue running the remaining preflight checks when possible.

Do not modify any project files during the preflight check.

## 6. Final Report

At the end, provide a concise report using this format:

```text
Preflight Check

Required files:   PASS / FAIL
Docker build:      PASS / FAIL
Terraform:         PASS / FAIL
Kubernetes YAML:   PASS / FAIL

Issues found:
- ...

Recommended fixes:
- ...

Overall status: READY FOR SUBMISSION / NOT READY
```

Report the project as `READY FOR SUBMISSION` only when all required checks pass.

If any check fails, report the project as `NOT READY` and explain what needs to be addressed.

Do not make any changes to the repository.
