gulp = require 'gulp'
$ = require('gulp-load-plugins')()
nib = require 'nib'
run_sequence = require 'run-sequence'
lazypipe = require 'lazypipe'

config = {
  production: false
  css:
    frontend: ['*/assets/**/*.styl', '!*/assets/admin/**/*']
    admin: '*/assets/admin/**/*.styl'
  js:
    frontend: ['*/assets/**/*.coffee', '!*/assets/admin/**/*']
    admin: '*/assets/admin/**/*.coffee'
  static:
    master: '//static.elk.today/'
    staging: '//static-staging.elk.today/'
    dev: '/static/'
  vendor_dir: './elk/static/vendor/'
  js_vendor_files: './build/js-vendor-files.json'
  css_vendor_files: './build/css-vendor-files.json'
}

static_path = () ->
  if process.env.CIRCLE_BRANCH
    configured_static_path = config.static[process.env.CIRCLE_BRANCH]
    if configured_static_path? then configured_static_path else config.static.dev

  else
    config.static.dev

css_pre_process = lazypipe()
  .pipe () ->
    $.if !config.production, $.sourcemaps.init()
  .pipe $.stylint
  .pipe $.stylint.reporter
  .pipe $.stylint.reporter, 'fail', { failOnWarning: true }
  .pipe $.stylus,
    use: nib()
    rawDefine:
      static: static_path()

css_post_process = lazypipe()
  .pipe $.uglifycss
  .pipe () ->
    $.if !config.production, $.sourcemaps.write()

js_pre_process = lazypipe()
  .pipe () ->
    $.if !config.production, $.sourcemaps.init()
  .pipe $.coffeelint
  .pipe $.coffeelint.reporter
  .pipe $.coffee

js_post_process = lazypipe()
  .pipe $.uglify
  .pipe () ->
    $.if !config.production, $.sourcemaps.write()

vendor_files = (file_list) ->
  files = require file_list
  files.map (f) ->
    f = config.vendor_dir + f
    f.replace '//', '/'

gulp.task 'css', ['css:vendor'], () ->
  gulp.src config.css.frontend
  .pipe css_pre_process()
  .pipe $.concat 'app.css'
  .pipe css_post_process()
  .pipe gulp.dest './elk/static/css/'

gulp.task 'css:admin', () ->
  gulp.src config.css.admin
  .pipe css_pre_process()
  .pipe $.concat 'admin.css'
  .pipe css_post_process()
  .pipe gulp.dest './elk/static/css/'

gulp.task 'css:vendor', () ->
  gulp.src vendor_files config.css_vendor_files
  .pipe $.concat 'vendor.css'
  .pipe gulp.dest './elk/static/css/'

gulp.task 'js', ['js:vendor'], () ->
  gulp.src config.js.frontend
  .pipe js_pre_process()
  .pipe $.concat 'app.js'
  .pipe js_post_process()
  .pipe gulp.dest './elk/static/js/'

gulp.task 'js:admin', () ->
  gulp.src config.js.admin
  .pipe js_pre_process()
  .pipe $.concat 'admin.js'
  .pipe js_post_process()
  .pipe gulp.dest './elk/static/js/'

gulp.task 'js:vendor', () ->
  gulp.src vendor_files config.js_vendor_files
  .pipe $.if '!*.min.js', $.uglify()
  .pipe $.concat 'vendor.js'
  .pipe gulp.dest './elk/static/js/'

gulp.task 'default', ['css', 'js', 'css:admin', 'js:admin'], () ->
  gulp.watch config.css.frontend, ['css']
  gulp.watch config.js.frontend, ['js']

  gulp.watch config.css.admin, ['css:admin']
  gulp.watch config.js.admin, ['js:admin']

gulp.task 'production', () ->
  $.util.log 'Building production assets with external static path', \
    $.util.colors.magenta static_path()

  config.production = true
  run_sequence ['css', 'js', 'css:admin', 'js:admin']
