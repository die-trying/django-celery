$.fn.load_user_calendar = () ->
  $popup = $ '.user-calendar__add-popup'

  this.fullCalendar
    events: this.attr 'data-calendar'
    dayClick: (date, jsEvent, view) ->
      $popup.load $popup.attr('data-src'), null, popupLoaded
      $popup.css
        display: 'block'
        top: jsEvent.pageY,
        left: jsEvent.pageX
      $.popup.popover()

popupLoaded = () ->
  $('.timeline-entry-form').each () ->
    $form       = $ this
    $event_type = $ '#id_event_type', $form
    $event      = $ '#id_event_id', $form
    $duration   = $ '#id_duration', $form

    $event_type.on 'change', () ->  # update event selector
      lessons = $form.attr 'data-lessons'
      lessons += "?event_id=" + $(this).val()

      $.getJSON lessons, (data) ->
        $event.html ''
        $event.append \
          sprintf '<option value="%d" data-duration="%s">%s</option>', \
          lesson.id, lesson.duration, lesson.name \
            for lesson in data
        $event.change()  # trigger update of a default duration

      $event.on 'change', () ->  # set default duration of a selected lesson
        option = $ 'option:selected', this
        $duration.val option.attr 'data-duration'


$(document).ready ->
  $('.user-calendar').load_user_calendar()
