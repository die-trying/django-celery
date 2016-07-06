var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var nib = require('nib')

gulp.task('css', function(){
    return gulp.src('*/assets/css/*.styl')
        .pipe($.sourcemaps.init())
        .pipe($.stylus({
            use: [nib()]
        }))
        .pipe($.concat('app.css'))
        .pipe($.sourcemaps.write())
        .pipe(gulp.dest('./elk/static/css/'));
});

gulp.task('js', function(){
    return gulp.src('*/assets/js/*.coffee')
        .pipe($.sourcemaps.init())
        .pipe($.coffee({bare: true}))
        .pipe($.concat('app.js'))
        .pipe($.sourcemaps.write())
        .pipe(gulp.dest('./elk/static/js/'));
});

gulp.task('default', function(){
    gulp.watch('*/assets/css/*.styl', ['css']);
    gulp.watch('*/assets/js/*.coffee', ['js']);
});
