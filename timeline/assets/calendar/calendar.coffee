dateFormat = 'L'
POPUP_WIDTH_PX = 300

class Model
  constructor: () ->
    @url =
      create: '/timeline/%s/create/'
      update: '/timeline/%s/%d/update/'
    @check_overlap_url = '/timeline/%s/check_overlap/%s/%s'
    @_set_err('none')

  get_url: (type) ->
    switch type
      when 'create' then sprintf @url.create, @username
      when 'update' then sprintf @url.update, @username, @pk

  fetch_lessons: () ->
    return if not this.lesson_type
    url = @form.attr 'data-lessons'
    url += '?lesson_type=' + this.lesson_type
    $.getJSON url, (data) =>
      lessons = []
      for lesson in data
        lesson.name = sprintf "%s | %d ppl.", lesson.name, lesson.slots if lesson.slots? and lesson.slots isnt 1
        lesson.selected = ''
        lesson.selected = ' selected ' if lesson.id is @initial_lesson_id
        lessons.push lesson

      @lesson = @_format_duration(lessons[0])  # set default lesson
      @lessons = lessons
      @update_fields()

  update_lessons: ($form) ->
    @form = $form
    @lesson_type = $('#id_lesson_type', @form).val()
    @initial_lesson_id = parseInt $('#initial_lesson', @form).val()
    @lessons = []
    # update lessons
    @fetch_lessons()

  update_fields: () ->
    for lesson in @lessons
      if lesson.id is parseInt $('#id_lesson_id', @form).val()
        @lesson = @_format_duration lesson
    @check_overlap()

  check_overlap: () ->
    return if @lesson? and @lesson.id is @initial_lesson_id

    @_set_err('none')

    datetime = $('#id_start_0').val() + ' ' + $('#id_start_1').val()
    start = moment datetime, ['MM/DD/YYYY hh:mm', 'YYYY-MM-DD hh:mm']
    return if not start.isValid()

    [h, m] = @_get_duration()
    end = moment(start)
    end.add h, 'h'
    .add m, 'm'

    return if start.isSame end
    start = start.format 'YYYY-MM-DD HH:mm'
    end = end.format 'YYYY-MM-DD HH:mm'
    url = sprintf @check_overlap_url, @username, start, end

    $.getJSON url, (response) =>
      if response
        @_set_err('overlap')
      else
        @_set_err('none')

  _format_duration: (lesson) ->
    [h, m, s] = lesson.duration.split ':'
    h = '0' + h if h.length is 1
    lesson.duration = h + ':' + m
    lesson

  _get_duration: () ->
    [h, m] = $('#id_duration').val().split ':'
    [h, m]

  _set_err: (err_type='none') ->
    if err_type is 'none'
      @has_err = false
    else
      @has_err = true
      switch err_type
        when 'overlap' then @is_overlapping = true


class Controller
  constructor: () ->
    @popup = $ '.user-calendar__add-popup'
    @model = new Model

  load_popup: (type, x, y, pk=null, date=null) ->
    @model.username = @popup.attr 'data-username'
    @model.pk = pk
    @model.date = date
    url = @model.get_url type

    @popup.load url, () =>
      [x, y] = @get_popup_coordinates x, y
      @popup
      .removeClass 'hidden'
      .css
        top: y
        left: x
      @form = $ '.timeline-entry-form form'

      # bind all
      rivets.bind(@form, {model: @model})

      # bind events
      $('#id_lesson_type').on 'change', () =>  # load lessons of selected type when type changed
        @model.update_lessons @form
      $('#id_lesson_id').on 'change', () =>  # change other fields (like duration) where the certain lesson is selected
        @model.update_fields()

      @model.update_lessons @form

      $('#id_start_0, #id_start_1').on 'change', () =>
        @model.check_overlap()

      # time and date selector
      $('#id_start_0').applyDatePicker()
      $('#id_start_1').applyTimepicker()

      # set date to the clicked cell in the calendar
      $('#id_start_0').val date if date

      # set beauty prompt in the lesson type selector
      $('#id_lesson_type option:first-child').text '(Choose lesson type)'

      @arm_popup_closing_logic()

  get_popup_coordinates: (x, y) ->  # open popup to the left when it is near the right edge of viewport
    if x + POPUP_WIDTH_PX >= $(window).width()
      x -= POPUP_WIDTH_PX
    [x, y]

  arm_popup_closing_logic: () ->
    $('.user-calendar__close_popup').on 'click', () =>
      @close_popup()

    $(document).on 'keyup', (e) =>
      return if e.keyCode isnt 27
      $(document).off 'keyup'
      @close_popup()

  close_popup: () ->
    @popup.addClass 'hidden'
    @model = new Model


$('.user-calendar').each () ->
  c = new Controller
  $(this).fullCalendar
    events: $(this).attr 'data-calendar' # from JSON
    dayClick: (date, jsEvent, view) ->
      c.load_popup 'create', jsEvent.pageX, jsEvent.pageY, null, date=date.format(dateFormat)
    eventClick: (calEvent, jsEvent, view) ->
      c.load_popup 'update', jsEvent.pageX, jsEvent.pageY, calEvent.id
