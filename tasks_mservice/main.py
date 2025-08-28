# import asyncio

# Temporary vars
# from entities_module.entities import Task

# async def main():
# task = await Task.from_template(
#     template={
#         "board_id": "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
#         "project_id": "a0f87369-9c36-417d-bfec-764f65332733",
#         "name": "title",
#         "description": "",
#         "collaborators": [{"usr_id": 1, "role": "loh", "salary": 0}],
#         "price": -1,
#         "priority": "high",
#         "status": "done",
#         "tags": ["tag1", "tag2", "tag3"],
#         "time_to_complete": -1,
#         "date_of_creation": "04-08-2025 16:15:56",
#         "custom_fields": [
#             {"type": "checkbox", "checked": True, "text": "slakjfalksjdf"}
#         ],
#     },
#     db=db,
# )
# await task.write_to_db()
# task = await Task.from_db("fcfb2a13-f530-4e5e-832b-ac5dd8bebad1", db)
# # await task.update(name="title", description="some_desc")
# print(task.dump_to_dict())

#     collection = db.get_collection('tasks')

#     # task = Task(template = collection.find_one({"_id": "f4ff2ec4-0790-467e-8b80-7119dd1aacc4"}))
#     task = await Task.from_db(id = "f4ff2ec4-0790-467e-8b80-7119dd1aacc4", db = db)
#     print(task.dump_to_dict())

# board = await Board.from_template(
#     template={
#         "_id": "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
#         "project_id": 1,
#         "page_id": 1,
#         "name": "board-1",
#         "description": "optional",
#         "priority": "high",
#         "date_of_creation": "04-08-2025 16:15:56",
#         "tasks": ["f4ff2ec4-0790-467e-8b80-7119dd1aacc4"],
#     },
#     db=db,
# )

# print(board.dump_to_dict())


# page = Page(template =  {
#         "_id": "da00cedd-13d1-4025-a3de-4d6d847ec0e5",
#         "project_id": 1,
#         "name": "page-1",
#         "description": "optional",
#         "date_of_creation": "04-08-2025 16:15:56",
#         "boards": [
# {"_id": "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
#         "project_id": 1,
#         "page_id": 1,
#         "name": "board-1",
#         "description": "optional",
#         "priority": "high",
#         "date_of_creation": "04-08-2025 16:15:56",
#         "tasks": [{
#         "_id":"2768aaa0-4872-4c4e-a31d-ab492c0d428f",
#         "board_id": 1,
#         "name": "title",
#         "description": "",
#         "collaborators": [{"usr_id": 1, "role": "loh", "salary": 0}],
#         "price": -1,
#         "priority":"high",
#         "status": "done",
#         "tags": ["tag1", "tag2", "tag3"],
#         "time_to_complete" : -1,
#         "date_of_creation": "04-08-2025 16:15:56",
#         "custom_fields": [{"type": "checkbox", 'checked': True, "text": "slakjfalksjdf"}]
#     }]
#     }]
#     })

# print(page.dump_to_dict())


# project = Project(template = {
#         "_id": "a0f87369-9c36-417d-bfec-764f65332733",
#         "admin_id": 13,
#         "name": "loh",
#         "description": "",
#         "collaborators": [{"usr_id": 1, "role": "loh", "salary": 0}],
#         "price": -1,
#         "date_of_creation": "04-08-2025 16:15:56",
#         "pages": [{
#         "_id": "da00cedd-13d1-4025-a3de-4d6d847ec0e5",
#         "project_id": "a0f87369-9c36-417d-bfec-764f65332733",
#         "name": "page-1",
#         "description": "optional",
#         "date_of_creation": "04-08-2025 16:15:56",
#         "boards": [{
#         "_id": "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
#         "project_id": "a0f87369-9c36-417d-bfec-764f65332733",
#         "page_id": "da00cedd-13d1-4025-a3de-4d6d847ec0e5",
#         "name": "board-1",
#         "description": "optional",
#         "priority": "high",
#         "date_of_creation": "04-08-2025 16:15:56",
#         "tasks": [{
#         "_id":"2768aaa0-4872-4c4e-a31d-ab492c0d428f",
#         "board_id": "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
#         "project_id": "a0f87369-9c36-417d-bfec-764f65332733",
#         "name": "title",
#         "description": "",
#         "collaborators": [{"usr_id": 1, "role": "loh", "salary": 0}],
#         "price": -1,
#         "priority":"high",
#         "status": "done",
#         "tags": ["tag1", "tag2", "tag3"],
#         "time_to_complete" : -1,
#         "date_of_creation": "04-08-2025 16:15:56",
#         "custom_fields": [{"type": "checkbox", 'checked': True, "text": "slakjfalksjdf"}]
# }]
#     }]
# }]
# })

# print(project.dump_to_dict())
# asyncio.run(main())
