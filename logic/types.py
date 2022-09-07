import typing


class Notifier(typing.Protocol):
    async def send_json(self, data: typing.Dict):
        pass
