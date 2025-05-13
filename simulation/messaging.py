import aio_pika
import json
from simulation.city import Vehicle
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)

class MigrationPublisher:
    def __init__(
        self,
        amqp_url: str = "amqp://guest:guest@localhost/",
        exchange_name: str = "migration"
    ):
        self.amqp_url = amqp_url
        self.exchange_name = exchange_name
        self.connection = None
        self.channel = None
        self.exchange = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0),  # sin espera para tests rápidos
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def connect(self):
        # Se reintentará hasta 3 veces ante cualquier excepción
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.FANOUT
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def publish(self, vehicle: Vehicle, from_zone: str, to_zone: str):
        message = {
            "vehicle_id": vehicle.id,
            "position": vehicle.posicion,
            "from_zone": from_zone,
            "to_zone": to_zone,
        }
        body = json.dumps(message).encode()
        # Si la publicación falla, tenacity reintentará
        await self.exchange.publish(
            aio_pika.Message(body=body),
            routing_key=""
        )

    async def close(self):
        if self.connection:
            await self.connection.close()


class MigrationConsumer:
    def __init__(
        self,
        amqp_url: str = "amqp://guest:guest@localhost/",
        queue_name: str = "migration_queue",
        exchange_name: str = "migration"
    ):
        self.amqp_url = amqp_url
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            self.exchange_name,
            aio_pika.ExchangeType.FANOUT
        )
        self.queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True
        )
        await self.queue.bind(self.exchange)

    async def consume(self, callback):
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    data = json.loads(message.body.decode())
                    await callback(data)

    async def close(self):
        if self.connection:
            await self.connection.close()
