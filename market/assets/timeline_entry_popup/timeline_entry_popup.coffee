$('.load-timeline-entry-popup').on 'click', (e) ->
  e.preventDefault()

  timeline_entry_id = $(this).data 'entry-id'

  $('body').append '<div class="modal fade timeline-entry-popup-container" role="dialog"></div>'
  $popup = $ '.timeline-entry-popup-container'

  $popup.load "/market/schedule/#{timeline_entry_id}", () ->
    $popup.modal 'show'