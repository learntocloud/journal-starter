# Explore Your Database

[Home](../../README.md) · [Capstone](../01-prerequisites.md) · **Optional**

Connect to the local PostgreSQL database with a VS Code PostgreSQL extension.

## 1. Install the Extension

Install the **PostgreSQL** extension by Chris Kolkman from the VS Code
Extensions view, then restart VS Code.

## 2. Add the Connection

Open the PostgreSQL panel and add a connection with:

| Setting | Value |
|---------|-------|
| Host | `postgres` |
| User | `postgres` |
| Password | `postgres` |
| Port | `5432` |
| Connection type | Standard / No SSL |
| Database | `career_journal` |
| Display name | `Journal Starter DB` |

These values match the sample local environment. Use your configured values if
you changed them.

## 3. Query the Entries

Open a new query for `career_journal` and run:

```sql
SELECT * FROM entries;
```

Use `Ctrl/Cmd + Enter` or the extension's **Run Query** command. This view lets
you inspect the schema and see how API entries are stored.
