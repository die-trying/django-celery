class Controller
  load_popup: (timeline_entry_id) ->
    $('body').append '<div class="modal fade timeline-entry-popup-container" role="dialog"></div>'

    @popup = $ '.timeline-entry-popup-container'

    @popup.load "/market/schedule/#{timeline_entry_id}", () =>
      @open_popup()

  open_popup: () ->
    @popup.modal 'show'




$('.load-timeline-entry-popup').on 'click', (e) ->
  e.preventDefault()
  c = new Controller
  $this = $ this


  c.load_popup $this.data 'entry-id'