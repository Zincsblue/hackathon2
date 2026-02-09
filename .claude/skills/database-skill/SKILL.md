---
name: database-skill
description: Manage database schemas, tables, and migrations. Use for designing data structures and SQL operations.
---

# Database Schema & Migration

## Instructions

1. **Schema Design**
   - Define clear entity relationships (One-to-One, One-to-Many)
   - Choose appropriate data types (UUID, JSONB, Timestamp)
   - Ensure normalization to reduce redundancy

2. **Table Management**
   - Use meaningful table and column names (snake_case)
   - Define Primary Keys and Foreign Keys explicitly
   - Set default values and constraints (NOT NULL, UNIQUE)

3. **Migrations**
   - Create versioned migration files
   - Include both Up (create) and Down (rollback) logic
   - Ensure migrations are transactional

## Best Practices
- Index columns frequently used in WHERE and JOIN clauses
- Use constraints to enforce data integrity at the database level
- Avoid `SELECT *`; fetch only necessary columns
- Plan for scalability (partitioning/sharding) early on

## Example Structure
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  settings JSONB DEFAULT '{}'
);

-- Index for faster lookups
CREATE INDEX idx_users_email ON users(email);