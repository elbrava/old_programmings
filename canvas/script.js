window.onload = function
    () {
        create()
        arc_rect()

    function create(){
        var canvas = document.getElementById("canvas")

        var initial=document.querySelector(".initial")
        var final=document.querySelector(".final")
        var cent=document.querySelector(".cent")

        let i = 0;
        center_y= cent.getBoundingClientRect().top+cent.style.height/2
        center_x=cent.getBoundingClientRect().left+cent.style.width/2
        var r=120
        let id = window.setInterval(circles, 70);
        function circles() {
          final.style.left = center_x - 10 + r * Math.cos(i);
          final.style.top = center_y - 10 + r * Math.sin(i);
          initial.style.left = center_x - 10 + r * Math.cos(-i);
          initial.style.top = center_y - 10 + r * Math.sin(-i);
          i += 0.07;
        }



    }

    function arc_rect() {

       
    }

    function what() {

        var canvas = document.getElementById("canvas")
        var ctx = canvas.getContext("2d")
        ctx.lineWidth = 2
        ctx.strokeStyle = "yellow"
        var width = window.innerWidth
        var height = window.innerHeight
        ctx.clearRect(0, 0, width, height)
        console.log(ctx)
        ctx.moveTo(0, 200)
        ctx.lineTo(width,200)
        ctx.moveTo(0,200)

        for (let index = 0; index <width; index++) {
            ctx.lineTo(index, 200+70*Math.sin(index/180))
            console.log(index, 200+70*Math.sin(index/180))
            console.log("working")
            
        }
        ctx.stroke()
        

    }
}