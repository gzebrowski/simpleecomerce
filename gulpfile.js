var gulp = require('gulp'),
  plugins = require("gulp-load-plugins")({lazy: false}),
  sass = require('gulp-sass'),
  // plumber = require('gulp-plumber'),
  //rev = require('gulp-rev'),
  runSequence = require('run-sequence');

var onError = function (err) {
  console.log('\007' + err);
};

gulp.task('sass', function () {
  return gulp.src(['./static/sass/style.scss'])
    .pipe(sass().on('error', function (err) {
        onError(err);
        this.emit('end');
    }))
    .pipe(gulp.dest('./static/css/'));
});

gulp.task('watch', function () {
  gulp.watch('./static/sass/**/*.scss', function() {runSequence('sass'); });

});
// task default: for developping process
gulp.task('default', function() {runSequence('sass', 'watch'); });

// task build: for production
gulp.task('build', function() {runSequence('sass'); });

