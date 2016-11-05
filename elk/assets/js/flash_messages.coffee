$(document).on 'ready', () ->
  window.setTimeout () ->
    $('.flash-message.alert').alert 'close'
  , 2000
