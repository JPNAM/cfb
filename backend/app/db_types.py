from sqlalchemy import JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator


class JSONB(TypeDecorator):
    """Compatibility JSONB column that degrades gracefully on SQLite for tests."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB(astext_type=None))
        return super().load_dialect_impl(dialect)

