function zeroPad(num, places) {
    let zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join("0") + num;
}

function setTimer(deadline_unix) {
    let deadline = new Date(deadline_unix * 1000);
    let submitted = false;

    if (!submitted) {
        setInterval(function() {
            let now = new Date();

            if (deadline > now) {
                let difference = deadline - new Date();

                let hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                let minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                let seconds = Math.floor((difference % (1000 * 60)) / 1000);

                $('#stickyTimerContent').text(zeroPad(hours, 2) + ':' + zeroPad(minutes, 2) + ':' + zeroPad(seconds, 2));
            } else {
                if (!submitted) {
                    $('#stickyTimerContent').text('00:00:00');
                    $('#examForm').submit();
                    submitted = true;
                }
            }
        }, 1000);
    }
}
