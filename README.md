# REST API за каталог с рецепти

## Стартиране в PowerShell

Изпълни командите в папката на проекта с Python 3.10 или по-нова версия.

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m alembic upgrade head
.venv/Scripts/python -m uvicorn main:app
```

Отвори [Swagger UI](http://127.0.0.1:8000/docs). Alembic създава локалния файл
`recipes.db` и прилага двете миграции. Втората добавя задължителното поле
`difficulty` и задава `easy` на съществуващите рецепти.

За да зададеш лимита според твоя факултетен номер, изпълни
`$env:FACULTY_NUMBER = "1234567890"` преди стартиране на Uvicorn и замени
примерния номер със своя. В този пример лимитът е 140 порции. Без настройката
демото използва 50.

## Пример в Swagger

Използвай **Try it out** за следните заявки. В примерите идентификаторите са
за празна база. При повторно тестване използвай върнатите от API стойности.

1. `POST /authors` с `{"name":"Иван","email":"ivan@example.com"}`
2. `POST /categories` с `{"name":"Десерти"}`
3. `POST /ingredients` с `{"name":"Брашно"}`
4. `POST /recipes` с
   `{"title":"Палачинки","instructions":"Разбъркай и изпържи.","prep_time":20,"servings":2,"difficulty":"easy","author_id":1,"category_id":1}`
5. `POST /recipes/1/ingredients` с `{"ingredient_id":1,"quantity":200,"unit":"g"}`
6. `GET /recipes/1/scaled?servings=4` връща 400 g. Оригиналното количество
   остава 200 g и се вижда в `GET /recipes/1/ingredients`.

Списъкът с рецепти поддържа едновременни филтри, например
`GET /recipes?title=палач&category_id=1&max_prep_time=20`.
Рецептите на автор са достъпни чрез `GET /authors/1/recipes`.

