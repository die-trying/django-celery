$frm = $ '.customer-profile form'
$submit = $ 'input[type=submit]', $frm

$('input[required]', $frm).on 'keyup', (e) ->
  if $frm[0].checkValidity()
    $submit.removeClass 'disabled'
  else
    $submit.addClass 'disabled'

.keyup()
