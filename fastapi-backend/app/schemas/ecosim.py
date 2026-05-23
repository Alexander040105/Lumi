from pydantic import BaseModel


class GetHouse(BaseModel):
    municipality : str
    # pesos per kilowhuttttttttt-hour
    electricity_rate : float = 14.35
    current_electricity_bill : float = 0.0
    # default is 50% savings but users may change it blah blah blah
    desired_savings : float = 0.50


class PostHouse(BaseModel):
    municipality: str
    # pesos per kilowhuttttttttt-hour
    electricity_rate : float = 14.35
    current_electricity_bill : float = 0.0
    # default is 50% savings but users may change it blah blah blah
    desired_savings : float = 0.50


# we get house list in order for the users to have more than one house on their accounts
class HouseList(BaseModel):
    items: list[PostHouse]
