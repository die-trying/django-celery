#
# System-wide defaults for bootstrap modal windows:
#  — Close on ESC
#  — Close on press on any button with type = cancel
#

$('.modal').on 'show.bs.modal', () ->
  $modal = $ this

  $(document).on 'keyup', (e) ->  # close popup on ESC
    return if e.keyCode isnt 27
    $(document).off 'keyup'
    $modal.modal 'hide'

  $('button[type=reset]', $modal).on 'click', () ->  # close popup on every button with type=cancel
    $modal.modal 'hide'
