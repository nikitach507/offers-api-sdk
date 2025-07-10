from enum import Enum


PRODUCTS_ENDPOINT = "/products/register"
GET_OFFERS_ENDPOINT = "/products/{product_id}/offers"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
