$('.issue-form').on 'shown.bs.modal', () ->
  $form = $ this
  $body = $form.find 'textarea[name="body"]'
  $submit = $form.find 'button[type=submit]'
  $thanks = $form.find '.thanks'
  $body_container = $form.find '.form-group'

  $body.focus()

  $body.on 'keyup', () ->
    submit_disabled = if $(this).val().length > 0 then false else true
    $submit.attr 'disabled', submit_disabled

  $form.on 'submit', () ->
    $submit.attr 'disabled', true

    $body.addClass 'hidden'
    $body_container.addClass 'pretty-loader'

    $.post '/crm/issue/', {body: $body.val()}, () ->
      $body.val ''

      $body_container.removeClass 'pretty-loader'
      $thanks.removeClass 'hidden'

    return false

  $form.on 'hidden.bs.modal', () ->
    $body_container.removeClass 'pretty-loader'
    $thanks.addClass 'hidden'
    $body.removeClass 'hidden'
