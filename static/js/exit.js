    var obj = document.getElementById('exit');
    obj.onclick=function(){
      window.location.href="/logout/account={{ account }}";
    }