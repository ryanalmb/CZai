(function(){
  function setLang(lang){
    try{ localStorage.setItem('czai_lang', lang); }catch(e){}
    document.documentElement.setAttribute('data-lang', lang);
    // toggle visibility for .en and .cn elements
    var showEn = lang === 'en';
    var ens = document.querySelectorAll('.en');
    var cns = document.querySelectorAll('.cn');
    ens.forEach(function(el){ el.style.display = showEn ? '' : 'none'; });
    cns.forEach(function(el){ el.style.display = showEn ? 'none' : ''; });
  }
  function getLang(){
    try{ return localStorage.getItem('czai_lang') || 'en'; }catch(e){ return 'en'; }
  }
  // Expose small API
  window.CZAI_I18N = { setLang: setLang, getLang: getLang };
  // Apply on load
  document.addEventListener('DOMContentLoaded', function(){
    setLang(getLang());
    // If landing index.html has language buttons, wire them
    var enBtn = document.getElementById('btn-en');
    var cnBtn = document.getElementById('btn-cn');
    if(enBtn){ enBtn.addEventListener('click', function(){ setLang('en'); /* allow default href */ }); }
    if(cnBtn){ cnBtn.addEventListener('click', function(){ setLang('cn'); /* allow default href */ }); }
  });
})();
