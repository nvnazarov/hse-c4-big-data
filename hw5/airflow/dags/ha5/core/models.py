from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ID = str
Money = str
Percent = str
Gender = Literal["male", "female"]
BankAccountType = Literal["kopilka", "nakopitelniy", "standard"]
DepositType = Literal["long", "short"]
CreditType = Literal["ipoteka", "auto", "potrebitelskaya"]


class Active(BaseModel):
    id: ID
    bank_account_id: ID
    instrument_id: ID
    count: int
    dt: datetime


class Instrument(BaseModel):
    id: ID
    cost: Money
    dt: datetime


class BankAccount(BaseModel):
    id: ID
    client_id: ID
    type: BankAccountType
    dt_created: datetime
    dt_loaded: datetime


class Client(BaseModel):
    id: ID
    full_name: str
    city_name: str
    gender: Gender
    birthday: datetime


class KeyRate(BaseModel):
    dt_since: datetime
    percent: Percent


class Deposit(BaseModel):
    id: ID
    client_id: ID
    dt_opened: datetime
    dt_closed: datetime
    amount: Money
    percent: Percent
    type: DepositType


class ClientProfile(BaseModel):
    id: ID
    client_id: ID
    work_company: str
    work_area: str
    salary: Money
    dt_loaded: datetime


class Credit(BaseModel):
    id: ID
    client_id: ID
    dt_opened: datetime
    amount: Money
    percent: Percent
    type: CreditType


class Transaction(BaseModel):
    id: ID
    send_bank_account_id: ID
    recv_bank_account_id: ID
    amount: Money
    dt: datetime
    is_successful: bool


class CreditPayment(BaseModel):
    id: ID
    credit_id: ID
    bank_account_id: ID
    dt: datetime
    amount: Money
    is_successful: bool


class Database(BaseModel):
    clients: list[Client] = []
    profiles: list[ClientProfile] = []
    actives: list[Active] = []
    instruments: list[Instrument] = []
    bank_accounts: list[BankAccount] = []
    credits: list[Credit] = []
    deposits: list[Deposit] = []
    transactions: list[Transaction] = []
    key_rates: list[KeyRate] = []
    credit_payments: list[CreditPayment] = []
