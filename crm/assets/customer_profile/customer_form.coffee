#
# Disable flashing of loaded bootstrap-select
#
# Loading is so slooow because of much countries to select

$frm = $ '.customer-profile__form'
$select = $ '.customer-profile__timezone'

$select.on 'loaded.bs.select', () ->
  $frm.children('.form-group').removeClass 'hidden'
