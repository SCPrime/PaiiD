from unittest.mock import AsyncMock, MagicMock

from unittest.mock import AsyncMock, MagicMock

from app.market_data.streaming import TradierStreamingClient


def run(coro):
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def test_tradier_streaming_client_reconnects_service():
    service = MagicMock()
    service.subscribe_quotes = AsyncMock()
    service.unsubscribe_quotes = AsyncMock()
    service.stop = AsyncMock()
    service.start = AsyncMock()
    service.is_running.return_value = False
    service.register_listener = MagicMock()

    client = TradierStreamingClient(stream_service=service)

    run(client.start())
    run(client.reconnect())

    service.stop.assert_awaited()
    service.start.assert_awaited()
    service.register_listener.assert_called_once()


def test_subscription_manager_tracks_consumers():
    service = MagicMock()
    service.subscribe_quotes = AsyncMock()
    service.unsubscribe_quotes = AsyncMock()
    service.stop = AsyncMock()
    service.start = AsyncMock()
    service.is_running.return_value = True
    service.register_listener = MagicMock()

    client = TradierStreamingClient(stream_service=service)

    run(client.subscribe(["AAPL", "MSFT"], "consumer-1"))
    run(client.subscribe(["AAPL"], "consumer-2"))

    service.subscribe_quotes.assert_awaited()
    assert client.subscription_manager.active_symbols() == {"AAPL", "MSFT"}

    run(client.unsubscribe(["MSFT"], "consumer-1"))
    service.unsubscribe_quotes.assert_awaited_with(["MSFT"])

    run(client.remove_consumer("consumer-1"))
    run(client.remove_consumer("consumer-2"))
    assert client.subscription_manager.active_symbols() == set()
