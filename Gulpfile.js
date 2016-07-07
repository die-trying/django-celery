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

gulp.task('js:vendor', function(){
    var files = require('./build/js-vendor-files.json');
    var vendor_dir = './elk/static/vendor/'
    files = files.map(function(f){
        f = vendor_dir + f
        f = f.replace('//', '/');
        return f;
    });
    return gulp.src(files)
        .pipe($.concat('vendor.js'))
        .pipe(gulp.dest('./elk/static/js'));
});

gulp.task('default', ['js:vendor'], function(){
    gulp.watch('*/assets/css/*.styl', ['css']);
    gulp.watch('*/assets/js/*.coffee', ['js']);
});

gulp.task('production', ['js', 'css', 'js:vendor']);
