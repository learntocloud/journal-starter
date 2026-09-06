from typing import Self
from urllib.parse import parse_qs, unquote

from pydantic import PostgresDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseTestSettings(BaseSettings):
    database_url: str
    test_database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    @model_validator(mode="after")
    def require_separate_test_database(self) -> Self:
        application_url = PostgresDsn(self.database_url)
        test_url = PostgresDsn(self.test_database_url)
        for url in (application_url, test_url):
            if {"database", "dbname"} & parse_qs(url.query or "", keep_blank_values=True).keys():
                raise ValueError(
                    "Database URLs must specify the database in the path, not a query."
                )

        application_database = unquote(application_url.path or "").removeprefix("/")
        test_database = unquote(test_url.path or "").removeprefix("/")
        if not test_database.endswith("_test"):
            raise ValueError("TEST_DATABASE_URL must name a dedicated database ending in '_test'.")
        # Compare names even across host aliases or different database users.
        if test_database == application_database:
            raise ValueError("TEST_DATABASE_URL must not name the application database.")
        return self
