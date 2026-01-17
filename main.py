# Пример работы
from Booking import ChangeSeat, EventSession, PurchaseTicket, ReserveSeat, Seat, User

if __name__ == "__main__":
    user1 = User("u1", "Ольга")
    session = EventSession("s1", "2026-02-01 19:00")

    # Добавляем места
    session.add_seat(Seat("A1", "A", 1))
    session.add_seat(Seat("A2", "A", 2))

    # Бронируем
    reserve_cmd = ReserveSeat()
    success = reserve_cmd.execute(session, "A1", user1)
    print("Бронь A1:", success)  # True
    print(session.get_seat("A1"))

    # Покупаем билет
    purchase_cmd = PurchaseTicket()
    success = purchase_cmd.execute(session, "A1", user1)
    print("Покупка A1:", success)  # True
    print(session.get_seat("A1"))

    # Отменяем покупку
    success = purchase_cmd.undo(session, "A1", user1)
    print("Отмена покупки:", success)  # True
    print(session.get_seat("A1"))  # теперь FREE

    # Бронируем снова и меняем место
    reserve_cmd.execute(session, "A1", user1)
    change_cmd = ChangeSeat()
    success = change_cmd.execute(session, "A2", user1)
    print("Изменить на A2:", success)  # True
    print("A1:", session.get_seat("A1"))
    print("A2:", session.get_seat("A2"))

    # Отменяем изменение
    change_cmd.undo(session, "A2", user1)
    print("После отмены изменений:")
    print("A1:", session.get_seat("A1"))
    print("A2:", session.get_seat("A2"))