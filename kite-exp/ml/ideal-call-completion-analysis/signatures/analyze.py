from typing import NamedTuple, List, Dict

from kite.asserts.asserts import FieldValidator


import datetime
import json

import numpy as np


class SignatureData(NamedTuple):
    user_id: str
    sent_at: datetime.datetime
    triggered: int
    shown: int

    @classmethod
    def from_json(cls, d: dict) -> 'SignatureData':
        v = FieldValidator(cls, d)
        return SignatureData(
            user_id=v.get('user_id', str),
            sent_at=datetime.datetime.fromtimestamp(v.get('sent_at', int)),
            triggered=v.get('signatures_triggered', int),
            shown=v.get('signatures_shown', int),
        )


def read_data(fname: str, num=100) -> List[SignatureData]:
    data = []
    with open(fname) as f:
        for line in f:
            if len(data) >= num > 0:
                return data
            data.append(SignatureData.from_json(json.loads(line)))
    return data


def by_user(data: List[SignatureData]) -> Dict[str, List[SignatureData]]:
    users = {}
    for d in data:
        if d.user_id not in users:
            users[d.user_id] = []
        users[d.user_id].append(d)
    return users


def by_day(data: List[SignatureData]) -> Dict[str, List[SignatureData]]:
    days = {}
    for d in data:
        ts = f'{d.sent_at.month}:{d.sent_at.day}'
        if ts not in days:
            days[ts] = []
        days[ts].append(d)
    return days


ByUserByDay = Dict[str, Dict[str, List[SignatureData]]]


def by_user_by_day(data: List[SignatureData]) -> ByUserByDay:
    return {usr: by_day(ds) for usr, ds in by_user(data).items()}


def filter_inactive_days(bubd: ByUserByDay, min_active_events: int) -> ByUserByDay:
    new_bubd = {}
    for usr, days in bubd.items():
        new_days = {}
        for day, evts in days.items():
            active_count = sum(1 for evt in evts if evt.triggered > 0)
            if active_count >= min_active_events:
                new_days[day] = evts
        if new_days:
            new_bubd[usr] = new_days
    return new_bubd


percentiles = [25, 50, 75, 95]


def percentiles_str(name: str, data: list) -> str:
    return f'{name} percentiles ({percentiles}): {np.percentile(data, percentiles)}'


def percentiles_triggered_per_day(bubd: ByUserByDay):
    per_days = []
    for _, days in bubd.items():
        per_days.extend(sum(evt.triggered for evt in day) for _, day in days.items())
    print(percentiles_str('Triggered per day', per_days))


def percentiles_shown_per_day(bubd: ByUserByDay):
    per_days = []
    for _, days in bubd.items():
        per_days.extend(sum(evt.shown for evt in day) for _, day in days.items())
    print(percentiles_str('Shown per day', per_days))


if __name__ == '__main__':
    data = read_data('data.json', 0)
    bubd = by_user_by_day(data)
    bubd = filter_inactive_days(bubd, 1)
    print('after filtering got', len(bubd))
    percentiles_triggered_per_day(bubd)
    percentiles_shown_per_day(bubd)
