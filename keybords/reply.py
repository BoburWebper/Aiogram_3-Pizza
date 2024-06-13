from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_keyboards(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple[int] = (2,),
):
    """
    get_keyboards(
        "Menu",
        "Savat",
        "Tolov turi",
        "Nomer yuborish",
        placeholder="writte messege",
        request_contact=4,
        sizes=(2, 2, 1)
    )
    """

    keyboard = ReplyKeyboardBuilder()
    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))
    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder
    )


start_key = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Menu"),
            KeyboardButton(text="Savat"),
        ],
        {
            KeyboardButton(text="Shipping"),
            KeyboardButton(text="Payment"),
        },
    ],
    resize_keyboard=True,
    input_field_placeholder='Choose one of them!',
)

del_kbrd = ReplyKeyboardRemove()

start_key1 = ReplyKeyboardBuilder()

start_key1.add(
    KeyboardButton(text="Menu"),
    KeyboardButton(text="Savat"),
    KeyboardButton(text="Shipping"),
    KeyboardButton(text="Payment"),
)
start_key1.adjust(2, 2)

start_key2 = ReplyKeyboardBuilder()
start_key2.attach(start_key1)  # ikkita keybordni qoshish
start_key2.row(
    KeyboardButton(text="Address"),  # qoshimcha keyboard qoshish
)

test_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Javob olish", request_poll=KeyboardButtonPollType())
        ],
        [
            KeyboardButton(text='Contact', request_contact=True),
            KeyboardButton(text="Location", request_location=True),
        ],
    ],
    resize_keyboard=True,

)
