# pager_duty_stats
Gathering and Aggregating Pager Duty Statistics

# API Token
1. Generate an api token from PagerDuty (My Profile -> User Settings -> Create API User Token)
2. Stick it in a file in the main directory of this repo called `.api_key`

# Building
make build

# Testing
make test

# Fetching & Aggregating All Stats
make fetch_all

# Fetching & Aggregating Some Stats (good for testing)
make fetch_some
