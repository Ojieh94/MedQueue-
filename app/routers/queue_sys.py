from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Appointment
from sqlalchemy import asc

router = APIRouter(
    tags=['Appointment Queue']
)


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        """ Accept WebSocket connection only if not already accepted """
        if websocket not in self.active_connections:
            await websocket.accept()  
            self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """ Remove disconnected WebSocket """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """ Send a message to all connected clients """
        for connection in self.active_connections:
            await connection.send_json(message) 



manager = ConnectionManager()



@router.websocket("/ws/queue")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        # Send the initial queue when the user connects
        await send_initial_queue(websocket, db)

        while True:
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


async def notify_queue_update(db: Session):
    """ Sends the updated queue to all WebSocket clients. """
    queue = db.query(Appointment).order_by(
        asc(Appointment.scheduled_time)).all()

    queue_data = [{
        "id": appt.id,
        "patient": appt.patient_id,
        "time": appt.scheduled_time.isoformat(),
        "status": appt.status.value
    } for appt in queue]

    await manager.broadcast({"type": "queue_update", "data": queue_data})


async def send_initial_queue(websocket: WebSocket, db: Session):
    """ Sends the current queue to a newly connected WebSocket client. """
    queue = db.query(Appointment).order_by(
        asc(Appointment.scheduled_time)).all()

    queue_data = [{
        "id": appt.id,
        "patient": appt.patient.user.first_name + " " + appt.patient.user.last_name,
        "time": appt.scheduled_time.isoformat(),
        "status": appt.status.value
    } for appt in queue]

    await websocket.send_json({"type": "queue_update", "data": queue_data})
