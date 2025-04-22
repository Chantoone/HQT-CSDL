from datetime import datetime
from sqlalchemy.orm import Session
from warehouse.etl_metadata.models.etl_metadata import ETLMetadata


def get_last_loaded_time(session: Session, table_name: str):
    meta = session.query(ETLMetadata).filter_by(table_name=table_name).first()
    return meta.last_loaded_time if meta else datetime(2000, 1, 1)  # mặc định nếu chưa có

def update_last_loaded_time(session: Session, table_name: str, new_time: datetime):
    meta = session.query(ETLMetadata).filter_by(table_name=table_name).first()
    if not meta:
        meta = ETLMetadata(table_name=table_name, last_loaded_time=new_time)
    else:
        meta.last_loaded_time = new_time
    session.merge(meta)
    session.commit()

