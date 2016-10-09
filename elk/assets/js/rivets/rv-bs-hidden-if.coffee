rivets.binders['hidden-if'] = (el, value) ->
  $el = $ el
  if not value
    $el.removeClass 'hidden'
  else
    $el.addClass 'hidden'

rivets.binders['hidden-unless'] = (el, value) ->
  $el = $ el
  if value
    $el.removeClass 'hidden'
  else
    $el.addClass 'hidden'
