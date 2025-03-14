from enum import Enum


class Request(str, Enum):
    NICKNAME: str = "NICKNAME"
    TRY_MOVE: str = "TRY_MOVE"
    GET_LEGAL_MOVES: str = "GET_LEGAL_MOVES"
    GET_BOARD_STATE: str = "GET_BOARD_STATE"


class Response(str, Enum):
    NICKNAME: str = "NICKNAME"
    OPPONENT: str = "OPPONENT"
    START: str = "START"
    DONE_MOVE: str = "DONE_MOVE"
    OPPONENT_MOVE: str = "OPPONENT_MOVE"
    LEGAL_MOVES: str = "LEGAL_MOVES"
    BOARD_STATE: str = "BOARD_STATE"
    ERROR: str = "ERROR"
    WINNER: str = "WINNER"
    OPPONENT_LEFT: str = "OPPONENT_LEFT"
    COLOR: str = "COLOR"
