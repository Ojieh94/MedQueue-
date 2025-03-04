from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import asc
from app.database import get_db
from app.models import Appointment
from app.utils import remaining_time

router = APIRouter(tags=['Appointment Queue'])


class ConnectionManager:
    def __init__(self):
        # Store active connections per hospital
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, hospital_id: int):
        """ Accept WebSocket connection and associate it with a hospital ID """
        await websocket.accept()
        if hospital_id not in self.active_connections:
            self.active_connections[hospital_id] = []
        self.active_connections[hospital_id].append(websocket)

    def disconnect(self, websocket: WebSocket, hospital_id: int):
        """ Remove a disconnected WebSocket """
        if hospital_id in self.active_connections:
            self.active_connections[hospital_id].remove(websocket)
            # Remove empty hospital lists
            if not self.active_connections[hospital_id]:
                del self.active_connections[hospital_id]

    async def broadcast(self, hospital_id: int, message: dict):
        """ Send a message to all clients connected to a specific hospital """
        if hospital_id in self.active_connections:
            for connection in self.active_connections[hospital_id]:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/queue/{hospital_id}")
async def websocket_endpoint(websocket: WebSocket, hospital_id: int, db: Session = Depends(get_db)):
    """ WebSocket endpoint that streams queue updates filtered by hospital """
    await manager.connect(websocket, hospital_id)

    try:
        # Send initial queue data when a client connects
        await send_initial_queue(websocket, db, hospital_id)

        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket, hospital_id)


async def notify_queue_update(db: Session, hospital_id: int):
    """ Sends updated queue only to clients connected to the specific hospital """
    queue = db.query(Appointment).filter(Appointment.hospital_id == hospital_id).order_by(
        asc(Appointment.scheduled_time)
    ).all()

    queue_data = [{
        "id": appt.id,
        "patient": appt.patient.user.first_name + " " + appt.patient.user.last_name,
        "patient_id": appt.patient_id,
        "time": appt.scheduled_time.isoformat(),
        "status": appt.status.value,
        "appointment_due": remaining_time(appt.scheduled_time)
    } for appt in queue]

    await manager.broadcast(hospital_id, {"type": "queue_update", "data": queue_data})


async def send_initial_queue(websocket: WebSocket, db: Session, hospital_id: int):
    """ Sends the current queue to a newly connected WebSocket client for a specific hospital """
    queue = db.query(Appointment).filter(Appointment.hospital_id == hospital_id).order_by(
        asc(Appointment.scheduled_time)
    ).all()

    queue_data = [{
        "id": appt.id,
        "patient": appt.patient.user.first_name + " " + appt.patient.user.last_name,
        "patient_id": appt.patient_id,
        "time": appt.scheduled_time.isoformat(),
        "status": appt.status.value,
        "appointment_due": remaining_time(appt.scheduled_time)
    } for appt in queue]

    await websocket.send_json({"type": "queue_update", "data": queue_data})
