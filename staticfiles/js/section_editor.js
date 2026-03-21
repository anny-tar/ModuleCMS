/**
 * section_editor.js
 * Динамические редакторы для каждого типа секции.
 * Unfold рендерит поля через .field-line.field-XXX (не .form-row.field-XXX).
 * Все поля всех типов рендерятся сразу (data-section-type на виджете),
 * JS показывает нужные при смене типа в дропдауне — без перезагрузки.
 */

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // Утилиты DOM
    // -----------------------------------------------------------------------

    function el(tag, attrs, children) {
        var node = document.createElement(tag);
        if (attrs) Object.keys(attrs).forEach(function (k) {
            if (k === 'className') node.className = attrs[k];
            else if (k === 'style') node.style.cssText = attrs[k];
            else if (k === 'html') node.innerHTML = attrs[k];
            else node.setAttribute(k, attrs[k]);
        });
        if (children) children.forEach(function (c) { if (c) node.appendChild(c); });
        return node;
    }

    function btn(label, cls, onClick) {
        var b = el('button', { type: 'button', className: 'se-btn ' + cls, html: label });
        b.addEventListener('click', onClick);
        return b;
    }

    function input(placeholder, value, cls) {
        return el('input', {
            type: 'text',
            className: 'se-input ' + (cls || ''),
            placeholder: placeholder,
            value: value || '',
        });
    }

    function textarea(placeholder, value) {
        var t = el('textarea', { className: 'se-input se-textarea', placeholder: placeholder });
        t.value = value || '';
        return t;
    }

    function select(options, value) {
        var s = el('select', { className: 'se-input se-select' });
        options.forEach(function (opt) {
            var o = el('option', { value: opt.value });
            o.textContent = opt.label;
            if (opt.value === value) o.selected = true;
            s.appendChild(o);
        });
        return s;
    }

    function checkbox(label, checked) {
        var wrap = el('label', { className: 'se-checkbox-label' });
        var cb = el('input', { type: 'checkbox' });
        cb.checked = !!checked;
        wrap.appendChild(cb);
        wrap.appendChild(document.createTextNode(' ' + label));
        return wrap;
    }

    function makeRow(fields) {
        var row = el('div', { className: 'se-row' });
        fields.forEach(function (f) { row.appendChild(f); });
        row.appendChild(btn('✕', 'se-btn--remove', function () {
            row.parentNode && row.parentNode.removeChild(row);
        }));
        return row;
    }

    function wrapEditor(title, list, addBtn) {
        var wrapper = el('div', { className: 'se-editor' });
        var header  = el('div', { className: 'se-editor__header' });
        header.appendChild(el('strong', { html: title }));
        wrapper.appendChild(header);
        wrapper.appendChild(list);
        wrapper.appendChild(addBtn);
        return wrapper;
    }

    function parseLines(raw, n) {
        if (!raw) return [];
        return raw.trim().split('\n').map(function (line) {
            return line.split('|', n);
        }).filter(function (p) { return p[0] && p[0].trim(); });
    }

    // -----------------------------------------------------------------------
    // Найти .field-line контейнер поля по имени (Unfold-специфично)
    // -----------------------------------------------------------------------

    function findFieldRow(fieldName) {
        // Unfold: <div class="field-line field-XXX ...">
        return document.querySelector('.field-line.field-' + fieldName);
    }

    function findFieldInput(fieldName) {
        return document.querySelector('[name="' + fieldName + '"]');
    }

    // -----------------------------------------------------------------------
    // Показать/скрыть поля по типу секции
    // -----------------------------------------------------------------------

    // Все поля специфичные для типов (те что рендерятся через SectionAdminForm)
    var ALL_TYPE_FIELD_NAMES = [
        'heading', 'subheading', 'button_text', 'button_url',  // hero
        'content',                                               // text
        'items_raw',                                             // counters/cards/team/steps/faq/testimonials/chart_pie
        'chart_title',                                           // chart_pie
        'fields_raw',                                            // form
        'headers_raw', 'rows_raw',                              // table
    ];

    // Какие поля показывать для каждого типа
    var TYPE_FIELDS = {
        'hero':         ['heading', 'subheading', 'button_text', 'button_url'],
        'text':         ['content'],
        'counters':     ['items_raw'],
        'cards':        ['items_raw'],
        'team':         ['items_raw'],
        'steps':        ['items_raw'],
        'faq':          ['items_raw'],
        'testimonials': ['items_raw'],
        'chart_pie':    ['chart_title', 'items_raw'],
        'form':         ['fields_raw'],
        'table':        ['headers_raw', 'rows_raw'],
        'contacts':     [],
    };

    function applyFieldVisibility(type) {
        var visibleFields = TYPE_FIELDS[type] || [];

        ALL_TYPE_FIELD_NAMES.forEach(function (name) {
            var row = findFieldRow(name);
            if (!row) return;
            if (visibleFields.indexOf(name) !== -1) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }

    // -----------------------------------------------------------------------
    // Контейнер для динамических редакторов (counters, cards, etc.)
    // -----------------------------------------------------------------------

    var editorMount   = null;
    var submitHandlers = [];

    function getOrCreateMount() {
        if (editorMount) return editorMount;
        editorMount = el('div', { className: 'se-mount' });

        // Вставляем после последнего fieldset внутри формы, перед submit-row
        var form = document.querySelector('#content-main form, form#section_form');
        if (!form) return editorMount;

        var submitRow = document.getElementById('submit-row');
        if (submitRow) {
            submitRow.parentNode.insertBefore(editorMount, submitRow);
        } else {
            form.appendChild(editorMount);
        }
        return editorMount;
    }

    function clearEditor() {
        if (editorMount) editorMount.innerHTML = '';
        submitHandlers = [];
    }

    function onSubmit(fn) {
        submitHandlers.push(fn);
    }

    // -----------------------------------------------------------------------
    // Редакторы — только для типов где нужен визуальный построитель
    // (hero и text используют стандартные поля Django, редактор не нужен)
    // -----------------------------------------------------------------------

    function initCounters() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(value, label) {
            list.appendChild(makeRow([
                input('Значение', value, 'se-input--sm'),
                input('Подпись', label),
            ]));
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow(p[0].trim(), (p[1] || '').trim());
        });
        if (!list.children.length) addRow('', '');

        getOrCreateMount().appendChild(
            wrapEditor('Счётчики / Достижения', list,
                btn('+ Добавить счётчик', 'se-btn--add', function () { addRow('', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var v = inputs[0].value.trim(), l = inputs[1].value.trim();
                if (v) lines.push(v + '|' + l);
            });
            field.value = lines.join('\n');
        });
    }

    function initCards() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(icon, title, text) {
            list.appendChild(makeRow([
                input('Иконка/эмодзи', icon, 'se-input--icon'),
                input('Заголовок', title),
                input('Текст', text, 'se-input--wide'),
            ]));
        }

        parseLines(field.value, 3).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim(), (p[2]||'').trim());
        });
        if (!list.children.length) addRow('', '', '');

        getOrCreateMount().appendChild(
            wrapEditor('Карточки с преимуществами', list,
                btn('+ Добавить карточку', 'se-btn--add', function () { addRow('', '', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var i = inputs[0].value.trim(), t = inputs[1].value.trim(), x = inputs[2].value.trim();
                if (t) lines.push(i + '|' + t + '|' + x);
            });
            field.value = lines.join('\n');
        });
    }

    function initTeam() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, position, description) {
            list.appendChild(makeRow([
                input('Имя', name),
                input('Должность', position),
                input('Описание', description, 'se-input--wide'),
            ]));
        }

        parseLines(field.value, 3).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim(), (p[2]||'').trim());
        });
        if (!list.children.length) addRow('', '', '');

        getOrCreateMount().appendChild(
            wrapEditor('Команда', list,
                btn('+ Добавить участника', 'se-btn--add', function () { addRow('', '', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var n = inputs[0].value.trim(), p = inputs[1].value.trim(), d = inputs[2].value.trim();
                if (n) lines.push(n + '|' + p + '|' + d);
            });
            field.value = lines.join('\n');
        });
    }

    function initSteps() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(title, description) {
            list.appendChild(makeRow([
                input('Заголовок шага', title),
                input('Описание', description, 'se-input--wide'),
            ]));
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim());
        });
        if (!list.children.length) addRow('', '');

        getOrCreateMount().appendChild(
            wrapEditor('Этапы / Нумерованный список', list,
                btn('+ Добавить шаг', 'se-btn--add', function () { addRow('', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var t = inputs[0].value.trim(), d = inputs[1].value.trim();
                if (t) lines.push(t + '|' + d);
            });
            field.value = lines.join('\n');
        });
    }

    function initFaq() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(question, answer) {
            list.appendChild(makeRow([
                input('Вопрос', question, 'se-input--wide'),
                textarea('Ответ', answer),
            ]));
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim());
        });
        if (!list.children.length) addRow('', '');

        getOrCreateMount().appendChild(
            wrapEditor('Вопросы и ответы', list,
                btn('+ Добавить вопрос', 'se-btn--add', function () { addRow('', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var q = row.querySelector('input[type="text"]').value.trim();
                var a = row.querySelector('textarea').value.trim().replace(/\n/g, ' ');
                if (q) lines.push(q + '|' + a);
            });
            field.value = lines.join('\n');
        });
    }

    function initTestimonials() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, text) {
            list.appendChild(makeRow([
                input('Имя', name, 'se-input--sm'),
                textarea('Текст отзыва', text),
            ]));
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim());
        });
        if (!list.children.length) addRow('', '');

        getOrCreateMount().appendChild(
            wrapEditor('Отзывы', list,
                btn('+ Добавить отзыв', 'se-btn--add', function () { addRow('', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var n = row.querySelector('input[type="text"]').value.trim();
                var t = row.querySelector('textarea').value.trim().replace(/\n/g, ' ');
                if (n) lines.push(n + '|' + t);
            });
            field.value = lines.join('\n');
        });
    }

    function initChartPie() {
        var field = findFieldInput('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(label, value) {
            list.appendChild(makeRow([
                input('Подпись', label, 'se-input--wide'),
                input('Значение', value, 'se-input--sm'),
            ]));
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'').trim());
        });
        if (!list.children.length) addRow('', '');

        getOrCreateMount().appendChild(
            wrapEditor('Сегменты круговой диаграммы', list,
                btn('+ Добавить сегмент', 'se-btn--add', function () { addRow('', ''); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var l = inputs[0].value.trim(), v = inputs[1].value.trim();
                if (l) lines.push(l + '|' + v);
            });
            field.value = lines.join('\n');
        });
    }

    var FIELD_TYPES = [
        { value: 'text',     label: 'Текст' },
        { value: 'email',    label: 'Email' },
        { value: 'tel',      label: 'Телефон' },
        { value: 'textarea', label: 'Большой текст' },
    ];

    function initFormSection() {
        var field = findFieldInput('fields_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, type, label, required) {
            var nameInput  = input('Имя поля (латиница)', name, 'se-input--sm');
            var typeSelect = select(FIELD_TYPES, type || 'text');
            var labelInput = input('Подпись', label);
            var reqLabel   = checkbox('Обязательное', required);
            var row = el('div', { className: 'se-row' });
            [nameInput, typeSelect, labelInput, reqLabel].forEach(function(f) { row.appendChild(f); });
            row.appendChild(btn('✕', 'se-btn--remove', function () {
                row.parentNode && row.parentNode.removeChild(row);
            }));
            list.appendChild(row);
        }

        parseLines(field.value, 4).forEach(function (p) {
            addRow((p[0]||'').trim(), (p[1]||'text').trim(), (p[2]||'').trim(), (p[3]||'').trim() === 'true');
        });
        if (!list.children.length) addRow('', 'text', '', false);

        getOrCreateMount().appendChild(
            wrapEditor('Поля формы обратной связи', list,
                btn('+ Добавить поле', 'se-btn--add', function () { addRow('', 'text', '', false); }))
        );

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input[type="text"]');
                var sel    = row.querySelector('select');
                var cb     = row.querySelector('input[type="checkbox"]');
                var name   = inputs[0].value.trim();
                var label  = inputs[1].value.trim();
                var type   = sel ? sel.value : 'text';
                var req    = cb && cb.checked ? 'true' : 'false';
                if (name) lines.push(name + '|' + type + '|' + label + '|' + req);
            });
            field.value = lines.join('\n');
        });
    }

    function initTable() {
        var headersField = findFieldInput('headers_raw');
        var rowsField    = findFieldInput('rows_raw');
        if (!headersField || !rowsField) return;

        var initHeaders = headersField.value
            ? headersField.value.split('|').map(function (h) { return h.trim(); })
            : [''];
        var initRows = rowsField.value
            ? rowsField.value.trim().split('\n').map(function (line) {
                return line.split('|').map(function (c) { return c.trim(); });
            })
            : [[]];
        var colCount = initHeaders.length || 1;

        var wrapper   = el('div', { className: 'se-editor se-table-editor' });
        var header    = el('div', { className: 'se-editor__header' });
        header.appendChild(el('strong', { html: 'Таблица' }));
        wrapper.appendChild(header);

        var tableWrap = el('div', { className: 'se-table-wrap' });
        var table     = el('table', { className: 'se-table' });
        var thead     = el('thead');
        var tbody     = el('tbody');
        table.appendChild(thead);
        table.appendChild(tbody);
        tableWrap.appendChild(table);
        wrapper.appendChild(tableWrap);

        function renderHead() {
            thead.innerHTML = '';
            var tr = el('tr');
            tr.appendChild(el('th', { className: 'se-table__ctrl' }));
            for (var i = 0; i < colCount; i++) {
                (function (ci) {
                    var th  = el('th');
                    var inp = input('Заголовок', initHeaders[ci] || '');
                    inp.dataset.col = ci; inp.dataset.isHeader = '1';
                    th.appendChild(inp);
                    th.appendChild(btn('✕', 'se-btn--remove se-btn--col', function () { removeCol(ci); }));
                    tr.appendChild(th);
                })(i);
            }
            var addColTh = el('th');
            addColTh.appendChild(btn('+ столбец', 'se-btn--add-col', addCol));
            tr.appendChild(addColTh);
            thead.appendChild(tr);
        }

        function renderBody() {
            tbody.innerHTML = '';
            initRows.forEach(function (rowData) { appendBodyRow(rowData); });
        }

        function appendBodyRow(rowData) {
            var tr     = el('tr');
            var tdCtrl = el('td', { className: 'se-table__ctrl' });
            tdCtrl.appendChild(btn('✕', 'se-btn--remove', function () { tbody.removeChild(tr); }));
            tr.appendChild(tdCtrl);
            for (var i = 0; i < colCount; i++) {
                var td = el('td');
                td.appendChild(input('', (rowData && rowData[i]) || ''));
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }

        function getCurrentHeaders() {
            var r = [];
            thead.querySelectorAll('input[data-is-header]').forEach(function (inp) { r.push(inp.value.trim()); });
            return r;
        }

        function getCurrentRows() {
            var r = [];
            tbody.querySelectorAll('tr').forEach(function (tr) {
                var cells = [];
                tr.querySelectorAll('td:not(.se-table__ctrl) input').forEach(function (inp) { cells.push(inp.value.trim()); });
                r.push(cells);
            });
            return r;
        }

        function addCol() {
            colCount++;
            initHeaders = getCurrentHeaders(); initHeaders.push('');
            initRows = getCurrentRows();
            renderHead(); renderBody();
        }

        function removeCol(ci) {
            if (colCount <= 1) return;
            var headers = getCurrentHeaders(); headers.splice(ci, 1);
            var rows = getCurrentRows().map(function (row) { var r = row.slice(); r.splice(ci, 1); return r; });
            colCount--; initHeaders = headers; initRows = rows;
            renderHead(); renderBody();
        }

        wrapper.appendChild(btn('+ Добавить строку', 'se-btn--add', function () { appendBodyRow([]); }));
        renderHead(); renderBody();
        getOrCreateMount().appendChild(wrapper);

        onSubmit(function () {
            headersField.value = getCurrentHeaders().join('|');
            rowsField.value    = getCurrentRows().map(function (r) { return r.join('|'); }).join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Реестр редакторов (только те типы где нужен визуальный построитель)
    // -----------------------------------------------------------------------

    var EDITORS = {
        'counters':     initCounters,
        'cards':        initCards,
        'team':         initTeam,
        'steps':        initSteps,
        'faq':          initFaq,
        'testimonials': initTestimonials,
        'chart_pie':    initChartPie,
        'form':         initFormSection,
        'table':        initTable,
    };

    // -----------------------------------------------------------------------
    // Запуск редактора для типа
    // -----------------------------------------------------------------------

    function runEditor(type) {
        clearEditor();
        applyFieldVisibility(type);
        var initFn = EDITORS[type];
        if (initFn) initFn();
    }

    // -----------------------------------------------------------------------
    // Привязка submit один раз
    // -----------------------------------------------------------------------

    function bindSubmit() {
        var form = document.querySelector('form#section_form') || document.querySelector('#content-main form');
        if (!form || form._seBound) return;
        form._seBound = true;
        form.addEventListener('submit', function () {
            submitHandlers.forEach(function (fn) { fn(); });
        });
    }

    // -----------------------------------------------------------------------
    // Init
    // -----------------------------------------------------------------------

    document.addEventListener('DOMContentLoaded', function () {
        var typeSelect = document.querySelector('select[name="type"]');
        if (!typeSelect) return;  // не на форме секции

        bindSubmit();

        // Начальный рендер
        runEditor(typeSelect.value);

        // Смена типа в дропдауне
        typeSelect.addEventListener('change', function () {
            runEditor(this.value);
        });
    });

})();