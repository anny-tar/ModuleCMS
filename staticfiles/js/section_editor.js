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

    // Подключаем Quill CSS если ещё не загружен
    if (!document.querySelector('link[href*="quill"]')) {
        var ql = document.createElement('link');
        ql.rel  = 'stylesheet';
        ql.href = 'https://cdn.jsdelivr.net/npm/quill@2/dist/quill.snow.css';
        document.head.appendChild(ql);
    }

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
            .catch(function (err) {
                console.error('SE ERROR:', err);
                mount.innerHTML = '<div class="se-error">Ошибка: ' + (err && err.message ? err.message : err) + '</div>';
            });
    }

    // -----------------------------------------------------------------------
    // Рендер редактора
    // -----------------------------------------------------------------------
    function renderEditor(type, fields) {
        mount.innerHTML = '';
        quillInstances = {};

        if (!fields.length) {
            var note = el('div', { cls: 'se-empty-note' });
            note.textContent = (ICONS[type] || '📄') + '  Эта секция не требует дополнительных данных.';
            mount.appendChild(note);
            setDataInput({});
            return;
        }

        var header = el('div', { cls: 'se-header' });
        var icon   = el('span', { cls: 'se-header__icon', text: ICONS[type] || '📄' });
        header.appendChild(icon);
        mount.appendChild(header);

        // Роутинг по типу полей — не по типу секции
        var hasRows = fields.some(function(f) { return f.type === 'rows'; });
        if (hasRows) {
            renderRowsBuilder(fields);
            bindLivePreview(type);
            return;
        }

        // Таблица
        var hasTable = fields.some(function(f) { return f.type === 'table'; });
        if (hasTable) {
            renderTableBuilder(fields);
            bindLivePreview(type);
            return;
        }

        // Форма обратной связи
        var hasFormFields = fields.some(function(f) { return f.type === 'form_fields'; });
        if (hasFormFields) {
            renderFormFieldsBuilder(fields);
            bindLivePreview(type);
            return;
        }

        // Контакты
        var hasContactsRows = fields.some(function(f) { return f.type === 'contacts_rows'; });
        if (hasContactsRows) {
            renderContactsBuilder(fields);
            bindLivePreview(type);
            return;
        }

        // Все остальные — простые поля
        renderSimpleFields(fields);

        // Живое превью для всех типов
        bindLivePreview(type);
    }

    // -----------------------------------------------------------------------
    // Медиапикер — выпадающий список с поиском
    // -----------------------------------------------------------------------
    function createMediaPicker(fieldName, initValue) {
        var wrap = el('div', { cls: 'se-media-picker-wrap' });

        // Скрытый input хранит выбранный ID
        var hidden = el('input', { type: 'hidden', name: fieldName });
        hidden.value = initValue || '';

        // Превью выбранного файла
        var thumb = el('div', { cls: 'se-media-thumb' });
        thumb.innerHTML = '<span style="opacity:.4;font-size:18px;">🖼️</span>';

        // Поле поиска — оно же триггер открытия
        var search = el('input', { type: 'text', cls: 'se-input se-media-search', placeholder: 'Поиск файла...' });

        // Дропдаун со списком
        var dropdown = el('div', { cls: 'se-media-dropdown' });

        // Кнопка сброса
        var clearBtn = el('button', { type: 'button', cls: 'se-media-clear', html: '&times;', title: 'Сбросить' });
        clearBtn.style.display = initValue ? 'flex' : 'none';

        var allItems  = [];
        var loaded    = false;
        var searchTimer = null;

        function loadItems(q) {
            var url = '/admin/media-list/?type=image' + (q ? '&q=' + encodeURIComponent(q) : '');
            fetch(url).then(function(r) { return r.json(); }).then(function(data) {
                allItems = data.items || [];
                renderDropdown(allItems);
            });
        }

        function renderDropdown(items) {
            dropdown.innerHTML = '';
            if (!items.length) {
                var empty = el('div', { cls: 'se-media-empty', text: 'Файлов не найдено' });
                dropdown.appendChild(empty);
                return;
            }
            items.forEach(function(item) {
                var row = el('div', { cls: 'se-media-item' + (item.id == hidden.value ? ' selected' : '') });
                var img = el('div', { cls: 'se-media-item-thumb' });
                img.innerHTML = '<img src="' + item.url + '" alt="">';
                var name = el('div', { cls: 'se-media-item-name', text: item.name });
                row.appendChild(img);
                row.appendChild(name);
                row.addEventListener('click', function(e) {
                    e.stopPropagation();
                    hidden.value = item.id;
                    thumb.innerHTML = '<img src="' + item.url + '" style="width:100%;height:100%;object-fit:cover;">';
                    search.value = item.name;
                    clearBtn.style.display = 'flex';
                    dropdown.classList.remove('open');
                    // Обновляем selected
                    dropdown.querySelectorAll('.se-media-item').forEach(function(r) {
                        r.classList.toggle('selected', r === row);
                    });
                });
                dropdown.appendChild(row);
            });
        }

        // Если есть начальное значение — подгружаем превью
        if (initValue) {
            fetch('/admin/media-url/?id=' + initValue)
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    if (d.url) {
                        thumb.innerHTML = '<img src="' + d.url + '" style="width:100%;height:100%;object-fit:cover;">';
                        search.value = d.name || '';
                    }
                });
        }

        search.addEventListener('focus', function() {
            dropdown.classList.add('open');
            if (!loaded) { loaded = true; loadItems(''); }
        });

        search.addEventListener('input', function() {
            clearTimeout(searchTimer);
            var q = search.value.trim();
            searchTimer = setTimeout(function() { loadItems(q); }, 300);
            dropdown.classList.add('open');
        });

        clearBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            hidden.value = '';
            thumb.innerHTML = '<span style="opacity:.4;font-size:18px;">🖼️</span>';
            search.value = '';
            clearBtn.style.display = 'none';
        });

        document.addEventListener('click', function(e) {
            if (!wrap.contains(e.target)) dropdown.classList.remove('open');
        });

        wrap.appendChild(thumb);
        var inputRow = el('div', { cls: 'se-media-input-row' });
        inputRow.appendChild(search);
        inputRow.appendChild(clearBtn);
        wrap.appendChild(inputRow);
        wrap.appendChild(dropdown);
        wrap.appendChild(hidden);
        return wrap;
    }

    // -----------------------------------------------------------------------
    // Эмодзи-пикер
    // -----------------------------------------------------------------------
    var EMOJI_CATS = {
        'Бизнес':     ['🚀','⭐','💡','🎯','🏆','💎','🔑','📈','💼','🤝','✅','🌟','💪','🎨','📊','🔥','⚡','🌈','✨','💫'],
        'Люди':       ['👤','👥','👨‍💼','👩‍💼','🧑‍💻','👨‍🔬','👩‍🏫','🧑‍🎨','👨‍⚕️','👩‍🍳','👷','🤵','🙋','💁','🫂'],
        'Технологии': ['💻','🖥️','📱','⌨️','🖱️','💾','📷','🎥','📡','🔭','🔬','⚙️','🔧','🔩','🛠️','⚗️','🧪','🔋','💡','🤖'],
        'Природа':    ['🌿','🌱','🌳','🌲','🍀','🌸','🌺','🌻','🌹','🌷','🍁','🌊','🏔️','🌋','🏝️','🌅','🌙','☀️','⛅','🌈'],
        'Символы':    ['❤️','🧡','💛','💚','💙','💜','✅','❌','⭕','🔴','🟢','🔵','⚫','⚪','🔶','🔷','💠','🔘','🔲','🔳'],
    };

    function createEmojiPicker(onSelect) {
        var wrap = el('div', { cls: 'se-emoji-wrap' });

        // preview — кнопка со стрелкой, отдельная кнопка "Выбрать" убрана
        var preview = el('button', { type: 'button', cls: 'se-emoji-preview', title: 'Выбрать эмодзи' });
        preview.textContent = '😀';

        var picker = el('div', { cls: 'se-emoji-picker' });

        // Категории
        var cats = el('div', { cls: 'se-emoji-cats' });
        Object.keys(EMOJI_CATS).forEach(function(cat, i) {
            var btn = el('button', { type: 'button', cls: 'se-emoji-cat-btn' + (i===0?' active':'') });
            btn.textContent = cat;
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                cats.querySelectorAll('.se-emoji-cat-btn').forEach(function(b){ b.classList.remove('active'); });
                btn.classList.add('active');
                renderGrid(EMOJI_CATS[cat]);
            });
            cats.appendChild(btn);
        });
        picker.appendChild(cats);

        var grid = el('div', { cls: 'se-emoji-grid' });
        picker.appendChild(grid);

        function renderGrid(emojis) {
            grid.innerHTML = '';
            emojis.forEach(function(em) {
                var cell = el('div', { cls: 'se-emoji-cell' });
                cell.textContent = em;
                cell.addEventListener('click', function(e) {
                    e.stopPropagation();
                    preview.textContent = em;
                    picker.classList.remove('open');
                    if (onSelect) onSelect(em);
                });
                grid.appendChild(cell);
            });
        }
        renderGrid(EMOJI_CATS['Бизнес']);

        preview.addEventListener('click', function(e) {
            e.stopPropagation();
            picker.classList.toggle('open');
        });
        picker.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        document.addEventListener('click', function() {
            picker.classList.remove('open');
        });

        wrap.appendChild(preview);
        wrap.appendChild(picker);
        return { wrap: wrap, preview: preview };
    }

    // -----------------------------------------------------------------------
    // Построитель строк (rows) — универсальный для counters, cards, team и т.д.
    // -----------------------------------------------------------------------
    function renderRowsBuilder(fields) {
        // Ищем все поля типа rows + обычные поля (настройки секции)
        var simpleFields = fields.filter(function(f) { return f.type !== 'rows'; });
        var rowsFields   = fields.filter(function(f) { return f.type === 'rows'; });

        // Сначала рендерим обычные поля (настройки) если есть
        if (simpleFields.length) {
            renderSimpleFields(simpleFields);
        }

        rowsFields.forEach(function(field) {
            var rowSchema = field.row_schema || [];
            var initItems = Array.isArray(field.value) ? field.value : [];

            var container = el('div', { cls: 'se-rows-builder' });
            var header    = el('div', { cls: 'se-rows-header' });
            header.textContent = field.label;
            container.appendChild(header);

            var list = el('div', { cls: 'se-rows-list', 'data-field': field.name });

            // Рендерим начальные строки
            if (initItems.length) {
                initItems.forEach(function(item) {
                    appendRowItem(list, rowSchema, item);
                });
            } else {
                appendRowItem(list, rowSchema, {});
            }

            container.appendChild(list);

            var addBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add' });
            addBtn.textContent = '+ Добавить';
            addBtn.addEventListener('click', function() {
                appendRowItem(list, rowSchema, {});
            });
            container.appendChild(addBtn);
            mount.appendChild(container);
        });

        // Сабмит — собираем все rows-поля
        onSubmit(function() {
            var result = {};

            // Обычные поля
            simpleFields.forEach(function(f) {
                if (f.type === 'hidden') return;
                if (f.type === 'quill') {
                    var q = quillInstances[f.name];
                    result[f.name] = q ? q.root.innerHTML : '';
                } else {
                    var inp = mount.querySelector('[name="' + f.name + '"]');
                    if (inp) result[f.name] = inp.value;
                }
            });

            // rows-поля
            rowsFields.forEach(function(field) {
                var listEl = mount.querySelector('.se-rows-list[data-field="' + field.name + '"]');
                if (!listEl) return;
                var items = [];
                listEl.querySelectorAll('.se-row-item').forEach(function(row) {
                    var item = {};
                    field.row_schema.forEach(function(col) {
                        if (col.type === 'emoji') {
                            var preview = row.querySelector('.se-emoji-preview[data-col="' + col.name + '"]');
                            item[col.name] = preview ? preview.textContent : '';
                        } else if (col.type === 'quill') {
                            var q = row._quills && row._quills[col.name];
                            item[col.name] = q ? q.root.innerHTML : '';
                        } else {
                            // media, rating, color, text — все хранят значение в input[name]
                            var inp = row.querySelector('[name="' + col.name + '"]');
                            item[col.name] = inp ? inp.value : '';
                        }
                    });
                    items.push(item);
                });
                result[field.name] = items;
            });

            setDataInput(result);
        });
    }

    function appendRowItem(list, rowSchema, initValues) {
        var row = el('div', { cls: 'se-row-item' });
        row._quills = {};

        // Drag handle
        var handle = el('div', { cls: 'se-row-handle', html: '⠿' });
        row.appendChild(handle);

        rowSchema.forEach(function(col) {
            var cell = el('div', { cls: 'se-row-cell se-row-cell--' + (col.width || 'md'), 'data-col': col.name });

            var lbl = el('div', { cls: 'se-row-cell-label' });
            lbl.textContent = col.label;
            cell.appendChild(lbl);

            if (col.type === 'emoji') {
                var picker = createEmojiPicker(null);
                if (initValues[col.name]) picker.preview.textContent = initValues[col.name];
                picker.preview.dataset.col = col.name;
                // Обновляем при выборе
                var origOnSelect = picker.preview;
                cell.appendChild(picker.wrap);
            } else if (col.type === 'quill') {
                var editorDiv = el('div', { cls: 'se-quill-editor se-quill-sm' });
                cell.appendChild(editorDiv);
                // Quill инициализируем после вставки в DOM
                setTimeout(function() {
                    loadQuill(function() {
                        var q = new Quill(editorDiv, {
                            theme: 'snow',
                            modules: { toolbar: [['bold','italic','underline'],['link']] }
                        });
                        if (initValues[col.name]) q.root.innerHTML = initValues[col.name];
                        row._quills[col.name] = q;
                    });
                }, 0);
            } else if (col.type === 'media') {
                cell.appendChild(createMediaPicker(col.name, initValues[col.name] || ''));
            } else if (col.type === 'rating') {
                var ratingInp = el('input', { type: 'hidden', name: col.name });
                ratingInp.value = initValues[col.name] || '0';
                var ratingWrap = el('div', { cls: 'se-rating' });
                for (var s = 1; s <= 5; s++) {
                    (function(star) {
                        var btn = el('button', { type: 'button', cls: 'se-star' });
                        btn.textContent = '★';
                        btn.dataset.val = star;
                        if (star <= parseInt(ratingInp.value)) btn.classList.add('active');
                        btn.addEventListener('click', function() {
                            ratingInp.value = star;
                            ratingWrap.querySelectorAll('.se-star').forEach(function(b) {
                                b.classList.toggle('active', parseInt(b.dataset.val) <= star);
                            });
                        });
                        ratingWrap.appendChild(btn);
                    })(s);
                }
                ratingWrap.appendChild(ratingInp);
                cell.appendChild(ratingWrap);
            } else if (col.type === 'color') {
                var colorInp = el('input', { type: 'color', cls: 'se-input se-input-color', name: col.name });
                colorInp.value = initValues[col.name] || '#3B8BD4';
                cell.appendChild(colorInp);
            } else if (col.type === 'textarea') {
                var taInp = el('textarea', { cls: 'se-input se-textarea-sm', name: col.name });
                taInp.value = initValues[col.name] || '';
                cell.appendChild(taInp);
            } else {
                var textInp = el('input', { type: col.type || 'text', cls: 'se-input', name: col.name });
                textInp.value = initValues[col.name] || '';
                cell.appendChild(textInp);
            }

            row.appendChild(cell);
        });

        // Кнопка удаления
        var rmBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
        rmBtn.addEventListener('click', function() { list.removeChild(row); });
        row.appendChild(rmBtn);

        list.appendChild(row);

        // Инициализируем зависимости ячеек строки
        bindRowCellDependencies(row, rowSchema, []);

        // Инициализируем DnD для списка
        initRowsDnd(list);
    }

    // -----------------------------------------------------------------------
    // DnD сортировка строк
    // -----------------------------------------------------------------------
    function initRowsDnd(list) {
        // Простой DnD через HTML5 drag events
        list.addEventListener('dragstart', function(e) {
            var item = e.target.closest('.se-row-item');
            if (!item) return;
            item.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        list.addEventListener('dragend', function(e) {
            var item = e.target.closest('.se-row-item');
            if (item) item.classList.remove('dragging');
        });
        list.addEventListener('dragover', function(e) {
            e.preventDefault();
            var target = e.target.closest('.se-row-item');
            var dragging = list.querySelector('.dragging');
            if (!target || target === dragging) return;
            var rect = target.getBoundingClientRect();
            if (e.clientY < rect.top + rect.height / 2) {
                list.insertBefore(dragging, target);
            } else {
                list.insertBefore(dragging, target.nextSibling);
            }
        });
        // Делаем строки draggable
        list.querySelectorAll('.se-row-item').forEach(function(item) {
            item.setAttribute('draggable', 'true');
        });
    }

    // -----------------------------------------------------------------------
    // -----------------------------------------------------------------------
    // Построитель контактов
    // -----------------------------------------------------------------------
    var CONTACT_TYPES = {
        phone:   { label: 'Телефон',       icon: '📞' },
        email:   { label: 'Email',          icon: '✉️' },
        address: { label: 'Адрес',          icon: '📍' },
        site:    { label: 'Сайт',           icon: '🌐' },
        social:  { label: 'Соцсеть',        icon: '💬' },
        hours:   { label: 'Режим работы',   icon: '🕐' },
    };

    function renderContactsBuilder(fields) {
        var simpleFields    = fields.filter(function(f) { return f.type !== 'contacts_rows'; });
        var contactsField   = fields.find(function(f) { return f.type === 'contacts_rows'; });
        var initItems       = Array.isArray(contactsField && contactsField.value) ? contactsField.value : [];

        // Простые поля (layout, map_url, map_label, map_description) с зависимостями
        renderSimpleFields(simpleFields);

        var container = el('div', { cls: 'se-rows-builder' });
        var header = el('div', { cls: 'se-rows-header' });
        header.textContent = 'Контактные данные';
        container.appendChild(header);

        var list = el('div', { cls: 'se-rows-list', 'data-field': 'items' });

        if (initItems.length) {
            initItems.forEach(function(item) { appendContactRow(list, item); });
        } else {
            appendContactRow(list, { type: 'phone', label: '', value: '', description: '' });
        }

        container.appendChild(list);

        var addBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add', text: '+ Добавить строку' });
        addBtn.addEventListener('click', function() {
            appendContactRow(list, { type: 'phone', label: '', value: '', description: '' });
        });
        container.appendChild(addBtn);
        mount.appendChild(container);

        onSubmit(function() {
            var result = {};
            simpleFields.forEach(function(f) {
                var inp = mount.querySelector('[name="' + f.name + '"]');
                if (inp) result[f.name] = inp.value;
            });
            var items = [];
            list.querySelectorAll('.se-contact-row').forEach(function(row) {
                var type = row.querySelector('.cr-type').value;
                var label = row.querySelector('.cr-label').value.trim();
                var value = row.querySelector('.cr-value').value.trim();
                var desc  = row.querySelector('.cr-desc').value.trim();
                if (value) items.push({ type: type, label: label, value: value, description: desc });
            });
            result['items'] = JSON.stringify(items);
            setDataInput(result);
        });
    }

    function appendContactRow(list, init) {
        var row = el('div', { cls: 'se-row-item se-contact-row' });

        // Иконка — обновляется при смене типа
        var iconEl = el('div', { cls: 'se-contact-icon' });
        iconEl.textContent = (CONTACT_TYPES[init.type] || CONTACT_TYPES.phone).icon;

        var typeSelect = el('select', { cls: 'se-input se-select cr-type' });
        Object.keys(CONTACT_TYPES).forEach(function(k) {
            var o = el('option', { value: k });
            o.textContent = CONTACT_TYPES[k].label;
            if (k === (init.type || 'phone')) o.selected = true;
            typeSelect.appendChild(o);
        });
        typeSelect.addEventListener('change', function() {
            iconEl.textContent = (CONTACT_TYPES[this.value] || CONTACT_TYPES.phone).icon;
        });

        var labelInp = el('input', { type: 'text', cls: 'se-input cr-label', placeholder: 'Название (необяз.)' });
        labelInp.value = init.label || '';

        var valueInp = el('input', { type: 'text', cls: 'se-input cr-value', placeholder: 'Значение' });
        valueInp.value = init.value || '';

        var descInp = el('input', { type: 'text', cls: 'se-input cr-desc', placeholder: 'Описание (необяз.)' });
        descInp.value = init.description || '';

        var rmBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
        rmBtn.addEventListener('click', function() { list.removeChild(row); });

        [iconEl, typeSelect, labelInp, valueInp, descInp, rmBtn].forEach(function(n) { row.appendChild(n); });
        list.appendChild(row);

        // DnD
        row.setAttribute('draggable', 'true');
        initRowsDnd(list);
    }

    // -----------------------------------------------------------------------
    // Построитель полей формы обратной связи
    // -----------------------------------------------------------------------
    var FORM_FIELD_TYPES = [
        { value: 'text',     label: 'Текст' },
        { value: 'email',    label: 'Email' },
        { value: 'tel',      label: 'Телефон' },
        { value: 'textarea', label: 'Большой текст' },
    ];

    function renderFormFieldsBuilder(fields) {
        var simpleFields = fields.filter(function(f) { return f.type !== 'form_fields'; });
        var formField    = fields.find(function(f) { return f.type === 'form_fields'; });
        var initFields   = Array.isArray(formField && formField.value) ? formField.value : [];

        // Простые поля (описание, кнопка, сообщение)
        renderSimpleFields(simpleFields);

        var container = el('div', { cls: 'se-rows-builder' });
        var header = el('div', { cls: 'se-rows-header' });
        header.textContent = 'Поля формы';
        container.appendChild(header);

        var list = el('div', { cls: 'se-rows-list', 'data-field': 'fields' });

        if (initFields.length) {
            initFields.forEach(function(f) { appendFormField(list, f); });
        } else {
            appendFormField(list, { name: 'name', type: 'text', label: 'Ваше имя', required: true });
        }

        container.appendChild(list);

        var addBtn = el('button', { type: 'button', cls: 'se-btn se-btn--add', text: '+ Добавить поле' });
        addBtn.addEventListener('click', function() {
            appendFormField(list, { name: '', type: 'text', label: '', required: false });
        });
        container.appendChild(addBtn);
        mount.appendChild(container);

        onSubmit(function() {
            var result = {};
            // Простые поля
            simpleFields.forEach(function(f) {
                var inp = mount.querySelector('[name="' + f.name + '"]');
                if (inp) result[f.name] = inp.value;
            });
            // Поля формы
            var formFields = [];
            list.querySelectorAll('.se-form-field-row').forEach(function(row, idx) {
                var type  = row.querySelector('.ff-type').value;
                var label = row.querySelector('.ff-label').value.trim();
                var req   = row.querySelector('.ff-req').checked;
                if (label) {
                    // Генерируем name автоматически: field_1, field_2...
                    var name = 'field_' + (idx + 1);
                    formFields.push({ name: name, type: type, label: label, required: req });
                }
            });
            result['fields'] = JSON.stringify(formFields);
            setDataInput(result);
        });
    }

    function appendFormField(list, init) {
        var row = el('div', { cls: 'se-row-item se-form-field-row' });

        // name генерируется автоматически по индексу — пользователь не видит
        var nameInp = el('input', { type: 'hidden', cls: 'ff-name' });
        nameInp.value = init.name || '';

        var typeSelect = el('select', { cls: 'se-input se-select ff-type' });
        FORM_FIELD_TYPES.forEach(function(opt) {
            var o = el('option', { value: opt.value });
            o.textContent = opt.label;
            if (opt.value === (init.type || 'text')) o.selected = true;
            typeSelect.appendChild(o);
        });

        var labelInp = el('input', { type: 'text', cls: 'se-input ff-label', placeholder: 'Подпись поля' });
        labelInp.value = init.label || '';

        var reqLabel = el('label', { cls: 'se-checkbox' });
        var reqCb = el('input', { type: 'checkbox', cls: 'ff-req' });
        reqCb.checked = !!init.required;
        reqLabel.appendChild(reqCb);
        reqLabel.appendChild(document.createTextNode(' Обяз.'));

        var rmBtn = el('button', { type: 'button', cls: 'se-btn se-btn--remove', html: '&times;' });
        rmBtn.addEventListener('click', function() { list.removeChild(row); });

        row.appendChild(nameInp);
        [typeSelect, labelInp, reqLabel, rmBtn].forEach(function(n) { row.appendChild(n); });
        list.appendChild(row);
    }

    // -----------------------------------------------------------------------
    // Quill-экземпляры (храним чтобы читать getValue перед сабмитом)
    // -----------------------------------------------------------------------
    var quillInstances = {};

    function loadQuill(callback) {
        if (window.Quill) { callback(); return; }
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/quill@2/dist/quill.js';
        script.onload = callback;
        document.head.appendChild(script);
    }

    // -----------------------------------------------------------------------
    // Обычные поля (hero, text, contacts)
    // -----------------------------------------------------------------------
    function renderSimpleFields(fields) {
        var wrapper  = el('div', { cls: 'se-simple' });
        var quillFields = [];

        fields.forEach(function (f) {
            if (f.type === 'hidden') return;

            // Проверяем depends_on
            var group = el('div', { cls: 'se-field-group', 'data-field': f.name });
            if (f.depends_on) {
                group.dataset.dependsField = f.depends_on.field;
                group.dataset.dependsValue = JSON.stringify(f.depends_on.value);
                group.style.display = 'none'; // скрыт по умолчанию, JS покажет
            }

            var label = el('label', { cls: 'se-label' });
            label.textContent = f.label + (f.required ? ' *' : '');
            group.appendChild(label);

            if (f.type === 'media') {
                // Медиапикер — выпадающий список с поиском (как в rows)
                group.appendChild(createMediaPicker(f.name, f.value || ''));
            } else if (f.type === 'quill') {
                var editorDiv = el('div', { cls: 'se-quill-editor' });
                editorDiv.dataset.fieldName = f.name;
                editorDiv.dataset.initValue = f.value || '';
                group.appendChild(editorDiv);
                quillFields.push({ name: f.name, div: editorDiv, value: f.value || '' });
            } else if (f.type === 'select') {
                var sel = el('select', { cls: 'se-input se-select', name: f.name });
                (f.options || []).forEach(function(opt) {
                    var o = el('option', { value: opt.value });
                    o.textContent = opt.label;
                    if (opt.value === (f.value || '')) o.selected = true;
                    sel.appendChild(o);
                });
                // Триггерим зависимости при смене
                sel.addEventListener('change', function() {
                    bindFieldDependencies(wrapper, fields);
                });
                group.appendChild(sel);
            } else if (f.type === 'textarea') {
                var textarea = el('textarea', { cls: 'se-input se-textarea', name: f.name });
                textarea.value = f.value || '';
                if (f.required) textarea.required = true;
                group.appendChild(textarea);
            } else {
                var input = el('input', { cls: 'se-input', type: f.type || 'text', name: f.name });
                input.value = f.value || '';
                if (f.required) input.required = true;

                // Специальный пикер для image_id
                if (f.name === 'image_id') {
                    renderImagePicker(group, input);
                }
                group.appendChild(input);
            }

            if (f.help_text) {
                group.appendChild(el('div', { cls: 'se-hint', text: f.help_text }));
            }

            wrapper.appendChild(group);
        });

        mount.appendChild(wrapper);

        // Инициализируем зависимости полей
        bindFieldDependencies(wrapper, fields);

        // Инициализируем Quill после вставки в DOM
        if (quillFields.length) {
            loadQuill(function () {
                quillFields.forEach(function (qf) {
                    var q = new Quill(qf.div, {
                        theme: 'snow',
                        modules: {
                            toolbar: [
                                [{ header: [1, 2, 3, false] }],
                                ['bold', 'italic', 'underline'],
                                [{ align: [] }],
                                [{ list: 'ordered' }, { list: 'bullet' }],
                                [{ indent: '-1' }, { indent: '+1' }],
                                ['link'],
                                ['clean']
                            ]
                        }
                    });
                    if (qf.value) q.root.innerHTML = qf.value;
                    quillInstances[qf.name] = q;
                });
            });
        }

        bindSimpleSubmit(fields);
    }

    // Показываем/скрываем поля в зависимости от значения другого поля
    function bindFieldDependencies(wrapper, fields) {
        var dependentGroups = wrapper.querySelectorAll('[data-depends-field]');
        if (!dependentGroups.length) return;

        function updateVisibility(changedFieldName, changedValue) {
            dependentGroups.forEach(function (group) {
                if (group.dataset.dependsField !== changedFieldName) return;
                var allowedValues = JSON.parse(group.dataset.dependsValue || '[]');
                var visible = allowedValues.indexOf(changedValue) !== -1;
                group.style.display = visible ? '' : 'none';
            });
        }

        fields.forEach(function (f) {
            if (f.type === 'hidden') return;
            var input = wrapper.querySelector('[name="' + f.name + '"]');
            if (!input) return;
            input.addEventListener('change', function () {
                updateVisibility(f.name, this.value);
            });
            updateVisibility(f.name, input.value || (f.value || ''));
        });
    }

    // depends_on в row_schema — скрываем ячейки строки
    function bindRowCellDependencies(row, rowSchema, simpleFields) {
        rowSchema.forEach(function(col) {
            if (!col.depends_on) return;
            var cell = row.querySelector('.se-row-cell[data-col="' + col.name + '"]');
            if (!cell) return;

            function update() {
                // Ищем значение поля-триггера в простых полях (select над списком)
                var triggerEl = mount.querySelector('[name="' + col.depends_on.field + '"]');
                if (!triggerEl) return;
                var visible = col.depends_on.value.indexOf(triggerEl.value) !== -1;
                cell.style.display = visible ? '' : 'none';
            }

            update();
            var triggerEl = mount.querySelector('[name="' + col.depends_on.field + '"]');
            if (triggerEl) triggerEl.addEventListener('change', update);
        });
    }

    function bindSimpleSubmit(fields) {
        onSubmit(function () {
            var result = {};
            fields.forEach(function (f) {
                if (f.type === 'hidden') return;
                if (f.type === 'quill') {
                    var q = quillInstances[f.name];
                    result[f.name] = q ? q.root.innerHTML : '';
                } else if (f.type === 'media') {
                    // media picker хранит значение в hidden input[name]
                    var inp = mount.querySelector('input[type="hidden"][name="' + f.name + '"]');
                    if (inp) result[f.name] = inp.value;
                } else {
                    var inp = mount.querySelector('[name="' + f.name + '"]');
                    if (inp) result[f.name] = inp.value;
                }
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
        // Сначала рендерим простые поля (style select)
        var simpleFields = fields.filter(function(f) { return f.type !== 'table'; });
        if (simpleFields.length) renderSimpleFields(simpleFields);

        var tableField = fields.find(function(f) { return f.type === 'table'; });
        var tableValue = tableField && tableField.value ? tableField.value : {};

        var headersField = { value: (tableValue.headers || []).join('|') };
        var rowsField    = { value: (tableValue.rows || []).map(function(r){ return r.join('|'); }).join('\n') };

        var initHeaders = headersField.value
            ? headersField.value.split('|').map(function (h) { return h.trim(); })
            : [''];
        var initRows = rowsField.value
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
            var result = {};
            // Простые поля (style select)
            simpleFields.forEach(function(f) {
                var inp = mount.querySelector('[name="' + f.name + '"]');
                if (inp) result[f.name] = inp.value;
            });
            // Данные таблицы как JSON
            result['table'] = JSON.stringify({
                headers: getHeaders(),
                rows:    getRows(),
            });
            setDataInput(result);
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
    // Панель превью (рендер через Django-эндпоинт)
    // -----------------------------------------------------------------------
    var previewPanel  = null;
    var previewIframe = null;
    var previewTimer  = null;

    function initPreviewPanel() {
        // Оборачиваем mount в flex-контейнер
        var wrapper = el('div', { cls: 'se-layout' });
        mount.parentNode.insertBefore(wrapper, mount);

        var settingsCol = el('div', { cls: 'se-layout__settings' });
        settingsCol.appendChild(mount);

        previewPanel = el('div', { cls: 'se-layout__preview' });

        // Заголовок панели
        var previewHeader = el('div', { cls: 'se-preview-header' });
        var previewTitle  = el('span', { cls: 'se-preview-title', text: 'Превью' });
        previewHeader.appendChild(previewTitle);

        // Кнопки ширины
        var widths = [
            { label: '📱', val: '375px', title: 'Мобильный' },
            { label: '💻', val: '768px', title: 'Планшет' },
            { label: '🖥️', val: '100%',  title: 'Десктоп' },
        ];
        var widthBtns = el('div', { cls: 'se-preview-widths' });
        widths.forEach(function(w) {
            var btn = el('button', { type: 'button', cls: 'se-preview-width-btn', title: w.title });
            btn.textContent = w.label;
            btn.addEventListener('click', function() {
                widthBtns.querySelectorAll('.se-preview-width-btn').forEach(function(b) { b.classList.remove('active'); });
                btn.classList.add('active');
                if (previewIframe) previewIframe.style.width = w.val;
            });
            widthBtns.appendChild(btn);
        });
        widthBtns.lastChild.classList.add('active');
        previewHeader.appendChild(widthBtns);

        // Кнопка обновления вручную
        var refreshBtn = el('button', { type: 'button', cls: 'se-preview-refresh-btn', title: 'Обновить превью' });
        refreshBtn.textContent = '↻';
        refreshBtn.addEventListener('click', function() { triggerPreviewUpdate(); });
        previewHeader.appendChild(refreshBtn);

        // Кнопка "Предпросмотр страницы" — только для существующих секций
        if (sectionId) {
            var pagePreviewBtn = el('button', { type: 'button', cls: 'se-btn se-preview-page-btn', title: 'Сохранить черновик и открыть страницу целиком' });
            pagePreviewBtn.textContent = '👁 Страница';
            pagePreviewBtn.addEventListener('click', function() { saveDraftAndOpenPage(); });
            previewHeader.appendChild(pagePreviewBtn);
        }

        previewPanel.appendChild(previewHeader);

        // Статус-строка (показываем ошибки / "обновляется...")
        var statusBar = el('div', { cls: 'se-preview-status' });
        previewPanel.appendChild(statusBar);
        previewPanel._statusBar = statusBar;

        // iframe
        var previewFrame = el('div', { cls: 'se-preview-frame' });
        previewIframe = el('iframe', { cls: 'se-preview-iframe', src: 'about:blank' });
        previewIframe.style.width = '100%';
        previewFrame.appendChild(previewIframe);
        previewPanel.appendChild(previewFrame);

        wrapper.appendChild(settingsCol);
        wrapper.appendChild(previewPanel);
    }

    // -----------------------------------------------------------------------
    // Привязка live preview к событиям редактора
    // -----------------------------------------------------------------------
    function bindLivePreview(type) {
        triggerPreviewUpdate();

        if (mount) {
            mount.addEventListener('input',  function() { schedulePreviewUpdate(); });
            mount.addEventListener('change', function() { schedulePreviewUpdate(); });
            // Для медиапикера — небольшая задержка (загрузка превью асинхронная)
            mount.addEventListener('click',  function() { setTimeout(schedulePreviewUpdate, 600); });
        }
    }

    function schedulePreviewUpdate() {
        clearTimeout(previewTimer);
        previewTimer = setTimeout(triggerPreviewUpdate, 400);
    }

    // -----------------------------------------------------------------------
    // Собираем данные из формы редактора и отправляем на сервер
    // -----------------------------------------------------------------------
    function triggerPreviewUpdate() {
        if (!previewIframe || !typeSelect) return;

        var type  = typeSelect.value;
        var title = (document.querySelector('[name="title"]') || {}).value || '';
        var data  = collectEditorData();

        setPreviewStatus('loading');

        fetch('/admin/section-preview/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken':  getCsrf(),
            },
            body: JSON.stringify({ type: type, title: title, data: data }),
        })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (resp.error) {
                setPreviewStatus('error', resp.error);
                return;
            }
            setPreviewStatus('ok');
            injectIntoIframe(resp.html);
        })
        .catch(function(err) {
            setPreviewStatus('error', err.message || 'Ошибка сети');
        });
    }

    // Вставляем HTML секции в iframe (с основным CSS сайта)
    function injectIntoIframe(sectionHtml) {
        // Ищем URL main.css из текущей страницы
        var cssUrl = '/static/css/main.css';
        var links  = document.querySelectorAll('link[rel="stylesheet"]');
        for (var i = 0; i < links.length; i++) {
            if (links[i].href.indexOf('main.css') !== -1) { cssUrl = links[i].href; break; }
        }

        var html = '<!DOCTYPE html><html lang="ru"><head>' +
            '<meta charset="UTF-8">' +
            '<meta name="viewport" content="width=device-width,initial-scale=1">' +
            '<link rel="stylesheet" href="' + cssUrl + '">' +
            '<style>' +
            ':root{--color-primary:#2563eb;--color-background:#fff;--color-surface:#f8fafc;' +
            '--color-accent:#1d4ed8;--color-text:#1e293b;--font-main:sans-serif;}' +
            'body{margin:0;}' +
            '</style>' +
            '</head><body>' + sectionHtml + '</body></html>';

        previewIframe.srcdoc = html;
    }

    // -----------------------------------------------------------------------
    // Сохранить черновик → открыть страницу целиком в новой вкладке
    // -----------------------------------------------------------------------
    function saveDraftAndOpenPage() {
        if (!sectionId || !typeSelect) return;

        var type  = typeSelect.value;
        var title = (document.querySelector('[name="title"]') || {}).value || '';
        var data  = collectEditorData();

        setPreviewStatus('loading');

        fetch('/admin/section-draft-save/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken':  getCsrf(),
            },
            body: JSON.stringify({ section_id: parseInt(sectionId), type: type, title: title, data: data }),
        })
        .then(function(r) { return r.json(); })
        .then(function(resp) {
            if (resp.error) {
                setPreviewStatus('error', resp.error);
                return;
            }
            setPreviewStatus('ok');
            window.open(resp.preview_url, '_blank');
        })
        .catch(function(err) {
            setPreviewStatus('error', err.message || 'Ошибка сети');
        });
    }

    // -----------------------------------------------------------------------
    // Собираем текущие данные из всех виджетов редактора
    // -----------------------------------------------------------------------
    function collectEditorData() {
        var data = {};
        if (!mount) return data;

        // Обычные поля
        mount.querySelectorAll('input:not([type="hidden"]), select, textarea').forEach(function(inp) {
            if (inp.name) data[inp.name] = inp.type === 'checkbox' ? inp.checked : inp.value;
        });

        // Скрытые поля media-пикера
        mount.querySelectorAll('input[type="hidden"][name]').forEach(function(inp) {
            data[inp.name] = inp.value;
        });

        // Quill-редакторы
        Object.keys(quillInstances).forEach(function(name) {
            data[name] = quillInstances[name].root.innerHTML;
        });

        // Таблица
        var thead = mount.querySelector('.se-table thead');
        var tbody = mount.querySelector('.se-table tbody');
        if (thead && tbody) {
            data.table = JSON.stringify({
                headers: Array.from(thead.querySelectorAll('input[data-is-header]')).map(function(i) { return i.value.trim(); }),
                rows:    Array.from(tbody.querySelectorAll('tr')).map(function(tr) {
                    return Array.from(tr.querySelectorAll('td:not(.se-table__ctrl) input')).map(function(i) { return i.value.trim(); });
                }),
            });
        }

        // Rows-builder (counters, cards, team, steps, faq, testimonials, chart)
        var rowsList = mount.querySelector('.se-rows-list');
        if (rowsList) {
            var items = [];
            rowsList.querySelectorAll('.se-row-item').forEach(function(row) {
                var item = {};
                var ep = row.querySelector('.se-emoji-preview');
                if (ep) item.icon = ep.textContent;
                row.querySelectorAll('input[name], select[name], textarea[name]').forEach(function(inp) {
                    item[inp.name] = inp.value;
                });
                if (row._quills) {
                    Object.keys(row._quills).forEach(function(n) { item[n] = row._quills[n].root.innerHTML; });
                }
                items.push(item);
            });
            data.items = JSON.stringify(items);
        }

        // Contacts-builder
        var contactRows = mount.querySelectorAll('.se-contact-row');
        if (contactRows.length) {
            var citems = [];
            contactRows.forEach(function(row) {
                citems.push({
                    type:        row.querySelector('.cr-type')  ? row.querySelector('.cr-type').value  : '',
                    label:       row.querySelector('.cr-label') ? row.querySelector('.cr-label').value : '',
                    value:       row.querySelector('.cr-value') ? row.querySelector('.cr-value').value : '',
                    description: row.querySelector('.cr-desc')  ? row.querySelector('.cr-desc').value  : '',
                });
            });
            data.items = JSON.stringify(citems);
        }

        // Form-fields-builder
        var formRows = mount.querySelectorAll('.se-form-field-row');
        if (formRows.length) {
            var fields = [];
            formRows.forEach(function(row, idx) {
                var label = row.querySelector('.ff-label') ? row.querySelector('.ff-label').value : '';
                if (label) {
                    fields.push({
                        name:     'field_' + (idx + 1),
                        type:     row.querySelector('.ff-type')  ? row.querySelector('.ff-type').value  : 'text',
                        label:    label,
                        required: row.querySelector('.ff-req')   ? row.querySelector('.ff-req').checked : false,
                    });
                }
            });
            data.fields = JSON.stringify(fields);
        }

        return data;
    }

    // -----------------------------------------------------------------------
    // Статус-строка превью
    // -----------------------------------------------------------------------
    function setPreviewStatus(state, message) {
        if (!previewPanel || !previewPanel._statusBar) return;
        var bar = previewPanel._statusBar;
        bar.className = 'se-preview-status se-preview-status--' + state;
        bar.textContent = state === 'loading' ? 'Обновление...'
                        : state === 'error'   ? ('Ошибка: ' + (message || ''))
                        : '';
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
        // Unfold рендерит форму внутри #content > fieldset-ов.
        // Вставляем mount в конец #content — прямо после последнего fieldset,
        // внутри того же flex-контейнера что и поля формы.
        mount = el('div', { cls: 'se-mount' });
        var contentDiv = document.getElementById('content');
        if (contentDiv) {
            contentDiv.appendChild(mount);
        } else {
            // Запасной вариант — после последнего fieldset
            var fieldsets = document.querySelectorAll('fieldset');
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

        // Создаём панель превью справа (кнопки ↻ и «Страница» внутри неё)
        initPreviewPanel();

        // Начальная загрузка
        loadFields(typeSelect.value);

        // Реагируем на смену типа
        typeSelect.addEventListener('change', function () {
            clearSubmitHandlers();
            loadFields(this.value);
        });
    });

})();