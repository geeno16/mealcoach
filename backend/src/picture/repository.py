from src.common import BaseRepository
from src.picture.model import Picture
from src.picture.schema import PictureWrite


class PictureRepository(BaseRepository[Picture, PictureWrite]):
    model = Picture
