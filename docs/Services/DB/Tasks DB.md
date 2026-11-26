# MongoDB
All logic for rising is in `docker-compose.yml`: [docker-compose](../docker-compose.md)
# DB
This database is designed for containing all necessary collections for [Tasks service](../Actual%20services/Tasks%20service.md) to work
## Collections
This database contains 5 collections

For `Collaborator` and `CustomField` schemes look [Tasks service](../Actual%20services/Tasks%20service.md) in `Important schemes` article
### Users
Designed to contain information about which user is participating in certain project
```json
{
"_id": str, // project_id
"name": str, // project name
"users": [int], // ids of allowed users
}
```

### Projects
Designed to contain project information
```json
{
  "_id": str, // id of the project
  "admin_id": int,
  "name": str,
  "description": str,
  "collaborators": [Collaborator] or [],
  "cost": int,
  "page_ids": [str]
}
```

### Pages
Designed to contain page information
```json
{
  "_id": str,
  "project_id": str,
  "name": str,
  "description": str,
  "cost": int,
  "board_ids": [str]
}
```

### Boards
Designed to contain board information
```json
{
  "_id": str,
  "project_id": str,
  "page_id": str,
  "name": str,
  "description": str,
  "cost": int,
  "task_ids": [str]
}
```

### Tasks
Designed to contain task information
```json
{
  "_id": str,
  "project_id": str,
  "board_id": str,
  "name": str,
  "description": str,
  "collaborators": [Collaborator],
  "priority": ["None", "low", "medium", "high"], // one of these
  "status": "complete",
  "tags": [str],
  "custom_fields": [CustomField],
  "time_to_complete": None,
  "cost": 0
}
```