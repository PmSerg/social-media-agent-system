# Детальное руководство по созданию Views в Notion

## 📊 Views для CMO

### 1. Brand Assets by Type (База: Brand Assets)

**Создание:**
1. Откройте базу "Brand Assets"
2. Нажмите "+ Add view"
3. Название: "Brand Assets by Type"
4. Тип: **Board**

**Настройки:**
- **Group by**: Asset Type
- **Sort**: Date Added → Descending (новые сверху)
- **Properties** (показать):
  ✅ Title
  ✅ Category
  ✅ Status
  ✅ Tags
  ✅ Date Added
  ❌ Content (скрыть - слишком длинный)
  ✅ Archetype Alignment

**Результат:** Канбан-доска с колонками:
- Brand Description
- Press Release
- Example Posts
- CEO Bio
- Product Info
- Audience Persona

---

### 2. Content Calendar (База: Content Plan - AI Workflow)

**Создание:**
1. Откройте базу "Content Plan - AI Workflow"
2. Нажмите "+ Add view"
3. Название: "Content Calendar"
4. Тип: **Calendar**

**Настройки:**
- **Calendar by**: Publication Date
- **Filter**: 
  - Status is "In Progress" OR
  - Status is "In Review" OR
  - Status is "Idea" AND Execution Mode is "Scheduled"
- **Properties** (показать на карточках):
  ✅ Task Name
  ✅ Channel
  ✅ Status
  ✅ Agent Status
  ✅ Archetype Used

**Дополнительно:**
- **Color by**: Channel (разные цвета для FB, IG, LinkedIn)

**Результат:** Календарь с запланированными постами

---

### 3. Performance Dashboard (База: Content Plan - AI Workflow)

**Создание:**
1. Откройте базу "Content Plan - AI Workflow"
2. Нажмите "+ Add view"
3. Название: "Performance Dashboard"
4. Тип: **Table** (с группировкой)

**Настройки:**
- **Group by**: Channel
- **Sub-group by**: Archetype Used
- **Filter**: Status is "Published"
- **Sort**: Publication Date → Descending
- **Properties** (столбцы):
  ✅ Task Name
  ✅ Publication Date
  ✅ Channel
  ✅ Archetype Used
  ✅ Performance Metrics
  ✅ Target Audience
  ❌ Research Data (скрыть)
  ❌ Command Used (скрыть)
  ❌ Error Log (скрыть)

**Дополнительно:**
- Добавить **Calculate** для Performance Metrics (если числовое поле)

**Результат:** Таблица с группировкой для анализа эффективности

---

## 🤖 Views для Агентов

### 4. Active Content Tasks (База: Content Plan - AI Workflow)

**Создание:**
1. Откройте базу "Content Plan - AI Workflow"
2. Нажмите "+ Add view"
3. Название: "Active Content Tasks"
4. Тип: **Table**

**Настройки:**
- **Filter**:
  - Status is not "Published" AND
  - Status is not "Rejected"
- **Sort**: 
  - Priority → Descending (High → Medium → Low)
  - Then by: Created time → Ascending (старые первые)
- **Properties** (столбцы):
  ✅ Task Name
  ✅ Status
  ✅ Agent Status
  ✅ Channel
  ✅ Category (relation)
  ✅ Execution Mode
  ✅ Command Used
  ❌ Publication Date (скрыть если не Scheduled)
  ❌ Error Log (показать только если есть ошибки)

**Результат:** Рабочий список активных задач для агентов

---

### 5. Research Resources (База: Brand Assets + Categories and Topics)

**Вариант А - Составной View:**

Это не один view, а набор:

**5.1 Brand Context (База: Brand Assets)**
1. Создайте view "Brand Context"
2. Тип: **Gallery**
3. **Filter**: 
   - Asset Type is "Brand Description" OR
   - Asset Type is "CEO Bio" OR
   - Asset Type is "Product Info"
4. **Sort**: Asset Type → Ascending
5. **Properties**:
   ✅ Title
   ✅ Asset Type
   ✅ Archetype Alignment
   ✅ Tags

**5.2 Topics Knowledge Base (База: Categories and Topics)**
1. Создайте view "Topics Knowledge Base"
2. Тип: **Table** с группировкой
3. **Group by**: Category
4. **Sort**: Priority → Descending
5. **Properties**:
   ✅ Topic Name
   ✅ Subcategory
   ✅ Benefits & Key Points
   ✅ Primary Archetype
   ✅ Target Audience
   ❌ Description (relation - скрыть)

**Результат:** Два view для быстрого доступа к информации

---

### 6. Brand Guidelines Quick Access (База: Rules / Examples)

**Создание:**
1. Откройте базу "Rules / Examples"
2. Нажмите "+ Add view"
3. Название: "Brand Guidelines Quick Access"
4. Тип: **Gallery**

**Настройки:**
- **Group by**: Channel
- **Sort within groups**: Name → Ascending
- **Card preview**:
  - Size: Medium
  - Cover: None (или добавить логотипы каналов)
  - Fit: Contain
- **Properties** (показать на карточках):
  ✅ Name
  ✅ Brand Voice
  ✅ Archetype Guidelines
  ✅ Tone of Voice
  ❌ Hashtags
  ❌ CTA Examples
  ❌ Post Format
  ❌ Content Examples

**Дополнительно:**
- **First load**: Archetype Guidelines (показать превью текста)

**Результат:** Визуальные карточки с быстрым доступом к гайдлайнам

---

## 🎯 Дополнительные полезные Views

### 7. Content by Archetype (База: Content Plan)
- Тип: **Board**
- Group by: Archetype Used
- Filter: Status is "Published"
- Для анализа какой архетип работает лучше

### 8. Industry Focus (База: Industries & Challenges)
- Тип: **Table**
- Sort: Content Priority → Descending
- Показать связанные Categories и Content Plan записи

### 9. Weekly Sprint (База: Content Plan)
- Тип: **Table**
- Filter: Created time is This week
- Для недельного планирования

### 10. Error Log (База: Content Plan)
- Тип: **Table**
- Filter: Error Log is not empty
- Sort: Last edited → Descending
- Для отслеживания проблем

---

## 💡 Советы по использованию Views

1. **Сохраняйте фильтры** - используйте "Save for everyone"
2. **Используйте цвета** - Color by Status или Channel
3. **Скрывайте лишнее** - не все поля нужны в каждом view
4. **Группируйте логично** - по статусу, каналу, архетипу
5. **Добавляйте иконки** - к названиям views для быстрой навигации

## 🔐 Права доступа

Можно настроить разные views для разных ролей:
- **CMO Views** - полный доступ ко всем данным
- **Agent Views** - только необходимое для работы
- **Public Views** - ограниченный просмотр