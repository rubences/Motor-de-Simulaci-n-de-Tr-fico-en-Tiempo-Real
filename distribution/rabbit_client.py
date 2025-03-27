# simulacion_trafico/distribution/rabbit_client.py

import asyncio
import aio_pika
import logging

logging.basicConfig(level=logging.INFO)

async def send_message(message, queue_name="simulacion_queue"):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key=queue_name
        )
    logging.info("Mensaje enviado: %s", message)

async def receive_messages(queue_name="simulacion_queue"):
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(queue_name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    logging.info("Mensaje recibido: %s", message.body.decode())

def start_rabbitmq_messaging():
    # Ejecuta el receptor de mensajes en un bucle asyncio
    asyncio.run(receive_messages())
