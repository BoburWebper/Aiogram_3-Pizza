from aiogram import types, F, Router
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_product, orm_get_products, orm_delete_product, orm_get_product, \
    orm_update_product, orm_get_categories, orm_get_info_pages, orm_change_banner_image
from filter.chat_types import ChatTypeFilter, IsAdmin
from keybords.inline import get_callback_btns
from keybords.reply import get_keyboards

admin_router = Router()
admin_router.message.filter(ChatTypeFilter(['private']), IsAdmin())

ADMIN_KB = get_keyboards(
    "Tovar qoshish",
    "Tovarlarni korish",
    "Banner ozgartrish",
    # "Tovarni ochirish",

    placeholder="select one",
    sizes=(2,),
)


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_for_change = None

    texts = {
        'AddProduct:name': 'Name state',
        'AddProduct:description': 'description state',
        'AddProduct:category': 'category state',
        'AddProduct:price': 'price state',
        'AddProduct:image': 'image state',
    }


@admin_router.message(Command('admin'))
async def connect_product(message: types.Message):
    await message.answer("Nima qilimoqchisz", reply_markup=ADMIN_KB)


@admin_router.message(F.text == 'Tovarlarni korish')
async def show_products(message: types.Message, session: AsyncSession):
    # for product in await orm_get_categories(session):
    categories = await orm_get_categories(session)
    btns = {category.name: f'category_{category.id}' for category in categories}
    await message.answer("All categories:", reply_markup=get_callback_btns(btns=btns))


@admin_router.callback_query(F.data.startswith('category_'))
async def starting_add_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    for product in await orm_get_products(session, int(category_id)):
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}</strong>\n{product.description}\n"
                    f"Price: {product.price:.2f}",
            reply_markup=get_callback_btns(btns={
                "Delete": f"delete_{product.id}",
                "Change": f"change_{product.id}",
            },
                sizes=(2,),
            ),
        )


@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split('delete_')[-1]
    await orm_delete_product(session, int(product_id))
    await callback.answer("Deleted product")
    await callback.message.answer("Deleted product")


# banner section
class AddBanner(StatesGroup):
    image = State()


@admin_router.message(StateFilter(None), F.text == 'Banner ozgartrish')
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f"Banner suratini yuboring.\nTavsifda qaysi sahifani koʻrsating:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)


@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Oddiy sahifa sarlavhasini kiriting, masalan:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Banner added")
    await state.clear()


@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def change_product(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    product_id = callback.data.split('change_')[-1]
    product_for_change = await orm_get_product(session, int(product_id))
    AddProduct.product_for_change = product_for_change
    await callback.answer()
    await callback.message.answer(
        "Add name for Change product", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


# FSM context


@admin_router.message(StateFilter(None), F.text == "Tovar qoshish")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer("Mahsulot nomini kirgizing", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@admin_router.message(StateFilter('*'), Command("cancel"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "cancel")
async def cancel_product(message: types.Message, state: FSMContext):
    current_state = state.get_state()
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.clear()
    await message.answer("Qaytarildi", reply_markup=ADMIN_KB)


@admin_router.message(StateFilter('*'), Command("back"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "back")
async def cancel_product(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer("Bundan oldingi state yoq otmena qiling")
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ok no problem\n {AddProduct.texts[previous.state]}")
            return
        previous = step


@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        if 4 >= len(message.text) >= 150:
            await message.answer(
                "150 dan kichik 4 dan katta bolishi kk"
            )
            return

        await state.update_data(name=message.text)
    await message.answer("add description")
    await state.set_state(AddProduct.description)


@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    await message.answer("Error")


@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        if 4 >= len(message.text):
            await message.answer(
                "Soz juda qisqa. \n Iltimos, qayta kiriting"
            )
            return
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name: str(category.id) for category in categories}
    await message.answer("Kategoriyani tanlang", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)


@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer("Siz noto‘g‘ri ma’lumotlarni kiritdingiz, mahsulot description matnini kiriting")


@admin_router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in (category.id for category in await orm_get_categories(session)):
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Tovar narxini kiriting")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Kategoriyani tugmadan tanlang")
        await callback.answer()


@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Tugmalardan toifani tanlang.'")


@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("To'g'ri narx qiymatini kiriting")
            return

        await state.update_data(price=message.text)
    await message.answer("Mahsulot rasmini yuklang")
    await state.set_state(AddProduct.image)


@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer("Siz noto'g'ri ma'lumotlarni kiritdingiz, mahsulot narxini kiriting.")


@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Oziq-ovqat fotosuratini yuboring")
        return
    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Mahsulot qo'shildi/o'zgartirildi", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Error: \n{str(e)}\nDasturchi bilan bog'laning, u yana pul istaydi",
            reply_markup=ADMIN_KB,
        )
        await state.clear()
    # await message.answer(str(data))
    AddProduct.product_for_change = None


@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Отправьте фото пищи")
