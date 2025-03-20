# Topic 5: Capstone

Now that you've got some Python skills, we've got an old codebase that needs some love! You will be deploying this to the cloud in the next phase, so completing this capstone is a requirement.

By the end of this capstone your API should be working locally.

## Capstone Goals

Create a complete Journal API solution that allows users to:

- Store journal entries
- Retrieve journal entries
- Delete journal entries
- Implement proper validation and error handling

## Development Tasks

### API Implementation

1. Implement missing endpoints in `journal_router.py`:
   - GET /entries - List all journal entries
   - GET /entries/{entry_id} - Get single entry
   - DELETE /entries/{entry_id} - Delete specific entry

### Logging Setup

1. Set up basic console logging in `main.py`:
   - Configure basic logging
   - Set logging level to INFO
   - Add console handler

### Data Model Improvements

1. Enhance the Entry model in `models/entry.py`:
   - Add basic field validation rules
   - Add input data sanitization
   - Add schema version tracking

### Development Environment

1. Configure cloud provider CLI in `.devcontainer/devcontainer.json`:
   - Choose and add one cloud CLI tool (Azure, AWS, or GCloud)
   - Test CLI tool installation and authentication

## Technical Implementation

### Data Schema

The journal entry data model is structured as follows:

| Field       | Type      | Description                                | Validation                   |
|-------------|-----------|--------------------------------------------|------------------------------|
| id          | string    | Unique identifier for the entry (UUID)     | Auto-generated UUID          |
| work        | string    | What did you work on today?                | Required, max 256 characters |
| struggle    | string    | What's one thing you struggled with today? | Required, max 256 characters |
| intention   | string    | What will you study/work on tomorrow?      | Required, max 256 characters |
| created_at  | datetime  | Timestamp when the entry was created       | Auto-generated UTC timestamp |
| updated_at  | datetime  | Timestamp when the entry was last updated  | Auto-updated UTC timestamp   |

All text fields require sanitization to prevent injection attacks and ensure data quality. The schema includes version tracking to handle potential future changes to the data structure.

### API Endpoints

1. **GetEntries:** Returns a JSON list of all journal entries - NEEDS IMPLEMENTATION
2. **GetEntry:** Returns a specific journal entry by ID - NEEDS IMPLEMENTATION
3. **DeleteEntry:** Removes a specific journal entry - NEEDS IMPLEMENTATION
4. **CreateEntry:** Creates a new journal entry - IMPLEMENTED
5. **UpdateEntry:** Updates an existing journal entry - IMPLEMENTED
6. **DeleteAllEntries:** Removes all journal entries - IMPLEMENTED

## Skills to Master

### Programming

- **Variables**: Understand how to declare and use variables.
- **Data Types**: Familiarize yourself with different data types (e.g., strings, integers, lists, dictionaries).
- **Comments**: Learn to write comments to document your code.
- **Functions**: Learn to define and call functions.
- **Object-Oriented Programming (OOP)**: Understand the basics of OOP (classes, objects, inheritance).
- **Lists**: Learn how to create and manipulate lists.
- **Modules**: Understand how to use and import modules.
- **Dictionaries**: Learn to use dictionaries for key-value data storage.
- **Loops**: Master loops (for, while) to iterate over data.
- **Control Statements**: Understand conditional statements (if, else, elif).
- **Exceptions**: Learn to handle exceptions and errors in your code.

### Git

- **Create a Git Repo Locally**: Initialize a repository and add files.
- **Create a GitHub Repo and Clone It Locally**: Understand the process of creating a remote repository and cloning it.
- **Create a Git Branch**: Learn to work with branches.
- **Add Changes to a Git Branch**: Stage and commit changes.
- **Merge Git Changes**: Merge changes from different branches.
- **Document Code with a README**: Write clear and informative README files.

## Getting Started

1. **Set up your development environment:**
   - Install Python and required dependencies
   - Configure your chosen cloud provider CLI tool
   - Set up a local PostgreSQL database for development and testing
     (You'll need to research and implement the appropriate setup for your system)
   - Configure logging and monitoring

2. **Implement core API features:**
   - Add missing API endpoints for journal entries
   - Implement proper error handling
   - Add input validation
   - Set up logging

3. **Test your implementation:**
   - Test database connectivity
   - Verify API endpoint functionality
   - Check error handling and validation
