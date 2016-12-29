#
# Init sentry.io frontend-error logging
#

raven = Raven.config Project.helpers.raven_dsn()
raven.install()