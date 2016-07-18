gulp = require 'gulp'
$ = require('gulp-load-plugins')()
nib = require 'nib'
run_sequence = require 'run-sequence'

config = {
  production: false
  css: '*/assets/**/*.styl'
  js: '*/assets/**/*.coffee'
  vendor_dir: './elk/static/vendor/'
  js_vendor_files: './build/js-vendor-files.json'
  css_vendor_files: './build/css-vendor-files.json'
}

vendor_files = (file_list) ->
  files = require file_list
  files.map (f) ->
    f = config.vendor_dir + f
    f.replace '//', '/'

gulp.task 'css', ['css:vendor'], () ->
  gulp.src config.css
  .pipe $.if !config.production, $.sourcemaps.init()
  .pipe $.stylint()
  .pipe $.stylint.reporter()
  .pipe $.stylint.reporter 'fail', { failOnWarning: true }
  .pipe $.stylus
    use: nib()
  .pipe $.concat 'app.css'
  .pipe $.if config.production, $.uglifycss()
  .pipe $.if !config.production, $.sourcemaps.write()
  .pipe gulp.dest './elk/static/css/'

gulp.task 'css:vendor', () ->
  gulp.src vendor_files config.css_vendor_files
  .pipe $.concat 'vendor.css'
  .pipe gulp.dest './elk/static/css/'

gulp.task 'js', ['js:vendor'], () ->
  gulp.src config.js
  .pipe $.if !config.production, $.sourcemaps.init()
  .pipe $.coffeelint()
  .pipe $.coffeelint.reporter()
  .pipe $.coffee()
  .pipe $.concat 'app.js'
  .pipe $.if config.production, $.uglify()
  .pipe $.if !config.production, $.sourcemaps.write()
  .pipe gulp.dest './elk/static/js/'

gulp.task 'js:vendor', () ->
  gulp.src vendor_files config.js_vendor_files
  .pipe $.concat 'vendor.js'
  .pipe gulp.dest './elk/static/js/'

gulp.task 'default', ['css', 'js'], () ->
  gulp.watch config.css, ['css']
  gulp.watch config.js, ['js']

gulp.task 'production', () ->
  config.production = true
  run_sequence ['css', 'js']
