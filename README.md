# Trading Bot Simulator

This was a little hobby project I had inspired by my time messing around with the ETC Challenge while at Jane Street FTTP. I couldn't find any other platforms where I could upload code to test out trades and see them interact with each other, so I decided to make this.

I'm curious how cloud hosting this efficiently would work, since on the backend I would have a Python queue processing trades 24/7 (supposedly, I couldn't have an external system for orderbook management because of fulfillment delays).

I'm currently focusing more on other projects at the moment, but feel free to try this out and contribute!

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

You will also need to setup other environmental and an Upstash instance for Apache Kafka


# TODO
- [ ] Brush up frontend
- [ ] Create more trading bot example scripts in `frontend/public`
- [ ] Create documentation (with Sphinx?) for `backend/utils/code_tooling`
- [ ] Keep track of fair value when tracking leaderboard with decaying average of recent trades + allow shorting (negative shares)
