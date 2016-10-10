$.fn.numonly = () ->

  blink = ($el) ->  # blink with error
    $group = $el.parents('.control-group.form-row')
    $group.addClass 'error'
    window.setTimeout () ->
      $group.removeClass 'error'
    , 100

  $(this).on 'keydown', (e) ->
    if $.inArray(e.keyCode, [46, 8, 9, 27, 13, 110]) > 0
      return

    if e.key.match /Shift|Control|Alt|Meta/
      return

    if e.key.match /^\d|\:$/
      return

    blink $ this

    e.preventDefault()


$('input.numonly').numonly()
