
$('#menuButton').click( () ->
  nav = $('#mainNav')
  if nav.attr('style')
    nav.attr('style', '')
    return true
  nav.attr('style', 'height: 7vh !important')
)