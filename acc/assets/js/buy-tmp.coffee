$('button[data-url]').click ->
    window.location.href = $(this).attr 'data-url'
