var catalog = new Array();

// Cross-browser event handlers.
function addEvent(obj, evType, fn) {
    if (obj.addEventListener) {
        obj.addEventListener(evType, fn, false);
        return true;
    } else if (obj.attachEvent) {
        var r = obj.attachEvent("on" + evType, fn);
        return r;
    } else {
        return false;
    }
}

function quickElement() {
    var obj = document.createElement(arguments[0]);
    if (arguments[2] != '' && arguments[2] != null) {
        var textNode = document.createTextNode(arguments[2]);
        obj.appendChild(textNode);
    }
    var len = arguments.length;
    for (var i = 3; i < len; i += 2) {
        obj.setAttribute(arguments[i], arguments[i+1]);
    }
    arguments[1].appendChild(obj);
    return obj;
}

// ----------------------------------------------------------------------------
// Find-position functions by PPK
// See http://www.quirksmode.org/js/findpos.html
// ----------------------------------------------------------------------------
function findPosX(obj) {
    var curleft = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curleft += obj.offsetLeft;
            obj = obj.offsetParent;
        }
    } else if (obj.x) {
        curleft += obj.x;
    }
    return curleft;
}

function findPosY(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        while (obj.offsetParent) {
            curtop += obj.offsetTop;
            obj = obj.offsetParent;
        }
    } else if (obj.y) {
        curtop += obj.y;
    }
    return curtop;
}

function gettext(msgid) {
  var value = catalog[msgid];
  if (typeof(value) == 'undefined') {
    return msgid;
  } else {
    return (typeof(value) == 'string') ? value : value[0];
  }
}


//-----------------------------------------------------------------------------
// Date object extensions
// ----------------------------------------------------------------------------
Date.prototype.getCorrectYear = function() {
    // Date.getYear() is unreliable --
    // see http://www.quirksmode.org/js/introdate.html#year
    var y = this.getYear() % 100;
    return (y < 38) ? y + 2000 : y + 1900;
}

Date.prototype.getTwoDigitMonth = function() {
    return (this.getMonth() < 9) ? '0' + (this.getMonth()+1) : (this.getMonth()+1);
}

Date.prototype.getTwoDigitDate = function() {
    return (this.getDate() < 10) ? '0' + this.getDate() : this.getDate();
}

Date.prototype.getTwoDigitHour = function() {
    return (this.getHours() < 10) ? '0' + this.getHours() : this.getHours();
}

Date.prototype.getTwoDigitMinute = function() {
    return (this.getMinutes() < 10) ? '0' + this.getMinutes() : this.getMinutes();
}

Date.prototype.getISODate = function() {
    return this.getTwoDigitDate() + '/' + this.getTwoDigitMonth() + '/' +  this.getCorrectYear();
}

Date.prototype.getHourMinute = function() {
    return this.getTwoDigitHour() + ':' + this.getTwoDigitMinute();
}
