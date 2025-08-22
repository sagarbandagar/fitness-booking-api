from pydantic import BaseModel, EmailStr    # type: ignore

class BookingRequest (BaseModel):  
    class_id : int
    client_name : str
    client_email : EmailStr
    
class DeleteBookingRequest(BaseModel):
    client_email: EmailStr
    client_name: str