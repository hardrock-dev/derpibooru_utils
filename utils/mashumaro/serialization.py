import datetime

from mashumaro.types import SerializationStrategy


class FormattedDateTime(SerializationStrategy):
    def __init__(self, fmt, utc):
        self.fmt = fmt
        self.utc = utc

    def serialize(self, value: datetime) -> str:
        return value.strftime(self.fmt)

    def deserialize(self, value: str) -> datetime:
        dt = datetime.datetime.strptime(value, self.fmt)
        if self.utc:
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt


iso_z_meta = {"serialization_strategy": FormattedDateTime(fmt="%Y-%m-%dT%H:%M:%SZ", utc=True)}
