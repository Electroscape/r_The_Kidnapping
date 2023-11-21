let puzzleIntervals = [];

function randomize(index) {
    $('#puzzle-' + index + ' i').each(function () {
        let wid = 100;
        for (let i = 0; i < $(".option").length; i++) {
            wid = $('#option' + i).width();
            if (wid > 100) {
                break;
            }
        }
        $(this).css({
            left: Math.random() * (wid - 50 - $(this).width()),
            top: Math.random() * (wid - 50 - $(this).height())
        });
    });

    // for (let i = 0; i < ul.length; i++) {
    //     ul[i].style.left = Math.random() * (window.innerWidth - 10) + 'px'
    //     ul[i].style.top = Math.random() * (window.innerHeight - 10) + 'px'
    //}
    // for (var i = ul.children.length; i >= 0; i--) {
    //   ul.appendChild(ul.children[Math.random() * i | 0]);
    // }

}

function reload(index) {
    let done = document.querySelectorAll('.done-' + index)
    done.forEach(function (e) {
        e.classList.toggle('done-' + index)
    })
    let dropped = document.querySelectorAll('.dropped-' + index)
    dropped.forEach(function (e) {
        e.classList.toggle('dropped-' + index)
    })
}

// desktop drag and drop
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.classList[1]);
}

function puzzleDrop(ev) {
    ev.preventDefault();
    let data = ev.dataTransfer.getData("text")
    let index = data.split("-").pop()
    const submitBtn = document.querySelector("#submit-btn-" + index);
    if (ev.target.classList.contains(data)) {
        ev.target.classList.add('dropped-' + index)
        document.querySelector('.' + data + "[draggable='true']").classList.add('done-' + index)

        if (document.querySelectorAll('.dropped-' + index).length === 9) {
            submitBtn.disabled = false;
        }
    }
}

function puzzleSubmit(index) {
    clearInterval(puzzleIntervals[index]);
    $(".loader-wrapper").removeClass("d-none");
    document.querySelector('#puz-' + index).classList.add('allDone-' + index)
    document.querySelector('#puz-' + index).style.border = 'none'
    document.querySelector('#puz-' + index).style.animation = 'allDone 1s linear forwards'

    socket.emit('msg_to_backend', {
        keypad_update: `${window.location.pathname} puzzleGame ${index} correct`
    })
    setTimeout(() => {
        swal("Stable Combination", "Sample has been released", "success");
        $(".loader-wrapper").addClass("d-none");
    }, 5000)

}

function checkPuzzleStatus(index, status) {
    if (status === "released") {
        clearInterval(puzzleIntervals[index]);
        document.querySelector('#puz-' + index).classList.add('allDone-' + index);
        document.querySelector('#puz-' + index).style.border = 'none';
        let pieces = document.querySelectorAll('.piece-' + index)
        pieces.forEach(function (e) {
            e.classList.toggle('done-' + index);
        })
        let board = document.querySelectorAll('.board-' + index)
        board.forEach(function (e) {
            e.classList.toggle('dropped-' + index);
        })
    }
}

