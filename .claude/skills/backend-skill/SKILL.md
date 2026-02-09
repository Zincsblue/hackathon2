---
name: backend-skill
description: Generate API routes, handle requests/responses, and connect to databases. Use for building RESTful endpoints.
---

# Backend API Development

## Instructions

1. **Route Definition**
   - Define clear endpoint paths
   - Use correct HTTP methods (GET, POST, PUT, DELETE)
   - Implement dependency injection

2. **Request Handling**
   - Validate incoming data with schemas (Pydantic)
   - Handle query and path parameters
   - Return standardized JSON responses

3. **Database Integration**
   - Manage database sessions
   - Execute CRUD operations securely
   - Handle transaction scopes

## Best Practices
- Use async/await for non-blocking I/O
- Return proper HTTP status codes (200, 201, 404, 500)
- Keep business logic separate from routes
- Validate all inputs strictly

## Example Structure
```python
@router.post("/items/", status_code=201)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    await db.commit()
    return db_item