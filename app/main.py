from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from app.websocket import WebSocketManager
from starlette.websockets import WebSocketDisconnect

app = FastAPI()
manager = WebSocketManager()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="connectWebSocket(event)">
            <input type="text" id="username" placeholder="Enter your username" autocomplete="off"/>
            <button>Connect</button>
        </form>
        <ul id='messages'>
        </ul>
        <form action="" onsubmit="sendMessageToServer(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <script>
            var ws;
            function connectWebSocket(event) {
                var username = document.getElementById("username").value;
                if (username) {
                    ws = new WebSocket("ws://localhost:8000/ws");
                    ws.onopen = function() {
                        ws.send(username);  // Надсилаємо нікнейм при підключенні
                    };
                    ws.onmessage = function(event) {
                        var messages = document.getElementById('messages');
                        var message = document.createElement('li');
                        var content = document.createTextNode(event.data);
                        message.appendChild(content);
                        messages.appendChild(message);
                    };
                }
                event.preventDefault();
            }

            function sendMessageToServer(event) {
                var input = document.getElementById("messageText");
                ws.send(input.value);  // Відправка повідомлення на сервер
                input.value = '';  // Очистка поля
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.send_message(websocket, message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)