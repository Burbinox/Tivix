from typing import List

from pydantic import BaseModel


class Budget(BaseModel):
    income: dict
    outcome: dict


class ShareBudget(BaseModel):
    budgets_id: List[int]
    share_target_users: List[int]
