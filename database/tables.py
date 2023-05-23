import geoalchemy2
import sqlalchemy.dialects

import database

water_usage_meta_data = sqlalchemy.MetaData(schema="water_usage")
geodata_meta_data = sqlalchemy.MetaData(schema="geodata")

usages = sqlalchemy.Table(
    "usages",
    water_usage_meta_data,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("municipality", sqlalchemy.VARCHAR),
    sqlalchemy.Column("date", sqlalchemy.TIMESTAMP),
    sqlalchemy.Column("consumer", sqlalchemy.dialects.postgresql.UUID(as_uuid=True)),
    sqlalchemy.Column("usage_type",
                      sqlalchemy.dialects.postgresql.UUID(as_uuid=True),
                      sqlalchemy.ForeignKey("usage_type.id")
    ),
    sqlalchemy.Column("recorded_at", sqlalchemy.TIMESTAMP),
    sqlalchemy.Column("amount", sqlalchemy.dialects.postgresql.DOUBLE_PRECISION),
)

usage_types = sqlalchemy.Table(
    "usage_types",
    water_usage_meta_data,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.Text),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("external_identifier", sqlalchemy.Text),
)

shapes = sqlalchemy.Table(
    "shapes",
    geodata_meta_data,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.Text),
    sqlalchemy.Column("key", sqlalchemy.Text),
    sqlalchemy.Column("nuts_key", sqlalchemy.Text),
)


def initialize_tables():
    """
    Initialize the used tables
    """
    water_usage_meta_data.create_all(bind=database.engine)
    geodata_meta_data.create_all(bind=database.engine)
