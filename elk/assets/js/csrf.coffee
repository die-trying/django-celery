#
# Take django's CSRF cookie and append it to every ajax POST request with same origin
#
csrftoken = Cookies.get 'csrftoken'

$.ajaxSetup
  beforeSend: (xhr, settings) ->
    if settings.type is 'POST' and not this.crossDomain
      xhr.setRequestHeader 'X-CSRFToken', csrftoken
