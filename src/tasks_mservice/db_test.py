from pymongo import MongoClient

client = MongoClient("localhost", 27017)

db = client.get_database("test")
collection = db.get_collection("tasks")

post = {
    '_id': 'f4ff2ec4-0790-467e-8b80-7119dd1aacc4',
    'board_id': "ef6c7ce2-5af5-457c-a803-9dd35f725c54",
    "project_id": "a0f87369-9c36-417d-bfec-764f65332733",
    'date_of_creation': '04-08-2025 16:15:56',
    'name': 'title',
    'description': '',
    'collaborators': [{'usr_id': 1, 'role': 'loh', 'salary': 0}], 
    'status': 'done', 
    'tags': ['tag1', 'tag2', 'tag3'], 
    'price': 10000, 
    'time_to_complete': 1.5, 
    'priority': 'high', 
    'custom_fields': [{'date': '04-08-2025 16:15:14', 'is_expired': True, 'type': 'deadline_date'}, {'checked': True, 'text': 'popa', 'type': 'checkbox'}]}

print(type(db))

post_id = collection.replace_one({"_id": "f4ff2ec4-0790-467e-8b80-7119dd1aacc4"}, post)
# print(collection.find_one({'_id': "f4ff2ec4-0790-467e-8b80-7119dd1aacc4"}))
