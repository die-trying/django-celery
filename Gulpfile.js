var gulp = require('gulp');
var $ = require('gulp-load-plugins')();

gulp.task('css', function(){
    return gulp.src('*/assets/css/*.styl')
        .pipe($.sourcemaps.init())
        .pipe($.concat('elk.styl'))
        .pipe($.stylus())
        .pipe($.sourcemaps.write())
        .pipe(gulp.dest('./elk/static/css/'));
});

gulp.task('default', function(){
    return gulp.watch('*/assets/css/*.styl', ['css']);
});
