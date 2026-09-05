from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    email: str
    password: str


@dataclass(frozen=True)
class CustomerRegistrationData:
    first_name: str
    last_name: str
    company_name: str
    email: str
    password: str
    accept_terms: bool = True
