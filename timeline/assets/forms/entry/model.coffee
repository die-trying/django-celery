class Model extends MicroEvent
  # This model represents a state of form. State should be updated by
  # Model.update_state('what_has_changed')

  constructor: (@username, @pk=null, date=null) ->
    @_set_err('none')
    @urls = {
      create: '/timeline/%s/create/'
      update: '/timeline/%s/%d/update/'
      lessons: '/lessons/%s/type/%s/available.json'
    }
    @_set_date(date) if date?

    @bind 'lessons_fetched', () =>
      @set_lesson()

  update_state: (what_has_changed) ->

    @lesson_type = $('#id_lesson_type', @form).val()
    @initial_lesson_id = parseInt $('#initial_lesson', @form).val()

    switch what_has_changed
      when 'lesson_type' then @fetch_lessons()
      when 'lesson_id' then @set_lesson()

  fetch_lessons: () ->
    # Get available lessons from server, based on selected lesson_type
    url = sprintf @urls['lessons'], @username, @lesson_type
    @lessons = []
    $.getJSON url, (response) =>
      for lesson in response
        lesson.selected = ''
        lesson.selected = ' selected ' if lesson.id is @initial_lesson_id
        lesson.duration = @_format_duration lesson.duration

        @lessons.push lesson

      if @lessons.length is 1  # if we've got only 1 lesson — it should be the default one
        @lessons[0].selected = ' selected '

      @trigger 'lessons_fetched'

  set_lesson: () ->
    selected_lesson_id = parseInt $('#id_lesson_id').val()
    for lesson in @lessons
      if lesson.id is selected_lesson_id
        @lesson = lesson
        @trigger 'lesson_set'

  _get_start_time: () ->
    # Construct start time in server understandable format

    date_str = $('#id_start_0').val() + ' ' + $('#id_start_1').val()

    time = moment date_str, ['MM/DD/YYYY hh:mm', 'YYYY-MM-DD hh:mm']

    if time.isValid()
      time.format 'YYYY-MM-DD HH:mm'
    else
      null

  _get_end_time: () ->
    # Construct end time from start time and duration
    duration_str = $('#id_duration').val()
    [h, m] = duration_str.split ':'
    time = moment @start  # make a copy
    time.add h, 'h'
    .add m, 'm'

    if time.isValid()
      time.format 'YYYY-MM-DD HH:mm'
    else
      null

  _set_date: (date) ->
    date = moment date
    if date.isValid()
      @date = date.format('MM/DD/YYYY')  # flex scope, only latin dates are supported yet

  _format_duration: (old_duration) ->
    [h, m, s] = old_duration.split ':'
    h = '0' + h if h.length is 1
    h + ':' + m

  _set_err: (err_type='none') ->
    if err_type is 'none'
      @has_err = false
      @overlap = false
      @besides_hours = false
      @absent = false
      @has_events = false
    else
      @has_err = true
      switch err_type
        when 'overlap' then @overlap = true
        when 'besides_hours' then @besides_hours = true
        when 'absent' then @absent = true
        when 'has_events' then @has_events = true

Project.models.TimelineEntryModel = Model
