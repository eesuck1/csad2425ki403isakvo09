import asyncio

import serial

from source.constants import PSOC_WRITE_CHARACTERISTIC, PSOC_READ_CHARACTERISTIC, PACKET_END_VALUE, PACKET_START_VALUE, \
    SEND_BUFFER_LENGTH, RECEIVE_BUFFER_LENGTH, ACK_PACKET


class Channel:
    def __init__(self, com: str) -> None:
        self._com_ = com

        self._port_ = serial.Serial(self._com_, 115200, timeout=0.005)

    def __del__(self) -> None:
        self._port_.close()

    def send_message(self, buffer: bytes, send_ack: bool = True, info: bool = False) -> None:
        packet = self.receive_message()

        if send_ack:
            while packet != ACK_PACKET:
                packet = self.receive_message()
                send_packet = PACKET_START_VALUE + buffer + PACKET_END_VALUE

                if info:
                    print(f"[INFO] Sending: {send_packet}")

                self._port_.write(send_packet)
        else:
            send_packet = PACKET_START_VALUE + buffer + PACKET_END_VALUE

            if info:
                print(f"[INFO] Sending: {send_packet}")

            self._port_.write(send_packet)

    def receive_message(self, decode: bool = False, info: bool = False) -> bytes | str:
        packet = self._port_.read(RECEIVE_BUFFER_LENGTH)[len(PACKET_START_VALUE):-len(PACKET_END_VALUE)]

        if packet and info:
            print(f"[INFO] Received: {packet}")

        return packet.decode("windows-1252") if decode else packet
