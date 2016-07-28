# ELK Dashboard

[![CircleCI](https://circleci.com/gh/f213/elk-dashboard.svg?style=svg&circle-token=2ce041d53271e60d7afa4efc393f981684951089)](https://circleci.com/gh/f213/elk-dashboard)


[![codecov](https://codecov.io/gh/f213/elk-dashboard/branch/master/graph/badge.svg?token=qDGzPnPA1v)](https://codecov.io/gh/f213/elk-dashboard)

## Configuration

Configuration is stored in `elk/.env`, for examples see `elk/.env.circle`, used during CI.

## Installing

This projects requires python3 (i don't test it on python2). For frontend building you need to install Node.JS. I run tests on OS X and Linux (Circle CI), so the project should work on both systems.

```bash
pip install -r requirements.txt
npm install -g gulp bower
npm install
bower install
```

## Building

Development host:

```bash
./manage.py loaddata crm lessons products teachers
gulp&
./manage.py runserver
```

For building production-ready frontend, run `gulp production`

## Coding style

Please use [flake8](https://pypi.python.org/pypi/flake8) for checking your python code. Imports should be sorted by [isort](https://github.com/timothycrosley/isort). For Stylus and CoffeeScript use stylint and coffeelint respectively (pre-configured in Gulp).

Configure your IDE with respect to [`.editorconfig`](http://editorconfig.org).

All comments and commit messages should be written in English.

Every model and model method should have a docstring.
