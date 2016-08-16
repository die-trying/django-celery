#
# For working with this plugin, control should define `data-dismiss-after-cancellation`
# with a selector of element, which to remove after successful unscheduling
#
$.fn.class_cancel = () ->
  $(this).on 'click', () ->
    $btn = $ this
    class_id = $btn.data 'class-id'
    if $btn.data 'dismiss-after-cancellation'
      $dismiss = $ $btn.data 'dismiss-after-cancellation'

    $popup = $ '.class_cancel-popup-container'

    if $popup.length  # if popup is loaded — simply show the popup
      $popup.modal 'show'

    else  # for the fist time — load popup contents from the server
      $('body').append('<div class="modal fade class_cancel-popup-container" role="dialog"></div>')
      $popup = $ '.class_cancel-popup-container'  # reload popup from DOM
      url = "/market/cancel/#{ class_id }/popup"
      $popup.load url, () ->
        $popup.modal 'show'

        # request the server when user has confirmed actual cancellation
        $('button[data-class-cancellation-url]').on 'click', () ->
          url = $(this).data 'class-cancellation-url'
          $.getJSON url, (response) ->
            $popup.modal 'hide'
            if $dismiss?
              $dismiss.remove()

      $popup.on 'shown.bs.modal', () ->
        $(document).on 'keyup', (e) ->  #close popup on ESC
          return if e.keyCode isnt 27
          $(document).off 'keyup'
          $popup.modal 'hide'


    return false


$('.class_cancel').class_cancel()
