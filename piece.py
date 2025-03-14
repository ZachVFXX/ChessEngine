from pydantic import BaseModel
from enum import Enum
import struct
from protocols import Request, Response


class Color(Enum):
    EMPTY = 0
    WHITE = 1
    BLACK = 2


class PieceType(str, Enum):
    PAWN = "p"
    KNIGHT = "n"
    BISHOP = "b"
    ROOK = "r"
    QUEEN = "q"
    KING = "k"
    EMPTY = "0"


class Piece(BaseModel):
    piece_type: PieceType
    board_index: int
    color: Color

    def __repr__(self) -> str:
        return f"{self.color.name} {self.piece_type.name}"


class move(BaseModel):
    from_: int
    to_: int


class Message(BaseModel):
    type: Request | Response
    data: str | list[Piece] | int | None | list[int] | move

    @classmethod
    def pack(cls, message):
        """Pack a message with a 4-byte length prefix."""
        json_data = message.model_dump_json().encode()
        # Pack the length as a 4-byte unsigned integer in network byte order
        length_prefix = struct.pack("!I", len(json_data))
        return length_prefix + json_data

    @classmethod
    def recv_message(cls, sock):
        """Receive a complete message from the socket."""
        # First, receive the 4-byte length prefix
        length_bytes = recv_all(sock, 4)
        if not length_bytes:
            return None
        # Unpack the length prefix
        message_length = struct.unpack("!I", length_bytes)[0]

        # Now receive the actual message data
        message_data = recv_all(sock, message_length)
        if not message_data:
            return None

        return cls.model_validate_json(message_data.decode())


def recv_all(sock, n):
    """Helper function to receive exactly n bytes or return None if EOF is hit."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
