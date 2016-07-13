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

popupLoaded = () ->
  $('.timeline-entry-form').each () ->
    $form        = $ this
    $lesson_type = $ '#id_lesson_type', $form
    $lesson      = $ '#id_lesson_id', $form
    $duration    = $ '#id_duration', $form

    $lesson_type.on 'change', () ->  # update lesson selector
      lessons = $form.attr 'data-lessons'
      lessons += "?lesson_id=" + $(this).val()

      $.getJSON lessons, (data) ->
        $lesson.html ''
        $lesson.append \
          sprintf '<option value="%d" data-duration="%s">%s</option>', \
          lesson.id, lesson.duration, lesson.name \
            for lesson in data
        $lesson.change()  # trigger update of a default duration

      $lesson.on 'change', () ->  # set default duration of a selected lesson
        option = $ 'option:selected', this
        $duration.val option.attr 'data-duration'


$(document).ready ->
  $('.user-calendar').load_user_calendar()
