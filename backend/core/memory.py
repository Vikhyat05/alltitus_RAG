from .prompt import prompt as SYSTEM_PROMPT


class Memory:
    def __init__(self):
        self.sessions = {}  # In-memory storage for chat histories

    def initialize_session(self, session_id: str):
        print(f"Got the System Prompt-----------")
        self.sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    def get_chat_history(self, session_id: str):
        return self.sessions.get(session_id, [])

    def update_chat_history(self, session_id: str, message: dict):
        if session_id in self.sessions:
            self.sessions[session_id].append(message)
        else:
            self.initialize_session(session_id)
            self.sessions[session_id].append(message)

    def clear_session(self, session_id: str):
        # Remove the chat history from memory once the session is complete
        if session_id in self.sessions:
            del self.sessions[session_id]


memory = Memory()
