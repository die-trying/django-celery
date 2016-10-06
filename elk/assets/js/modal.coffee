$('.modal').on 'show.bs.modal', () ->
  # close all modals on ESC globally
  $modal = $ this

  $(document).on 'keyup', (e) ->  #close popup on ESC
    return if e.keyCode isnt 27
    $(document).off 'keyup'
    $modal.modal 'hide'
