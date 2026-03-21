/**
 * section_editor.js
 * Динамические редакторы для каждого типа секции.
 * Заменяет textarea с | на удобные поля ввода.
 * Бэкенд не меняется — перед сабмитом данные сериализуются обратно в |.
 */

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // Утилиты
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
        var t = el('textarea', {
            className: 'se-input se-textarea',
            placeholder: placeholder,
        });
        t.value = value || '';
        return t;
    }

    function select(options, value) {
        var s = el('select', { className: 'se-input se-select' });
        options.forEach(function (opt) {
            var o = el('option', { value: opt.value }, []);
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

    function removeBtn(row) {
        return btn('✕', 'se-btn--remove', function () {
            row.parentNode && row.parentNode.removeChild(row);
        });
    }

    function makeRow(fields, onRemove) {
        var row = el('div', { className: 'se-row' });
        fields.forEach(function (f) { row.appendChild(f); });
        var rb = btn('✕', 'se-btn--remove', function () {
            row.parentNode && row.parentNode.removeChild(row);
        });
        row.appendChild(rb);
        return row;
    }

    function makeList(containerId) {
        var c = document.getElementById(containerId);
        if (!c) c = el('div', { className: 'se-list' });
        return c;
    }

    function hideOriginal(fieldName) {
        var row = document.querySelector('.form-row.field-' + fieldName);
        if (row) row.style.display = 'none';
        var field = document.querySelector('[name="' + fieldName + '"]');
        return field;
    }

    function wrapEditor(title, list, addBtn, hint) {
        var wrapper = el('div', { className: 'se-editor' });
        var header = el('div', { className: 'se-editor__header' });
        var titleEl = el('strong', { html: title });
        header.appendChild(titleEl);
        if (hint) {
            var hintEl = el('span', { className: 'se-editor__hint', html: hint });
            header.appendChild(hintEl);
        }
        wrapper.appendChild(header);
        wrapper.appendChild(list);
        wrapper.appendChild(addBtn);
        return wrapper;
    }

    // -----------------------------------------------------------------------
    // Парсеры из |
    // -----------------------------------------------------------------------

    function parseLines(raw, n) {
        if (!raw) return [];
        return raw.trim().split('\n').map(function (line) {
            return line.split('|', n);
        }).filter(function (p) { return p[0] && p[0].trim(); });
    }

    // -----------------------------------------------------------------------
    // Сериализация обратно в | перед сабмитом
    // -----------------------------------------------------------------------

    function onSubmit(form, serializers) {
        form.addEventListener('submit', function () {
            serializers.forEach(function (fn) { fn(); });
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: счётчики (значение | подпись)
    // -----------------------------------------------------------------------

    function initCounters() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(value, label) {
            var row = makeRow([
                input('Значение', value, 'se-input--sm'),
                input('Подпись', label),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 2).forEach(function (p) { addRow(p[0].trim(), (p[1] || '').trim()); });
        if (!list.children.length) addRow('', '');

        var addButton = btn('+ Добавить счётчик', 'se-btn--add', function () { addRow('', ''); });
        var wrapper = wrapEditor('Счётчики', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input');
                var v = inputs[0].value.trim(), l = inputs[1].value.trim();
                if (v) lines.push(v + '|' + l);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: карточки (иконка | заголовок | текст)
    // -----------------------------------------------------------------------

    function initCards() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(icon, title, text) {
            var row = makeRow([
                input('Иконка/эмодзи', icon, 'se-input--icon'),
                input('Заголовок', title),
                input('Текст', text, 'se-input--wide'),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 3).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim(), (p[2] || '').trim());
        });
        if (!list.children.length) addRow('', '', '');

        var addButton = btn('+ Добавить карточку', 'se-btn--add', function () { addRow('', '', ''); });
        var wrapper = wrapEditor('Карточки', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input');
                var i = inputs[0].value.trim(), t = inputs[1].value.trim(), x = inputs[2].value.trim();
                if (t) lines.push(i + '|' + t + '|' + x);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: команда (имя | должность | описание)
    // -----------------------------------------------------------------------

    function initTeam() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, position, description) {
            var row = makeRow([
                input('Имя', name),
                input('Должность', position),
                input('Описание', description, 'se-input--wide'),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 3).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim(), (p[2] || '').trim());
        });
        if (!list.children.length) addRow('', '', '');

        var addButton = btn('+ Добавить участника', 'se-btn--add', function () { addRow('', '', ''); });
        var wrapper = wrapEditor('Команда', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input');
                var n = inputs[0].value.trim(), p = inputs[1].value.trim(), d = inputs[2].value.trim();
                if (n) lines.push(n + '|' + p + '|' + d);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: шаги (заголовок | описание)
    // -----------------------------------------------------------------------

    function initSteps() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(title, description) {
            var row = makeRow([
                input('Заголовок шага', title),
                input('Описание', description, 'se-input--wide'),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim());
        });
        if (!list.children.length) addRow('', '');

        var addButton = btn('+ Добавить шаг', 'se-btn--add', function () { addRow('', ''); });
        var wrapper = wrapEditor('Шаги', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input');
                var t = inputs[0].value.trim(), d = inputs[1].value.trim();
                if (t) lines.push(t + '|' + d);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: FAQ (вопрос | ответ)
    // -----------------------------------------------------------------------

    function initFaq() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(question, answer) {
            var row = makeRow([
                input('Вопрос', question, 'se-input--wide'),
                textarea('Ответ', answer),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim());
        });
        if (!list.children.length) addRow('', '');

        var addButton = btn('+ Добавить вопрос', 'se-btn--add', function () { addRow('', ''); });
        var wrapper = wrapEditor('Вопросы и ответы', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var q = row.querySelector('input').value.trim();
                var a = row.querySelector('textarea').value.trim().replace(/\n/g, ' ');
                if (q) lines.push(q + '|' + a);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: отзывы (имя | текст)
    // -----------------------------------------------------------------------

    function initTestimonials() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, text) {
            var row = makeRow([
                input('Имя', name, 'se-input--sm'),
                textarea('Текст отзыва', text),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim());
        });
        if (!list.children.length) addRow('', '');

        var addButton = btn('+ Добавить отзыв', 'se-btn--add', function () { addRow('', ''); });
        var wrapper = wrapEditor('Отзывы', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var n = row.querySelector('input').value.trim();
                var t = row.querySelector('textarea').value.trim().replace(/\n/g, ' ');
                if (n) lines.push(n + '|' + t);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: круговая диаграмма (подпись | значение)
    // -----------------------------------------------------------------------

    function initChartPie() {
        var field = hideOriginal('items_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(label, value) {
            var row = makeRow([
                input('Подпись', label, 'se-input--wide'),
                input('Значение', value, 'se-input--sm'),
            ]);
            list.appendChild(row);
        }

        parseLines(field.value, 2).forEach(function (p) {
            addRow((p[0] || '').trim(), (p[1] || '').trim());
        });
        if (!list.children.length) addRow('', '');

        var addButton = btn('+ Добавить сегмент', 'se-btn--add', function () { addRow('', ''); });
        var wrapper = wrapEditor('Сегменты диаграммы', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('input');
                var l = inputs[0].value.trim(), v = inputs[1].value.trim();
                if (l) lines.push(l + '|' + v);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: форма обратной связи
    // -----------------------------------------------------------------------

    var FIELD_TYPES = [
        { value: 'text',     label: 'Текст' },
        { value: 'email',    label: 'Email' },
        { value: 'tel',      label: 'Телефон' },
        { value: 'textarea', label: 'Большой текст' },
    ];

    function initFormSection() {
        var field = hideOriginal('fields_raw');
        if (!field) return;

        var list = el('div', { className: 'se-list' });

        function addRow(name, type, label, required) {
            var nameInput  = input('Имя поля (латиница)', name, 'se-input--sm');
            var typeSelect = select(FIELD_TYPES, type || 'text');
            var labelInput = input('Подпись', label);
            var reqLabel   = checkbox('Обязательное', required);

            var row = el('div', { className: 'se-row' });
            row.appendChild(nameInput);
            row.appendChild(typeSelect);
            row.appendChild(labelInput);
            row.appendChild(reqLabel);
            row.appendChild(btn('✕', 'se-btn--remove', function () {
                row.parentNode && row.parentNode.removeChild(row);
            }));
            list.appendChild(row);
        }

        parseLines(field.value, 4).forEach(function (p) {
            addRow(
                (p[0] || '').trim(),
                (p[1] || 'text').trim(),
                (p[2] || '').trim(),
                (p[3] || '').trim() === 'true'
            );
        });
        if (!list.children.length) addRow('', 'text', '', false);

        var addButton = btn('+ Добавить поле', 'se-btn--add', function () { addRow('', 'text', '', false); });
        var wrapper = wrapEditor('Поля формы', list, addButton);
        field.parentNode.parentNode.insertBefore(wrapper, field.parentNode);

        getForm().addEventListener('submit', function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs  = row.querySelectorAll('input[type="text"]');
                var sel     = row.querySelector('select');
                var cb      = row.querySelector('input[type="checkbox"]');
                var name    = inputs[0].value.trim();
                var label   = inputs[1].value.trim();
                var type    = sel ? sel.value : 'text';
                var req     = cb && cb.checked ? 'true' : 'false';
                if (name) lines.push(name + '|' + type + '|' + label + '|' + req);
            });
            field.value = lines.join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Редактор: таблица (Excel-стиль)
    // -----------------------------------------------------------------------

    function initTable() {
        var headersField = hideOriginal('headers_raw');
        var rowsField    = hideOriginal('rows_raw');
        if (!headersField || !rowsField) return;

        // Парсим начальное состояние
        var initHeaders = headersField.value ? headersField.value.split('|').map(function (h) { return h.trim(); }) : [''];
        var initRows = rowsField.value
            ? rowsField.value.trim().split('\n').map(function (line) {
                return line.split('|').map(function (c) { return c.trim(); });
            })
            : [[]];

        var colCount = initHeaders.length || 1;

        var wrapper  = el('div', { className: 'se-editor se-table-editor' });
        var header   = el('div', { className: 'se-editor__header' });
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

        // Рендер заголовков
        function renderHead() {
            thead.innerHTML = '';
            var tr = el('tr');
            // Кнопка удаления строки (заглушка для выравнивания)
            tr.appendChild(el('th', { className: 'se-table__ctrl' }));
            for (var i = 0; i < colCount; i++) {
                (function (ci) {
                    var th = el('th');
                    var inp = input('Заголовок', initHeaders[ci] || '');
                    inp.dataset.col = ci;
                    inp.dataset.isHeader = '1';
                    th.appendChild(inp);
                    // Кнопка удалить столбец
                    var delCol = btn('✕', 'se-btn--remove se-btn--col', function () {
                        removeCol(ci);
                    });
                    th.appendChild(delCol);
                    tr.appendChild(th);
                })(i);
            }
            // Кнопка добавить столбец
            var addColTh = el('th');
            addColTh.appendChild(btn('+ столбец', 'se-btn--add-col', addCol));
            tr.appendChild(addColTh);
            thead.appendChild(tr);
        }

        // Рендер строк
        function renderBody() {
            tbody.innerHTML = '';
            initRows.forEach(function (rowData, ri) {
                appendBodyRow(rowData, ri);
            });
        }

        function appendBodyRow(rowData, ri) {
            var tr = el('tr');
            // Кнопка удалить строку
            var tdCtrl = el('td', { className: 'se-table__ctrl' });
            tdCtrl.appendChild(btn('✕', 'se-btn--remove', function () {
                tbody.removeChild(tr);
            }));
            tr.appendChild(tdCtrl);

            for (var i = 0; i < colCount; i++) {
                var td = el('td');
                var inp = input('', (rowData && rowData[i]) || '');
                td.appendChild(inp);
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }

        function addCol() {
            initHeaders.push('');
            // Добавляем заголовок
            colCount++;
            initRows = getCurrentRows();
            initHeaders = getCurrentHeaders();
            renderHead();
            renderBody();
        }

        function removeCol(ci) {
            if (colCount <= 1) return;
            var headers = getCurrentHeaders();
            headers.splice(ci, 1);
            var rows = getCurrentRows().map(function (row) {
                var r = row.slice();
                r.splice(ci, 1);
                return r;
            });
            colCount--;
            initHeaders = headers;
            initRows = rows;
            renderHead();
            renderBody();
        }

        function getCurrentHeaders() {
            var result = [];
            thead.querySelectorAll('input[data-is-header]').forEach(function (inp) {
                result.push(inp.value.trim());
            });
            return result;
        }

        function getCurrentRows() {
            var result = [];
            tbody.querySelectorAll('tr').forEach(function (tr) {
                var cells = [];
                tr.querySelectorAll('td:not(.se-table__ctrl) input').forEach(function (inp) {
                    cells.push(inp.value.trim());
                });
                result.push(cells);
            });
            return result;
        }

        // Кнопка добавить строку
        var addRowBtn = btn('+ Добавить строку', 'se-btn--add', function () {
            appendBodyRow([], tbody.children.length);
        });
        wrapper.appendChild(addRowBtn);

        renderHead();
        renderBody();

        // Вставляем редактор перед скрытым полем headers_raw
        headersField.parentNode.parentNode.insertBefore(wrapper, headersField.parentNode);

        getForm().addEventListener('submit', function () {
            headersField.value = getCurrentHeaders().join('|');
            rowsField.value    = getCurrentRows().map(function (r) { return r.join('|'); }).join('\n');
        });
    }

    // -----------------------------------------------------------------------
    // Определяем тип секции и запускаем нужный редактор
    // -----------------------------------------------------------------------

    function getForm() {
        return document.querySelector('#content-main form') || document.querySelector('form');
    }

    function getSectionType() {
        // Django рендерит поле type как readonly span или select
        var typeSelect = document.querySelector('[name="type"]');
        if (typeSelect) return typeSelect.value;
        // readonly — ищем текстовое значение в data-атрибуте или hidden input
        var hidden = document.querySelector('input[type="hidden"][name="type"]');
        if (hidden) return hidden.value;
        // Unfold может рендерить как текст внутри .field-type
        var fieldType = document.querySelector('.field-type .readonly');
        if (fieldType) return fieldType.textContent.trim();
        return null;
    }

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

    document.addEventListener('DOMContentLoaded', function () {
        var type = getSectionType();
        if (type && EDITORS[type]) {
            EDITORS[type]();
        }
    });

})();