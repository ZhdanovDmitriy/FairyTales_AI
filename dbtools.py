from config import get_async_connection
from typing import Any, Optional
import asyncio

async def get_user_field(user_id: int, field_name: str) -> Optional[Any]:
    """
    Возвращает значение поля field_name для пользователя с данным user_id.
    Если пользователя нет или поле имеет значение NULL — возвращает None.
    """
    allowed_fields = {"sex", "age", "hobby", "menu", "name", "last_message "}
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

async def get_tale_field(tale_num: int, field_name: str) -> Optional[Any]:
    """
    Возвращает значение поля field_name для пользователя с данным tale_num в таблице tales.
    Если пользователя нет или поле имеет значение NULL — возвращает None.
    """
    allowed_fields = {"tale_size", "cur_stage", "genre"}
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

async def add_user(user_id: int, sex: str, age: int, hobby: str, menu: int, name: str, last_message: int):
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("""
            INSERT INTO users (user_id, sex, age, hobby, menu, name, last_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE sex=%s, age=%s, hobby=%s, menu=%s, name=%s, last_message=%s
        """, (user_id, sex, age, hobby, menu, name, last_message, sex, age, hobby, menu, name, last_message))
    conn.close()

async def update_user_field(user_id: int, field: str, value):
    allowed_fields = {'sex', 'age', 'hobby', 'menu', 'name', 'last_message'}
    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' is not allowed to be updated.")

    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        query = f"UPDATE users SET {field} = %s WHERE user_id = %s"
        await cursor.execute(query, (value, user_id))
    conn.close()

async def update_tale_field(tale_num: int, field_name: str, new_value: Any) -> bool:
    """
    Обновляет значение поля field_name для записи с данным tale_num в таблице tales.
    Возвращает True, если обновление прошло успешно, и False в случае ошибки.
    """
    allowed_fields = {"tale_size", "cur_stage", "genre"}
    if field_name not in allowed_fields:
        raise ValueError(f"Запрос поля {field_name} запрещён")

    sql = f"UPDATE tales SET {field_name} = %s WHERE tale_num = %s;"
    conn = await get_async_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(sql, (new_value, tale_num))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Ошибка при обновлении: {e}")
        return False
    finally:
        conn.close()

async def user_exists(user_id: int) -> bool:
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT 1 FROM users WHERE user_id = %s LIMIT 1", (user_id,))
        result = await cursor.fetchone()
    conn.close()
    return result is not None

async def get_tale_num(user_id: int, tale_size: int, cur_stage: int, genre: str):
    """
    Создаёт новую сказку для пользователя, только если у него нет незаконченных сказок.
    Незаконченная сказка — это запись, у которой cur_stage < tale_size.
    Если такая сказка существует, возвращает её ID.
    """
    conn = await get_async_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT tale_num
                FROM tales
                WHERE user_id = %s
                  AND cur_stage < tale_size
                LIMIT 1
                """,
                (user_id,)
            )
            unfinished = await cursor.fetchone()
            if unfinished:
                return unfinished[0]
            await cursor.execute(
                """
                INSERT INTO tales (user_id, tale_size, cur_stage, genre)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, tale_size, cur_stage, genre)
            )
            await cursor.execute("SELECT LAST_INSERT_ID()")
            result = await cursor.fetchone()
            return result[0]
    finally:
        conn.close()

async def check_all_users():
    conn = await get_async_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM users")
        result = await cursor.fetchall()
        for row in result:
            print(row)
    conn.close()

async def add_small_tale_if_not(tale_num: int):
    conn = await get_async_connection()
    if not conn:
        print("🛑 Ошибка: Соединение не установлено")
        return

    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT tale_num FROM small_tale WHERE tale_num = %s", (tale_num,))
            if not await cursor.fetchone():
                print(f"Создаем запись для tale_num={tale_num}")
                try:
                    await cursor.execute("INSERT INTO small_tale (tale_num) VALUES (%s)", (tale_num,))
                    await conn.commit()
                    print(f"Запись с tale_num={tale_num} успешно создана.")
                except Exception as insert_error:
                    print(f"🔥 Ошибка при вставке данных: {insert_error}")
                    await conn.rollback()
    except Exception as e:
        print(f"🔥 Критическая ошибка: {e}")
        raise
    finally:
        if conn and not conn.closed:
            conn.close()
            print(f"Соединение для tale_num={tale_num} закрыто")

async def add_data_to_small_tale(tale_num: int, text: str):
    conn = await get_async_connection()
    if not conn:
        print("🛑 Не удалось подключиться к БД")
        return

    try:
        async with conn.cursor() as cursor:
            # Берём всю строку
            await cursor.execute("SELECT * FROM small_tale WHERE tale_num = %s", (tale_num,))
            result = await cursor.fetchone()
            if not result:
                print(f"⚠ Запись {tale_num} не найдена")
                return

            # Поля, которые заполняем по очереди
            fields = [
                'p0', 'ans0', 'p1', 'ans1', 'p2', 'ans2',
                'p3', 'ans3', 'p4', 'ans4', 'p5', 'ans5',
                'p6', 'ans6', 'p7', 'ans7'
            ]

            # Найдём первое пустое поле и запишем в него
            updated = False
            for idx, field in enumerate(fields, start=1):
                if result[idx] is None:
                    await cursor.execute(
                        f"UPDATE small_tale SET {field} = %s WHERE tale_num = %s",
                        (text, tale_num)
                    )
                    updated = True
                    print(f"✅ Данные записаны в {field}")
                    break

            if updated:
                await conn.commit()
                print("✅ Изменения сохранены в базе данных.")
            else:
                print("ℹ Все поля уже заполнены")
    except Exception as e:
        print(f"🚨 Ошибка записи: {e}")
    finally:
        if conn and not conn.closed:
            conn.close()


async def get_user_context_small_tale(tale_num: int):
    conn = await get_async_connection()
    context = []
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM small_tale WHERE tale_num = %s", (tale_num,))
            result = await cursor.fetchone()
            if not result:
                print(f"Record with tale_num {tale_num} does not exist.")
                return []
            fields = [
                'p0', 'ans0', 'p1', 'ans1', 'p2', 'ans2',
                'p3', 'ans3', 'p4', 'ans4', 'p5', 'ans5',
                'p6', 'ans6', 'p7', 'ans7'
            ]
            for i, field in enumerate(fields):
                cell = result[i+1]
                if cell is not None:
                    role = "user" if i % 2 == 0 else "assistant"
                    context.append({"role": role, "content": cell})
    finally:
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
