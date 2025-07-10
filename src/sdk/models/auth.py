from pydantic import BaseModel, Field


class AuthApiResponse(BaseModel):
    """
    Model representing the response from the authentication API.

    Attributes:
        access_token (str): The access token received from the authentication API.
    """
    
    access_token: str = Field(..., description="Bearer access token")
