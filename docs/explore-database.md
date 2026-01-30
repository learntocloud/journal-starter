# Explore Your Database

Want to see your data directly in the database? You can connect to PostgreSQL using VS Code's PostgreSQL extension.

## 1. Install PostgreSQL Extension

1. **Install the PostgreSQL extension** in VS Code (search for "PostgreSQL" by Chris Kolkman)
2. **Restart VS Code** after installation

## 2. Connect to Your Database

1. **Open the PostgreSQL extension** (click the PostgreSQL icon in the sidebar)
2. **Click "Add Connection"** or the "+" button
3. **Enter these connection details**:
   - **Host name**: `postgres`
   - **User name**: `postgres`
   - **Password**: `postgres`
   - **Port**: `5432`
   - **Connection Type**: `Standard/No SSL`
   - **Database**: `career_journal`
   - **Display name**: `Journal Starter DB` (or any name you prefer)

## 3. Explore Your Data

1. **Expand your connection** in the PostgreSQL panel
2. **Left-click on "Journal Starter DB" to expand**
3. **Right-click on "career_journal"**
4. **Select "New Query"**
5. **Type this query** to see all your entries:

   ```sql
   SELECT * FROM entries;
   ```

6. **Run the query** to see all your journal data! (Ctrl/Cmd + Enter OR use the PostgreSQL command palette: Run Query)

You can now explore the database structure, see exactly how your data is stored, and run custom queries to understand PostgreSQL better.
