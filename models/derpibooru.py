import datetime
from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin

from utils.mashumaro.serialization import iso_z_meta


# noinspection SpellCheckingInspection
@dataclass
class Image(DataClassJSONMixin):
    animated: int
    comment_count: int
    id: int
    format: str
    description: str
    score: int
    name: str
    faves: int
    view_url: str
    tag_count: int
    width: int
    tags: list[str]
    size: int
    representations: dict[str, str]
    wilson_score: float
    downvotes: int
    height: int
    upvotes: int
    uploader: str
    created_at: datetime.datetime = field(metadata=iso_z_meta)
    uploader_id: int | None


@dataclass
class SearchPayload(DataClassJSONMixin):
    images: list[Image]
    total: int
