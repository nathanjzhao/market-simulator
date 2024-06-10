# Trading Bot Simulator

This was a little hobby project I had inspired by my time messing around with the ETC Challenge while at Jane Street FTTP. I couldn't find any other Feel free to try this out and

# Initialization Instructions

git clone this repository, then:

```
yarn add
cd apps/backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then, for database/auth features, setup `.env` with 
```
SQLALCHEMY_DATABASE_URL=sqlite:///./backend/sql_app.db (example)
JWT_SECRET=some-jwt-secret
```

You will also need to setup other environmental variables and an Upstash instance for Apache Kafka


# TODO
