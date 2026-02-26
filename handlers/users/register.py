from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.db_api.sqllite import DB


router = Router()


class RegisterStates(StatesGroup):
    role = State()

    student_full_name = State()
    student_age = State()
    student_phone = State()
    student_group = State()

    teacher_full_name = State()
    teacher_age = State()
    teacher_phone = State()
    teacher_subject = State()

    confirm_inline = State()
    final_confirm = State()


def get_role_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="O'quvchi"),
                KeyboardButton(text="O'qituvchi"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_yes_no_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Ha"),
                KeyboardButton(text="Yo'q"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_inline_confirm_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="Tasdiqlash", callback_data="inline_confirm")
    kb.adjust(1)
    return kb.as_markup()


@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    """
    Yangi foydalanuvchini (o'quvchi yoki o'qituvchi) ro'yxatdan o'tkazish.
    """
    await state.clear()
    await state.update_data(mode="new")
    await state.set_state(RegisterStates.role)
    await message.answer(
        "Ro'yxatdan o'tish uchun rolni tanlang:",
        reply_markup=get_role_kb(),
    )


@router.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    """
    Foydalanuvchining o'z ma'lumotlarini tahrirlash.
    """
    row = await DB.execute(
        sql="""
        SELECT id, role, full_name, age, phone, group_name, subject
        FROM persons
        WHERE tg_id = ?
        """,
        parameters=(message.from_user.id,),
        fetchone=True,
    )

    if not row:
        await message.answer(
            "Siz hali ro'yxatdan o'tmagansiz. Avval /register orqali ro'yxatdan o'ting."
        )
        return

    _, role, full_name, age, phone, group_name, subject = row

    text = "Hozirgi ma'lumotlaringiz:\n\n"
    text += f"Rol: {'O\'quvchi' if role == 'student' else 'O\'qituvchi'}\n"
    text += f"F.I.Sh: {full_name}\n"
    if age is not None:
        text += f"Yosh: {age}\n"
    if phone:
        text += f"Telefon: {phone}\n"
    if role == "student" and group_name:
        text += f"Sinf/Guruh: {group_name}\n"
    if role == "teacher" and subject:
        text += f"Fan: {subject}\n"

    text += "\nEndi yangilangan ma'lumotlarni qayta kiriting."

    await state.clear()
    await state.update_data(mode="edit", db_id=row[0])
    await state.set_state(RegisterStates.role)
    await message.answer(text)
    await message.answer(
        "Qaysi rolda ro'yxatdan o'tmoqchisiz?",
        reply_markup=get_role_kb(),
    )


@router.message(RegisterStates.role)
async def choose_role(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "O'quvchi":
        await state.update_data(role="student")
        await state.set_state(RegisterStates.student_full_name)
        await message.answer("O'quvchi F.I.Sh ni kiriting:")
    elif text == "O'qituvchi":
        await state.update_data(role="teacher")
        await state.set_state(RegisterStates.teacher_full_name)
        await message.answer("O'qituvchi F.I.Sh ni kiriting:")
    else:
        await message.answer(
            "Iltimos, tugmalar orqali tanlang: 'O'quvchi' yoki 'O'qituvchi'.",
            reply_markup=get_role_kb(),
        )


# --------- O'QUVCHI KETMA-KETLIGI ---------

@router.message(RegisterStates.student_full_name)
async def student_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegisterStates.student_age)
    await message.answer("Yoshingizni kiriting:")


@router.message(RegisterStates.student_age)
async def student_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Yosh faqat son bo'lishi kerak, qaytadan kiriting:")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(RegisterStates.student_phone)
    await message.answer("Telefon raqamingizni kiriting (+998...):")


@router.message(RegisterStates.student_phone)
async def student_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(RegisterStates.student_group)
    await message.answer("Qaysi sinf/guruhda o'qiysiz? (masalan: 9-A, Python-1):")


@router.message(RegisterStates.student_group)
async def student_group(message: Message, state: FSMContext):
    await state.update_data(group_name=message.text.strip())
    data = await state.get_data()

    text = (
        "Quyidagi ma'lumotlar kiritildi:\n\n"
        f"Rol: O'quvchi\n"
        f"F.I.Sh: {data['full_name']}\n"
        f"Yosh: {data['age']}\n"
        f"Telefon: {data['phone']}\n"
        f"Sinf/Guruh: {data['group_name']}\n\n"
        "Agar hammasi to'g'ri bo'lsa, quyidagi 'Tasdiqlash' tugmasini bosing."
    )

    await state.set_state(RegisterStates.confirm_inline)
    await message.answer(text, reply_markup=get_inline_confirm_kb())


# --------- O'QITUVCHI KETMA-KETLIGI ---------

@router.message(RegisterStates.teacher_full_name)
async def teacher_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(RegisterStates.teacher_age)
    await message.answer("Yoshingizni kiriting:")


@router.message(RegisterStates.teacher_age)
async def teacher_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Yosh faqat son bo'lishi kerak, qaytadan kiriting:")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(RegisterStates.teacher_phone)
    await message.answer("Telefon raqamingizni kiriting (+998...):")


@router.message(RegisterStates.teacher_phone)
async def teacher_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(RegisterStates.teacher_subject)
    await message.answer("Qaysi fan bo'yicha dars berasiz?")


@router.message(RegisterStates.teacher_subject)
async def teacher_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text.strip())
    data = await state.get_data()

    text = (
        "Quyidagi ma'lumotlar kiritildi:\n\n"
        f"Rol: O'qituvchi\n"
        f"F.I.Sh: {data['full_name']}\n"
        f"Yosh: {data['age']}\n"
        f"Telefon: {data['phone']}\n"
        f"Fan: {data['subject']}\n\n"
        "Agar hammasi to'g'ri bo'lsa, quyidagi 'Tasdiqlash' tugmasini bosing."
    )

    await state.set_state(RegisterStates.confirm_inline)
    await message.answer(text, reply_markup=get_inline_confirm_kb())


# --------- TASDIQLASH BOSQICHLARI ---------

@router.callback_query(RegisterStates.confirm_inline, F.data == "inline_confirm")
async def inline_confirm(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RegisterStates.final_confirm)
    await callback.message.edit_text(
        "Aniq tasdiqlansinmi?\n\n"
        "Agar ma'lumotlar to'g'ri bo'lsa, 'Ha' tugmasini bosing.\n"
        "Agar xato bo'lsa, 'Yo'q' tugmasini bosing va qaytadan /register yuboring."
    )
    await callback.message.answer(
        "Tanlang:",
        reply_markup=get_yes_no_kb(),
    )
    await callback.answer()


@router.message(RegisterStates.final_confirm)
async def final_confirm(message: Message, state: FSMContext):
    text = message.text.strip().lower()
    if text not in ["ha", "yo'q", "yoq"]:
        await message.answer(
            "Iltimos, 'Ha' yoki 'Yo'q' tugmasini bosing.",
            reply_markup=get_yes_no_kb(),
        )
        return

    if text in ["yo'q", "yoq"]:
        await state.clear()
        await message.answer("Ma'lumotlar saqlanmadi. Qayta boshlash uchun /register yuboring.")
        return

    # "Ha" bo'lsa – bazaga saqlaymiz (yangi yoki tahrir)
    data = await state.get_data()

    role = data["role"]
    tg_id = message.from_user.id
    full_name = data["full_name"]
    age = data["age"]
    phone = data["phone"]
    group_name = data.get("group_name")
    subject = data.get("subject")

    mode = data.get("mode", "new")

    if mode == "edit":
        db_id = data["db_id"]
        await DB.execute(
            sql="""
            UPDATE persons
            SET role = ?, full_name = ?, age = ?, phone = ?, group_name = ?, subject = ?
            WHERE id = ?
            """,
            parameters=(role, full_name, age, phone, group_name, subject, db_id),
            commit=True,
        )
        await message.answer("Ma'lumotlaringiz muvaffaqiyatli yangilandi.")
    else:
        await DB.execute(
            sql="""
            INSERT INTO persons (tg_id, role, full_name, age, phone, group_name, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            parameters=(
                tg_id,
                role,
                full_name,
                age,
                phone,
                group_name,
                subject,
            ),
            commit=True,
        )
        await message.answer("Ma'lumotlaringiz muvaffaqiyatli saqlandi. Rahmat!")

    await state.clear()

