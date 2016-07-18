$.fn.load_schedule_popup = () ->
  popup_loaded = () ->
    $('.selectpicker').selectpicker()

  $(this).on 'click', () ->
    $popup = $ $(this).attr 'data-target'
    $popup.load '/timeline/schedule/', popup_loaded


$(document).ready () ->
  $('.load_schedule_popup').load_schedule_popup()
