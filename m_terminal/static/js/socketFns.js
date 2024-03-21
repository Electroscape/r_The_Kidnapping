var socket;
$(document).ready(function () {
    socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
    socket.on('connect', function () {
        socket.emit('join', {});
    });
    socket.on('status', function (data) {
        $('#chatArea').val($('#chatArea').val() + '<' + data.msg + '>\n');
        $('#chatArea').scrollTop($('#chatArea')[0].scrollHeight);
    });
    socket.on('message', function (data) {
        $('#chatArea').val($('#chatArea').val() + data.msg + '\n');
        $('#chatArea').scrollTop($('#chatArea')[0].scrollHeight);
    });
    $('#send').click(function (e) {
        text = $('#chatText').val();
        $('#chatText').val('');
        socket.emit('text', {msg: text});
    });
});

function leave_room() {
    socket.emit('left', {}, function () {
        socket.disconnect();
        // go back to the login page
        window.location.href = "{{ url_for('index') }}";
    });
}