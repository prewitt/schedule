/*
 * javascript for plugin window
 * by lagtan
 * @2010-11-20
 * -----------------
 * add mask
 * --2012-05-06--
 * add function scrollTop and scrollLeft, make sure setCenter add scrollTop
*/
if (typeof(miniYUI) == 'undefined') {var miniYUI = {};}
miniYUI.win = {
    getScrollTop: function(){
        var D = document;
        return Math.max(D.body.scrollTop, D.documentElement.scrollTop)
    },

    getScrollLeft: function(){
        var D = document;
        return Math.max(D.body.scrollLeft, D.documentElement.scrollLeft)
    },

    _setCenter: function(win, oSize) {
        win.style.top = '50%';
        win.style.left = '50%';
        win.style.margin = '-' + parseInt(oSize.height/2) + 'px 0 0 -' + parseInt(oSize.width/2) + 'px';

        //add scrollTop and scrollLeft
        var oPos = miniYUI.dom.getPosition(win),
            iScrollTop = this.getScrollTop(),
            iScrollLeft = this.getScrollLeft();
        win.style.top = oPos.top + iScrollTop + 'px';
    },

    _setRelativeCenter: function(win, node, oDiff) {
        var oPos = miniYUI.dom.getPosition(node);
        var iTop = 0, iLeft = 0;
        if (typeof(oDiff) == 'undefined') {
            var iWidth = miniYUI.dom.getStyle(node, 'width', true),
                iHeight = miniYUI.dom.getStyle(node, 'height', true);
            var iWinw = miniYUI.dom.getStyle(win, 'width', true),
                iWinh = miniYUI.dom.getStyle(win, 'height', true);
            iTop = parseInt(iHeight/2 - iWinh/2);
            iLeft = parseInt(iWidth/2 - iWinw/2);
        }else {
            iTop = oDiff.top;
            iLeft = oDiff.left;
        }
        win.style.top = (oPos.top + iTop) + 'px';
        win.style.left = (oPos.left + iLeft) + 'px';
        win.style.margin = '0';
    },

    _win: null,
    _getWin: function() {
        if (!this._win) {
            this._win = document.getElementById('mwin');
        }
        return this._win;
    },

    alert: function(msg, title, node) {
        var win = this._getWin();
        if (!win) {return;}

        if (typeof(title) != 'undefined') {
            var dTitle = win.getElementsByTagName('h6')[0];
            dTitle.innerHTML = title;
        }

        var dMsg = miniYUI.dom.getElementsByClassName('msg', 'div', win)[0];
        dMsg.innerHTML = msg;

        win.style.display = 'block';
        //show by the node or center of the page
        if (typeof(node) != 'undefined') {
            this._setRelativeCenter(win, node, {top:-78, left:-95});
        }else {
            this._setCenter(win, {width:266, height:104});
        }

        var dInput = win.getElementsByTagName('input')[0];
        dInput.focus();
    },

    _closeAlertCallback: null,
    onClose: function(fn) {
        var args = Array.prototype.slice.call(arguments, 2);
        this._closeAlertCallback = {fn: fn, args: args};
    },

    close: function() { //close alert window
        var win = this._getWin();
        if (win) {win.style.display = 'none';}
        if(this._closeAlertCallback) {this._closeAlertCallback.fn.apply(this, this._closeAlertCallback.args);}
    },

    _loadWin: null,
    _getLoadWin: function() {
        if (!this._loadWin) {
            this._loadWin = document.getElementById('mload');
        }
        return this._loadWin;
    },

    showLoading: function(node) {
        var win = this._getLoadWin();
        if (!win) {return;}
        win.style.display = 'block';

        //show by the node or center of the page
        if (typeof(node) != 'undefined') {
            this._setRelativeCenter(win, node);
        }else {
            this._setCenter(win, {width:32, height:32});
        }
    },

    hideLoading: function() {
        var win = this._getLoadWin();
        if (win) {win.style.display = 'none';}
    },

    mask: function(show) {
        var sId = 'mmask',
            dMask = document.getElementById(sId);
        var iBodyHeight = miniYUI.dom.getHeight(document.body),
            iDocHeight = document.documentElement.clientHeight,
            iMheight = iBodyHeight > iDocHeight ? iBodyHeight : iDocHeight;
        var iBodyWidth = miniYUI.dom.getWidth(document.body),
            iDocWidth = document.documentElement.clientWidth,
            iMwidth = iBodyWidth > iDocWidth ? iBodyWidth : iDocWidth;

        if (typeof(show) == 'undefined' || !show) {    //hide mask
            if (dMask) {dMask.style.display = 'none';}
            return;
        }else if (show && dMask) {
            dMask.style.display = 'block';
            dMask.style.width = iMwidth + 'px';
            dMask.style.height = iMheight + 'px';
            return;
        }

        var sHtml = '<!--[if lte IE 6.5]><iframe style="position:absolute;top:0;left:0;z-index:-10;width:100%;height:100%;filter:mask();"></iframe><![endif]-->';
        dMask = document.createElement('div');
        dMask.id = sId;
        dMask.innerHTML = sHtml;
        document.body.appendChild(dMask);
        dMask.style.display = 'block';
        dMask.style.width = iMwidth + 'px';
        dMask.style.height = iMheight + 'px';
    }
};
