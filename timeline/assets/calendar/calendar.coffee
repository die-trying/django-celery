dateFormat = 'L'
class Model
  constructor: () ->
    @url =
      create: '/timeline/%s/create/'
      update: '/timeline/%s/%d/update/'

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

  update_from_form: ($form) ->
    @form = $form
    @lesson_type = $('#id_lesson_type', @form).val()
    @initial_lesson_id = parseInt $('#initial_lesson', @form).val()

    # update lessons
    @fetch_lessons()
    if @lessons
      for lesson in @lessons
        if lesson.id = $('#id_lesson_id', @form).val()
          @lesson = @_format_duration lesson

    # update start datetime and duration

    start = moment $('#id_start_0').val(), ['L', 'DD/MM/YYYY', 'YYYY-MM-DD']
    @start = start.format('L')


  _format_duration: (lesson) ->
    [h, m, s] = lesson.duration.split ':'
    h = '0' + h if h.length is 1
    lesson.duration = h + ':' + m
    lesson

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
      @popup
      .removeClass 'hidden'
      .css
        top: y
        left: x
      @form = $ '.timeline-entry-form form'

      # bind all
      rivets.bind(@form, {model: @model})
      $('.form-control').on 'change', () =>
        @model.update_from_form @form

      # time and date selector
      $('#id_start_0').applyDatePicker()
      $('#id_start_1').applyTimepicker()

      # set date to the clicked cell in the calendar
      $('#id_start_0').val date if date

      # set beauty prompt in the lesson type selector
      $('#id_lesson_type option:first-child').text '(Choose lesson type)'

      @arm_popup_closing_logic()


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

c = new Controller

$('.user-calendar').each () ->
  $(this).fullCalendar
    events: $(this).attr 'data-calendar' # from JSON
    dayClick: (date, jsEvent, view) ->
      c.load_popup 'create', jsEvent.pageX, jsEvent.pageY, null, date=date.format(dateFormat)
    eventClick: (calEvent, jsEvent, view) ->
      c.load_popup 'update', jsEvent.pageX, jsEvent.pageY, calEvent.id
