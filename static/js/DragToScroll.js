const body = document.querySelector("body");
let MouseisDown = false;
let startY;
let scrollLeft;

body.addEventListener("mousedown", (e) => {
  MouseisDown = true;

  body.classList.add("active");
  body.style.cursor = 'grabbing';
  body.style.userSelect = 'none';

  startY = e.pageY - body.offsetTop;
  scrollTop = body.scrollTop;
});

body.addEventListener("mouseleave", () => {
  MouseisDown = false;
  body.classList.remove("active");
});

body.addEventListener("mouseup", () => {
  MouseisDown = false;
  body.classList.remove("active");
  body.style.cursor = 'grab';
});

body.addEventListener("mousemove", (e) => {
  if (!MouseisDown) return;
  e.preventDefault();

  const y = e.pageY - body.offsetTop;
  const accelerate = (y - startY) * 1.5; // How fast 
  body.scrollTop = scrollTop - accelerate;
});
