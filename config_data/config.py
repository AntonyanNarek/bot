from dataclasses import dataclass

from environs import Env


@dataclass
class ContractorVerificationBot:
    token: str


@dataclass
class PayMethodAPI:
    you_kassa: str


@dataclass
class ContractorVerificationDataBase:
    db_host: str
    db_database: str
    db_user: str
    db_password: str


@dataclass
class ContractorVerificationAPI:
    zcb_token: str


@dataclass
class Config:
    bot_config: ContractorVerificationBot
    db_config: ContractorVerificationDataBase
    api_config: ContractorVerificationAPI
    api_pay: PayMethodAPI


@dataclass
class APIConfig:
    api_config: ContractorVerificationAPI


@dataclass
class DataBaseConfig:
    db_config: ContractorVerificationDataBase


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path=path)
    return Config(
        bot_config=ContractorVerificationBot(
            token=env('BOT_TOKEN')
        ),
        db_config=ContractorVerificationDataBase(
            db_host=env('DB_HOST'),
            db_database=env('DB_DATABASE'),
            db_user=env('DB_USER'),
            db_password=env('DB_PASSWORD')
        ),
        api_config=ContractorVerificationAPI(
            zcb_token=env('ZCB_TOKEN')
        ),
        api_pay=PayMethodAPI(
            you_kassa=env('YOU_KASSA')
        )
    )
