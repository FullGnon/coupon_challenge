from enum import StrEnum
from functools import lru_cache

from pydantic import MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBBackendEnum(StrEnum):
    mongo = "mongo"
    sqlite = "sqlite"


APP_CHALLENGE_SETTINGS_PREFIX = "araiko_challenge_"


class AppChallengeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=APP_CHALLENGE_SETTINGS_PREFIX)

    db_backend: DBBackendEnum = DBBackendEnum.mongo


MONGO_SETTINGS_PREFIX = f"{APP_CHALLENGE_SETTINGS_PREFIX}mongo_"


class MongoDBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix=MONGO_SETTINGS_PREFIX)

    db_uri: MongoDsn


# Using lru_cache ensure that settings does not change after starting the application
# We could have also use the app.state storage of FastAPI client with hook on startup
@lru_cache
def get_app_settings() -> AppChallengeSettings:
    return AppChallengeSettings()


@lru_cache
def get_mongodb_settings() -> MongoDBSettings:
    return MongoDBSettings()
