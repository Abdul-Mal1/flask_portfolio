// Small JS only for mobile menu + footer year
(function(){
  const btn = document.getElementById("menuBtn");
  const links = document.getElementById("navLinks");
  const year = document.getElementById("year");

  if (year) year.textContent = new Date().getFullYear();

  if (btn && links){
    btn.addEventListener("click", () => {
      links.classList.toggle("show");
    });

    links.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => links.classList.remove("show"));
    });
  }
})();
