$.fn.load_user_calendar = () ->
  this.fullCalendar
    events: this.attr 'data-calendar'

$(document).ready ->
  $('.user-calendar').load_user_calendar()
