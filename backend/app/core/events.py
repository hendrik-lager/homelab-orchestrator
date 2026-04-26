from typing import Callable

_callbacks: list[Callable] = []

def register_event_callback(callback: Callable):
    _callbacks.append(callback)

async def emit_event(event_type: str, data: dict):
    for callback in _callbacks:
        await callback(event_type, data)
