class Model extends MicroEvent
  #  - date — currenlt sealected date
  #  - lesson_type — the content type of lesson, selected in filters
  #  - query_type — the type of slots we need to query:
  #     - 'lessons': for lessons, that do not require planning (default)
  #     - 'teachers':  for lessons, that require planning (like master classes etc.)
  constructor: (@lesson_type, @date, @query_type='teahers') ->
    @urls = {  # two different urls for query types
      teachers: "/market/%s/type/%d/teachers.json"
      lessons: "/market/%s/type/%d/lessons.json"
    }
    @from_json()
    @timout = 1

  class Record
    constructor: (@name, @photo, @author, @description) ->
      @slots = []

  from_json: () ->
    url = sprintf @urls[@query_type], @date, parseInt @lesson_type
    @records= []

    @loaded = false
    @loading = true
    setTimeout () =>
      @loading = false
    , 3000
    $.getJSON url, (data) =>
      @loaded = true
      setTimeout () =>
        @timeout = 700  # TODO: remove this timeout after debugging
        @loading = false
        for event in data
          record = new Record(
            name = event.name
            photo = event.profile_photo
            author = if event.host? then event.host.name
            description = event.announce
          )
          for time in event.slots
            time_for_id = time.replace ':', '_'
            slot = {
              id: "teacher_#{ event.id }_time_#{ time_for_id }"
              teacher: if event.host? then event.host.id else event.id
              time: time
            }
            record.slots.push slot

          @records.push record
        @trigger 'update'
      , @timeout

  submit_url: (data) ->
    "/market/schedule/step2/teacher/#{ data.teacher }/#{ data.lesson }/#{ data.date }/#{ data.time }/"

Project.models.SchedulePopupModel = Model
