from datetime import datetime
from sqlalchemy.orm import Session
from warehouse.etl_metadata.models.etl_metadata import ETLMetadata
from datetime import timezone

def get_last_loaded_time(session, table_name):
    meta = session.query(ETLMetadata).filter_by(table_name=table_name).first()
    if meta and meta.last_loaded_time:
        last_time = meta.last_loaded_time
        # Nếu last_time là naive, hãy làm cho nó aware (UTC)
        if last_time.tzinfo is None or last_time.tzinfo.utcoffset(last_time) is None:
            last_time = last_time.replace(tzinfo=timezone.utc)
        return last_time
    return datetime(1970, 1, 1, tzinfo=timezone.utc) # Hoặc một giá trị aware mặc định  # mặc định nếu chưa có

def update_last_loaded_time(session: Session, table_name: str, new_time: datetime):
    meta = session.query(ETLMetadata).filter_by(table_name=table_name).first()
    if not meta:
        meta = ETLMetadata(table_name=table_name, last_loaded_time=new_time)
    else:
        meta.last_loaded_time = new_time
    session.merge(meta)
    session.commit()

