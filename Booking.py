from enum import Enum
from typing import Dict, Optional


class SeatStatus(Enum):
    """Перечисление возможных статусов места на мероприятии."""
    FREE = "свободно"
    RESERVED = "забронировано"
    SOLD = "продано"


class User:
    """Представляет пользователя системы бронирования.

    Attributes:
        user_id (str): Уникальный идентификатор пользователя.
        name (str): Имя пользователя (для отображения).
    """

    def __init__(self, user_id: str, name: str):
        """Инициализирует пользователя.

        Args:
            user_id: Уникальный ID (например, из базы данных).
            name: Полное или отображаемое имя.
        """
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return f"Польз({self.user_id}, {self.name})"


class Seat:
    """Представляет одно место на мероприятии.

    Attributes:
        seat_id (str): Уникальный идентификатор места (например, 'A1').
        row (str): Обозначение ряда (например, 'A', 'B').
        number (int): Номер места в ряду.
        status (SeatStatus): Текущий статус места (свободно, забронировано, продано).
        current_user (Optional[User]): Пользователь, связанный с местом (если забронировано или куплено).
    """

    def __init__(self, seat_id: str, row: str, number: int):
        """Инициализирует место.

        Args:
            seat_id: Уникальный ID места.
            row: Буквенное обозначение ряда.
            number: Номер места в ряду.
        """
        self.seat_id = seat_id
        self.row = row
        self.number = number
        self.status = SeatStatus.FREE
        self.current_user: Optional[User] = None

    def __repr__(self):
        return f"Seat({self.seat_id}, {self.row}{self.number}, {self.status.value}, user={self.current_user})"


class EventSession:
    """Представляет одну сессию (сеанс) мероприятия с набором мест.

    Attributes:
        session_id (str): Уникальный идентификатор сессии.
        time (str): Время проведения (в любом удобном формате, например ISO 8601).
        seats (Dict[str, Seat]): Карта мест, индексированных по seat_id.
    """

    def __init__(self, session_id: str, time: str):
        """Инициализирует сессию мероприятия.

        Args:
            session_id: Уникальный ID сессии.
            time: Время проведения (например, '2026-02-01T19:00').
        """
        self.session_id = session_id
        self.time = time
        self.seats: Dict[str, Seat] = {}

    def add_seat(self, seat: Seat):
        """Добавляет место в сессию.

        Args:
            seat: Объект Seat для добавления.
        """
        self.seats[seat.seat_id] = seat

    def get_seat(self, seat_id: str) -> Optional[Seat]:
        """Возвращает место по его ID.

        Args:
            seat_id: Идентификатор места.

        Returns:
            Seat или None, если место не найдено.
        """
        return self.seats.get(seat_id)

    def __repr__(self):
        return f"EventSession({self.session_id}, {self.time}, seats={len(self.seats)})"


class BookingCommand:
    """Абстрактный интерфейс команды для операций с бронированием.

    Каждая команда должна реализовывать логику выполнения (`execute`) и отмены (`undo`).
    Все изменения состояния системы должны происходить только через эти методы.
    """

    def execute(self, session: EventSession, seat_id: str, user: User) -> bool:
        """Выполняет операцию над указанным местом в сессии от имени пользователя.

        Args:
            session: Сессия мероприятия.
            seat_id: Идентификатор места.
            user: Пользователь, инициирующий операцию.

        Returns:
            True, если операция успешна; False в противном случае.
        """
        raise NotImplementedError

    def undo(self, session: EventSession, seat_id: str, user: User) -> bool:
        """Отменяет ранее выполненную операцию.

        Args:
            session: Сессия мероприятия.
            seat_id: Идентификатор места.
            user: Пользователь, чья операция отменяется.

        Returns:
            True, если отмена успешна; False в противном случае.
        """
        raise NotImplementedError


class ReserveSeat(BookingCommand):
    """Команда для бронирования свободного места.

    Место должно быть в статусе FREE. После бронирования переходит в RESERVED,
    и к нему привязывается пользователь.
    """

    def execute(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or seat.status != SeatStatus.FREE:
            return False
        seat.status = SeatStatus.RESERVED
        seat.current_user = user
        return True

    def undo(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or seat.status != SeatStatus.RESERVED or seat.current_user != user:
            return False
        seat.status = SeatStatus.FREE
        seat.current_user = None
        return True


class CancelReservation(BookingCommand):
    """Команда для отмены существующей брони.

    Место должно быть в статусе RESERVED и принадлежать указанному пользователю.
    После отмены становится FREE.
    """

    def execute(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or seat.status != SeatStatus.RESERVED or seat.current_user != user:
            return False
        seat.status = SeatStatus.FREE
        seat.current_user = None
        return True

    def undo(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or seat.status != SeatStatus.FREE:
            return False
        seat.status = SeatStatus.RESERVED
        seat.current_user = user
        return True


class PurchaseTicket(BookingCommand):
    """Команда для подтверждения брони (оплаты) или прямой покупки места.

    Может применяться к FREE или RESERVED месту. После выполнения место переходит в SOLD.
    Привязывает место к пользователю (даже если оно было FREE).
    """

    def execute(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or (seat.status != SeatStatus.RESERVED and seat.status != SeatStatus.FREE):
            return False
        # Можно покупать как забронированное, так и свободное место
        seat.status = SeatStatus.SOLD
        seat.current_user = user
        return True

    def undo(self, session: EventSession, seat_id: str, user: User) -> bool:
        seat = session.get_seat(seat_id)
        if not seat or seat.status != SeatStatus.SOLD or seat.current_user != user:
            return False
        # Возвращаем в состояние "свободно" — можно усложнить логику, если нужно восстанавливать резерв
        seat.status = SeatStatus.FREE
        seat.current_user = None
        return True


class ChangeSeat(BookingCommand):
    """Команда для переноса брони или билета с одного места на другое.

    Ищет текущее место пользователя (RESERVED или SOLD), освобождает его,
    и переносит статус на новое свободное место.
    Сохраняет данные для корректного отката.
    """

    def __init__(self):
        self._old_seat_id: Optional[str] = None
        self._old_status: Optional[SeatStatus] = None
        self._old_user: Optional[User] = None

    def execute(self, session: EventSession, new_seat_id: str, user: User) -> bool:
        # Найдём старое место пользователя
        old_seat = None
        for seat in session.seats.values():
            if seat.current_user == user and seat.status in (SeatStatus.RESERVED, SeatStatus.SOLD):
                old_seat = seat
                break
        if not old_seat:
            return False

        new_seat = session.get_seat(new_seat_id)
        if not new_seat or new_seat.status != SeatStatus.FREE:
            return False

        # Сохраняем данные для отмены
        self._old_seat_id = old_seat.seat_id
        self._old_status = old_seat.status
        self._old_user = user

        # Меняем
        old_seat.status = SeatStatus.FREE
        old_seat.current_user = None

        new_seat.status = self._old_status
        new_seat.current_user = user
        return True

    def undo(self, session: EventSession, new_seat_id: str, user: User) -> bool:
        if self._old_seat_id is None:
            return False

        old_seat = session.get_seat(self._old_seat_id)
        new_seat = session.get_seat(new_seat_id)

        if not old_seat or not new_seat:
            return False

        # Отмена
        new_seat.status = SeatStatus.FREE
        new_seat.current_user = None

        old_seat.status = self._old_status
        old_seat.current_user = self._old_user
        return True


class BookingProcessor:
    """Центральный процессор для выполнения и отслеживания команд бронирования.

    Обеспечивает последовательность операций и хранит историю для отмены.


    Attributes:
        _history (list): Стек выполненных команд в формате (command, session_id, seat_id, user).
    """

    def __init__(self):
        self._history = []  

    def execute_command(self, command: BookingCommand, session: EventSession, seat_id: str, user: User) -> bool:
        success = command.execute(session, seat_id, user)
        if success:
            self._history.append((command, session.session_id, seat_id, user))
        return success

    def undo_last(self) -> bool:
        """Отменяет последнюю выполненную команду.

        Returns:
            True, если отмена возможна и выполнена; False — иначе.
        """
        if not self._history:
            return False
        command, session_id, seat_id, user = self._history.pop()
        success = command.undo(None, seat_id, user)
        return success

