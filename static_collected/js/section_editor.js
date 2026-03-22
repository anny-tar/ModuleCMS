/**
 * section_editor.js
 *
 * Логика работы:
 * 1. При загрузке страницы читаем текущий тип из дропдауна.
 * 2. Делаем GET /pages/section/fields/?type=X&section_id=Y
 * 3. Django возвращает JSON с описанием полей и текущими значениями.
 * 4. JS рендерит редактор — красивые инпуты вместо сырых textarea.
 * 5. Перед сабмитом собираем данные из редактора в JSON
 *    и кладём в скрытый input #section-data-input.
 * 6. Django читает этот JSON и сохраняет в Section.data.
 */

(function () {
    'use strict';

    // -----------------------------------------------------------------------
    // Иконки типов — дублируем из Python для использования в UI
    // -----------------------------------------------------------------------
    var ICONS = {
        hero:         '🖼️',
        text:         '📝',
        counters:     '🔢',
        cards:        '🃏',
        team:         '👥',
        steps:        '👣',
        table:        '📊',
        chart_pie:    '🥧',
        form:         '📬',
        faq:          '❓',
        testimonials: '💬',
        contacts:     '📍',
    };

    // -----------------------------------------------------------------------
    // Типы у которых нужен построитель строк (вместо одного textarea)
    // -----------------------------------------------------------------------
    var ROW_BUILDERS = {
        counters:     { cols: ['Значение', 'Подпись'],                        field: 'items_raw', addLabel: '+ Добавить счётчик' },
        cards:        { cols: ['Иконка', 'Заголовок', 'Текст'],               field: 'items_raw', addLabel: '+ Добавить карточку' },
        team:         { cols: ['Имя', 'Должность', 'Описание'],               field: 'items_raw', addLabel: '+ Добавить участника' },
        steps:        { cols: ['Заголовок шага', 'Описание'],                 field: 'items_raw', addLabel: '+ Добавить шаг' },
        faq:          { cols: ['Вопрос', 'Ответ'],                            field: 'items_raw', addLabel: '+ Добавить вопрос', lastTextarea: true },
        testimonials: { cols: ['Имя', 'Текст отзыва'],                       field: 'items_raw', addLabel: '+ Добавить отзыв',  lastTextarea: true },
        chart_pie:    { cols: ['Подпись', 'Значение'],                        field: 'items_raw', addLabel: '+ Добавить сегмент' },
    };

    // -----------------------------------------------------------------------
    // Утилиты DOM
    // -----------------------------------------------------------------------
    function el(tag, attrs) {
        var node = document.createElement(tag);
        if (!attrs) return node;
        Object.keys(attrs).forEach(function (k) {
            if (k === 'cls')       node.className = attrs[k];
            else if (k === 'html') node.innerHTML = attrs[k];
            else if (k === 'text') node.textContent = attrs[k];
            else                   node.setAttribute(k, attrs[k]);
        });
        return node;
    }

    function getCsrf() {
        var v = '; ' + document.cookie, p = v.split('; csrftoken=');
        if (p.length === 2) return p.pop().split(';').shift();
        return '';
    }

    // -----------------------------------------------------------------------
    // Состояние
    // -----------------------------------------------------------------------
    var mount      = null;   // контейнер куда рендерим редактор
    var dataInput  = null;   // #section-data-input (скрытый)
    var typeSelect = null;   // select[name="type"]
    var sectionId  = null;   // pk секции если редактируем существующую

    // Текущие данные редактора — заполняются при загрузке полей
    var currentFields = [];  // [{name, type, value, ...}]

    // -----------------------------------------------------------------------
    // Главная функция: загрузить поля для типа
    // -----------------------------------------------------------------------
    function loadFields(type) {
        if (!mount) return;

        mount.innerHTML = '<div class="se-loading">Загрузка полей…</div>';

        var url = '/admin/section-fields/?type=' + encodeURIComponent(type);
        if (sectionId) url += '&section_id=' + sectionId;

        fetch(url, {
            headers: { 'X-CSRFToken': getCsrf(), 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                currentFields = data.fields || [];
                renderEditor(type, currentFields);
            })
            .catch(function () {
                mount.innerHTML = '<div class="se-error">Не удалось загрузить поля. Перезагрузите страницу.</div>';
            });
    }

    // -----------------------------------------------------------------------
    // Рендер редактора
    // -----------------------------------------------------------------------
    function renderEditor(type, fields) {
        mount.innerHTML = '';

        if (!fields.length) {
            // contacts и подобные — нет своих полей, данные берутся из SiteSettings
            var note = el('div', { cls: 'se-empty-note' });
            note.textContent = ICONS[type] + '  Эта секция не требует дополнительных данных.';
            mount.appendChild(note);
            setDataInput({});
            return;
        }

        var header = el('div', { cls: 'se-header' });
        var icon   = el('span', { cls: 'se-header__icon', text: ICONS[type] || '📄' });
        header.appendChild(icon);
        mount.appendChild(header);

        // Построитель строк (counters, cards, team, steps, faq, testimonials, chart_pie)
        var builder = ROW_BUILDERS[type];
        if (builder) {
            renderRowBuilder(type, fields, builder);
            return;
        }

        // table — особый случай
        if (type === 'table') {
            renderTableBuilder(fields);
            return;
        }

        // form — построитель полей формы
        if (type === 'form') {
            renderFormBuilder(fields);
            return;
        }

        // hero, text, contacts — обычные поля
        renderSimpleFields(fields);
    }

    // -----------------------------------------------------------------------
    // Обычные поля (hero, text, contacts)
    // -----------------------------------------------------------------------
    function renderSimpleFields(fields) {
        var wrapper = el('div', { cls: 'se-simple' });

        fields.forEach(function (f) {
            if (f.type === 'hidden') return;

            var group = el('div', { cls: 'se-field-group' });
            var label = el('label', { cls: 'se-label' });
            label.textContent = f.label + (f.required ? ' *' : '');
            group.appendChild(label);

            var input;
            if (f.type === 'textarea') {
                input = el('textarea', { cls: 'se-input se-textarea', name: f.name });
                input.value = f.value || '';
            } else {
                input = el('input', { cls: 'se-input', type: f.type || 'text', name: f.name });
                input.value = f.value || '';
            }
            if (f.required) input.required = true;
            group.appendChild(input);

            if (f.help_text) {
                var hint = el('div', { cls: 'se-hint', text: f.help_text });
                group.appendChild(hint);
            }

            // Специальный пикер для image_id
            if (f.name === 'image_id') {
                renderImagePicker(group, input);
            }

            wrapper.appendChild(group);
        });

        mount.appendChild(wrapper);
        bindSimpleSubmit(fields);
    }

    function bindSimpleSubmit(fields) {
        onSubmit(function () {
            var result = {};
            fields.forEach(function (f) {
                if (f.type === 'hidden') return;
                var inp = mount.querySelector('[name="' + f.name + '"]');
                if (inp) result[f.name] = inp.value;
            });
            setDataInput(result);
        });
    }

    // -----------------------------------------------------------------------
    // Пикер медиафайла для hero.image_id
    // -----------------------------------------------------------------------
    function renderImagePicker(group, hiddenInput) {
        var preview = el('div', { cls: 'se-image-preview' });
        var btn     = el('button', { type: 'button', cls: 'se-btn se-btn--pick', text: 'Выбрать из медиабиблиотеки' });

        // Если уже есть значение — показываем id
        if (hiddenInput.value) {
            preview.textContent = 'Текущий файл ID: ' + hiddenInput.value;
        }

        btn.addEventListener('click', function () {
            // Открываем медиабиблиотеку в popup (стандартный Django related-popup)
            var url = '/admin/media_library/mediafile/?_popup=1&_to_field=id';
            var popup = window.open(url, 'media_popup', 'width=900,height=600,resizable=yes');
            // Django вызывает window.opener.dismissRelatedLookupPopup при выборе
            window._mediaPickerCallback = function (id, repr) {
                hiddenInput.value = id;
                preview.textContent = 'Выбран файл ID: ' + id + ' (' + repr + ')';
                popup && popup.close();
            };
        });

        group.appendChild(preview);
        group.appendChild(btn);
    }

    // -----------------------------------------------------------------------
    // Построитель строк (counters, cards, team, steps, faq, testimonials, chart_pie)
    // -----------------------------------------------------------------------
    function renderRowBuilder(type, fields, builder) {
        // Достаём сырое значение items_raw из fields
        var rawField = fields.find(function (f) { return f.name === builder.field; });
        var rawValue = rawField ? (rawField.value || '') : '';

        var list = el('div', { cls: 'se-list' });

        // Парсим текущие строки
        var lines = rawValue ? rawValue.split('\n').filter(Boolean) : [];
        if (!lines.length) lines = [''];  // хотя бы одна пустая строка

        lines.forEach(function (line) {
            var parts = line.split('|');
            addRow(list, builder, parts);
        });

        var addBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add', text: builder.addLabel });
        addBtn.addEventListener('click', function () {
            addRow(list, builder, []);
        });

        mount.appendChild(list);
        mount.appendChild(addBtn);

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var inputs = row.querySelectorAll('.se-row-input');
                var vals = Array.from(inputs).map(function (i) {
                    return (i.tagName === 'TEXTAREA' ? i.value : i.value).trim();
                });
                if (vals[0]) lines.push(vals.join('|'));
            });
            var result = {};
            result[builder.field] = lines.join('\n');
            setDataInput(result);
        });
    }

    function addRow(list, builder, values) {
        var row = el('div', { cls: 'se-row' });

        builder.cols.forEach(function (placeholder, i) {
            var isLast    = i === builder.cols.length - 1;
            var useArea   = isLast && builder.lastTextarea;
            var inp;
            if (useArea) {
                inp = el('textarea', { cls: 'se-row-input se-input se-textarea-sm', placeholder: placeholder });
                inp.value = (values[i] || '').trim();
            } else {
                inp = el('input', { type: 'text', cls: 'se-row-input se-input', placeholder: placeholder });
                inp.value = (values[i] || '').trim();
            }
            row.appendChild(inp);
        });

        var removeBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
        removeBtn.addEventListener('click', function () {
            list.removeChild(row);
        });
        row.appendChild(removeBtn);
        list.appendChild(row);
    }

    // -----------------------------------------------------------------------
    // Построитель таблицы
    // -----------------------------------------------------------------------
    function renderTableBuilder(fields) {
        var headersField = fields.find(function (f) { return f.name === 'headers_raw'; });
        var rowsField    = fields.find(function (f) { return f.name === 'rows_raw'; });

        var initHeaders = headersField && headersField.value
            ? headersField.value.split('|').map(function (h) { return h.trim(); })
            : [''];
        var initRows = rowsField && rowsField.value
            ? rowsField.value.trim().split('\n').map(function (line) {
                return line.split('|').map(function (c) { return c.trim(); });
            })
            : [[]];

        var colCount = initHeaders.length || 1;

        var tableWrap = el('div', { cls: 'se-table-wrap' });
        var table     = el('table', { cls: 'se-table' });
        var thead     = el('thead');
        var tbody     = el('tbody');
        table.appendChild(thead);
        table.appendChild(tbody);
        tableWrap.appendChild(table);
        mount.appendChild(tableWrap);

        function renderHead() {
            thead.innerHTML = '';
            var tr = el('tr');
            var ctrlTh = el('th', { cls: 'se-table__ctrl' });
            tr.appendChild(ctrlTh);
            for (var i = 0; i < colCount; i++) {
                (function (ci) {
                    var th  = el('th');
                    var inp = el('input', { type: 'text', cls: 'se-input', placeholder: 'Заголовок' });
                    inp.value = initHeaders[ci] || '';
                    inp.dataset.col = ci;
                    inp.dataset.isHeader = '1';
                    var rmBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove-col', html: '&times;' });
                    rmBtn.addEventListener('click', function () { removeCol(ci); });
                    th.appendChild(inp);
                    th.appendChild(rmBtn);
                    tr.appendChild(th);
                })(i);
            }
            var addColTh = el('th');
            var addColBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add-col', text: '+ столбец' });
            addColBtn.addEventListener('click', addCol);
            addColTh.appendChild(addColBtn);
            tr.appendChild(addColTh);
            thead.appendChild(tr);
        }

        function renderBody() {
            tbody.innerHTML = '';
            initRows.forEach(function (rowData) { appendRow(rowData); });
        }

        function appendRow(rowData) {
            var tr = el('tr');
            var ctrlTd = el('td', { cls: 'se-table__ctrl' });
            var rmBtn  = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
            rmBtn.addEventListener('click', function () { tbody.removeChild(tr); });
            ctrlTd.appendChild(rmBtn);
            tr.appendChild(ctrlTd);
            for (var i = 0; i < colCount; i++) {
                var td  = el('td');
                var inp = el('input', { type: 'text', cls: 'se-input' });
                inp.value = (rowData && rowData[i]) || '';
                td.appendChild(inp);
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }

        function getHeaders() {
            return Array.from(thead.querySelectorAll('input[data-is-header]')).map(function (i) { return i.value.trim(); });
        }
        function getRows() {
            return Array.from(tbody.querySelectorAll('tr')).map(function (tr) {
                return Array.from(tr.querySelectorAll('td:not(.se-table__ctrl) input')).map(function (i) { return i.value.trim(); });
            });
        }
        function addCol() {
            colCount++;
            initHeaders = getHeaders(); initHeaders.push('');
            initRows = getRows();
            renderHead(); renderBody();
        }
        function removeCol(ci) {
            if (colCount <= 1) return;
            var h = getHeaders(); h.splice(ci, 1);
            var r = getRows().map(function (row) { var c = row.slice(); c.splice(ci, 1); return c; });
            colCount--; initHeaders = h; initRows = r;
            renderHead(); renderBody();
        }

        renderHead();
        renderBody();

        var addRowBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add', text: '+ Добавить строку' });
        addRowBtn.addEventListener('click', function () { appendRow([]); });
        mount.appendChild(addRowBtn);

        onSubmit(function () {
            setDataInput({ headers_raw: getHeaders().join('|'), rows_raw: getRows().map(function (r) { return r.join('|'); }).join('\n') });
        });
    }

    // -----------------------------------------------------------------------
    // Построитель полей формы (тип section = 'form')
    // -----------------------------------------------------------------------
    var FIELD_TYPES = [
        { value: 'text',     label: 'Текст' },
        { value: 'email',    label: 'Email' },
        { value: 'tel',      label: 'Телефон' },
        { value: 'textarea', label: 'Большой текст' },
    ];

    function renderFormBuilder(fields) {
        var rawField = fields.find(function (f) { return f.name === 'fields_raw'; });
        var rawValue = rawField ? (rawField.value || '') : '';

        var list = el('div', { cls: 'se-list' });

        var lines = rawValue ? rawValue.split('\n').filter(Boolean) : [];
        if (!lines.length) lines = [''];

        lines.forEach(function (line) {
            var parts = line.split('|');
            addFormFieldRow(list, parts[0], parts[1], parts[2], parts[3] === 'true');
        });

        var addBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add', text: '+ Добавить поле' });
        addBtn.addEventListener('click', function () {
            addFormFieldRow(list, '', 'text', '', false);
        });

        mount.appendChild(list);
        mount.appendChild(addBtn);

        onSubmit(function () {
            var lines = [];
            list.querySelectorAll('.se-row').forEach(function (row) {
                var nameInp  = row.querySelector('.se-form-name');
                var typeInp  = row.querySelector('.se-form-type');
                var labelInp = row.querySelector('.se-form-label');
                var reqInp   = row.querySelector('.se-form-req');
                var name = nameInp ? nameInp.value.trim() : '';
                if (name) {
                    lines.push([
                        name,
                        typeInp  ? typeInp.value  : 'text',
                        labelInp ? labelInp.value.trim() : '',
                        reqInp   && reqInp.checked ? 'true' : 'false',
                    ].join('|'));
                }
            });
            setDataInput({ fields_raw: lines.join('\n') });
        });
    }

    function addFormFieldRow(list, name, type, label, required) {
        var row = el('div', { cls: 'se-row se-row--form' });

        var nameInp = el('input', { type: 'text', cls: 'se-input se-form-name', placeholder: 'Имя (латиница)' });
        nameInp.value = (name || '').trim();

        var typeSelect = el('select', { cls: 'se-input se-select se-form-type' });
        FIELD_TYPES.forEach(function (opt) {
            var o = el('option', { value: opt.value });
            o.textContent = opt.label;
            if (opt.value === (type || 'text')) o.selected = true;
            typeSelect.appendChild(o);
        });

        var labelInp = el('input', { type: 'text', cls: 'se-input se-form-label', placeholder: 'Подпись' });
        labelInp.value = (label || '').trim();

        var reqLabel = el('label', { cls: 'se-checkbox' });
        var reqCb    = el('input', { type: 'checkbox', cls: 'se-form-req' });
        reqCb.checked = !!required;
        reqLabel.appendChild(reqCb);
        reqLabel.appendChild(document.createTextNode(' Обяз.'));

        var rmBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
        rmBtn.addEventListener('click', function () { list.removeChild(row); });

        [nameInp, typeSelect, labelInp, reqLabel, rmBtn].forEach(function (n) { row.appendChild(n); });
        list.appendChild(row);
    }

    // -----------------------------------------------------------------------
    // Сброс данных в скрытый input перед сабмитом
    // -----------------------------------------------------------------------
    function setDataInput(obj) {
        if (dataInput) dataInput.value = JSON.stringify(obj);
    }

    // -----------------------------------------------------------------------
    // Очередь колбэков сабмита
    // -----------------------------------------------------------------------
    var submitHandlers = [];

    function onSubmit(fn) {
        submitHandlers.push(fn);
    }

    function clearSubmitHandlers() {
        submitHandlers = [];
    }

    // -----------------------------------------------------------------------
    // Init
    // -----------------------------------------------------------------------
    document.addEventListener('DOMContentLoaded', function () {
        typeSelect = document.querySelector('select[name="type"]');

        if (!typeSelect) return;  // не на форме секции

        // Ищем скрытое поле section_data — Unfold может рендерить его по-разному
        dataInput = document.getElementById('section-data-input')
                 || document.querySelector('input[name="section_data"]');

        // Если поле не нашли в DOM — создаём сами и добавляем в форму
        if (!dataInput) {
            var form = document.querySelector('#content-main form');
            if (!form) return;
            dataInput = document.createElement('input');
            dataInput.type = 'hidden';
            dataInput.name = 'section_data';
            dataInput.id   = 'section-data-input';
            form.appendChild(dataInput);
        }

        // Определяем pk секции (если редактируем, а не создаём)
        var match = window.location.pathname.match(/\/pages\/section\/(\d+)\/change\//);
        sectionId = match ? match[1] : null;

        // Создаём контейнер редактора.
        // НЕ вставляем его рядом с section_data — Unfold прячет это поле
        // в .field-line с нулевыми размерами. Вставляем перед #submit-row,
        // который находится в корне #content-main и всегда виден.
        mount = el('div', { cls: 'se-mount' });
        var submitRow = document.getElementById('submit-row');
        if (submitRow && submitRow.parentNode) {
            submitRow.parentNode.insertBefore(mount, submitRow);
        } else {
            // Запасной вариант — после последнего fieldset
            var fieldsets = document.querySelectorAll('#content-main fieldset');
            var lastFieldset = fieldsets[fieldsets.length - 1];
            if (lastFieldset && lastFieldset.parentNode) {
                lastFieldset.parentNode.insertBefore(mount, lastFieldset.nextSibling);
            } else {
                document.getElementById('content-main').appendChild(mount);
            }
        }

        // Привязываем сабмит формы
        var form = document.querySelector('#content-main form');
        if (form) {
            form.addEventListener('submit', function () {
                submitHandlers.forEach(function (fn) { fn(); });
            });
        }

        // Начальная загрузка
        loadFields(typeSelect.value);

        // Реагируем на смену типа
        typeSelect.addEventListener('change', function () {
            clearSubmitHandlers();
            loadFields(this.value);
        });
    });

})();