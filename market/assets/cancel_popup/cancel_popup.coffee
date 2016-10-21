#
# For working with this plugin, control should define `data-dismiss-after-cancellation`
# with a selector of element, which to remove after successful unscheduling
#

$('.class_cancel').on 'click', (e) ->
  $btn = $ e.target

  class_id = $btn.data 'class-id'
  $popup = $ '.class_cancel-popup-container'


  $popup.load "/market/cancel/#{class_id}/popup", () ->
    $popup.modal 'show'

    # request the server when user has confirmed actual cancellation
    $('button[data-class-cancellation-url]').on 'click', (e) ->
      $this = $ e.target

      $this.button 'loading'

      url = $this.data 'class-cancellation-url'
      $.getJSON url, (response) ->
        $popup.modal 'hide'
        $this.button 'reset'

        $('.dismiss-after-class-cancellation').remove()

        # reset 'Plan another lesson' to 'Plan a lesson'
        $('.homepage-big-blue-button .load_schedule_popup').html 'Plan a lesson'
        # sorry :(

  e.preventDefault()
