# Automatically set width of all bootstrap progressbars on the page
# https://getbootstrap.com/components/#progress

$.fn.update_bootstrap_progressbar = () ->
  $bar = $ this
  max = parseInt $bar.attr 'aria-valuemax'
  now = parseInt $bar.attr 'aria-valuenow'
  width = Math.round now / max * 100

  $bar.css 'width', width + '%'

$('.progress .progress-bar').each () ->
  $(this).update_bootstrap_progressbar()
