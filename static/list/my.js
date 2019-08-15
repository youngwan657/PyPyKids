<script>
// textarea tab
textarea = document.getElementById('answer');
textarea.onkeydown = function(event) {
    //support tab on textarea
    if (event.keyCode == 8 || event.keyCode == 9 && event.shiftKey) {    // shift+tab or backspace
        var v = textarea.value, s = textarea.selectionStart, e = textarea.selectionEnd;
        if (textarea.value.substring(s-4, s) == ' '.repeat(4)) {
            textarea.value = v.substring(0, s-4) + v.substring(e);
            textarea.selectionStart = textarea.selectionEnd = s - 4;
            return false
        }

        if (event.keyCode == 9 && evevnt.shiftKey) {
            return false;
        }
        return true;
    } else if (event.keyCode == 9) { // tab
        var v = textarea.value, s = textarea.selectionStart, e = textarea.selectionEnd;
        textarea.value = v.substring(0, s) + ' '.repeat(4) + v.substring(e);
        textarea.selectionStart = textarea.selectionEnd = s + 4;
        return false;
    }


    if (event.keyCode == 13) {  // enter
        var v = textarea.value, s = textarea.selectionStart,e = textarea.selectionEnd;
        var lines = textarea.value.split("\n");
        var startPos = 0;
        var previousLine = lines[lines.length-1];
        var i = 0
        for(i = 0; i < lines.length; i++) {
            if(textarea.selectionStart < startPos) {
                previousLine = lines[i-1];
                break;
            }
            startPos += (lines[i].length+1);
        }
        for(i = 0; i < previousLine.length; i++) {
            if(previousLine.charAt(i) != ' ') {
                break;
            }
        }
        var space = "\n";
        if (previousLine.charAt(previousLine.length - 1) == ':') {
            space += ' '.repeat(i + 4);
        } else {
            space += ' '.repeat(i);
        }

        textarea.value = v.substring(0, s) + space + v.substring(e);
        textarea.selectionStart = textarea.selectionEnd = s + space.length;
        return false;
    }
}
</script>
