from config import get_async_connection
from typing import Any, Optional
import asyncio

allowed_fields = {"users": {"sex", "age", "hobby", "menu", "name", "last_message", "cur_tale", "process"},
                  "tales": {"tale_size", "cur_stage", "genre", "hero", "moral"}}

table_map = {
        3: ("tiny_tale", 3),
        8: ("small_tale", 8),
        16: ("medium_tale", 16),
        32: ("large_tale", 32),
    }

return_fail_value = "Запрос не завершен"

async def get_user_field(user_id: int, field_name: str) -> Optional[Any]:
    """
    Получает значение указанного поля из таблицы 'users' по user_id.

    :param user_id: Telegram user ID
    :param field_name: Название поля для получения
    :return: Значение поля или None, если не найдено, при ошибке return_fail_value
    :raises ValueError: Если поле не входит в список разрешённых
    """

    if field_name not in allowed_fields["users"]:
        print(f"[ERROR] Попытка запроса запрещённого поля: {field_name}")
        raise ValueError(f"Запрос поля '{field_name}' запрещён")

    sql = f"SELECT {field_name} FROM users WHERE user_id = %s;"

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value
        
        print(f"[DEBUG] Установлено соединение с базой данных")
        async with conn.cursor() as cursor:
            print(f"[DEBUG] Выполнение запроса: {sql} с user_id={user_id}")
            await cursor.execute(sql, (user_id,))
            row = await cursor.fetchone()
            result = row[0] if row else None
            print(f"[DEBUG] Получено значение: {result}")
            return result

    except Exception as e:
        print(f"[ERROR] Ошибка при получении поля '{field_name}' для user_id={user_id}: {e}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с базой данных закрыто")
            except Exception as close_error:
                print(f"[WARNING] Ошибка при закрытии соединения: {close_error}")

async def get_tales_field(tale_num: int, field_name: str) -> Optional[Any]:
    """
    Получает значение указанного поля из таблицы 'tales' по tale_num.

    :param tale_num: Уникальный номер сказки
    :param field_name: Название поля для получения
    :return: Значение поля или None, если не найдено или равно NULL, при ошибке return_fail_value
    :raises ValueError: Если поле не входит в список разрешённых
    """

    if field_name not in allowed_fields["tales"]:
        print(f"[ERROR] Попытка запроса запрещённого поля: {field_name}")
        raise ValueError(f"Запрос поля '{field_name}' запрещён")

    sql = f"SELECT {field_name} FROM tales WHERE tale_num = %s;"

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        print(f"[DEBUG] Установлено соединение с базой данных")

        async with conn.cursor() as cursor:
            print(f"[DEBUG] Выполнение запроса: {sql} с tale_num={tale_num}")
            await cursor.execute(sql, (tale_num,))
            row = await cursor.fetchone()

            result = row[0] if row else None
            print(f"[DEBUG] Получено значение: {result}")
            return result

    except Exception as e:
        print(f"[ERROR] Ошибка при получении поля '{field_name}' для tale_num={tale_num}: {e}")
        return return_fail_value

    finally:
        try:
            conn.close()
            print("[DEBUG] Соединение с базой данных закрыто")
        except Exception as close_error:
            print(f"[WARNING] Ошибка при закрытии соединения: {close_error}")

async def get_tales_num(user_id: int) -> Optional[int | str]:
    """
    Получает номер незавершённой сказки пользователя (где cur_stage < tale_size).

    :param user_id: Идентификатор пользователя
    :return: Номер незавершённой сказки, если такая существует, иначе None, при ошибке return_fail_value
    :raises TypeError: Если user_id не является целым числом
    """

    if not isinstance(user_id, int):
        raise TypeError("user_id должен быть целым числом")

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value
        
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT tale_num
                  FROM tales
                 WHERE user_id = %s
                   AND cur_stage IS NOT NULL
                   AND tale_size IS NOT NULL
                   AND cur_stage < tale_size
                 LIMIT 1
                """,
                (user_id,)
            )
            result = await cursor.fetchone()
            if result:
                print(f"[DEBUG] Найдена незавершённая сказка: tale_num = {result[0]}")
                return result[0]
            else:
                print("[DEBUG] Незавершённые сказки не найдены")
                return None
    except Exception as e:
        print(f"[ERROR] Ошибка при получении незавершённой сказки: {e}")
        return return_fail_value
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {e}")

async def get_new_tales_num(user_id: int) -> Optional[int | str]:
    """
    Завершает все предыдущие сказки пользователя и создаёт новую запись в таблице tales.
    Все поля новой записи, кроме user_id, инициализируются как NULL.
    Возвращает tale_num новой записи.

    :param user_id: Идентификатор пользователя
    :return: Номер новой сказки или return_fail_value при ошибке
    :raises TypeError: Если user_id не является целым числом
    """

    if not isinstance(user_id, int):
        print(f"[ERROR] Некорректный тип user_id: {type(user_id)}")
        raise TypeError("user_id должен быть целым числом")

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value
        
        print(f"[DEBUG] Создание новой сказки для user_id={user_id}")

        async with conn.cursor() as cursor:
            # Завершаем все предыдущие незаконченные сказки пользователя 
            await cursor.execute(
                """
                UPDATE tales
                   SET cur_stage = tale_size
                 WHERE user_id = %s
                """,
                (user_id,)
            )
            print(f"[DEBUG] Завершено {cursor.rowcount} предыдущих сказок")
            
            # Фиксируем изменения (если автокоммит отключен)
            await conn.commit()

            # Создаём новую запись со всеми полями, кроме user_id, равными NULL
            await cursor.execute(
                """
                INSERT INTO tales (user_id, tale_size, cur_stage, genre, hero, moral)
                     VALUES (%s,       %s,        %s,        %s,    %s,   %s)
                """,
                (user_id, 8, None, None, None, None)
            )
            
            # Получаем идентификатор только что созданной записи
            await cursor.execute("SELECT LAST_INSERT_ID()")
            new_id = (await cursor.fetchone())[0]
            print(f"[DEBUG] Создана новая сказка с tale_num={new_id}")

            await conn.commit()
            return new_id

    except Exception as e:
        print(f"[ERROR] Ошибка при создании сказки для user_id={user_id}: {e}")
        return return_fail_value

    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {e}")

async def get_user_context_tale(tale_num: int, tale_size: int) -> Optional[list]:
    """
    Получает контекст сказки в формате диалога (роль + содержание) для заданного tale_num.
    
    :param tale_num: Номер сказки
    :param tale_size: Размер сказки (8, 16 или 32)
    :return: Список словарей с контекстом в формате {"role": str, "content": str}
             или return_fail_value при ошибках
    """
    print(f"[DEBUG] Начало get_user_context_tale(tale_num={tale_num}, tale_size={tale_size})")

    if tale_size not in table_map:
        print(f"[ERROR] Неподдерживаемый размер сказки: {tale_size}")
        return return_fail_value

    table_name, num_pairs = table_map[tale_size]
    fields = [f"p{i}" if j % 2 == 0 else f"ans{i}" for i in range(num_pairs) for j in range(2)]
    print(f"[DEBUG] Используется таблица: {table_name}, полей: {len(fields)}")

    context = []
    conn = None
    
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name} WHERE tale_num = %s"
            print(f"[DEBUG] Выполнение запроса: {query} с tale_num={tale_num}")
            
            await cursor.execute(query, (tale_num,))
            result = await cursor.fetchone()

            if not result:
                print(f"[WARNING] Запись tale_num={tale_num} не найдена в таблице {table_name}")
                return None

            for i in range(len(fields)): # Тут enumerate -> range, тк field не использовался 
                cell = result[i + 1]  # result[0] — это tale_num
                if cell is not None:
                    role = "user" if i % 2 == 0 else "assistant"
                    context.append({"role": role, "content": cell})
                    
            print(f"[DEBUG] Получено {len(context)} элементов контекста")
            
    except Exception as e:
        print(f"[ERROR] Ошибка при получении контекста: {str(e)}")
        context = return_fail_value
        
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

    return context

async def get_parts_tale(tale_num: int, tale_size: int) -> Optional[list]:
    """
    Получает фрагменты ответов (ответы ассистента) для заданной сказки.
    
    :param tale_num: Номер сказки
    :param tale_size: Размер сказки (8, 16 или 32)
    :return: Список фрагментов ответов или return_fail_value при ошибках
    """

    print(f"[DEBUG] Начало get_parts_tale(tale_num={tale_num}, tale_size={tale_size})")

    if tale_size not in table_map:
        print(f"[ERROR] Неподдерживаемый размер сказки: {tale_size}")
        return return_fail_value

    table_name, _ = table_map[tale_size]
    print(f"[DEBUG] Используется таблица: {table_name}")

    fragments = []
    conn = None
    
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name} WHERE tale_num = %s"
            print(f"[DEBUG] Выполнение запроса: {query} с tale_num={tale_num}")
            
            await cursor.execute(query, (tale_num,))
            result = await cursor.fetchone()

            if not result:
                print(f"[WARNING] Запись tale_num={tale_num} не найдена в таблице {table_name}")
                return None

            # result[0] — это tale_num, данные начинаются с result[1]
            data_fields = result[1:]  # Пропускаем tale_num

            # Берем каждое второе поле начиная со второго (индексация с 0 → data_fields[1], data_fields[3], ...)
            fragments = [cell for i, cell in enumerate(data_fields) if i % 2 == 1 and cell is not None]
            print(f"[DEBUG] Получено {len(fragments)} фрагментов")
            
    except Exception as e:
        print(f"[ERROR] Ошибка при получении фрагментов: {str(e)}")
        fragments = return_fail_value
        
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

    return fragments

async def fetch_current_db() -> Optional[str]:
    """
    Проверяет текущее подключение к базе данных и выводит имя активной базы.
    Выводит диагностическую информацию в консоль.

    :return: None или return_fail_value
    """

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с базой данных (conn is None)")
            return return_fail_value

        async with conn.cursor() as cursor:
            await cursor.execute("SELECT DATABASE();")
            result = await cursor.fetchone()

            if result and result[0]:
                print(f"[DEBUG] Подключение к базе: {result[0]}")
            else:
                print("[WARNING] Не удалось получить имя базы данных")

    except Exception as e:
        print(f"[ERROR] Ошибка при работе с базой: {e}")
        return return_fail_value

    finally:
        if conn:
            try:
                conn.close()
            except Exception as close_error:
                print(f"[WARNING] Ошибка при закрытии соединения: {close_error}")

async def add_user(user_id: int, sex: str, age: int, hobby: str, menu: int, name: str, last_message: int, cur_tale: int = 0) -> Optional[str]:
    """
    Добавляет или обновляет данные пользователя в таблице users.
    
    :param user_id: ID пользователя
    :param sex: Пол
    :param age: Возраст
    :param hobby: Хобби
    :param menu: Текущее меню
    :param name: Имя
    :param last_message: ID последнего сообщения
    :param cur_tale: Текущая сказка (по умолчанию 0)

    :return: None или return_fail_value
    """
    print(f"[DEBUG] Начало add_user(user_id={user_id}, name={name})")
    
    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value
        
        async with conn.cursor() as cursor:
            query = """
                INSERT INTO users (user_id, sex, age, hobby, menu, name, last_message, cur_tale, process)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    sex=%s, age=%s, hobby=%s, menu=%s, name=%s, last_message=%s, cur_tale=%s, process=%s
            """
            print(f"[DEBUG] Выполнение запроса: {query}")
            
            await cursor.execute(query, (
                user_id, sex, age, hobby, menu, name, last_message, cur_tale, "no",
                sex, age, hobby, menu, name, last_message, cur_tale, "no"
            ))
            await conn.commit()
            print(f"[DEBUG] Данные пользователя {user_id} успешно добавлены или обновлены")

    except Exception as e:
        print(f"[ERROR] Ошибка при добавлении/обновлении пользователя {user_id}: {str(e)}")
        return return_fail_value

    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")


async def add_tale_if_not(tale_num: int, tale_size: int) -> Optional[str]:
    """
    Добавляет запись о сказке в соответствующую таблицу, если ее еще нет.
    
    :param tale_num: Номер сказки
    :param tale_size: Размер сказки (8, 16 или 32)
    :return: None или return_fail_value при ошибках
    """

    print(f"[DEBUG] Начало add_tale_if_not(tale_num={tale_num}, tale_size={tale_size})")

    if tale_size not in table_map:
        error_msg = f"Недопустимый размер сказки: {tale_size}. Ожидаются 8, 16 или 32."
        print(f"[ERROR] {error_msg}")
        return return_fail_value

    table_name, _ = table_map[tale_size]

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            # Проверка наличия записи
            query = f"SELECT tale_num FROM {table_name} WHERE tale_num = %s"
            print(f"[DEBUG] Выполнение запроса: {query}")
            
            await cursor.execute(query, (tale_num,))
            exists = await cursor.fetchone()

            if not exists:
                print(f"[DEBUG] Создаем запись в {table_name} для tale_num={tale_num}")
                try:
                    # Вставляем только tale_num — все остальные поля автоматически NULL
                    insert_query = f"INSERT INTO {table_name} (tale_num) VALUES (%s)"
                    print(f"[DEBUG] Выполнение запроса: {insert_query}")
                    
                    await cursor.execute(insert_query, (tale_num,))
                    await conn.commit()

                    print(f"[DEBUG] Запись с tale_num={tale_num} успешно создана в {table_name}")
                except Exception as insert_error:
                    print(f"[ERROR] Ошибка при вставке в {table_name}: {str(insert_error)}")
                    raise
            else:
                print(f"[DEBUG] Запись с tale_num={tale_num} уже существует в {table_name}")

    except Exception as e:
        print(f"[ERROR] Ошибка при работе с таблицей {table_name}: {str(e)}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def add_data_to_tale(tale_num: int, prompt: str, tale_size: int) -> Optional[str]:
    """
    Добавляет данные в первую пустую ячейку указанной сказки.
    
    :param tale_num: Номер сказки
    :param prompt: Текст для добавления
    :param tale_size: Размер сказки (8, 16 или 32)

    :return: None или return_fail_value при ошибке
    """
    print(f"[DEBUG] Начало add_data_to_tale(tale_num={tale_num}, tale_size={tale_size})")

    if tale_size not in table_map:
        error_msg = f"Недопустимый размер сказки: {tale_size}. Ожидаются 8, 16 или 32."
        print(f"[ERROR] {error_msg}")
        return return_fail_value
    
    table_name, num_pairs = table_map[tale_size]

    # Генерация всех полей p0, ans0, p1, ans1, ...
    fields = [f"p{i}" if j % 2 == 0 else f"ans{i}" for i in range(num_pairs) for j in range(2)]
    print(f"[DEBUG] Используется таблица: {table_name}, полей: {len(fields)}")

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name} WHERE tale_num = %s"
            print(f"[DEBUG] Выполнение запроса: {query}")
            
            await cursor.execute(query, (tale_num,))
            row = await cursor.fetchone()

            if not row:
                print(f"[ERROR] Запись tale_num={tale_num} не найдена в таблице {table_name}")
                return return_fail_value

           # row[0] — это tale_num, дальше идут p0, ans0, ...
            for idx, field in enumerate(fields, start=1):
                if row[idx] is None:
                    update_query = f"UPDATE {table_name} SET {field} = %s WHERE tale_num = %s"
                    print(f"[DEBUG] Выполнение запроса: {update_query}")
                    
                    await cursor.execute(update_query, (prompt, tale_num))
                    await conn.commit()
                    print(f"[DEBUG] Данные записаны в поле {field} сказки {tale_num}")
                    return None

            print(f"[DEBUG] Все поля сказки {tale_num} уже заполнены")

    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении сказки {tale_num}: {str(e)}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def update_user_field(user_id: int, field: str, value: Any) -> Optional[str]:
    """
    Обновляет указанное поле пользователя в таблице users.
    
    :param user_id: ID пользователя
    :param field: Название поля для обновления
    :param value: Новое значение поля
    :return: None при успехе или return_fail_value при ошибке
    :raises ValueError: При попытке обновления запрещённого поля
    """
    print(f"[DEBUG] Начало update_user_field(user_id={user_id}, field={field})")

    if field not in allowed_fields['users']:
        error_msg = f"Попытка обновления запрещённого поля: {field}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = f"UPDATE users SET {field} = %s WHERE user_id = %s"
            print(f"[DEBUG] Выполнение запроса: {query}")
            
            await cursor.execute(query, (value, user_id))
            await conn.commit()
            print(f"[DEBUG] Поле {field} пользователя {user_id} успешно обновлено")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении поля {field}: {str(e)}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def update_tales_field(tale_num: int, field_name: str, new_value: Any) -> Optional[str]:
    """
    Обновляет значение поля в таблице tales для указанной сказки.
    
    :param tale_num: Номер сказки
    :param field_name: Название поля для обновления
    :param new_value: Новое значение поля
    :return: None при успехе или return_fail_value при ошибке
    :raises ValueError: При попытке обновления запрещённого поля
    """
    print(f"[DEBUG] Начало update_tales_field(tale_num={tale_num}, field_name={field_name})")

    if field_name not in allowed_fields["tales"]:
        error_msg = f"Попытка обновления запрещённого поля: {field_name}"
        print(f"[ERROR] {error_msg}")
        raise ValueError(error_msg)

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = f"UPDATE tales SET {field_name} = %s WHERE tale_num = %s"
            print(f"[DEBUG] Выполнение запроса: {query}")
            
            await cursor.execute(query, (new_value, tale_num))
            await conn.commit()
            
            if cursor.rowcount == 0:
                print(f"[WARNING] Запись tale_num={tale_num} не найдена")
                return None
            
            print(f"[DEBUG] Поле {field_name} сказки {tale_num} успешно обновлено")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении поля {field_name}: {str(e)}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def user_exists(user_id: int) -> bool | str:
    """
    Проверяет существование пользователя в базе данных.
    
    :param user_id: ID пользователя для проверки
    :return: True если пользователь существует, False если нет, при ошибке return_fail_value
    """
    print(f"[DEBUG] Проверка существования пользователя {user_id}")
    
    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = "SELECT 1 FROM users WHERE user_id = %s LIMIT 1"
            print(f"[DEBUG] Выполнение запроса: {query} с user_id={user_id}")
            
            await cursor.execute(query, (user_id,))
            result = await cursor.fetchone()
            
            exists = result is not None
            print(f"[DEBUG] Пользователь {user_id} {'существует' if exists else 'не существует'}")
            return exists

    except Exception as e:
        print(f"[ERROR] Ошибка при проверке пользователя {user_id}: {str(e)}")
        return return_fail_value
        
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def check_all_users() -> None | str:
    """
    Выводит в консоль информацию о всех пользователях из базы данных.
    Используется только для отладки и администрирования.
    :return: None или return_fail_value при ошибке
    """

    print("[DEBUG] Получение списка всех пользователей")
    
    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = "SELECT * FROM users"
            print("[DEBUG] Выполнение запроса: SELECT * FROM users")
            
            await cursor.execute(query)
            result = await cursor.fetchall()
            
            if not result:
                print("[DEBUG] В базе нет пользователей")
                return None
            
            print(f"[DEBUG] Найдено {len(result)} пользователей:")
            for row in result:
                print(f"[USER] {row}")
                return None

    except Exception as e:
        print(f"[ERROR] Ошибка при получении списка пользователей: {str(e)}")
        return return_fail_value
    
    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def print_table(table_name: str) -> Optional[str]:
    """
    Выводит содержимое указанной таблицы в консоль в удобочитаемом табличном формате.
    
    :param table_name: Название таблицы для вывода
    :return: None при успешном выполнении или return_fail_value при ошибке
    """
    print(f"[DEBUG] Начало вывода таблицы {table_name}")

    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cur:
            print(f"[DEBUG] Выполнение запроса: SELECT * FROM {table_name}")
            await cur.execute(f"SELECT * FROM {table_name}")
            rows = await cur.fetchall()
            headers = [desc[0] for desc in cur.description]

            MAX_CELL_WIDTH = 5
            col_widths = [MAX_CELL_WIDTH] * len(headers)

            def make_line(char="-", junction="+"):
                return junction + junction.join(char * (w + 2) for w in col_widths) + junction

            def format_row(row):
                return "| " + " | ".join(
                    (str(cell) if cell is not None else "NULL")[:MAX_CELL_WIDTH].ljust(MAX_CELL_WIDTH)
                    for cell in row
                ) + " |"

            print(f"mysql> SELECT * FROM {table_name};")
            print(make_line())
            print(format_row(headers))
            print(make_line())
            for row in rows:
                await asyncio.sleep(0)
                print(format_row(row))
            print(make_line())

            print(f"[DEBUG] Успешно выведено {len(rows)} строк таблицы {table_name}")
            return None

    except Exception as e:
        print(f"[ERROR] Ошибка при выводе таблицы {table_name}: {str(e)}")
        return return_fail_value

    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")

async def reset_all_process_values() -> Optional[str]:
    """
    Устанавливает значение 'no' в поле process для всех пользователей.
    :return: None или return_fail_value
    """
    print("[DEBUG] Начало reset_all_process_values()")
    conn = None
    try:
        conn = await get_async_connection()
        if not conn:
            print("[ERROR] Не удалось установить соединение с БД")
            return return_fail_value

        async with conn.cursor() as cursor:
            query = "UPDATE users SET process = 'no'"
            print(f"[DEBUG] Выполнение запроса: {query}")

            await cursor.execute(query)
            await conn.commit()
            print("[DEBUG] Поле process для всех пользователей успешно обновлено")

    except Exception as e:
        print(f"[ERROR] Ошибка при обновлении поля process: {str(e)}")
        return return_fail_value

    finally:
        if conn:
            try:
                conn.close()
                print("[DEBUG] Соединение с БД закрыто")
            except Exception as e:
                print(f"[WARNING] Ошибка при закрытии соединения: {str(e)}")
