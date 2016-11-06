POPUP_WIDTH_PX = 300

class Controller
  constructor: () ->
    @popup = $ '.user-calendar__add-popup'

  open: (type='create', x, y, pk=null, date=null) ->
    @model = new Project.models.TimelineEntryModel(
      username = @popup.attr 'data-username'
      userid = @popup.attr 'data-userid'

      pk = pk
      date = date
    )
    popup_url = sprintf @model.urls[type], @model.username, pk
    @load_popup popup_url, x, y

  load_popup: (url, x, y) ->
    @popup.load url, () =>
      [x, y] = @_get_popup_coordinates x, y
      @popup.removeClass 'hidden'
      .css
        left: x
        top: y

      @popup_loaded()

  popup_loaded: () ->
    @bind_events()
    @prettify()
    @arm_popup_closing_logic()

    @model.update_state 'lesson_type' if @model.pk?  # if we have a pk — load lessons

  bind_events: () ->
    $form = $ '.timeline-entry-form form'

    @model.form = $form
    rivets.bind $form, {model: @model}

    $('#id_lesson_type').on 'change', () =>
      @model.update_state 'lesson_type'

    $('#id_lesson_id').on 'change', () =>
      @model.update_state 'lesson_id'

    $('#id_start_0, #id_start_1').on 'change', (e) =>
      @model.update_state 'start'

  prettify: () ->
    # time and date selector
    $('#id_start_0').applyDatePicker()
    $('#id_start_1').applyTimepicker()

    # set selected date
    if @model.date?
      $('#id_start_0').datepicker 'setDate', @model.date
      $('#id_start_0').val @model.date

    # set default value for the time. It better would be set by now + 1h
    if not $('#id_start_1').val()
      $('#id_start_1').val @_default_time()

    $('#id_duration').focus().blur()  # suddenly safari does not clear the placeholder 'HH:MM' without that

    # apply selectpicker
    $('#id_lesson_type, #id_lesson_id').selectpicker()
    @model.bind 'lessons_fetched', () ->
      $('#id_lesson_id').selectpicker 'refresh'

  arm_popup_closing_logic: () ->
    $('.user-calendar__close_popup').on 'click', () =>
      @_close_popup()

    $(document).on 'keyup', (e) =>
      return if e.keyCode isnt 27
      $(document).off 'keyup'
      @_close_popup()

  _close_popup: () ->
    @popup.addClass 'hidden'

  _get_popup_coordinates: (x, y) ->
    # Popup should be open to the left when it is near the right edge of viewport
    # This method recalculates popup coordinates from the actual clicked position
    if x + POPUP_WIDTH_PX >= $(window).width()
      x -= POPUP_WIDTH_PX
    [x, y]

  _default_time: () ->
    t = moment()
    t.add 1, 'h'
    t.format 'HH:30'

$('.user-calendar').each () ->
  c = new Controller
  $(this).fullCalendar
    timezone: 'local'
    eventSources: [
      url: $(this).attr 'data-calendar' # from JSON
      startParam: 'start_0'
      endParam: 'start_1'
    ]
    dayClick: (date, jsEvent, view) ->
      c.open 'create', jsEvent.pageX, jsEvent.pageY, null, date=date.format('YYYY-MM-DD')
    eventClick: (calEvent, jsEvent, view) ->
      c.open 'update', jsEvent.pageX, jsEvent.pageY, calEvent.id
