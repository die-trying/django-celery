class IssueController
  constructor: (@form, @body) ->
    @still = true
    @submitting = false
    @submitted = false
    @submit_disabled = true

    @body.on 'keyup', () =>
      @update()

    @form.on 'submit', () =>
      @submit()
      return false

    @update()

  update: () ->
    @msg = @body.val()
    @submit_disabled = if @msg.length > 0 then false else true

  submit: () ->
    @still = false
    @submitting = true
    @submit_disabled = true
    $.post '/crm/issue/', {body: @msg}, () =>
      @submitting = false
      @submitted = true


$('.issue-form').on 'shown.bs.modal', () ->
  $form = $ this
  $body = $ 'textarea[name="body"]', $form
  c = new IssueController(
    form = $form
    body = $body
  )
  rivets.bind $form, {c: c}
  $body.focus()
