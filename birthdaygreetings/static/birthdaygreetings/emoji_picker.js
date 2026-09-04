// Inserts a small clickable emoji toolbar above the birthday "custom_message" field
// so admins can add festive emojis without hunting for an OS emoji picker.
(function () {
    var EMOJIS = ['🎉', '🎂', '🎈', '🎁', '🥳', '🌟', '❤️', '🎊', '👏', '😊', '🙌', '✨'];

    function buildToolbar(field) {
        var toolbar = document.createElement('div');
        toolbar.className = 'emoji-picker-toolbar';

        EMOJIS.forEach(function (emoji) {
            var btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = emoji;
            btn.setAttribute('aria-label', 'Insert ' + emoji);
            btn.addEventListener('click', function () {
                insertAtCursor(field, emoji);
            });
            toolbar.appendChild(btn);
        });

        return toolbar;
    }

    function insertAtCursor(field, text) {
        var start = field.selectionStart || field.value.length;
        var end = field.selectionEnd || field.value.length;
        field.value = field.value.slice(0, start) + text + field.value.slice(end);
        var newPos = start + text.length;
        field.focus();
        field.setSelectionRange(newPos, newPos);
    }

    document.addEventListener('DOMContentLoaded', function () {
        var field = document.getElementById('id_custom_message');
        if (!field) {
            return;
        }
        field.insertAdjacentElement('afterend', buildToolbar(field));
    });
})();
