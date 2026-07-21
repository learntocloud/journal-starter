# Journal API

## Overview

This repository documents my work extending the **Journal Starter API** from the **Learn to Cloud** repository.

Rather than building a new application from scratch, I worked within an existing FastAPI backend, implementing new functionality while following a software development workflow. The project involved understanding an established codebase, extending existing components, maintaining automated tests, and ensuring code quality throughout development.

The result is a journal API that supports CRUD operations, request validation, structured logging, automated testing, and AI-powered journal analysis.

---

## Project Goals

The primary goal of this project was to gain practical experience contributing to an existing software project rather than creating a greenfield application.

In many software engineering roles, developers spend far more time understanding and extending existing systems than writing entirely new ones. This project provided experience reading unfamiliar code, understanding design decisions, implementing new functionality without breaking existing behavior, and following a structured Git workflow similar to what would be used on a development team.

---

## Features

### CRUD Operations

The API allows users to create, retrieve, update, and delete journal entries stored in PostgreSQL using SQLAlchemy.

### Request Validation

Incoming requests are validated using Pydantic models before reaching the application logic.

Validation ensures:

- Required fields are present
- Journal entries are automatically stripped of surrounding whitespace
- Empty submissions are rejected
- Input length is limited to prevent invalid data from reaching the database

### Application Logging

Python's built-in logging framework records application events and errors instead of relying on `print()` statements.

Logging provides better visibility into application behavior, making debugging significantly easier.

### AI-Powered Journal Analysis

Journal entries can be analyzed using a Large Language Model through the OpenAI Python SDK using an OpenAI-compatible provider.

The API generates structured insights including:

- Sentiment analysis
- Concise summaries

Responses are validated before being returned to the client.

### Automated Testing

The project includes automated tests using **pytest**.

External AI services are mocked during testing, allowing tests to run quickly, consistently, and without making real API calls.

### Static Analysis

Code quality is maintained using:

- Ruff for linting and formatting
- Pyright for static type checking

---

## Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- OpenAI Python SDK
- pytest
- Ruff
- Pyright
- Git
- GitHub Actions

---

## Development Workflow

Every feature was developed using a feature-branch workflow to simulate a professional software development process.

```text
Create Feature Branch
        │
        ▼
Implement Feature
        │
        ▼
Run pytest
        │
        ▼
Run Ruff
        │
        ▼
Run Pyright
        │
        ▼
Commit Changes
        │
        ▼
Push Branch
        │
        ▼
Create Pull Request
        │
        ▼
     Merge
```

---

## My Contributions

This project began from the **Learn to Cloud Journal Starter** repository. My work focused on extending the existing application while following a production-style development workflow.

### Logging Setup

- Configured Python's built-in logging framework
- Replaced print-based debugging with structured application logging
- Improved application observability and troubleshooting

### GET Single Entry Endpoint

- Implemented retrieval of individual journal entries by ID
- Added appropriate error handling for non-existent entries
- Returned proper HTTP status codes

### DELETE Single Entry Endpoint

- Implemented an endpoint to delete individual journal entries
- Returned appropriate HTTP responses for successful and unsuccessful operations
- Ensured database records were properly removed

### Input Validation

- Introduced reusable Pydantic validation models
- Implemented shared string constraints using `Annotated`
- Added automatic whitespace stripping
- Prevented empty submissions
- Added maximum input length validation
- Created separate request models for create and update operations

### AI-Powered Journal Analysis

- Integrated the OpenAI Python SDK using an OpenAI-compatible provider
- Implemented asynchronous journal analysis
- Generated structured summaries and sentiment analysis
- Returned validated JSON responses
- Used dependency injection to improve testability
- Implemented mocked AI clients for automated testing

### Testing & Code Quality

- Expanded automated test coverage
- Used pytest for feature validation
- Mocked external AI services during testing
- Maintained code quality using Ruff and Pyright
- Verified all features before creating pull requests

---

## What I Learned

One of the biggest lessons from this project was realizing that working within an existing codebase is very different from building a project from scratch.

I learned that adding a new feature isn't just about writing code. It first requires understanding how the application is structured, why certain design decisions were made, how the existing components work together, and how to introduce new functionality without breaking what's already there.

This experience also showed me the importance of writing code that's easy to read and maintain. While shorter code isn't always better, clear variable names, consistent organization and helpful comments make it much easier for other developers and even your future self to understand and build on your work.

Through this project I gained practical experience with:

- Extending an existing production-style codebase
- Building REST APIs with FastAPI
- Working with PostgreSQL through SQLAlchemy
- Request validation using Pydantic
- Dependency injection
- Automated testing with pytest
- Mocking external services
- Static type checking with Pyright
- Linting and formatting with Ruff
- Integrating Large Language Models using the OpenAI Python SDK
- Following a professional Git workflow using feature branches and pull requests
- Debugging and maintaining an unfamiliar codebase

---

## Architecture

The diagram below illustrates the high-level architecture of the application.

```text
                Client
                   │
                   ▼
             FastAPI API
          ┌────────┴────────┐
          ▼                 ▼
   SQLAlchemy ORM     OpenAI Python SDK
          │                 │
          ▼                 ▼
    PostgreSQL      AI Journal Analysis
```
