class Controller
  # This controls the first screen — teacher or lesson selection
  constructor: () ->
    @model = new Project.models.SchedulePopupModel(
      lesson_type = $('.schedule-popup__filters input[name=lesson_type]').val()
      date = $('.schedule-popup__filters select').val()
      query_type = $('.schedule-popup__filters .btn-group label:first-child input').data 'query-type'
    )

    @model.bind 'update', () =>
      @bind_slot_buttons()

    @bind_filters()
    @mark_active_lesson()
    @hide_filter_without_options()

    @view_main = rivets.bind $('.schedule-popup__content'), {model: @model}
    @view_footer = rivets.bind $('.schedule-popup__footer'), {c: this}

    @submit = 'disabled'   # can the form be submitted
    @response = undefined  # server response to time validation
    @step2_url = ''        # server url to validate time and submit form

  bind_filters: () ->
    $('.schedule-popup__filters input').on 'change', (e) =>
      @model.lesson_type = e.target.value
      @model.query_type = e.target.dataset.queryType
      @model.from_json()
      @submit = 'disabled'


    $('.schedule-popup__filters select').on 'change', (e) =>
      @model.date = $('.schedule-popup__filters select').val()
      @model.from_json()
      @submit = 'disabled'

  bind_slot_buttons: () ->
    $('.schedule-popup__time-label').on 'click', (e) =>
      target_input = e.target.getElementsByClassName('schedule-popup__time-selector')[0]
      @step2_url = @model.submit_url(target_input.dataset)

      @uncheck_all_slots $(target_input).attr 'name'  # uncheck all other time slots

      @check_server()

    label_hovered = false
    $('label.btn').hover () ->
      label_hovered = true
    , () ->
      label_hovered = false

    $('.schedule-popup').on 'click', () =>  # uncheck all time slots when clicking outside them
      @uncheck_all_slots() if not label_hovered

    $('.schedule-popup__submit').on 'click', () ->
      window.location.href = $(this).attr 'data-step2-url'

  check_server: () ->
    url = @step2_url + '?check'

    $.getJSON url, (response) =>
      @response = response
      if response.result
        @submit = ''
      else
        @submit = 'disabled'

  mark_active_lesson: () ->
    $('.schedule-popup__filter .btn-group label:first-child input').click()
    $('.schedule-popup__filter .btn-group label:first-child').addClass 'btn-active'

  uncheck_all_slots: (except_one='non-existant-name') ->
    # trick with parameter is used for ability to uncheck all labels, or except one from unchecking with one method

    if except_one is 'non-existant-name'  # disable user's submit if we r unchecking all slots
      @submit = 'disabled'
      @response = undefined

    $(".schedule-popup__time-selector").not("[name=#{ except_one }]").each () ->
      $(this).parent('label.btn.active').each () ->
        $(this).button 'toggle'
        .removeClass 'active'

  hide_filter_without_options: () ->
    $z = $ '.lesson_type>label'
    if $z.length is 1
      $z.addClass 'hidden'

  destroy: () ->
    @view_footer.unbind()
    @view_main.unbind()   # Disarm rivets.
                          # If the popup will be opened one more time, the new controller will arm in one more time

    $('.schedule-popup-container').load '/market/schedule/step1/', () ->
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
