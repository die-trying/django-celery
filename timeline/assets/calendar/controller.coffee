POPUP_WIDTH_PX = 300

class Controller
  constructor: () ->
    @popup = $ '.user-calendar__add-popup'

  open: (type='create', x, y, pk=null, date=null) ->
    @model = new Project.models.TimelineEntryModel(
      username = @popup.attr 'data-username'
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

    # set beauty prompt in the lesson type selector
    $('#id_lesson_type option:first-child').text '(Lesson type)'

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

$('.user-calendar').each () ->
  c = new Controller
  $(this).fullCalendar
    events: $(this).attr 'data-calendar' # from JSON
    dayClick: (date, jsEvent, view) ->
      c.open 'create', jsEvent.pageX, jsEvent.pageY, null, date=date.format('YYYY-MM-DD')
    eventClick: (calEvent, jsEvent, view) ->
      c.open 'update', jsEvent.pageX, jsEvent.pageY, calEvent.id
