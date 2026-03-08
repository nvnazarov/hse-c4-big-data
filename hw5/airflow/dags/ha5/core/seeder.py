from datetime import datetime
from random import Random
from typing import TypeVar
from uuid import uuid4

from ha5.core.models import (
    ID,
    Client,
    ClientProfile,
    Active,
    Instrument,
    BankAccount,
    Database,
    Credit,
    Transaction,
    CreditPayment,
    Deposit,
    KeyRate,
    Gender,
    Money,
)
from pydantic import BaseModel

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

    def work_company(self) -> str:
        return self.r.choice([""])

    def work_area(self) -> str:
        return self.r.choice([""])

    def dt(self) -> datetime:
        return datetime(
            year=self.r.randint(1970, 2011),
            month=self.r.randint(1, 12),
            day=self.r.randint(1, 28),
        )

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
                work_company=self.work_company(),
                work_area=self.work_area(),
                salary=self.money(),
                dt_loaded=self.dt(),
            )
            for client in clients
        ]
        instruments = [
            Instrument(id=self.id(), cost=self.money(), dt=self.dt())
            for _ in range(100)
        ]
        bank_accounts = [
            BankAccount(
                id=self.id(),
                client_id=self.id(),
                type="kopilka",
                dt_created=self.dt(),
                dt_loaded=self.dt(),
            )
        ]
        actives = [
            Active(
                id=self.id(),
                bank_account_id=bank_account_id,
                instrument_id=instrument_id,
                count=self.r.randint(1, 5),
                dt=self.dt(),
            )
            for bank_account_id in map(lambda b: b.id, bank_accounts)
            for instrument_id in map(lambda i: i.id, instruments)
        ]
        credits = [
            Credit(
                id=self.id(),
                client_id=self.id(),
                dt_opened=self.dt(),
                amount=self.money(),
                percent="0.1",
                type="ipoteka",
            )
        ]
        deposits = [
            Deposit(
                id=self.id(),
                client_id=self.id(),
                dt_opened=self.dt(),
                dt_closed=self.dt(),
                amount=self.money(),
                percent="0.5",
                type="",
            )
        ]
        transactions = [
            Transaction(
                id=self.id(),
                send_bank_account_id=self.r.choice(bank_accounts).id,
                recv_bank_account_id=self.r.choice(bank_accounts).id,
                amount=self.money(),
                dt=self.dt(),
                is_successful=True,
            )
        ]
        credit_payments = [
            CreditPayment(
                id=self.id(),
                credit_id=self.r.choice(credits).id,
                bank_account_id=self.r.choice(bank_accounts).id,
                dt=self.dt(),
                amount=self.money(),
                is_successful=True,
            )
        ]
        key_rates = [KeyRate(dt_since=self.dt(), percent="")]
        return Database(
            clients=clients,
            profiles=profiles,
            actives=actives,
            instruments=instruments,
            bank_accounts=bank_accounts,
            credits=credits,
            deposits=deposits,
            transactions=transactions,
            credit_payments=credit_payments,
            key_rates=key_rates,
        )
