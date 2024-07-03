import json
import os
from sse_starlette.sse import EventSourceResponse
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from common.utils import get_rabbitmq_connection
import pika
import asyncio


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")


@app.post("/query")
async def handle_query(request: Request):
    data = await request.json()
    query = data.get("query")
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='nlp_queue')
    channel.basic_publish(exchange='', routing_key='nlp_queue', body=json.dumps({"query": query}))
    connection.close()
    return JSONResponse(content={"message": "Query sent to NLP Service"})

# Update the credentials (DB)
@app.post("/credentials")
async def update_credentials(request: Request):
    data = await request.json()
    connection = get_rabbitmq_connection(RABBITMQ_HOST)
    channel = connection.channel()
    channel.queue_declare(queue='credentials_queue')
    channel.basic_publish(exchange='', routing_key='credentials_queue', body=json.dumps(data))
    connection.close()
    return JSONResponse(content={"message": "Credentials updated and metadata update requested"})


@app.get("/events")
async def handle_events(request: Request):
    async def event_generator():
        connection = get_rabbitmq_connection(RABBITMQ_HOST)
        channel = connection.channel()
        channel.queue_declare(queue='response_queue')

        while True:
            for method_frame, properties, body in channel.consume('response_queue', inactivity_timeout=1):
                if method_frame:
                    data = json.loads(body)
                    yield {
                        "event": "message",
                        "data": json.dumps(data)
                    }
                    channel.basic_ack(method_frame.delivery_tag)
                await asyncio.sleep(0.1)

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)