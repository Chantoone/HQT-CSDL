from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import Base from your SQLAlchemy models
from configs.database import Base
from configs.conf import settings

# Import all models that should be included in migrations
# Add imports for all your model files here

from role.routers import role
from user.routers import user
from user_role.routers import user_role
from auth_credential.routers import auth_credential
from authen.routers import authen
from cinema.routers import cinema
from film.routers import film
from food.routers import food
from rate.routers import rate
from room.routers import room
from showtime.routers import showtime
from promotion.routers import promotion
from seat.routers import seat
from ticket.routers import ticket
from bill.routers import bill
from bill_prom.routers import bill_prom
from user_bill.routers import user_bill
from genre.routers import genre
from film_genre.routers import film_genre
from showtime_seat.routers import showtime_seat
from etl_metadata.routers import etl_metadata



# Import any other models that you have

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Set compare_type to True to detect column type changes
            compare_type=True,
            # Set include_schemas to True if using schemas
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
