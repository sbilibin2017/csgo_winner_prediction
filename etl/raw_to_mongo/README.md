# CSGO GAMES ETL RAW -> MONGO

## description:
Checks new games in parser and loads them to database(mongodb)

## build:
1. clone repository
2. replace ```.env``` -> ```.env.example```, ```env.example``` -> ```env``` 
3. build ```docker-compose -f docker-compose.dev.yaml up --build```