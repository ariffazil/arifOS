'use strict';

var obsidian = require('obsidian');

/*! *****************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
/* global Reflect, Promise */

var extendStatics = function(d, b) {
    extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
    return extendStatics(d, b);
};

function __extends(d, b) {
    if (typeof b !== "function" && b !== null)
        throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
}

function __awaiter(thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
}

function __generator(thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (_) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
}

function __values(o) {
    var s = typeof Symbol === "function" && Symbol.iterator, m = s && o[s], i = 0;
    if (m) return m.call(o);
    if (o && typeof o.length === "number") return {
        next: function () {
            if (o && i >= o.length) o = void 0;
            return { value: o && o[i++], done: !o };
        }
    };
    throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
}

function __read(o, n) {
    var m = typeof Symbol === "function" && o[Symbol.iterator];
    if (!m) return o;
    var i = m.call(o), r, ar = [], e;
    try {
        while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
    }
    catch (error) { e = { error: error }; }
    finally {
        try {
            if (r && !r.done && (m = i["return"])) m.call(i);
        }
        finally { if (e) throw e.error; }
    }
    return ar;
}

var LabView = /** @class */ (function (_super) {
    __extends(LabView, _super);
    function LabView(leaf, commandId, command) {
        var _this = _super.call(this, leaf) || this;
        _this.command = command;
        _this.commandId = commandId;
        return _this;
    }
    LabView.prototype.getViewType = function () {
        return this.commandId;
    };
    LabView.prototype.getDisplayText = function () {
        return this.command.label == null ? this.commandId : this.command.label;
    };
    LabView.prototype.getIcon = function () {
        return this.command.icon == null ? 'lab' : this.command.icon;
    };
    return LabView;
}(obsidian.ItemView));

var path = require('path');
// A panel that shows notes or text.
var LabPanel = /** @class */ (function (_super) {
    __extends(LabPanel, _super);
    function LabPanel(leaf, commandId, command) {
        var _this = _super.call(this, leaf, commandId, command) || this;
        /**
         * Updates the panel
         */
        _this.draw = function () {
            var openFile = _this.app.workspace.getActiveFile();
            var rootEl = createDiv({ cls: 'nav-folder mod-root' });
            _this.state =
                _this.state == null
                    ? {
                        label: '',
                        contents: '',
                    }
                    : _this.state;
            // Label of the panel
            var context = rootEl.createDiv({
                title: 'title',
                cls: 'nav-file python-lab-title',
                text: _this.state.label,
            });
            // Function open on click
            var clickElement = function (file, shouldSplit) {
                if (shouldSplit === void 0) { shouldSplit = false; }
                var filePath = file.path;
                // If it applies, remove the vault path
                if (_this.app.vault.adapter instanceof obsidian.FileSystemAdapter) {
                    var vaultPath = _this.app.vault.adapter.getBasePath();
                    if (filePath.startsWith(vaultPath)) {
                        filePath = path.relative(vaultPath, filePath);
                    }
                }
                var targetFile = _this.app.vault
                    .getFiles()
                    .find(function (f) { return f.path === filePath; });
                if (targetFile) {
                    var leaf = _this.app.workspace.getMostRecentLeaf();
                    if (shouldSplit) {
                        leaf = _this.app.workspace.createLeafBySplit(leaf);
                    }
                    leaf.openFile(targetFile);
                }
                else {
                    new obsidian.Notice("'" + file.path + "' not found");
                    if (Array.isArray(_this.state.contents)) {
                        _this.state.contents = _this.state.contents.filter(function (fp) { return fp.path !== file.path; });
                    }
                    _this.draw();
                }
            };
            // Draw a list, when is a list
            if (Array.isArray(_this.state.contents)) {
                _this.state.contents.forEach(function (currentFile) {
                    var childrenEl = rootEl.createDiv({ cls: 'nav-folder-children' });
                    // The info that will appear on hover
                    var jsonInfo = JSON.stringify(currentFile, null, 4);
                    var navFile = childrenEl.createDiv({
                        title: jsonInfo,
                        cls: 'nav-file',
                    });
                    var navFileTitle = navFile.createDiv({ cls: 'nav-file-title' });
                    if (openFile && currentFile.path === openFile.path) {
                        navFileTitle.addClass('is-active');
                    }
                    navFileTitle.createDiv({
                        cls: 'nav-file-title-content',
                        text: currentFile.name,
                    });
                    navFile.onClickEvent(function (event) {
                        return clickElement(currentFile, event.ctrlKey || event.metaKey);
                    });
                });
            }
            else if (String.isString(_this.state.contents)) {
                // Draw the contents as a list
                rootEl.createDiv({
                    title: 'contents',
                    cls: 'python-lab-text',
                    text: _this.state.contents,
                });
            }
            else {
                rootEl.createDiv({
                    title: 'contents',
                    cls: 'python-lab-text',
                    text: JSON.stringify(_this.state, null, 2),
                });
            }
            var contentEl = _this.containerEl.children[1];
            contentEl.empty();
            contentEl.appendChild(rootEl);
        };
        _this.draw();
        return _this;
    }
    LabPanel.prototype.setData = function (state) {
        this.state = state;
    };
    // Used to handle 'file-open'
    LabPanel.prototype.registerOnFileOpen = function (callback) {
        var _this = this;
        var handleOpenFile = function (openedFile) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        if (!openedFile) {
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, callback()];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        }); };
        this.registerEvent(this.app.workspace.on('file-open', handleOpenFile));
    };
    /**
     * The menu that appears with right click on the icon
     */
    LabPanel.prototype.onHeaderMenu = function (menu) {
        var _this = this;
        menu
            .addItem(function (item) {
            item
                .setTitle('Clear list')
                .setIcon('sweep')
                .onClick(function () { return __awaiter(_this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    this.state = null;
                    this.draw();
                    return [2 /*return*/];
                });
            }); });
        })
            .addItem(function (item) {
            item
                .setTitle('Close')
                .setIcon('cross')
                .onClick(function () {
                _this.app.workspace.detachLeavesOfType(_this.commandId);
            });
        });
    };
    LabPanel.prototype.load = function () {
        _super.prototype.load.call(this);
    };
    return LabPanel;
}(LabView));

// This chat widget is based on the 'dual' prototype.
// I found it pretty.
// https://github.com/Psionica/Dual/blob/master/vault-replica/.obsidian/plugins/Dual/view.ts
var ChatView = /** @class */ (function (_super) {
    __extends(ChatView, _super);
    function ChatView(leaf, commandId, command) {
        var _this = _super.call(this, leaf, commandId, command) || this;
        _this.draw();
        return _this;
    }
    ChatView.prototype.registerOnSendMessage = function (callbackWithView) {
        this.onSendMessage = callbackWithView;
    };
    ChatView.prototype.load = function () {
        _super.prototype.load.call(this);
        this.draw();
    };
    // The use input
    ChatView.prototype.getLastInput = function () {
        return this.lastInput;
    };
    ChatView.prototype.sendMessage = function () {
        var _this = this;
        var input = document.getElementById('input');
        var replied = false;
        if (input.value != '') {
            this.drawMessage(input.value, 'right');
            var typingPromise = new Promise(function (resolve) {
                return setTimeout(resolve, 3000);
            }).then(function () {
                if (replied == false) {
                    _this.setStatus('loading...');
                }
            });
            this.lastInput = input.value;
            this.onSendMessage().then(function (response) {
                if (response.contents) {
                    var message = JSON.stringify(response.contents);
                    _this.drawMessage(message, 'left');
                }
                replied = true;
            });
            input.value = '';
        }
    };
    ChatView.prototype.draw = function () {
        var _this = this;
        var container = this.containerEl.children[1];
        var rootEl = document.createElement('div');
        var headerDiv = rootEl.createDiv({ cls: 'nav-header' });
        var footerDiv = rootEl.createDiv({ cls: 'nav-header' });
        var header = headerDiv.createEl('h3');
        header.appendText(_super.prototype.getDisplayText.call(this));
        header.style.textAlign = 'left';
        header.style.marginTop = '0px';
        header.style.marginBottom = '0px';
        header.style.position = 'absolute';
        header.style.top = '15px';
        var status = headerDiv.createEl('h6');
        status.id = 'status';
        if (this.status) {
            status.appendText('online');
        }
        status.style.textAlign = 'left';
        status.style.marginTop = '0px';
        status.style.marginBottom = '5px';
        status.style.color = 'grey';
        var conversationDiv = headerDiv.createDiv({ cls: 'nav-header' });
        conversationDiv.id = 'conversationDiv';
        conversationDiv.style.padding = '0';
        conversationDiv.style.backgroundColor = 'var(--background-secondary-alt)';
        conversationDiv.style.position = 'absolute';
        conversationDiv.style.left = '0';
        conversationDiv.style.width = '100%';
        conversationDiv.style.paddingLeft = '10px';
        conversationDiv.style.paddingRight = '10px';
        conversationDiv.style.overflowY = 'scroll';
        conversationDiv.style.height = 'calc(100% - 110px)';
        var input = footerDiv.createEl('input');
        input.id = 'input';
        input.type = 'text';
        input.style.fontSize = '0.8em';
        input.style.paddingInlineStart = '2%';
        input.style.paddingInlineEnd = '2%';
        input.style.marginTop = '0px';
        input.style.marginBottom = '10px';
        input.style.maxWidth = '68%';
        input.style.minWidth = '68%';
        input.style.position = 'absolute';
        input.style.bottom = '0';
        input.style.left = '5%';
        var button = footerDiv.createEl('button');
        button.appendText('Send');
        button.id = 'send-button';
        button.style.alignItems = 'left';
        button.style.paddingInlineStart = '2%';
        button.style.paddingInlineEnd = '2%';
        button.style.marginTop = '0px';
        button.style.marginBottom = '10px';
        button.style.width = '20%';
        button.style.position = 'absolute';
        button.style.bottom = '0';
        button.style.left = '75%';
        this.registerDomEvent(button, 'click', function () { return _this.sendMessage(); });
        this.registerDomEvent(input, 'keydown', function (event) {
            if (event.key == 'Enter') {
                _this.sendMessage();
            }
        });
        container.empty();
        container.appendChild(rootEl);
    };
    ChatView.prototype.drawMessage = function (content, side) {
        var conversationDiv = (document.getElementById('conversationDiv'));
        var p = conversationDiv.createEl('p');
        p.appendText(content);
        p.style.textAlign = 'left';
        p.style.fontSize = '0.8em';
        p.style.borderRadius = '5px';
        p.style.lineHeight = '18px';
        p.style.padding = '5px';
        if (side == 'right') {
            p.style.backgroundColor = 'var(--background-primary)';
        }
        else {
            p.style.backgroundColor = 'var(--background-secondary)';
        }
        p.style.width = '90%';
        p.style.position = 'relative';
        if (side == 'right') {
            p.style.left = '10%';
        }
        conversationDiv.scrollBy(0, 1000);
    };
    ChatView.prototype.setStatus = function (content) {
        var statusP = document.getElementById('status');
        statusP.setText(content);
    };
    return ChatView;
}(LabView));

var sweepIcon = "\n<svg fill=\"currentColor\" stroke=\"currentColor\" version=\"1.1\" viewBox=\"0 0 512 512\" xmlns=\"http://www.w3.org/2000/svg\">\n  <path d=\"m495.72 1.582c-7.456-3.691-16.421-0.703-20.142 6.694l-136.92 274.08-26.818-13.433c-22.207-11.118-49.277-2.065-60.396 20.083l-6.713 13.405 160.96 80.616 6.713-13.411c11.087-22.143 2.227-49.18-20.083-60.381l-26.823-13.435 136.92-274.08c3.706-7.412 0.703-16.421-6.694-20.141z\"/>\n  <circle cx=\"173\" cy=\"497\" r=\"15\"/>\n  <circle cx=\"23\" cy=\"407\" r=\"15\"/>\n  <circle cx=\"83\" cy=\"437\" r=\"15\"/>\n  <path d=\"m113 482h-60c-8.276 0-15-6.724-15-15 0-8.291-6.709-15-15-15s-15 6.709-15 15c0 24.814 20.186 45 45 45h60c8.291 0 15-6.709 15-15s-6.709-15-15-15z\"/>\n  <path d=\"m108.64 388.07c-6.563 0.82-11.807 5.845-12.92 12.349-1.113 6.519 2.153 12.993 8.057 15.952l71.675 35.889c12.935 6.475 27.231 9.053 41.177 7.573-1.641 6.65 1.479 13.784 7.852 16.992l67.061 33.589c5.636 2.78 12.169 1.8 16.685-2.197 2.347-2.091 53.436-48.056 83.3-98.718l-161.6-80.94c-36.208 48.109-120.36 59.39-121.28 59.511z\"/>\n</svg>";
// From: https://github.com/mgmeyers/obsidian-icon-swapper
var icons = [
    'lab',
    'sweep',
    'any-key',
    'audio-file',
    'blocks',
    'bold-glyph',
    'bracket-glyph',
    'broken-link',
    'bullet-list-glyph',
    'bullet-list',
    'calendar-with-checkmark',
    'check-in-circle',
    'check-small',
    'checkbox-glyph',
    'checkmark',
    'clock',
    'cloud',
    'code-glyph',
    'create-new',
    'cross-in-box',
    'cross',
    'crossed-star',
    'dice',
    'document',
    'documents',
    'dot-network',
    'double-down-arrow-glyph',
    'double-up-arrow-glyph',
    'down-arrow-with-tail',
    'down-chevron-glyph',
    'enter',
    'exit-fullscreen',
    'expand-vertically',
    'filled-pin',
    'folder',
    'forward-arrow',
    'fullscreen',
    'gear',
    'go-to-file',
    'hashtag',
    'heading-glyph',
    'help',
    'highlight-glyph',
    'horizontal-split',
    'image-file',
    'image-glyph',
    'indent-glyph',
    'info',
    'install',
    'italic-glyph',
    'keyboard-glyph',
    'languages',
    'left-arrow-with-tail',
    'left-arrow',
    'left-chevron-glyph',
    'lines-of-text',
    'link-glyph',
    'link',
    'logo-crystal',
    'magnifying-glass',
    'microphone-filled',
    'microphone',
    'minus-with-circle',
    'note-glyph',
    'number-list-glyph',
    'open-vault',
    'pane-layout',
    'paper-plane',
    'paused',
    'pdf-file',
    'pencil',
    'percent-sign-glyph',
    'pin',
    'plus-with-circle',
    'popup-open',
    'presentation',
    'price-tag-glyph',
    'quote-glyph',
    'redo-glyph',
    'reset',
    'right-arrow-with-tail',
    'right-arrow',
    'right-chevron-glyph',
    'right-triangle',
    'run-command',
    'search',
    'sheets-in-box',
    'stacked-levels',
    'star-list',
    'star',
    'strikethrough-glyph',
    'switch',
    'sync-small',
    'sync',
    'tag-glyph',
    'three-horizontal-bars',
    'trash',
    'undo-glyph',
    'unindent-glyph',
    'up-and-down-arrows',
    'up-arrow-with-tail',
    'up-chevron-glyph',
    'uppercase-lowercase-a',
    'vault',
    'vertical-split',
    'vertical-three-dots',
    'wrench-screwdriver-glyph',
];

var COMMAND_PREFIX = 'obsidian_lab_';
var DEFAULT_ICON = 'gear';
var DEFAULT_SETTINGS = {
    server_url: 'http://localhost:5000',
    debug: 'verbose',
    commands: {
        hello_world: {
            active: true,
            label: 'Hello world',
            type: 'insert-text',
        },
        to_upper_case: {
            active: false,
            label: 'Convert to upper case',
            type: 'replace-text',
        },
        chat: {
            active: false,
            label: 'Simple chat service',
            type: 'command-line',
        },
        random_similarity: {
            active: true,
            label: 'Random score similarity',
            type: 'panel',
            icon: DEFAULT_ICON,
            invokeOnOpen: true,
        },
    },
};
function getServerStatus(serverUrl) {
    return __awaiter(this, void 0, void 0, function () {
        var result;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, fetch(serverUrl, {
                        method: 'GET',
                        headers: {
                            'content-type': 'application/json',
                        },
                    })
                        .then(function (response) {
                        return response.json();
                    })
                        .then(function (data) {
                        var status = {
                            status: 'available',
                            availableCommandUrls: data.scripts ? data.scripts : [],
                        };
                        return status;
                    })
                        .catch(function (error) {
                        return {
                            status: 'unavailable',
                            availableCommandUrls: [],
                            error: error,
                        };
                    })];
                case 1:
                    result = _a.sent();
                    return [2 /*return*/, result];
            }
        });
    });
}
function commandIdFromName(command_name) {
    return "" + COMMAND_PREFIX + command_name;
}
function getNameFromUrl(currentUrl) {
    return currentUrl.substring(currentUrl.lastIndexOf('/') + 1);
}
function loadCommands(commandUrls, commandSettings) {
    var e_1, _a;
    var result = new Map();
    try {
        for (var commandUrls_1 = __values(commandUrls), commandUrls_1_1 = commandUrls_1.next(); !commandUrls_1_1.done; commandUrls_1_1 = commandUrls_1.next()) {
            var commandURL = commandUrls_1_1.value;
            var commandName = getNameFromUrl(commandURL);
            // If the settings for this command are already stored
            if (commandSettings[commandName]) {
                result.set(commandName, commandSettings[commandName]);
            }
            else {
                // Otherwise use the default one
                result.set(commandName, {
                    label: commandName,
                    type: 'insert-text',
                    active: false,
                    invokeOnOpen: false,
                    icon: 'lab',
                });
            }
        }
    }
    catch (e_1_1) { e_1 = { error: e_1_1 }; }
    finally {
        try {
            if (commandUrls_1_1 && !commandUrls_1_1.done && (_a = commandUrls_1.return)) _a.call(commandUrls_1);
        }
        finally { if (e_1) throw e_1.error; }
    }
    return result;
}
var PythonLabPlugin = /** @class */ (function (_super) {
    __extends(PythonLabPlugin, _super);
    function PythonLabPlugin() {
        var _this = _super !== null && _super.apply(this, arguments) || this;
        /**
         * Init all commands
         */
        _this.initViews = function (commands) {
            return function () {
                var e_2, _a;
                try {
                    // Attach only commands that have a view.
                    for (var commands_1 = __values(commands), commands_1_1 = commands_1.next(); !commands_1_1.done; commands_1_1 = commands_1.next()) {
                        var _b = __read(commands_1_1.value, 2), name_1 = _b[0], command = _b[1];
                        var hasView = command.type == 'panel' || command.type == 'command-line';
                        if (hasView && command.active) {
                            var commandId = commandIdFromName(name_1);
                            _this.showPanel(commandId);
                        }
                    }
                }
                catch (e_2_1) { e_2 = { error: e_2_1 }; }
                finally {
                    try {
                        if (commands_1_1 && !commands_1_1.done && (_a = commands_1.return)) _a.call(commands_1);
                    }
                    finally { if (e_2) throw e_2.error; }
                }
            };
        };
        return _this;
    }
    PythonLabPlugin.prototype.commandUrlFromName = function (command_name) {
        return this.settings.server_url + "/" + command_name;
    };
    PythonLabPlugin.prototype.getVaultPath = function () {
        if (!(this.app.vault.adapter instanceof obsidian.FileSystemAdapter)) {
            throw new Error('app.vault is not a FileSystemAdapter instance');
        }
        return this.app.vault.adapter.getBasePath();
    };
    PythonLabPlugin.prototype.loadCommandPanes = function () {
        return __awaiter(this, void 0, void 0, function () {
            var serverStatus, availableCommands, availableCommands_1, availableCommands_1_1, _a, name_2, command, init;
            var e_3, _b;
            var _this = this;
            return __generator(this, function (_c) {
                switch (_c.label) {
                    case 0: return [4 /*yield*/, this.loadSettings()];
                    case 1:
                        _c.sent();
                        return [4 /*yield*/, getServerStatus(this.settings.server_url)];
                    case 2:
                        serverStatus = _c.sent();
                        // Detach panes
                        // Disclaimer: I still cannot figure out how to detach or unregister all leaves produced by this plugin
                        // The intention here is to clean all leaves of created by the lab. @TODO detach properly in the future
                        this.app.workspace.iterateAllLeaves(function (leaf) {
                            if (leaf.getViewState().type.startsWith(COMMAND_PREFIX)) {
                                if (_this.settings.debug == 'verbose') {
                                    console.log('detaching', leaf.getViewState().type);
                                }
                                leaf.detach();
                            }
                        });
                        if (serverStatus.status == 'available') {
                            availableCommands = loadCommands(serverStatus.availableCommandUrls, this.settings.commands);
                            try {
                                for (availableCommands_1 = __values(availableCommands), availableCommands_1_1 = availableCommands_1.next(); !availableCommands_1_1.done; availableCommands_1_1 = availableCommands_1.next()) {
                                    _a = __read(availableCommands_1_1.value, 2), name_2 = _a[0], command = _a[1];
                                    if (command.active) {
                                        this.initCommand(name_2, command);
                                    }
                                }
                            }
                            catch (e_3_1) { e_3 = { error: e_3_1 }; }
                            finally {
                                try {
                                    if (availableCommands_1_1 && !availableCommands_1_1.done && (_b = availableCommands_1.return)) _b.call(availableCommands_1);
                                }
                                finally { if (e_3) throw e_3.error; }
                            }
                            init = this.initViews(availableCommands);
                            if (this.app.workspace.layoutReady) {
                                init();
                            }
                            else {
                                this.app.workspace.onLayoutReady(init);
                            }
                        }
                        else {
                            new obsidian.Notice('Lab disconected, Start server');
                            if (this.settings.debug == 'verbose') {
                                console.log(serverStatus);
                            }
                        }
                        return [2 /*return*/];
                }
            });
        });
    };
    PythonLabPlugin.prototype.onload = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                console.log('loading python lab plugin');
                obsidian.addIcon('sweep', sweepIcon);
                this.loadCommandPanes();
                this.addSettingTab(new PythonLabSettings(this.app, this));
                return [2 /*return*/];
            });
        });
    };
    PythonLabPlugin.prototype.initCommand = function (name, command) {
        var _this = this;
        var commandId = commandIdFromName(name);
        var commandUrl = this.commandUrlFromName(name);
        if (this.settings.debug == 'verbose') {
            console.log("init [" + name + "] as [" + command.type + "]");
        }
        if (command.type == 'command-line') {
            var viewCreator = function (leaf) {
                var commandLine = new ChatView(leaf, commandId, command);
                var commandLineCallback = function () { return __awaiter(_this, void 0, void 0, function () {
                    var parameters;
                    return __generator(this, function (_a) {
                        switch (_a.label) {
                            case 0:
                                parameters = this.getDefaultPostParameters();
                                parameters.data = {
                                    input: commandLine.getLastInput(),
                                };
                                return [4 /*yield*/, this.doPost(commandUrl, parameters)];
                            case 1: return [2 /*return*/, _a.sent()];
                        }
                    });
                }); };
                commandLine.registerOnSendMessage(commandLineCallback);
                _this.addCommand({
                    id: commandId,
                    name: command.label,
                    callback: function () { return commandLineCallback(); },
                    hotkeys: [],
                });
                return commandLine;
            };
            // I would love to know if this view is already registered, but I don't know how.
            this.registerView(commandId, viewCreator);
        }
        else if (command.type == 'panel') {
            var viewCreator = function (leaf) {
                var panel = new LabPanel(leaf, commandId, command);
                var panelCallback = function () { return __awaiter(_this, void 0, void 0, function () {
                    var parameters, data;
                    return __generator(this, function (_a) {
                        switch (_a.label) {
                            case 0:
                                parameters = this.getDefaultPostParameters();
                                return [4 /*yield*/, this.doPost(commandUrl, parameters)];
                            case 1:
                                data = _a.sent();
                                data.label = command.label;
                                // Update the state of the view panel
                                panel.setData(data);
                                panel.draw();
                                return [2 /*return*/];
                        }
                    });
                }); };
                _this.addCommand({
                    id: commandId,
                    name: command.label,
                    callback: function () { return panelCallback(); },
                    hotkeys: [],
                });
                if (command.invokeOnOpen) {
                    panel.registerOnFileOpen(panelCallback);
                }
                return panel;
            };
            // I would love to know if this view is already registered, but I don't know how.
            this.registerView(commandId, viewCreator);
        }
        else if (command.type == 'insert-text' ||
            command.type == 'replace-text') {
            var callbackWithoutView_1 = function () { return __awaiter(_this, void 0, void 0, function () {
                var parameters, data, activeView, editor, doc, cursor;
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            parameters = this.getDefaultPostParameters();
                            return [4 /*yield*/, this.doPost(commandUrl, parameters)];
                        case 1:
                            data = _a.sent();
                            activeView = this.app.workspace.getActiveViewOfType(obsidian.MarkdownView);
                            if (command.type == 'replace-text' &&
                                activeView instanceof obsidian.MarkdownView) {
                                // Replaces the current selection
                                // const editor = activeView.sourceMode.cmEditor;
                                if (data.contents) {
                                    editor = activeView.editor;
                                    editor.replaceSelection(data.contents);
                                }
                            }
                            else if (command.type == 'insert-text' &&
                                activeView instanceof obsidian.MarkdownView) {
                                doc = activeView.editor.getDoc();
                                cursor = doc.getCursor();
                                if (data.contents) {
                                    doc.replaceRange(data.contents, cursor);
                                }
                            }
                            else {
                                console.error("Cannot process: ", command);
                            }
                            return [2 /*return*/];
                    }
                });
            }); };
            this.addCommand({
                id: commandId,
                name: command.label,
                callback: function () { return callbackWithoutView_1(); },
                hotkeys: [],
            });
        }
    };
    PythonLabPlugin.prototype.doPost = function (command_url, parameters) {
        return __awaiter(this, void 0, void 0, function () {
            var requestBody, response, data;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        requestBody = JSON.stringify(parameters);
                        if (this.settings.debug == 'verbose') {
                            console.info('Post:', command_url);
                            console.info('requestBody', requestBody);
                        }
                        return [4 /*yield*/, fetch(command_url, {
                                method: 'POST',
                                body: requestBody,
                                headers: {
                                    'content-type': 'application/json',
                                },
                            })];
                    case 1:
                        response = _a.sent();
                        return [4 /*yield*/, response.json()];
                    case 2:
                        data = _a.sent();
                        if (this.settings.debug == 'verbose') {
                            console.info('response data', data);
                        }
                        if (data.errors) {
                            console.error(data);
                            new Notification(data.message);
                        }
                        return [2 /*return*/, data];
                }
            });
        });
    };
    PythonLabPlugin.prototype.getDefaultPostParameters = function () {
        var parameters = {
            vaultPath: this.getVaultPath(),
        };
        var activeView = this.app.workspace.getActiveViewOfType(obsidian.MarkdownView);
        if (activeView) {
            var editor = activeView.editor;
            var selectedText = editor.getSelection();
            if (selectedText) {
                parameters.text = selectedText;
            }
            if (activeView.file && activeView.file.path) {
                parameters.notePath = activeView.file.path;
            }
        }
        return parameters;
    };
    PythonLabPlugin.prototype.loadSettings = function () {
        return __awaiter(this, void 0, void 0, function () {
            var _a, _b, _c, _d;
            return __generator(this, function (_e) {
                switch (_e.label) {
                    case 0:
                        _a = this;
                        _c = (_b = Object).assign;
                        _d = [DEFAULT_SETTINGS];
                        return [4 /*yield*/, _super.prototype.loadData.call(this)];
                    case 1:
                        _a.settings = _c.apply(_b, _d.concat([_e.sent()]));
                        return [2 /*return*/];
                }
            });
        });
    };
    PythonLabPlugin.prototype.saveSettings = function () {
        return __awaiter(this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0: return [4 /*yield*/, this.saveData(this.settings)];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    PythonLabPlugin.prototype.showPanel = function (commandId) {
        return __awaiter(this, void 0, void 0, function () {
            var existing;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        existing = this.app.workspace.getLeavesOfType(commandId);
                        if (existing.length) {
                            this.app.workspace.revealLeaf(existing[0]);
                            return [2 /*return*/];
                        }
                        return [4 /*yield*/, this.app.workspace.getRightLeaf(false).setViewState({
                                type: commandId,
                                active: true,
                            })];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        });
    };
    return PythonLabPlugin;
}(obsidian.Plugin));
/**
 * Settings
 */
var PythonLabSettings = /** @class */ (function (_super) {
    __extends(PythonLabSettings, _super);
    function PythonLabSettings(app, plugin) {
        var _this = _super.call(this, app, plugin) || this;
        _this.plugin = plugin;
        return _this;
    }
    PythonLabSettings.prototype.display = function () {
        var _this = this;
        var containerEl = this.containerEl;
        containerEl.empty();
        containerEl.createEl('h2', { text: 'Obsidian lab settings' });
        containerEl.createEl('h4', { text: 'Restart after making changes' });
        var settings = this.plugin.settings;
        var serverURLSetting = new obsidian.Setting(this.containerEl)
            .setName('Server url')
            .addText(function (text) {
            text.setValue(settings.server_url);
            text.onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    this.plugin.settings.server_url = value;
                    return [2 /*return*/];
                });
            }); });
        })
            .addExtraButton(function (b) {
            b.setIcon('reset')
                .setTooltip('set and refresh')
                .onClick(function () { return __awaiter(_this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0: return [4 /*yield*/, this.plugin.saveSettings()];
                        case 1:
                            _a.sent();
                            return [4 /*yield*/, this.plugin.loadCommandPanes()];
                        case 2:
                            _a.sent();
                            this.display();
                            return [2 /*return*/];
                    }
                });
            }); });
        });
        var updateSetting = function (commandId, command) { return __awaiter(_this, void 0, void 0, function () {
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        this.plugin.settings.commands[commandId] = command;
                        if (this.plugin.settings.debug == 'verbose') {
                            console.log('save', command);
                        }
                        return [4 /*yield*/, this.plugin.saveSettings()];
                    case 1:
                        _a.sent();
                        return [2 /*return*/];
                }
            });
        }); };
        getServerStatus(settings.server_url).then(function (serverStatus) {
            var e_4, _a;
            if (serverStatus.status == 'available') {
                var availableCommands = loadCommands(serverStatus.availableCommandUrls, settings.commands);
                var n = 0;
                try {
                    for (var availableCommands_2 = __values(availableCommands), availableCommands_2_1 = availableCommands_2.next(); !availableCommands_2_1.done; availableCommands_2_1 = availableCommands_2.next()) {
                        var _b = __read(availableCommands_2_1.value, 2), name_3 = _b[0], command = _b[1];
                        addCommandSetting(name_3, command);
                        n++;
                    }
                }
                catch (e_4_1) { e_4 = { error: e_4_1 }; }
                finally {
                    try {
                        if (availableCommands_2_1 && !availableCommands_2_1.done && (_a = availableCommands_2.return)) _a.call(availableCommands_2);
                    }
                    finally { if (e_4) throw e_4.error; }
                }
                serverURLSetting.setName("Server online [" + n + "]");
            }
            else {
                serverURLSetting
                    .setName('⚠ Cannot reach server')
                    .setDesc('')
                    .setClass('python-lab-error');
                console.log(serverStatus);
            }
            _this.setFooter(containerEl, settings);
        });
        /**
         * Given a command, adds the configuration
         * @param name
         * @param command
         */
        var addCommandSetting = function (name, command) {
            var commandEl = containerEl.createEl('div', {});
            var commandUrl = _this.plugin.commandUrlFromName(name);
            var commandDesc = "" + commandUrl;
            if (command.active) {
                new obsidian.Setting(commandEl)
                    .setName("" + name)
                    .setDesc(commandDesc)
                    // Type
                    .addDropdown(function (dropdown) {
                    dropdown.addOption('insert-text', 'Insert text');
                    dropdown.addOption('replace-text', 'Replace selected text');
                    dropdown.addOption('panel', 'Panel: text or lists');
                    dropdown.addOption('command-line', 'Chat');
                    // dropdown.addOption('graph', 'a graph');
                    dropdown.setValue(String(command.type)).onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0:
                                    command.type = value;
                                    return [4 /*yield*/, updateSetting(name, command)];
                                case 1:
                                    _a.sent();
                                    this.display();
                                    return [2 /*return*/];
                            }
                        });
                    }); });
                })
                    // Active or not
                    .addToggle(function (toggle) {
                    toggle.setValue(command.active);
                    toggle.onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0:
                                    command.active = value;
                                    return [4 /*yield*/, updateSetting(name, command)];
                                case 1:
                                    _a.sent();
                                    this.display();
                                    return [2 /*return*/];
                            }
                        });
                    }); });
                });
                var isWidget = command.type == 'panel' || command.type == 'command-line';
                new obsidian.Setting(commandEl)
                    .setDesc(isWidget ? 'Widget name' : 'Command name')
                    // Name
                    .addText(function (text) {
                    text.setValue(command.label);
                    text.onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0:
                                    command.label = value;
                                    return [4 /*yield*/, updateSetting(name, command)];
                                case 1:
                                    _a.sent();
                                    return [2 /*return*/];
                            }
                        });
                    }); });
                });
                if (isWidget) {
                    new obsidian.Setting(commandEl)
                        .setDesc('Widget icon')
                        // Icon
                        .addDropdown(function (dropdown) {
                        icons.forEach(function (icon) {
                            dropdown.addOption(icon, icon);
                        });
                        dropdown
                            .setValue(String(command.icon))
                            .onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        command.icon = value;
                                        return [4 /*yield*/, updateSetting(name, command)];
                                    case 1:
                                        _a.sent();
                                        this.display();
                                        return [2 /*return*/];
                                }
                            });
                        }); });
                    })
                        .addExtraButton(function (b) {
                        b.setIcon(command.icon)
                            .setTooltip('Icon shown in the widget tab')
                            .onClick(function () { return __awaiter(_this, void 0, void 0, function () { return __generator(this, function (_a) {
                            return [2 /*return*/];
                        }); }); });
                    });
                }
                if (command.type == 'panel') {
                    new obsidian.Setting(commandEl)
                        .setDesc('Additional triggers for panel')
                        .addDropdown(function (dropdown) {
                        dropdown.addOption('false', 'no triggers');
                        dropdown.addOption('true', 'trigers when opening a file');
                        dropdown
                            .setValue(String(command.invokeOnOpen))
                            .onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                            return __generator(this, function (_a) {
                                switch (_a.label) {
                                    case 0:
                                        command.invokeOnOpen = value == 'true';
                                        return [4 /*yield*/, updateSetting(name, command)];
                                    case 1:
                                        _a.sent();
                                        this.display();
                                        return [2 /*return*/];
                                }
                            });
                        }); });
                    });
                }
            }
            else {
                new obsidian.Setting(commandEl)
                    .setName("" + name)
                    .setDesc(commandDesc)
                    // Active or not
                    .addToggle(function (toggle) {
                    toggle.setValue(command.active);
                    toggle.onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                        return __generator(this, function (_a) {
                            switch (_a.label) {
                                case 0:
                                    command.active = value;
                                    return [4 /*yield*/, updateSetting(name, command)];
                                case 1:
                                    _a.sent();
                                    this.display();
                                    return [2 /*return*/];
                            }
                        });
                    }); });
                });
            }
        };
    };
    PythonLabSettings.prototype.setFooter = function (containerEl, settings) {
        var _this = this;
        new obsidian.Setting(containerEl)
            .setName('Debug')
            .setDesc('')
            .addDropdown(function (dropdown) {
            dropdown.addOption('off', 'off');
            dropdown.addOption('verbose', 'verbose');
            // dropdown.addOption('graph', 'a graph');
            dropdown.setValue(String(settings.debug)).onChange(function (value) { return __awaiter(_this, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            this.plugin.settings.debug = value;
                            return [4 /*yield*/, this.plugin.saveSettings()];
                        case 1:
                            _a.sent();
                            this.display();
                            return [2 /*return*/];
                    }
                });
            }); });
        });
        containerEl.createEl('a', {
            text: 'You can find a simple server at github: obsidian-lab-py',
            href: 'https://github.com/cristianvasquez/obsidian-lab-py',
        });
        containerEl.createEl('p', {
            text: 'Pull requests are both welcome and appreciated. :)',
        });
    };
    return PythonLabSettings;
}(obsidian.PluginSettingTab));

module.exports = PythonLabPlugin;


/* nosourcemap */