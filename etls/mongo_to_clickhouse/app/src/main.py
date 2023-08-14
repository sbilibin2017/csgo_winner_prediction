import json
import os
import time

import numpy as np
import pandas as pd
import pymongo
from clickhouse_driver import Client
from core.config import config
from core.logger import logger
from tqdm import tqdm


def get_game_profile(game) -> pd.DataFrame:
    PLAYER_STAT_KEYS =[
        'adr', 'assists', 'deaths', 'first_kills_diff', 'flash_assists', 
        'headshots', 'k_d_diff', 'kast', 'kills', 'rating'
    ] 
    PROFILE_KEYS = [
        'id', 'date', 'timestamp', 'year', 'month', 'year_month', 'day',
        'weekday', 'hour', 'map_id', 'tier', 't_id', 't_loc', 't_opp_id',
        'p_id', 'p_nat', 'p_ht', 'adr', 'assists', 'deaths', 'first_kills_diff',
        'flash_assists', 'headshots', 'k_d_diff', 'kast', 'kills', 'rating',
        'total_rounds', 'start_ct', 'map_id_start_ct', 'h1_win_count',
        'h2_win_count', 'r1_win', 'r2_win', 'r16_win', 'r17_win',
        'h1_eliminated_count', 'h1_timeout_count', 'h1_exploded_count', 'h1_defused_count', 
        'h2_eliminated_count', 'h2_timeout_count', 'h2_exploded_count', 'h2_defused_count', 
        'win'
    ]      
    try:
        profile = {}
        profile['id'] = game['id']
        profile['date'] = parser.parse(game['begin_at'])
        profile['timestamp'] = profile['date'].timestamp()
        profile['year'] = profile['date'].year
        profile['month'] = profile['date'].month
        profile['year_month'] = profile['year']*100+profile['month']
        profile['day'] = profile['date'].day
        profile['weekday'] = profile['date'].weekday()
        profile['hour'] = profile['date'].hour
        profile['map_id'] = game['map']['id']
        profile['tier'] = game['match']['serie']['tier'] or 'default'
        df_team_player_id = pd.DataFrame.from_records([{'t_id':p['team']['id'], 'p_id':p['player']['id']} for p in game['players']])
        df_rounds = pd.DataFrame.from_records(game['rounds'])
        mask_map = profile['map_id'] is not None
        mask_team = df_team_player_id['t_id'].nunique()==2
        mask_player = (df_team_player_id.groupby('t_id')['p_id'].nunique()==5).all()
        mask_round_min = df_rounds['round'].min()==1
        mask_round_max = df_rounds['round'].max()>=16
        mask_round_diff_nunique = df_rounds['round'].diff().dropna().nunique()==1
        if mask_map&mask_team&mask_player&mask_round_min&mask_round_max&mask_round_diff_nunique:
            total_rounds = df_rounds['round'].max()
            start_ct_id = df_rounds.query('round==1')['ct'].iloc[0]
            winner_id = df_rounds['winner_team'].value_counts().idxmax()
            r1_winner_id = df_rounds.query('round==1')['winner_team'].iloc[0]
            r2_winner_id = df_rounds.query('round==2')['winner_team'].iloc[0]
            r16_winner_id = df_rounds.query('round==16')['winner_team'].iloc[0]
            try:
                r17_winner_id = df_rounds.query('round==17')['winner_team'].iloc[0]
            except:
                r17_winner_id = r16_winner_id
            d_h1_win_count = df_rounds.query('round<=15')['winner_team'].value_counts().to_dict()
            d_h2_win_count = df_rounds.query('round>15')['winner_team'].value_counts().to_dict()
            d_h1_outcome_count = df_rounds.query('round<=15')['outcome'].value_counts().to_dict()
            d_h2_outcome_count = df_rounds.query('round>15')['outcome'].value_counts().to_dict()
            rows = []
            for p in game['players']:
                d = profile.copy()
                d['t_id'] = p['team']['id']
                d['t_loc'] = p['team']['location']
                d['t_opp_id'] = p['opponent']['id']
                d['p_id'] = p['player']['id']
                d['p_nat'] = p['player']['nationality']
                d['p_ht'] = p['player']['hometown']
                d.update({k:p[k] for k in PLAYER_STAT_KEYS})
                d['total_rounds'] = total_rounds
                start_ct = int(start_ct_id==d['t_id'])
                d['start_ct'] = start_ct
                d['map_id_start_ct'] = str(d['map_id']) + '_' + str(start_ct) 
                d['h1_win_count'] = d_h1_win_count.get(d['t_id'], 0)
                d['h2_win_count'] = d_h1_win_count.get(d['t_id'], 0)
                d['r1_win'] = int(r1_winner_id==d['t_id'])
                d['r2_win'] = int(r2_winner_id==d['t_id'])
                d['r16_win'] = int(r16_winner_id==d['t_id'])
                d['r17_win'] = int(r17_winner_id==d['t_id'])
                for outcome, count in d_h1_outcome_count.items():
                    d[f'h1_{outcome}_count'] = count
                for outcome, count in d_h2_outcome_count.items():
                    d[f'h2_{outcome}_count'] = count
                d['win'] = int(winner_id==d['t_id'])   
                for k,v in d.items():
                    try:
                        d[k] = float(v)
                    except:
                        d[k] = str(v)
                rows.append(d)
                del d
            subdf = pd.DataFrame.from_records(rows)
            del rows
            for key in PROFILE_KEYS:
                if key not in subdf.columns:
                    subdf[key] = 0.0
                else:
                    try:
                        subdf[key]=subdf[key].fillna(0.0).astype('float')
                    except:
                        subdf[key]=subdf[key].fillna(0.0).astype('str')                        
            return subdf[PROFILE_KEYS]
    except:
        pass


def main():    
    try:
        mongo_client = pymongo.MongoClient(config.mongo.host, config.mongo.port)      
        games = mongo_client.games        
        clickhouse_client = Client(host=config.docker.clickhouse_server_host, port=config.clickhouse.port)
        clickhouse_client.execute(
            """
            CREATE TABLE IF NOT EXISTS profile(
                id Integer, date DateTime, timestamp Float32, year Float32, month Float32, year_month Float32, day Float32,
                weekday Float32, hour Float32, map_id Float32, tier Float32, t_id Float32, t_loc String, t_opp_id Float32,
                p_id Float32, p_nat String, p_ht String, adr Float32, assists Float32, deaths Float32, first_kills_diff Float32,
                flash_assists Float32, headshots Float32, k_d_diff Float32, kast Float32, kills Float32, rating Float32,
                total_rounds Float32, start_ct Float32, map_id_start_ct Float32, h1_win_count Float32,
                h2_win_count Float32, r1_win Float32, r2_win Float32, r16_win Float32, r17_win Float32,
                h1_eliminated_count Float32, h1_timeout_count Float32, h1_exploded_count Float32, h1_defused_count Float32,
                h2_eliminated_count Float32, h2_timeout_count Float32, h2_exploded_count Float32, h2_defused_count Float32,
                win Float32) ENGINE = Memory"""
        )
        
        for game in games.raw.find():
            id = game['id']  
            logger.info(id)
            count = clickhouse_client.execute(f"SELECT count(*) FROM profile WHERE id={id}")
            if count[0][0]==0:
                df_profile = get_game_profile(game)
                if df_profile is not None:                
                    clickhouse_client.execute("INSERT INTO profile VALUES", df_profile.to_dict('records'))
                    del df_profile
    except Exception as e:
        logger.error(e)
    finally:
        mongo_client.close()        


if __name__ =='__main__':
    while True:
        main()
        time.sleep(1)
