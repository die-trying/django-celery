class Model extends MicroEvent
  # This model represents a state of form. State should be updated by
  # Model.update_state('what_has_changed')

  constructor: (@username, @pk=null, date=null) ->
    @_set_err('none')
    @urls = {
      create: '/timeline/%s/create/'
      update: '/timeline/%s/%d/update/'
      check_overlap: '/timeline/%s/check_entry/%s/%s'
    }
    @_set_date(date) if date?

    @bind 'lessons_fetched', () =>
      @set_lesson()
      @check_entry()

    @bind 'lesson_set', () =>
      @check_entry()

  update_state: (what_has_changed) ->

    @lesson_type = $('#id_lesson_type', @form).val()
    @initial_lesson_id = parseInt $('#initial_lesson', @form).val()

    switch what_has_changed
      when 'lesson_type' then @fetch_lessons()
      when 'lesson_id' then @set_lesson()
      when 'start', 'end' then @check_entry()

  fetch_lessons: () ->
    # Get available lessons from server, based on selected lesson_type
    url = @form.attr 'data-lessons-url'
    url += '?lesson_type=' + @lesson_type
    @lessons = []
    $.getJSON url, (response) =>
      for lesson in response
        lesson.selected = ''
        lesson.selected = ' selected ' if lesson.id is @initial_lesson_id
        lesson.duration = @_format_duration lesson.duration

        @lessons.push lesson

      @trigger 'lessons_fetched'

  set_lesson: () ->
    selected_lesson_id = parseInt $('#id_lesson_id').val()
    for lesson in @lessons
      if lesson.id is selected_lesson_id
        @lesson = lesson
        @trigger 'lesson_set'

  check_entry: () ->
    # Check with server if current time (start_time, start_date and duration) are
    # overlapping with already existant timeline entries

    @_set_err('none')

    return if not @lesson # no need to check duration if we don't know a lesson
    return if @lesson.id is @initial_lesson_id  # with initial lesson, there is no need to check anything

    @start = @_get_start_time()
    @end = @_get_end_time()

    return if not @start? or not @end?

    url = sprintf @urls['check_overlap'], @username, @start, @end
    $.getJSON url, (response) =>
      if not response.is_fitting_hours
        @_set_err('besides_hours')
      if response.is_overlapping
        @_set_err('overlap')

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
    else
      @has_err = true
      switch err_type
        when 'overlap' then @overlap = true
        when 'besides_hours' then @besides_hours = true

Project.models.TimelineEntryModel = Model
