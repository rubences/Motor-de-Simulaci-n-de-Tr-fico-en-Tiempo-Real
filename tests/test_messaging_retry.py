import pytest
import aio_pika
from simulation.messaging import MigrationPublisher

# Helpers para simular una conexión válida tras errores
def make_fake_connection():
    class FakeChannel:
        async def declare_exchange(self, name, type):
            return None
    class FakeConnection:
        async def channel(self):
            return FakeChannel()
    return FakeConnection()

@pytest.mark.asyncio
async def test_connect_retries_and_succeeds(monkeypatch):
    calls = []

    async def unstable_connect(url):
        # Los dos primeros intentos fallan, en el tercero devuelve una conexión válida
        if len(calls) < 2:
            calls.append(1)
            raise Exception("AMQP down")
        calls.append(1)
        return make_fake_connection()

    # Reemplazamos aio_pika.connect_robust para simular fallo y éxito
    monkeypatch.setattr(aio_pika, "connect_robust", unstable_connect)

    pub = MigrationPublisher()
    # No debe lanzar excepción
    await pub.connect()
    # Debió reintentar 2 veces y funcionar en el 3.º intento
    assert len(calls) == 3

@pytest.mark.asyncio
async def test_publish_retries(monkeypatch):
    pub = MigrationPublisher()
    
    # DummyExchange que siempre falla
    class DummyExchange:
        def __init__(self):
            self.calls = 0
        async def publish(self, *args, **kwargs):
            self.calls += 1
            raise Exception("Publish error")

    # Inyectamos el DummyExchange en el publisher
    dummy = DummyExchange()
    pub.exchange = dummy

    # La publicación debe reintentar 3 veces y luego propagar la excepción
    with pytest.raises(Exception):
        await pub.publish(vehicle=type("V", (), {"id":"v","posicion":(0,0)})(), from_zone="a", to_zone="b")
    assert dummy.calls == 3
