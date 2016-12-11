# Simple plugin to allow input only of numbers.
# Take a look at the last line — it's the usage example.

$.fn.numonly = () ->

  blink = ($el) ->  # blink with error
    $group = $el.parents('.control-group.form-row')
    $group.addClass 'error'
    window.setTimeout () ->
      $group.removeClass 'error'
    , 100

  $(this).on 'keypress', (e) ->
    if $.inArray(e.keyCode, [46, 8, 9, 27, 13, 110]) > 0
      return

    if not e.key?
      return
    if e.key.match /Shift|Control|Alt|Meta/
      return

    if e.key.match /^\d|\:$/
      return

    blink $ this

    e.preventDefault()


$('input.numonly').numonly()
