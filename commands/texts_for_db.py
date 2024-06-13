from aiogram.utils.formatting import Bold, as_list, as_marked_section

categories = ['Food', 'Drink']

description_for_info_pages = {
    "main": "Welcome to Pizza Bot",
    "about": "Mazali Pitsalar",
    "payment": as_marked_section(
        Bold("Oplata turlari"),
        "Bot orqali",
        "Karta keshi orqali",
        "Naqt pul",
        marker="✅",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Dastavka turlari: "),
            "Kurier orqali",
            "Tezkor yetkazish",
            "Olib ketish",
            marker="✅",
        ),
        as_marked_section(Bold("Mumkin emas"), "Pochat orqali", "Havo yoli orqali", marker="x"),
        sep="\n---------------\n",
    ).as_html(),
    'catalog': "Kategoriya",
    'cart': "Savat"
}
