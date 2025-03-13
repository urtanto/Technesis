import uuid

from sqlalchemy import Column, String, UUID

from database import SqlAlchemyBase


class Products(SqlAlchemyBase):
    __tablename__ = 'products'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    xpath = Column(String, nullable=False)
