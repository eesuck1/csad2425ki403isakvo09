import asyncio

import bleak

from source.constants import PSOC_WRITE_CHARACTERISTIC, PSOC_READ_CHARACTERISTIC


class Channel:
    def __init__(self, device_address: str) -> None:
        self._device_address_ = device_address

        self._send_buffer_: list[bytes, ...] = []
        self._receive_buffer_: list[bytes, ...] = []

    def run(self) -> None:
        asyncio.run(self.run_communication())

    async def run_communication(self) -> None:
        async with bleak.BleakClient(self._device_address_) as client:
            print(f"Connected to {self._device_address_}")

            while True:
                if len(self._send_buffer_) > 0:
                    await client.write_gatt_char(PSOC_WRITE_CHARACTERISTIC, self._send_buffer_.pop(0), False)

                packet = await client.read_gatt_char(PSOC_READ_CHARACTERISTIC)

                if packet:
                    self._receive_buffer_.append(packet)

                await asyncio.sleep(1e-3)

                self.info()

    def set_buffer(self, buffer: bytes, no_repeat: bool) -> None:
        if no_repeat and buffer in self._send_buffer_:
            return

        self._send_buffer_.append(buffer)

    def get_buffer(self) -> bytes:
        if len(self._receive_buffer_) > 0:
            return self._receive_buffer_.pop(0)
        else:
            return b""

    def clear(self) -> None:
        self._send_buffer_.clear()
        self._receive_buffer_.clear()

    def info(self) -> None:
        print(f"[INFO] Send Buffer: {self._send_buffer_}")
        print(f"[INFO] Receive Buffer: {self._receive_buffer_}")
