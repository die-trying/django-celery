$.fn.numonly = () ->
  $(this).on 'keydown', (e) ->
    if $.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) > 0
      return

    if e.keyCode is 65 and (e.ctrlKey or e.metaKey)
      return

    if e.keyCode >= 48 and e.keyCode <= 57
      return

    if e.keyCode is 186  # allow ':'
      return

    e.preventDefault()


$('input.numonly').numonly()
