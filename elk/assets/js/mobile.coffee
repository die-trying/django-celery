if window.matchMedia('(max-width: 767px)').matches
  $('body').addClass 'mobile'
else
  $('body').addClass 'desktop'
