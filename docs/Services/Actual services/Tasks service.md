# Tasks Service
'Tasks' service is provided for managing operations with projects, pages, boards and tasks. Also contains `WebSocket` logic for reactivity
## Dependencies:
```
fastapi[standard]==0.116.1
pymongo==4.14.1
python-dotenv==1.1.1
pydantic==2.11.7
pydantic-settings==2.10.1
python-jose==3.5.0
google-genai==1.46.0
motor==3.7.1
```

## Structure (may be changed)
For structure has been chosen 3 layer logic:
- Repository level - provides communication with database (CRUD)
- Service level - provides main business logic
- API level - provides communication with front-end 
```
├── api
│   ├── dependencies.py
│   ├── __init__.py
│   ├── routers
│   │   ├── boards.py
│   │   ├── __init__.py
│   │   ├── pages.py
│   │   ├── projects.py
│   │   └── tasks.py
│   └── schemas.py
├── config.py
├── db
│   ├── database.py
│   ├── __init__.py
│   ├── models.py
│   └── repositories.py
├── Dockerfile
├── main.py
├── requirements.txt
├── services
│   ├── board_service.py
│   ├── exceptions.py
│   ├── __init__.py
│   ├── page_service.py
│   ├── project_service.py
│   └── task_service.py
├── tree.txt
└── utils
    ├── ai_processing.py
    ├── check_access.py
    ├── __init__.py
    └── websocket_hub.py
```
# Important schemes

^6c3a97

This schemes is going to be used in requests and responses
## Collaborator scheme. Further - [Collaborator]
```json
    {
      "user_id": int,
      "role": str,
      "salary": int
    }
```

## CustomField scheme. Further - [CustomField]
```json
// Deadline
{
type: "deadline_date",
date: str,
is_expired: bool
}

// Checkbox 
{
type: "checkbox",
checked: bool,
text: str
}
  
// Text
{
type: "text",
text: str
}
  
// Dropdown
{
type: "dropdown",
elements: List[str],
index_of_selected: int
}
```

# Routers
This service has 4 routers with endpoints
With `NGINX` this service is on `localhost:1313/lirililarila`, e.g. if we want to make [POST] request to some endpoint on project router we must make this via `localhost:1313/lirililarila/projects/<endpoint>`
## Projects
### [POST] `/create_project`
An endpoint which creates new project
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
```
#### Request body
```json
{
  "admin_id": int, // from `[GET] localhost:1313/auth/get_current_user`
  "name": str,
  "description": str,
  "collaborators": [Collaborator] or []
}
```
#### Returns
Successful response `CODE 200`
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
### [GET] `/get_project/{project_id}`
An endpoint which returns project using `project_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
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
### [GET] `/my_projects`
Gets a list of project where user is an owner or a collaborator
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
[
	{
	  "_id": str, // id of the project
	  "admin_id": int,
	  "name": str,
	  "description": str,
	  "collaborators": [Collaborator] or [],
	  "cost": int,
	  "page_ids": [str]
	}
]
```
### [PUT] `/edit_project`
An endpoint for editing project using its id
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id as query param
```
#### Request body
```json
{
// All fields are optional e.g. can be only name, name and description etc. But not empty
  "name": str,
  "description": str,
  "collaborators": [Collaborator]
}
```
#### Returns
Successful response `CODE 200`
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
### [DELETE] `/delete_project/{project_id}`
An endpoint which deletes project using `project_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
"deleted_project": str, //project_id
"deleted_pages": int,
"deleted_boards": int,
"deleted_tasks": int,
}
```
### [GET] `/get_cost_evaluation/{project_id}`
An endpoint which returns project cost using `project_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
  "project_id": str,
  "project_name": str,
  "overall": int,
  "per_page": [
    {
      "page_id": str,
      "name": str,
      "overall": int,
      "per_board": [
        {
          "board_id": str,
          "name": str,
          "overall": int,
          "per_task": [
            {
              "task_id": str,
              "name": str,
              "total_cost": int,
              "cost_breakdown": [
                {
                  "usr_id": int,
                  "hourly_rate": int,
                  "hours_worked": int,
                  "total_pay": int
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```
### [GET] `/get_ai_evaluation/{project_id}`
An endpoint which returns project AI priority evaluation and recomendations using `project_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
  "prioritized_tasks": [
    {
      "task_id": "string",
      "priority": "low"
    }
  ],
  "recommendations": [
    "string"
  ]
}
```
### [WS] `/ws/{project_id}?token=<token>`
`WebSocket` for receiving updates
#### To connect
```
ws://localhost:1313/lirililarila/projects/ws/{project_id}?token=<token>
```
#### Message
```json
{
"category": ["boards", "pages", "tasks"],
"content": dict,  
"operation": ['create', 'edit', 'move', "delete"],
}
```
##### Explanation of content
- If `operation` is "delete", returns an id of deleted category, example: `{"id": page_id}`
- If `operation` is "create", of "edit" returns full object of category, example:
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
- If `operation` is "move", returns an details of moving, example:
```json
{
  "taskId": "string",
  "boardGiverId": "string",
  "boardReceiverId": "string"
}
```
## Pages
### [POST] `/create_page`
An endpoint which creates new page in project
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
project_id in query param
```
#### Request body
```json
{
  "name": str,
  "description": str
}
```
#### Returns
Successful response `CODE 200`
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
### [DELETE] `/delete_page/{page_id}`
An endpoint which deletes page using `page_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
page_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
"deleted_page":str, // page_id
"deleted_boards": int,
"deleted_tasks": int,
}
```
### [GET] `/get_page/{page_id}`
An endpoint which returns page using `page_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
page_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
  "_id": str,
  "project_id": str,
  "name": str,
  "description": str,
  "cost": 0,
  "board_ids": [str]
}
```
### [PUT] `/edit_page`
An endpoint for editing project using its id
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
page_id as query param
```
#### Request body
```json
{
// All fields are optional e.g. can be only name, name and description etc. But not empty
  "name": "string",
  "description": "string"
}
```
#### Returns
Successful response `CODE 200`
```json
{
  "_id": str,
  "project_id": str,
  "name": str,
  "description": str,
  "cost": 0,
  "board_ids": [str]
}
```
## Boards
### [POST] `/create_board`
An endpoint which creates new board on page
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
page_id in query param
```
#### Request body
```json
{
  "name": str,
  "description": str
}
```
#### Returns
Successful response `CODE 200`
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
### [GET] `/get_board/{board_id}`
An endpoint which returns board using `board_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
board_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
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
### [PUT] `/edit_board`
An endpoint for editing board using its id
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
board_id as query param
```
#### Request body
```json
{
// All fields are optional e.g. can be only name, name and description etc. But not empty
  "name": "string",
  "description": "string"
}
```
#### Returns
Successful response `CODE 200`
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
### [DELETE] `/delete_board/{board_id}`
An endpoint which deletes board using `board_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
board_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
"deleted_board": str, // board_id
"deleted_tasks": int
}
```
## Tasks
### [POST] `/create_task`
An endpoint which creates new task on board
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
board_id in query param
```
#### Request body
```json
{
  "name": str,
  "description": str,
  "priority": ["None", "low", "medium", "high"], // one of these
  "status": ["complete", "in progress", "not done"], // one of these
  "tags": [str],
  "collaborators": [Collaborator],
  "custom_fields": [CustomField]
}
```
#### Returns
Successful response `CODE 200`
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

### [DELETE] `/delete_task/{task_id}`
An endpoint which deletes task using `task_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
task_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
```json
{
"deleted_task": str, // task_id
}
```
### [PUT] `/move_task`
An endpoint for moving task between boards
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
```
#### Request body
```json
{
  "taskId": str,
  "boardGiverId": str,
  "boardReceiverId": str
}
```
#### Returns
Successful response `CODE 200`
```json
{
"status": "success"
}
```
### [GET] `/get_task/{task_id}`
An endpoint which returns task using `task_id`
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
task_id in path
```
#### Request body
```
None
```
#### Returns
Successful response `CODE 200`
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
### [PUT] `/edit_task`
An endpoint for editing task using its id
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
task_id as query param
```
#### Request body
```json
{
// All fields are optional e.g. can be only name, name and description etc. But not empty
  "name": str,
  "description": str,
  "priority": ["None", "low", "medium", "high"], // one of these
  "status": ["complete", "in progress", "not done"], // one of these
  "tags": [str],
  "collaborators": [Collaborator],
  "custom_fields": [CustomField]
}
```
#### Returns
Successful response `CODE 200`
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