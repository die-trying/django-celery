#
# Simple plugin for duration input fields
#
$.fn.duration = () ->
  $field = $(this)
  format = () ->
    d = $field.val()
    d = d.replace /:\d*$/, '' if d.match /^\d+:\d+:/
    d = d.replace /^0:/, '00:'
    $field.val d

  $field.on 'change', format
  format()

  $field.on 'keyup', (e) ->
    if $field.val().match /^\d{2}$/
      if e.keyCode isnt 8
        $field.val($field.val() + ':')

    if $field.val().match /^\d{3}$/
      d = $field.val()
      a = d.split ''
      $field.val(a[0] + a[1] + ':' + a[2])
