memory_store = {}

def get_memory(conversation_id):
    if conversation_id not in memory_store:
        memory_store[conversation_id] = []
    return memory_store[conversation_id]

def add_message(conversation_id, role, content):
    if conversation_id not in memory_store:
        memory_store[conversation_id] = []
    memory_store[conversation_id].append({
        "role": role,
        "content": content
    })