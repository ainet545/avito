import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from avito_app.models import Category, SubCategory, Product

# 1x1 прозрачный PNG-плейсхолдер для обязательных ImageField
PLACEHOLDER_IMAGE = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
    b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

# Структура: категория (en/ru) -> список подкатегорий (en/ru) ->
# список базовых названий товаров (en/ru), из которых будут собраны вариации
CATALOG = {
    ("Electronics", "Электроника"): {
        ("Smartphones", "Смартфоны"): [
            ("iPhone 15 Pro", "Айфон 15 Про"),
            ("iPhone 14", "Айфон 14"),
            ("Samsung Galaxy S24", "Самсунг Гэлакси S24"),
            ("Samsung Galaxy A54", "Самсунг Гэлакси A54"),
            ("Xiaomi Redmi Note 13", "Сяоми Редми Ноут 13"),
            ("Google Pixel 8", "Гугл Пиксель 8"),
        ],
        ("Laptops", "Ноутбуки"): [
            ("MacBook Air M2", "Макбук Эйр M2"),
            ("MacBook Pro 16", "Макбук Про 16"),
            ("Dell XPS 13", "Делл XPS 13"),
            ("Lenovo ThinkPad X1", "Леново ThinkPad X1"),
            ("Asus ROG Strix", "Асус ROG Strix"),
        ],
        ("Headphones", "Наушники"): [
            ("AirPods Pro 2", "Аирподс Про 2"),
            ("Sony WH-1000XM5", "Сони WH-1000XM5"),
            ("JBL Tune 510BT", "JBL Tune 510BT"),
        ],
        ("TVs", "Телевизоры"): [
            ("Samsung QLED 55", "Самсунг QLED 55"),
            ("LG OLED 65", "LG OLED 65"),
            ("Xiaomi Smart TV 43", "Сяоми Смарт ТВ 43"),
        ],
    },
    ("Clothing", "Одежда"): {
        ("Men's Clothing", "Мужская одежда"): [
            ("Denim Jacket", "Джинсовая куртка"),
            ("Wool Coat", "Шерстяное пальто"),
            ("Cotton T-Shirt", "Хлопковая футболка"),
            ("Slim Fit Jeans", "Зауженные джинсы"),
        ],
        ("Women's Clothing", "Женская одежда"): [
            ("Summer Dress", "Летнее платье"),
            ("Knit Sweater", "Вязаный свитер"),
            ("Leather Skirt", "Кожаная юбка"),
            ("Trench Coat", "Плащ тренч"),
        ],
        ("Kids' Clothing", "Детская одежда"): [
            ("Kids Hoodie", "Детское худи"),
            ("Kids Sneakers", "Детские кроссовки"),
        ],
    },
    ("Home & Garden", "Дом и сад"): {
        ("Furniture", "Мебель"): [
            ("Sofa 3-Seater", "Диван трёхместный"),
            ("Office Chair", "Офисное кресло"),
            ("Dining Table", "Обеденный стол"),
            ("Bookshelf", "Книжный шкаф"),
        ],
        ("Kitchen", "Кухня"): [
            ("Blender 600W", "Блендер 600Вт"),
            ("Air Fryer", "Аэрогриль"),
            ("Coffee Machine", "Кофемашина"),
        ],
        ("Garden Tools", "Садовый инвентарь"): [
            ("Lawn Mower", "Газонокосилка"),
            ("Garden Hose 20m", "Садовый шланг 20м"),
        ],
    },
    ("Sports & Outdoors", "Спорт и отдых"): {
        ("Fitness", "Фитнес"): [
            ("Yoga Mat", "Коврик для йоги"),
            ("Adjustable Dumbbells", "Разборные гантели"),
            ("Treadmill", "Беговая дорожка"),
        ],
        ("Camping", "Кемпинг"): [
            ("4-Person Tent", "Палатка на 4 человека"),
            ("Sleeping Bag", "Спальный мешок"),
            ("Portable Camping Stove", "Портативная туристическая плита"),
        ],
        ("Cycling", "Велоспорт"): [
            ("Mountain Bike 27.5", "Горный велосипед 27.5"),
            ("Bike Helmet", "Велошлем"),
        ],
    },
    ("Beauty & Health", "Красота и здоровье"): {
        ("Skincare", "Уход за кожей"): [
            ("Moisturizing Cream", "Увлажняющий крем"),
            ("Vitamin C Serum", "Сыворотка с витамином C"),
            ("Sunscreen SPF50", "Солнцезащитный крем SPF50"),
        ],
        ("Makeup", "Макияж"): [
            ("Matte Lipstick", "Матовая помада"),
            ("Foundation", "Тональный крем"),
            ("Mascara", "Тушь для ресниц"),
        ],
    },
    ("Toys & Games", "Игрушки и игры"): {
        ("Board Games", "Настольные игры"): [
            ("Monopoly", "Монополия"),
            ("Chess Set", "Набор для шахмат"),
            ("Jenga", "Дженга"),
        ],
        ("Kids Toys", "Детские игрушки"): [
            ("Lego Classic Set", "Лего Классик набор"),
            ("Remote Control Car", "Машинка на радиоуправлении"),
            ("Plush Teddy Bear", "Плюшевый мишка"),
        ],
    },
    ("Books & Stationery", "Книги и канцтовары"): {
        ("Fiction", "Художественная литература"): [
            ("Mystery Novel", "Роман детектив"),
            ("Fantasy Novel", "Роман фэнтези"),
        ],
        ("Stationery", "Канцтовары"): [
            ("Notebook A5", "Блокнот A5"),
            ("Gel Pen Set", "Набор гелевых ручек"),
            ("Backpack for School", "Школьный рюкзак"),
        ],
    },
    ("Automotive", "Автотовары"): {
        ("Car Accessories", "Автоаксессуары"): [
            ("Car Phone Holder", "Автодержатель для телефона"),
            ("Seat Covers Set", "Комплект чехлов на сиденья"),
            ("Dash Cam", "Видеорегистратор"),
        ],
        ("Tools", "Инструменты"): [
            ("Tire Inflator", "Компрессор для шин"),
            ("Tool Kit 100pcs", "Набор инструментов 100 предметов"),
        ],
    },
    ("Pet Supplies", "Товары для животных"): {
        ("Dog Supplies", "Товары для собак"): [
            ("Dog Leash", "Поводок для собаки"),
            ("Dog Food 10kg", "Корм для собак 10кг"),
            ("Dog Bed", "Лежанка для собаки"),
        ],
        ("Cat Supplies", "Товары для кошек"): [
            ("Cat Litter Box", "Кошачий лоток"),
            ("Cat Food 5kg", "Корм для кошек 5кг"),
            ("Scratching Post", "Когтеточка"),
        ],
    },
    ("Groceries", "Продукты"): {
        ("Snacks", "Снеки"): [
            ("Potato Chips", "Картофельные чипсы"),
            ("Chocolate Bar", "Шоколадный батончик"),
            ("Mixed Nuts", "Смесь орехов"),
        ],
        ("Beverages", "Напитки"): [
            ("Green Tea 100 bags", "Зелёный чай 100 пакетиков"),
            ("Instant Coffee", "Растворимый кофе"),
            ("Sparkling Water", "Газированная вода"),
        ],
    },
}

# Вариации, чтобы из одного базового товара сделать несколько разных записей
# (у Product.article должна быть уникальность, поэтому вариации нужны)
VARIANTS_EN = ["Standard", "Pro", "Lite", "New", "Limited Edition", "2024 Model", "Basic", "Premium"]
VARIANTS_RU = ["Стандарт", "Про", "Лайт", "Новинка", "Лимитированная серия", "Модель 2024", "Базовая", "Премиум"]


class Command(BaseCommand):
    help = "Заполняет базу большим объёмом тестовых категорий, подкатегорий и товаров (en/ru)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить существующие Category/SubCategory/Product перед заполнением",
        )
        parser.add_argument(
            "--variants",
            type=int,
            default=3,
            help="Сколько вариаций каждого товара создать (по умолчанию 3)",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Удаляю старые данные...")
            Product.objects.all().delete()
            SubCategory.objects.all().delete()
            Category.objects.all().delete()

        variants_count = options["variants"]
        article_counter = 100000
        total_products = 0

        for (cat_en, cat_ru), subcats in CATALOG.items():
            category, created = Category.objects.get_or_create(
                category_name_en=cat_en,
                defaults={
                    "category_name_ru": cat_ru,
                    "category_image": ContentFile(PLACEHOLDER_IMAGE, name=f"{cat_en}.png"),
                },
            )
            self.stdout.write(f"Категория: {category.category_name_en} ({'создана' if created else 'уже была'})")

            for (sub_en, sub_ru), products in subcats.items():
                subcategory, created = SubCategory.objects.get_or_create(
                    category=category,
                    subcategory_name_en=sub_en,
                    defaults={
                        "subcategory_name_ru": sub_ru,
                        "subcategory_image": ContentFile(PLACEHOLDER_IMAGE, name=f"{sub_en}.png"),
                    },
                )
                self.stdout.write(f"  Подкатегория: {subcategory.subcategory_name_en} ({'создана' if created else 'уже была'})")

                for name_en, name_ru in products:
                    for i in range(variants_count):
                        variant_en = VARIANTS_EN[i % len(VARIANTS_EN)]
                        variant_ru = VARIANTS_RU[i % len(VARIANTS_RU)]
                        article_counter += 1

                        full_name_en = f"{name_en} {variant_en}"
                        full_name_ru = f"{name_ru} {variant_ru}"
                        price = round(random.uniform(5, 1500), 2)

                        product, created = Product.objects.get_or_create(
                            article=article_counter,
                            defaults={
                                "subcategory": subcategory,
                                "product_name_en": full_name_en,
                                "product_name_ru": full_name_ru,
                                "description_en": f"{full_name_en} - great quality, fast delivery.",
                                "description_ru": f"{full_name_ru} - отличное качество, быстрая доставка.",
                                "price": price,
                                "product_image": ContentFile(PLACEHOLDER_IMAGE, name=f"{full_name_en}.png"),
                            },
                        )
                        if created:
                            total_products += 1

        self.stdout.write(self.style.SUCCESS(
            f"Готово! Создано товаров: {total_products}. "
            f"Категорий: {Category.objects.count()}, подкатегорий: {SubCategory.objects.count()}."
        ))