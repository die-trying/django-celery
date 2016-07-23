class Model
  constructor: (lesson_type, date) ->
    @url = "/teachers/%s/slots.json?lesson_type=%d"
    @from_json(lesson_type, date)

  class Teacher
    constructor: (@name, @profile_photo, @description) ->
      @slots = []

  from_json: (lesson_type, date) ->
    url = sprintf @url, date, parseInt(lesson_type)
    @teachers = []
    @loaded = false
    $.getJSON url, (data) =>
      @loaded = true
      for t in data
        teacher = new Teacher(
          name = t.name
          profile_photo = t.profile_photo
          description = t.announce
        )

        for s in t.slots
          time_for_id = s.replace ':', '_'
          slot = {
            id: "teacher_#{ t.id }_time_#{ time_for_id }"
            time: s
          }
          teacher.slots.push slot
        @teachers.push teacher

class Controller
  constructor: () ->
    @lesson_type = $('.schedule-popup__filters input[name=lesson_type]').val()
    @date = $('.schedule-popup__filters select').val()

    @model = new Model(
      lesson_type = @lesson_type
      date = @date
    )

    @bind_events()
    @mark_active_lesson()

    rivets.bind($('.schedule-popup__content'), {model: @model})

  bind_events: () ->
    $('.schedule-popup__filters input').on 'change', (e) =>
      @lesson_type = e.target.value
      @model.from_json(@lesson_type, @date)

    $('.schedule-popup__filters select').on 'change', (e) =>
      @date = $('.schedule-popup__filters select').val()
      @model.from_json(@lesson_type, @date)

  mark_active_lesson: () ->
    $('.schedule-popup__filter .btn-group label:first-child input').click()
    $('.schedule-popup__filter .btn-group label:first-child').addClass 'btn-active'

$('.schedule-popup-container').on 'show.bs.modal', () ->
  c = new Controller
