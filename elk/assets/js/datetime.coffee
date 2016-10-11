#
# jQuery methods for 3 fields:
#   - $('#field').applyTimePicker() based on https://github.com/jonthornton/jquery-timepicker
#   - $('#field').applyDatepicker() based on https://github.com/eternicode/bootstrap-datepicker
#   - $('#field').applyDurationSelector() based on own simple plugin (see duration.coffee)
#

$.fn.applyTimepicker = () ->
  $(this).timepicker
    timeFormat: 'H:i',
    scrollDefault: 'now'

$.fn.applyDatePicker = () ->
  $(this).datepicker
    autoclose: true,
    startDate: Date(),
    todayBtn: 'linked',
    todayHighlight: true

$.fn.applyDurationSelector = () ->
  $(this).duration()
