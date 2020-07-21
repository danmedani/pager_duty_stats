
# pager_duty_stats

[![Build Status](https://travis-ci.com/danmedani/pager_duty_stats.svg?branch=master)](https://travis-ci.com/github/danmedani/pager_duty_stats)

Aggregates PagerDuty incident statistics to help you figure out what's happening with your on-call.


# Auth
Oauth is coming soon - for now you'll need to enter your PagerDuty API Token into the site. The website is totally stateless at this point, so we aren't saving any tokens on the backend.

To generate an api token from PagerDuty, go to My Profile -> User Settings -> Create API User Token

# Setting Up Dev Environment
Steps to setting up dev environment (you'll need `git`, `npm`, and `python3`:
1) `git clone https://github.com/danmedani/pager_duty_stats.git`
2) `cd pager_duty_stats/`
3) `make init` (builds front and back ends)
4) `make web` (launches site locally at `http://localhost:3031/`)

If you are working on the backend, it usually helps to be in the virtualenv:
`source virtual_env/bin/activate`

If you are working with the fronend, it's super useful to have webpack running in dev mode (it will automatically pick up changes):
`make webpackdev`

# Contributing
This is a small personal project, but I'd love to see it grow. Feel free to make an issue or a pull request!
