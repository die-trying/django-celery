$selector = $ '.add-a-student__selector'
$btn = $ '.add-a-student__add-btn'
$selector.selectpicker()

$selector.on 'change', () ->
  if $(this).val() and $(this).val().length
    $btn.removeClass 'disabled'
  else
    $btn.addClass 'disabled'

$btn.on 'click', () ->
  window.location.href = $selector.val()
