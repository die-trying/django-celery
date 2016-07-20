$.fn.load_user_calendar = () ->
  $popup = $ '.user-calendar__add-popup'

  this.fullCalendar
    events: this.attr 'data-calendar'  # load events from JSON

    dayClick: (date, jsEvent, view) ->
      # store clicked date, to load it after popup appears
      $(this).parents('.user-calendar').data 'clickedDay', date

      url = sprintf '/timeline/%s/create/', $popup.attr('data-username')
      $popup.load url, null, popupLoaded
      $popup.css
        display: 'block'
        top: jsEvent.pageY,
        left: jsEvent.pageX

    eventClick: (calEvent, jsEvent, view) ->
      url = sprintf '/timeline/%s/%d/update/', $popup.attr('data-username'), calEvent.id
      $popup.load url, null, popupLoaded
      $popup.css
        display: 'block'
        top: jsEvent.pageY,
        left: jsEvent.pageX

# TODO — escape and click outside a popup should close the popup

popupLoaded = () ->
  $('.timeline-entry-form form').each () ->
    $form        = $ this
    $lesson_type = $ '#id_lesson_type', $form
    $lesson      = $ '#id_lesson_id', $form
    $duration    = $ '#id_duration', $form
    $time        = $ '#id_start_1', $form
    $date        = $ '#id_start_0', $form
    $calendar    = $ '.user-calendar'

    $date.val $calendar.data('clickedDay').format 'L' if $calendar.data 'clickedDay'

    $date.applyDatePicker()

    $time.applyTimepicker()

    $duration.applyDurationSelector()


    # update lesson selector
    $lesson_type.on 'change', () ->
      lessons = $form.attr 'data-lessons'
      lessons += "?lesson_id=" + $(this).val()

      $.getJSON lessons, (data) ->
        $lesson.html ''

        for lesson in data
          lesson.name = sprintf "%s | %d ppl.", lesson.name, lesson.slots if lesson.slots? and lesson.slots isnt 1
          selected = ''
          selected = ' selected ' if $ '#initial_lesson' and lesson.id is $('#initial_lesson').val()

          option = sprintf '<option value="%d" %s data-duration="%s">%s</option>', \
          lesson.id, selected, lesson.duration, lesson.name
          $lesson.append option

        $lesson.change()  # trigger update of a default duration


      # set default duration of a selected lesson
      $lesson.on 'change', () ->
        option = $ 'option:selected', this
        $duration.val option.attr 'data-duration'
        $duration.change()

    # some prettyness
    # i need to use JS here, because to customize Django's SplitDateTimeField
    # i would have to break my brain subclassing it
    $time.attr 'placeholder', 'HH:MM'
    $time.attr 'maxlength', 5
    $time.attr 'required', true

    $duration.attr 'required', true

    $lesson_type.attr 'required', true
    $lesson.attr 'required', true

    $('option:first-child', $lesson_type).text('Choose lesson type')

    $lesson_type.change() if $lesson_type.val()

$(document).ready ->
  $('.user-calendar').load_user_calendar()
