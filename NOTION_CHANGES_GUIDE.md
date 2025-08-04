# Пошаговое руководство по обновлению баз данных Notion

## Этап 1: Подготовка (День 1)

### Шаг 1.1: Создание новой базы "Brand Assets"

1. Откройте страницу с базами данных
2. Создайте новую базу данных "Brand Assets"
3. Добавьте поля:

```
- Title (title) - уже есть по умолчанию
- Asset Type (select) с опциями:
  • Brand Description
  • Press Release
  • Example Posts
  • CEO Bio
  • Product Info
  • Audience Persona
  
- Content (text) - основной контент
- Category (select) с опциями:
  • About Company
  • Leadership
  • Products
  • Target Audience
  • PR Materials
  
- Date Added (date)
- Status (select): Active, Archived, Draft
- Tags (multi_select) - создать без опций, будут добавляться по мере использования
- Archetype Alignment (multi_select): Caregiver, Explorer, Regular Guy
```

### Шаг 1.2: Создание базы "Industries & Challenges"

1. Создайте новую базу данных "Industries & Challenges"
2. Добавьте поля:

```
- Industry Name (title)
- Category (select) - добавить ВСЕ категории из скриншота:
  • Adult Industry
  • Alternative Lending & Finance
  • Art & Collectibles
  • Cryptocurrency & Blockchain
  • Crowdfunding & Peer-to-Peer Platforms
  • Cybersecurity & VPN Services
  • E-commerce & Dropshipping
  • Escort & Dating Services
  • Fintech & Digital Banks
  • Gaming & eSports
  • Gambling & Betting
  • High-Risk Travel & Hospitality
  • Money Services & Payment Processors
  • Online Education & Coaching
  • Remittance & Money Transfer
  • Subscription-Based Services
  • Web Hosting & Cloud Services
  • DeFi & Web3 Financial Services
  • Nutraceuticals & Alternative Payment Systems
  • Precious Metals & Mining
  • CBD & Cannabis
  • NGOs & Activist Groups
  • Freelance & Gig Economy
  
- Banking Challenges (text) - из второй колонки скриншота
- Risk Level (select): High, Medium, Low
- Example Clients (text)
- Content Priority (number)
- Key Messages (text)
```

## Этап 2: Обновление Categories and Topics (День 2)

### Шаг 2.1: Добавление новых полей

1. Откройте базу "Categories and Topics"
2. Добавьте новые поля:

```
- Primary Archetype (select): Caregiver, Explorer, Regular Guy
- Archetype Balance (text) - например: "35% Caregiver, 35% Explorer, 30% Regular Guy"
- Target Audience (multi_select) с опциями:
  • Underbanked businesses
  • E-commerce
  • Crypto traders
  • SMEs
  • Startups
  • High-risk businesses
  
- Priority (select): High, Medium, Low
- Key Messages (text)
- Product Type (select):
  • Payment Rails
  • Banking Services
  • Crypto Services
  • Compliance Tools
  
- Content Frequency (select): Weekly, Bi-weekly, Monthly, Quarterly
```

3. Добавьте связи (relation):
```
- Industry (relation → Industries & Challenges)
- Related Brand Assets (relation → Brand Assets)
```

### Шаг 2.2: Обновление опций в Subcategory

Измените опции на более логичные:
```
Удалить старые и добавить:
- Payment Rails
- Crypto Services
- Banking Features
- Industry Trends
- Regulatory Updates
- Market Analysis
- Client Success
- Implementation Stories
```

## Этап 3: Обновление Content Plan (День 3)

### Шаг 3.1: Переименование полей

1. Переименуйте "Название задачи" → "Task Name"

### Шаг 3.2: Удаление устаревших полей

Удалите:
- Month
- Week  
- Position in Week

### Шаг 3.3: Добавление новых полей

```
- Archetype Used (select): Caregiver, Explorer, Regular Guy, Mixed
- Target Audience (multi_select) - скопировать опции из Categories
- Content Type (select):
  • Educational
  • Promotional
  • News
  • Engagement
  • Support
  
- Performance Metrics (text)
- A/B Test Version (text)
- CEO Quote Included (checkbox)
- Press Release Based (checkbox)
```

Добавьте связи:
```
- Related Content (relation → Content Plan)
- Industry Focus (relation → Industries & Challenges)
- Brand Assets Used (relation → Brand Assets)
```

### Шаг 3.4: Обновление Command Used

Измените тип поля на select с опциями:
- /create-content-post
- /research-only
- /bulk-content
- /scheduled-post

## Этап 4: Обновление Rules / Examples (День 4)

### Шаг 4.1: Переименование и обновление

1. Переименуйте "Tone of Voice" → "Brand Voice"
2. Обновите опции:
```
- Caregiver Professional
- Explorer Innovative
- Regular Guy Friendly
- Mixed Balanced
```

### Шаг 4.2: Удаление дублей

Удалите поле "Content" (дублирует Content Examples)

### Шаг 4.3: Добавление новых полей

```
- Archetype Guidelines (text)
- Archetype Examples (text)
- Do's and Don'ts (text)
- Target Audience per Channel (text)
- Optimal Posting Times (text)
- Visual Guidelines (text)
- CEO Quotes (text)
```

Добавьте связи:
```
- Industry-Specific Rules (relation → Industries & Challenges)
- Example Posts (relation → Brand Assets)
```

## Этап 5: Обновление Image Styles (День 5)

### Шаг 5.1: Обновление Mood

Добавьте новые опции к существующим:
- Trustworthy
- Innovative
- Approachable

### Шаг 5.2: Добавление новых полей

```
- Archetype Alignment (select): Caregiver, Explorer, Regular Guy, Universal
- Color Palette (text)
- Visual Elements (text)
- Avoid Elements (text)
- Example Images (files)
```

## Этап 6: Загрузка данных от CMO (День 6-7)

### В базу Brand Assets загрузить:

1. **Brand Description** (Asset Type: Brand Description)
   - Полное описание Kea с архетипами
   
2. **Press Releases** (Asset Type: Press Release)
   - Все пресс-релизы по отдельности
   
3. **Example Posts** (Asset Type: Example Posts)
   - 10 примеров постов с тегами
   
4. **CEO Bio** (Asset Type: CEO Bio)
   - Биография Mark
   
5. **Products** (Asset Type: Product Info)
   - Описание каждого продукта
   
6. **Audience Personas** (Asset Type: Audience Persona)
   - Описания целевых аудиторий

## Этап 7: Создание Views (День 8)

### Для CMO:
1. Brand Assets by Type
2. Content Calendar
3. Performance Dashboard

### Для агентов:
1. Active Content Tasks
2. Research Resources
3. Brand Guidelines Quick Access

## Чек-лист проверки

После каждого этапа проверьте:
- [ ] Все поля добавлены корректно
- [ ] Связи (relations) работают в обе стороны
- [ ] Опции в select полях правильные
- [ ] Нет дублирующихся полей
- [ ] Все поля на английском языке

## Тестирование

После завершения всех изменений:
1. Создайте тестовую задачу в Content Plan
2. Проверьте все связи между базами
3. Убедитесь, что агенты могут читать данные
4. Протестируйте фильтры и сортировки