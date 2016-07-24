class Model extends MicroEvent
  constructor: (@lesson_type, @date) ->
    @url = "/teachers/%s/slots.json?lesson_type=%d"
    @from_json()

  class Teacher
    constructor: (@name, @profile_photo, @description) ->
      @slots = []

  from_json: () ->
    url = sprintf @url, @date, parseInt @lesson_type
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
            teacher: t.id
            time: s
          }
          teacher.slots.push slot
        @teachers.push teacher
        @trigger 'update'

  build_step2_url: (data) ->
    data.contenttype = 'type'  # flex scope, we support planning only be lesson type yet
    "/hub/schedule/step02/#{ data.teacher }/#{ data.contenttype }/#{ data.lesson }/#{ data.date }/#{ data.time }/"

class Controller
  # This controls the first screen — teacher or lesson selection
  constructor: () ->
    @model = new Model(
      lesson_type = $('.schedule-popup__filters input[name=lesson_type]').val()
      date = $('.schedule-popup__filters select').val()
    )

    @model.bind 'update', () =>
      @bind_slot_buttons()

    @bind_filters()
    @mark_active_lesson()

    @view_main = rivets.bind $('.schedule-popup__content'), {model: @model}
    @view_footer = rivets.bind $('.schedule-popup__footer'), {c: this}

    @submit = 'disabled'
    @step2_url = ''

  bind_filters: () ->
    $('.schedule-popup__filters input').on 'change', (e) =>
      @model.lesson_type = e.target.value
      @model.from_json()

    $('.schedule-popup__filters select').on 'change', (e) =>
      @model.date = $('.schedule-popup__filters select').val()
      @model.from_json()

  bind_slot_buttons: () ->
    $('.schedule-popup__time-selector').on 'change', (e) =>
      @step2_url = @model.build_step2_url(e.target.dataset)
      @submit = ''



  mark_active_lesson: () ->
    $('.schedule-popup__filter .btn-group label:first-child input').click()
    $('.schedule-popup__filter .btn-group label:first-child').addClass 'btn-active'

  destroy: () ->
    # this is for rivets to return DOM to the initial state
    @model.teachers = []
    @model.loaded = false

    @viww_footer.unbind()
    @view_main.unbind()   # Disarm rivets.
                          # If the popup will be opened one more time, the new controller will arm in one more time

    $('.schedule-popup-container').load '/hub/schedule/step1/', () ->
      $('.selectpicker').selectpicker()  # arm bootstrap-selectpicker in the popup


c = ''

$('.schedule-popup-container').on 'show.bs.modal', () ->
  c = new Controller

  $(document).on 'keyup', (e) ->  #close popup on ESC
    return if e.keyCode isnt 27
    $(document).off 'keyup'
    $('.schedule-popup-container').modal 'hide'

$('.schedule-popup-container').on 'hidden.bs.modal', () ->
  c.destroy()
