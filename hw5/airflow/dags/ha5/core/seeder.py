from random import Random
from typing import TypeVar
from uuid import uuid4

from ha5.core.models import ID, Money, Gender, Database, Client, ClientProfile
from pydantic import BaseModel
from datetime import datetime

T = TypeVar("T")
U = BaseModel


class Seeder:
    _cities = [
        "Moscow",
        "St.Petersburg",
        "Ekaterinburg",
        "Omsk",
        "Novosibirsk",
        "Kazan",
    ]

    def __init__(self, seed: int = 0):
        self.r = Random(seed)

    def id(self) -> ID:
        return ID(uuid4().hex[:6])

    def money(self, low: int = 1, up: int = 10000) -> Money:
        return Money(self.r.randint(low, up))

    def gender(self) -> Gender:
        if self.r.uniform(0, 1) < 0.5:
            return "male"
        return "female"

    def full_name(self) -> str:
        return f"fio {uuid4().hex[:6]}"

    def city_name(self) -> str:
        return self.r.choice(self._cities)

    def dt(self) -> datetime:
        return datetime(
            year=self.r.randint(1970, 2011),
            month=self.r.randint(1, 12),
            day=self.r.randint(1, 28),
        )

    def model(self, cls: type[U]) -> U: ...

    def generate_database(self) -> Database:
        clients = [
            Client(
                id=self.id(),
                full_name=self.full_name(),
                city_name=self.city_name(),
                gender=self.gender(),
                birthday=self.dt(),
            )
            for _ in range(100)
        ]
        profiles = [
            ClientProfile(
                id=self.id(),
                client_id=client.id,
                work_company="",
                work_area="it",
                salary=self.money(),
                dt_loaded=self.dt(),
            )
            for client in clients
        ]
        return Database(
            clients=clients,
            profiles=profiles,
        )
