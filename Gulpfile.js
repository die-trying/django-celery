var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var nib = require('nib')

gulp.task('css', function(){
    return gulp.src('*/assets/css/*.styl')
        .pipe($.sourcemaps.init())
        .pipe($.concat('elk.styl'))
        .pipe($.stylus({
            use: [nib()]
        }))
        .pipe($.sourcemaps.write())
        .pipe(gulp.dest('./elk/static/css/'));
});

gulp.task('default', function(){
    return gulp.watch('*/assets/css/*.styl', ['css']);
});
