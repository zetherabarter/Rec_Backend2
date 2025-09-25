from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class BulkRoundUpdateRequest(BaseModel):
    emails: List[EmailStr]
    screening: Optional[dict] = None  # {"status": str, "datetime": datetime}
    gd: Optional[dict] = None         # {"status": str, "datetime": datetime, "remarks": str}
    pi: Optional[dict] = None         # {"status": str, "datetime": datetime, "remarks": list}
