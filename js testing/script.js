window.onload = function () {
  let cent_x = window.innerWidth / 2;
  let cent_y = window.innerHeight / 2;
  let round = document.querySelector(".round");
  round.style.right = cent_x - 200;
  round.style.top = cent_y - 294;
  let round_area = document.querySelector(".round").getBoundingClientRect();
  let center_x = (round_area.left + round_area.right) / 2;
  let center_y = (round_area.top + round_area.bottom) / 2;
  console.log(center_x, center_y);

  let n = document.createElement("button");
  let z = document.createElement("div");
  let m = document.createElement("button");
  let r = 240;
  let size = 10;
  n.style.width = 20;
  n.style.width = 20;
  n.style.height = 20;
  n.style.borderRadius = "50%";
  n.style.background = "blue";
  n.style.position = "absolute";
  n.style.visibility = "visible";
  n.style.opacity = 1;
  n.onclick = function (event) {
    count(event);
  };

  m.style.width = 20;
  m.style.width = 20;
  m.style.height = 20;
  m.style.borderRadius = "50%";
  m.style.background = "red";
  m.style.position = "absolute";
  m.style.visibility = "visible";
  m.style.opacity = 1;
  m.onclick = function (event) {
    count(event);
  };

  z.style.background = "yellow";
  z.style.border = "4px solid blue";
  z.style.zIndex = -1;
  z.style.width = r * 2;
  z.style.height = r * 2;
  z.style.borderRadius = "50%";
  z.style.right = cent_x - r;
  z.style.bottom = cent_y - r;

  document.body.appendChild(n);
  document.body.appendChild(m);
  document.body.appendChild(z);

  console.log(document.body.children);
  let i = 0;
  let id = window.setInterval(circles, 70);
  function circles() {
    n.style.left = center_x - 10 + r * Math.cos(i);
    n.style.top = center_y - 10 + r * Math.sin(i);
    m.style.left = center_x - 10 + r * Math.cos(-i);
    m.style.top = center_y - 10 + r * Math.sin(-i);
    i += 0.007;
  }
  let counting = false;
  function count(event) {
    console.log("working");
    if (counting == false) {
      window.clearInterval(id);
      work(m);
      counting=true
    }
    else{
        let id = window.setInterval(circles, 70);
        document.body.onmousemove = function (event) {}
        counting = false

    }

  }
  function work(element) {
    document.body.onmousemove = function (event) {
      if (
        event.clientX >= round_area.left &&
        event.clientX <= round_area.right
      ) {
        if (event.clientY >> cent_y) {
          let val =
            ((round_area.right - event.clientX) /
              (round_area.right - round_area.left)*3.5)+90
            ;
          console.log(round_area.right - event.clientX);
          element.style.left = center_x - 10 + r * Math.cos(val);
          element.style.top = center_y - 10 + r * Math.sin(val);
        } else {
          let val =
            ((round_area.right - event.clientX) /
              (round_area.right - round_area.left)*3.5)+90 ;
          val = val + 180;
          element.style.left = center_x - 10 + r * Math.cos(val);
          element.style.top = center_y - 10 + r * Math.sin(val);
          console.log(val);
        }
      }
    };
  }
};
