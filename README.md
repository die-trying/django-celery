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

### Frontend

#### CoffeeScript
All frontend programming should be done in [CoffeeScript](http://coffeescript.org). You can learn it in 3 hours, and it will save you nearly 30% of code by removing plenty of JS boilerplate. The price is a slightly bigger cognitive load, but the absence of the boilerplate worth it.

#### Stylus
All CSS is written in Stylus. You event don't need to learn it — just omit everything boilerplate-like: `{`, `}`, `:` and `;`

#### Global namespace
CoffeeScript has a wonderful protector from polluting global namespace — it wraps every file like this:
```javascript
(function(){
    # your code here
})()
```
So you can't pollute global namespace even if you want it.
When you really need to publish something globally, you can use the `Project` objects. It is allowed to store Models, Controllers and Helpers there, like this:
```coffeescript
class Model extends MicroEvent:
    constructor (@a, @b, @c) ->
        # your wonerful code here

Project.Models.YourModel = Model
```

#### Local assets
By default all vendor assets, located it `build/js-vendor-filters.json` and `build/css-vendor-files.json` are cross-site. If you need a heavy library, you can include it with templatetags `css` and `js`, like this:
```django
{% block css %}
<link rel="stylesheet" href="{% static 'vendor/fullcalendar/dist/fullcalendar.min.css' %}">
{% endblock %}

{% block js %}
<script type="text/javascript" src="{% static 'vendor/fullcalendar/dist/fullcalendar.min.js' %}"></script>
{% endblock %}
```
