
# pager_duty_stats

[![Build Status](https://travis-ci.com/danmedani/pager_duty_stats.svg?branch=master)](https://travis-ci.com/github/danmedani/pager_duty_stats)

Aggregates PagerDuty incident statistics to help you figure out what's happening with your on-call.

https://www.pagerdutystats.com

# Setting Up Dev Environment
Steps to setting up dev environment (you should already have `git`, `npm`, and `python3`)
1) `git clone https://github.com/danmedani/pager_duty_stats.git`
2) `cd pager_duty_stats/`
3) `make init` (builds front and back ends)
4) `source env/bin/activate`
5) `make dev` (launches site locally)

If you are working on the backend, it usually helps to be in the virtualenv:
`source virtual_env/bin/activate`

If you are working with the fronend, it's super useful to have webpack running in dev mode (it will automatically pick up changes):
`make webpackdev`

# Contributing
This is a small personal project, but I'd love to see it grow. Feel free to make an issue or a pull request!
