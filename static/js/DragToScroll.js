const DragToScroll = (param) => {
  const container = document.querySelector(param);
  container.style.cursor = 'auto';
  container.style.userSelect = 'text';

  if ((container.scrollHeight > container.clientHeight) == true) {
    let MouseisDown = false;
    let startY;

    container.addEventListener("mouseover", () => {
      container.style.cursor = 'grab';
    });

    container.addEventListener("mousedown", (e) => {

      MouseisDown = true;

      container.classList.add("active");
      container.style.cursor = 'grabbing';
      container.style.userSelect = 'none';

      startY = e.pageY - container.offsetTop;
      scrollTop = container.scrollTop;
    });

    container.addEventListener("mouseleave", () => {

      MouseisDown = false;
      container.classList.remove("active");
    });

    container.addEventListener("mouseup", () => {

      MouseisDown = false;
      container.classList.remove("active");
      container.style.cursor = 'grab';
    });

    container.addEventListener("mousemove", (e) => {

      if (!MouseisDown) return;
      e.preventDefault();

      const y = e.pageY - container.offsetTop;
      const accelerate = (y - startY) * 1.5; // How fast 
      container.scrollTop = scrollTop - accelerate;
      
    });

    
  } else {
    container.replaceWith(container.cloneNode(true));
  }

}