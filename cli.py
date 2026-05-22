#!/usr/bin/env python
import asyncio
import typer
from passlib.context import CryptContext
from sqlalchemy import text
from pydantic import EmailStr, ValidationError, BaseModel

from src.db.db import database
from src.db.repositories.users import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = typer.Typer()


async def _create_admin_user_async(
    first_name: str,
    last_name: str,
    username: str,
    email: str,
    password: str,
):
    class EmailModel(BaseModel):
        email_field: EmailStr

    try:
        EmailModel(email_field=email)
    except ValidationError:
        typer.secho(
            f"Error: '{email}' is not a valid email address.", fg=typer.colors.RED
        )
        raise typer.Exit(code=1)

    async with database.session() as session:
        user_repository = UserRepository(session)
        existing_user = await user_repository.get_by_username(username)
        if existing_user:
            typer.secho(
                f"Error: User with username '{username}' already exists.",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)

        existing_email = await user_repository.get_by_email(email)
        if existing_email:
            typer.secho(
                f"Error: User with email '{email}' already exists.", fg=typer.colors.RED
            )
            raise typer.Exit(code=1)

        hashed_password = pwd_context.hash(password)
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "is_superuser": True,
            "is_active": True,
        }
        await user_repository.create(user_data)
        await session.commit()
        typer.secho(
            f"Admin user '{username}' created successfully.", fg=typer.colors.GREEN
        )


@app.command()
def create_admin(
    first_name: str = typer.Option(..., prompt=True),
    last_name: str = typer.Option(..., prompt=True),
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
):
    """
    Create a new admin user.
    """
    asyncio.run(
        _create_admin_user_async(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
        )
    )


async def _db_status_async():
    typer.echo("Checking database connection...")
    try:
        async with database.session() as session:
            await session.execute(text("SELECT 1"))
        typer.secho("Database connection successful.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho("Database connection failed.", fg=typer.colors.RED)
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def db_status():
    """
    Check the status of the database connection.
    """
    asyncio.run(_db_status_async())


if __name__ == "__main__":
    app()
