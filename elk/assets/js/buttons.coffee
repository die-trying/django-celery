$('button[data-url]').click ->
  window.location.href = $(this).attr 'data-url'

$('button[data-popup-url]').click ->
  $popup = $ $(this).attr 'data-target'
  $popup.load $(this).attr 'data-popup-url'
