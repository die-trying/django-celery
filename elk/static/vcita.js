  window.liveSiteAsyncInit = function() {
    LiveSite.init({
      id : 'WI-XROT703T6TBH6MWL8Z1C',
      ui : false
    });
  };
  (function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0],
        p = (('https:' == d.location.protocol) ? 'https://' : 'http://'),
        r = Math.floor(new Date().getTime() / 1000000);
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = p + "www.vcita.com/assets/livesite.js?" + r;
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'livesite-jssdk'));
