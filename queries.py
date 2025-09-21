import classes, db


async def auth_start(user: classes.UserIn):
    pool = await db.get_db()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT * FROM users WHERE id=$1", user.id)

        if not existing:
            await conn.execute(
                "INSERT INTO users (id, username, phone, status) VALUES ($1, $2, $3, $4)",
                user.id, user.username, user.phone, "not_authorized"
            )
            status = "not_authorized"
        else:
            status = existing["status"]

    return {"status": status}