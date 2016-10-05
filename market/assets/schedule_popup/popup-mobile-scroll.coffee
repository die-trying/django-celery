#
# Spies the scroll of scheduling popup
# Hides filters when the position X is reached
#

$('.schedule-popup-container').on 'show.bs.modal', () ->
  if $('body').hasClass 'desktop'
    return

  $('.schedule-popup__content').on 'scroll', () ->
    $content = $ this
    $filters = $content.siblings('.schedule-popup__filters').find '.lesson_type'

    position = $content.scrollTop()

    if position > 150 and $filters.css('display') isnt 'none'
      $filters.css 'display', 'none'
    else if position < 20
      $filters.css 'display', 'block'
