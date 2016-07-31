$('.calendar__teacher-selector').on 'change', () ->
  # Replace window href on change of current teacher

  $this = $ this
  initial_username = $('option:first-child', $this).val()
  selected_username = $this.val()
  new_url = window.location.href.replace "/#{ initial_username }/", "/#{ selected_username }/"
  window.location.href = new_url
