$frm = $ '.customer-profile form'
$submit = $ 'input[type=submit]', $frm
$birthday = $ 'input[name=birthday]', $frm
$birthday_label = $ '.customer-profile__birthday', $frm

$('input[required]', $frm).on 'keyup', (e) ->
  $parent = $(e.target).parents '.form-group'

  if $frm[0].checkValidity()
    $submit.removeClass 'disabled'
    $parent.removeClass 'has-error'
  else
    $submit.addClass 'disabled'
    $parent.addClass 'has-error'

.keyup()

$birthday.datepicker
  autoclose: true,
  startView: 'years',
  endDate: '-15y',
  todayHighlight: false

.on 'changeDate', (e) ->
  date = moment e.date
  $birthday_label.text date.format 'll'



$('.change-birthday').on 'click', (e) ->
  $birthday.datepicker('show')
  e.preventDefault()
