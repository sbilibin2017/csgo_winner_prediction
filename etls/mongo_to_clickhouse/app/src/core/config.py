from pathlib import Path

from dotenv import dotenv_values
from pydantic_settings import BaseSettings

ROOT     = Path().resolve().parent.parent.parent.parent
config   = dotenv_values(ROOT / ".env")
dev      = bool(int(config["DEV"]))
env_file = '.env.dev' if dev else '.env'
mongo    = dotenv_values(ROOT / f"env/mongo/{env_file}")
clickhouse = dotenv_values(ROOT / f"env/clickhouse/{env_file}")
docker   = dotenv_values(ROOT / f"env/docker/{env_file}")


class Mongo(BaseSettings):
    username: str = mongo["MONGO_INITDB_ROOT_USERNAME"]
    password: str = mongo["MONGO_INITDB_ROOT_PASSWORD"]
    port    : int = mongo["MONGO_PORT"]
    host    : str = mongo["MONGO_HOST"]


class Clickhouse(BaseSettings):    
    port : int = clickhouse["CLICKHOUSE_SERVER_PORT"]
    host : str = clickhouse["CLICKHOUSE_SERVER_HOST"]


class Docker(BaseSettings):
    mongo_host            : str = docker["MONGO_HOST"]    
    clickhouse_server_host: str = docker["CLICKHOUSE_SERVER_HOST"] 


class Config(BaseSettings):
    mongo            : Mongo      = Mongo()
    clickhouse       : Clickhouse = Clickhouse()
    docker           : Docker     = Docker()    
    chunk_size       : int        = 1000
    dev              : int        = 1


config = Config()
