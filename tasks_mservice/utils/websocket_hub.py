from typing import Annotated, Dict, List, Literal, Optional, Union

from fastapi import WebSocket
from pydantic import BaseModel, Field

"""
Models for stability and security
"""


class PageCreate(BaseModel):
    operation: Literal["create"]
    category: str
    content: dict


class PageEdit(BaseModel):
    operation: Literal["edit"]
    category: str
    content: dict


class PageMove(BaseModel):
    operation: Literal["move"]
    category: str
    content: dict


class PageDelete(BaseModel):
    operation: Literal["delete"]
    category: str
    content: Optional[dict] = None


PageOperation = Annotated[
    Union[PageMove, PageCreate, PageEdit, PageDelete], Field(discriminator="operation")
]

"""
Websockets Hub class for websockets rooms realisation
"""


class WSHub:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect_to_room(self, room: str, websocket: WebSocket):
        """
        Method that adds websocket connection to room (it will be created if not exist yet)
        """
        await websocket.accept()  # Handshake

        if room not in self.active_connections:
            self.active_connections[room] = []

        self.active_connections[room].append(websocket)

    def disconnect_from_room(self, room: str, websocket: WebSocket):
        """
        Method that deletes websocket connection from room and deletes room if it is empty
        """
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                self.active_connections.pop(room)

    async def broadcast(self, room: str, message: PageOperation):
        """
        Method that sends message to all the connections in room
        """

        if room in self.active_connections:
            for ws in self.active_connections[room]:
                await ws.send_json(message)
