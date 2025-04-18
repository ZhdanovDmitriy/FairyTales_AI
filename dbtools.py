from config import get_async_connection
from typing import Any, Optional
import asyncio

async def get_user_field(user_id: int, field_name: str) -> Optional[Any]:
    allowed_fields = {"sex", "age", "hobby", "menu", "name", "last_message", "cur_tale"}
    if field_name not in allowed_fields:
        raise ValueError(f"Запрос поля {field_name} запрещён")
    sql = f"SELECT {field_name} FROM users WHERE user_id = %s;"
    conn = await get_async_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else None
    finally:
        try:
            conn.close()
        except:
            pass

async def get_tales_field(tale_num: int, field_name: str) -> Optional[Any]:
    """
    Возвращает значение поля field_name для записи с данным tale_num в таблице tales.
    Если записи нет или поле имеет значение NULL — возвращает None.
    """
    allowed_fields = {"tale_size", "cur_stage", "genre", "hero", "moral"}
    if field_name not in allowed_fields:
        raise ValueError(f"Запрос поля {field_name} запрещён")

    sql = f"SELECT {field_name} FROM tales WHERE tale_num = %s;"
    conn = await get_async_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, (tale_num,))
            row = await cursor.fetchone()
            return row[0] if row else None
    finally:
        try:
            conn.close()
        except:
            pass

async def fetch_current_db():
    try:
        conn = await get_async_connection()
        if conn is None:
            print("❌ Соединение не установлено (conn is None)")
            return

        async with conn.cursor() as cursor:
            await cursor.execute("SELECT DATABASE();")
            result = await cursor.fetchone()
            print(f"✅ Успешное подключение к базе: {result[0]}")
    except Exception as e:
        print(f"❌ Ошибка при работе с базой: {e}")
    finally:
        if conn:
            conn.close()

async def add_user(user_id: int, sex: str, age: int, hobby: str, menu: int, name: str, last_message: int, cur_tale: int = 0):
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("""
            INSERT INTO users (user_id, sex, age, hobby, menu, name, last_message, cur_tale)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE sex=%s, age=%s, hobby=%s, menu=%s, name=%s, last_message=%s, cur_tale=%s
        """, (user_id, sex, age, hobby, menu, name, last_message, cur_tale,
              sex, age, hobby, menu, name, last_message, cur_tale))
    conn.close()

async def update_user_field(user_id: int, field: str, value):
    allowed_fields = {'sex', 'age', 'hobby', 'menu', 'name', 'last_message', 'cur_tale'}
    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' is not allowed to be updated.")

    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        query = f"UPDATE users SET {field} = %s WHERE user_id = %s"
        await cursor.execute(query, (value, user_id))
        print(f"✅Поле {field} успешно обновлены в user")
    conn.close()

async def update_tales_field(tale_num: int, field_name: str, new_value: Any) -> bool:
    """
    Обновляет значение поля field_name для записи с данным tale_num в таблице tales.
    Возвращает True, если обновление прошло успешно (затронута хотя бы одна строка),
    и False в случае ошибки или если запись не найдена.
    """
    allowed_fields = {"tale_size", "cur_stage", "genre", "hero", "moral"}
    if field_name not in allowed_fields:
        raise ValueError(f"Обновление поля {field_name} запрещено")

    sql = f"UPDATE tales SET {field_name} = %s WHERE tale_num = %s;"
    conn = await get_async_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, (new_value, tale_num))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка при обновлении tales.{field_name}: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

async def user_exists(user_id: int) -> bool:
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT 1 FROM users WHERE user_id = %s LIMIT 1", (user_id,))
        result = await cursor.fetchone()
    conn.close()
    return result is not None

async def get_tales_num(user_id: int) -> Optional[int]:
    """
    Возвращает tale_num незавершённой сказки пользователя (где cur_stage != tale_size).
    Если таких записей нет — возвращает None.
    """
    conn = await get_async_connection()
    try:
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
            return result[0] if result else None
    except Exception as e:
        print(f"🚨 Ошибка при получении незавершённой сказки: {e}")
        return None
    finally:
        try:
            conn.close()
        except:
            pass


async def get_new_tales_num(user_id: int) -> int:
    """
    Завершает все предыдущие сказки пользователя и создаёт новую запись в таблице tales.
    Все поля, кроме user_id, заполняются NULL.
    Возвращает tale_num новой записи.
    """
    conn = await get_async_connection()
    try:
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
            # Фиксируем изменения (если автокоммит отключен)
            await conn.commit()

            # Создаём новую запись со всеми полями, кроме user_id, равными NULL
            await cursor.execute(
                """
                INSERT INTO tales (user_id, tale_size, cur_stage, genre, hero, moral)
                     VALUES (%s,       %s,        %s,        %s,    %s,   %s)
                """,
                (user_id, None, None, None, None, None)
            )
            # Получаем идентификатор только что созданной записи
            await cursor.execute("SELECT LAST_INSERT_ID()")
            new_id = (await cursor.fetchone())[0]
            await conn.commit()
            return new_id
    finally:
        try:
            conn.close()
        except:
            pass


async def check_all_users():
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM users")
        result = await cursor.fetchall()
        for row in result:
            print(row)
    conn.close()

async def add_tale_if_not(tale_num: int, tale_size: int):
    # Сопоставляем размер сказки с именем таблицы
    table_map = {
        8: "small_tale",
        16: "medium_tale",
        32: "large_tale",
    }

    table_name = table_map.get(tale_size)
    if not table_name:
        print(f"❌ Недопустимый размер сказки: {tale_size!r}. Ожидаются 8, 16 или 32.")
        return

    conn = await get_async_connection()
    if not conn:
        print("❌ Ошибка: соединение не установлено")
        return

    try:
        async with conn.cursor() as cursor:
            # Проверка наличия записи
            await cursor.execute(
                f"SELECT tale_num FROM {table_name} WHERE tale_num = %s",
                (tale_num,),
            )
            exists = await cursor.fetchone()

            if not exists:
                print(f"Создаем запись в {table_name} для tale_num={tale_num}")
                try:
                    # Вставляем только tale_num — все остальные поля автоматически NULL
                    await cursor.execute(
                        f"INSERT INTO {table_name} (tale_num) VALUES (%s)",
                        (tale_num,),
                    )
                    await conn.commit()
                    print(f"✅ Запись с tale_num={tale_num} успешно создана в {table_name}.")
                except Exception as insert_error:
                    print(f"🔥 Ошибка при вставке в {table_name}: {insert_error}")
                    await conn.rollback()
            else:
                print(f"ℹ️ Запись с tale_num={tale_num} уже есть в {table_name}.")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        if conn and not conn.closed:
            conn.close()
            print("🔒 Соединение закрыто")



async def add_data_to_tale(tale_num: int, prompt: str, tale_size: int):
    table_map = {
        8: ("small_tale", 8),
        16: ("medium_tale", 16),
        32: ("large_tale", 32),
    }

    if tale_size not in table_map:
        print(f"❌ Неверный размер сказки: {tale_size}")
        return

    table_name, num_pairs = table_map[tale_size]

    # Генерация всех полей p0, ans0, p1, ans1, ...
    fields = [f"p{i}" if j % 2 == 0 else f"ans{i}" for i in range(num_pairs) for j in range(2)]

    conn = await get_async_connection()
    if not conn:
        print("❌ Не удалось подключиться к БД")
        return

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM {table_name} WHERE tale_num = %s", (tale_num,))
            row = await cursor.fetchone()

            if not row:
                print(f"⚠ Запись с tale_num={tale_num} не найдена в {table_name}")
                return

            # row[0] — это tale_num, дальше идут p0, ans0, ...
            for idx, field in enumerate(fields, start=1):
                if row[idx] is None:
                    await cursor.execute(
                        f"UPDATE {table_name} SET {field} = %s WHERE tale_num = %s",
                        (prompt, tale_num)
                    )
                    await conn.commit()
                    print(f"✅ Данные записаны в {field} таблицы {table_name}")
                    return

            print(f"ℹ Все поля в {table_name} уже заполнены")
    except Exception as e:
        print(f"🚨 Ошибка при записи данных: {e}")
    finally:
        if conn and not conn.closed:
            conn.close()

async def get_user_context_tale(tale_num: int, tale_size: int):
    table_map = {
        8: ("small_tale", 8),
        16: ("medium_tale", 16),
        32: ("large_tale", 32),
    }

    if tale_size not in table_map:
        print(f"❌ Неверный размер сказки: {tale_size}")
        return []

    table_name, num_pairs = table_map[tale_size]
    fields = [f"p{i}" if j % 2 == 0 else f"ans{i}" for i in range(num_pairs) for j in range(2)]

    conn = await get_async_connection()
    context = []

    if not conn:
        print("❌ Не удалось подключиться к БД")
        return []

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT * FROM {table_name} WHERE tale_num = %s", (tale_num,))
            result = await cursor.fetchone()
            if not result:
                print(f"⚠ Запись с tale_num={tale_num} не найдена в {table_name}")
                return []

            for i, field in enumerate(fields):
                cell = result[i + 1]  # result[0] — это tale_num
                if cell is not None:
                    role = "user" if i % 2 == 0 else "assistant"
                    context.append({"role": role, "content": cell})
    except Exception as e:
        print(f"🚨 Ошибка получения контекста: {e}")
    finally:
        if conn and not conn.closed:
            conn.close()

    return context


async def print_table(table_name: str):
    conn = await get_async_connection()
    async with conn.cursor() as cur:
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
