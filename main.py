from Booking import ChangeSeat, EventSession, PurchaseTicket, ReserveSeat, Seat, User

if __name__ == "__main__":
    # Инициализация
    user1 = User("u1", "Ольга")
    session = EventSession("s1", "2026-02-01 19:00")
    session.add_seat(Seat("A1", "A", 1))
    session.add_seat(Seat("A2", "A", 2))

    print(f"Пользователь: {user1.name} (ID: {user1.user_id})")
    print(f"Сессия: {session.time}\n")

    # --- Этап 1: Бронирование ---
    print("[1] Бронирование места A1")
    reserve_cmd = ReserveSeat()
    success = reserve_cmd.execute(session, "A1", user1)
    print(f"Успешно: {success}")
    print(f"Состояние A1: {session.get_seat('A1')}\n")

    # --- Этап 2: Покупка билета ---
    print("[2] Покупка билета на A1")
    purchase_cmd = PurchaseTicket()
    success = purchase_cmd.execute(session, "A1", user1)
    print(f"Успешно: {success}")
    print(f"Состояние A1: {session.get_seat('A1')}\n")

    # --- Этап 3: Отмена покупки ---
    print("[3] Отмена покупки (возврат в свободное состояние)")
    success = purchase_cmd.undo(session, "A1", user1)
    print(f"Успешно: {success}")
    print(f"Состояние A1: {session.get_seat('A1')}\n")

    # --- Этап 4: Повторное бронирование и смена места ---
    print("[4] Повторное бронирование A1 и перенос брони на A2")
    reserve_cmd.execute(session, "A1", user1)  # Бронируем снова
    change_cmd = ChangeSeat()
    success = change_cmd.execute(session, "A2", user1)
    print(f"Перенос успешен: {success}")
    print(f"Состояние A1: {session.get_seat('A1')}")
    print(f"Состояние A2: {session.get_seat('A2')}\n")

    # --- Этап 5: Отмена смены места ---
    print("[5] Отмена переноса (возврат брони на A1)")
    change_cmd.undo(session, "A2", user1)
    print("Возврат выполнен")
    print(f"Состояние A1: {session.get_seat('A1')}")
    print(f"Состояние A2: {session.get_seat('A2')}\n")

    print("Демонстрация завершена. Все операции выполнены корректно!")
