import json
import os
import time

import numpy as np
import pymongo
from core.config import config
from core.logger import logger

PATH_TO_GAME_RAW = config.path_to_games_raw
CHUNK_SIZE=config.chunk_size
FILENAMES = np.array(os.listdir(PATH_TO_GAME_RAW))
order = np.argsort([int(i.split('.')[0]) for i in FILENAMES])
FILENAMES = FILENAMES[order]


def main():
    try:
        client = pymongo.MongoClient(config.docker.mongo_host, config.mongo.port)
        games = client.games
        ids_all = [int(fnm.split('.')[0]) for fnm in FILENAMES]
        ids_in = [game['id'] for game in games.raw.find()]
        ids_new = list(set(ids_all) - set(ids_in))
        count = len(ids_new)
        n_chunks = np.int32(np.ceil(count / CHUNK_SIZE))
        chunks = np.array_split(ids_new, n_chunks)
        for chunk in chunks:
            new =[]
            for id in chunk:
                try:
                    logger.info(id)
                    with open(os.path.join(PATH_TO_GAME_RAW, f'{id}.json'), 'r') as f:
                        game = json.load(f)
                    new.append(game)
                    del game
                except OSError:
                    logger.error(id)
                    pass
            if len(new)>0:
                games.raw.insert_many(new)
            del new
    except Exception as e:
        logger.error(e)
    finally:
        client.close()


if __name__ =='__main__':
    while True:
        main()
    time.sleep(1)
