$('.load-timeline-entry-popup').on 'click', (e) ->
  e.preventDefault()

  timeline_entry_id = $(this).data 'entry-id'

  $popup = $ '.timeline-entry-popup-container'

  $popup.load "/market/schedule/#{timeline_entry_id}", () ->
    $popup.modal 'show'