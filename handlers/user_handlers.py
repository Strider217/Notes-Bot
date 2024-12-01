from aiogram import F, Router
from aiogram.filters import Command,StateFilter
from aiogram.types import Message
from keyboards import main_kb, del_kb
from dictionary import dict_ru
from aiogram_calendar import SimpleCalendar,SimpleCalendarCallback 
from aiogram.types import CallbackQuery
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData

rt = Router()

tasks = {}


class FSM_calendar(StatesGroup):
    select_date = State()
    write_task = State()
    select_date_for_del = State()
    select_task = State()





@rt.message(Command(commands = 'start'))
async def start_command(msg: Message):
    await msg.answer(text=f'Привет, {msg.chat.first_name}.\n'
                     'Этот бот предназначет для людей, которые'
                     'не хотят ебланить. Для более подробной'
                     'информации напишите /help \n\n'
                     '1. Записать новую задачу\n'
                     '2. Просмотр активных задач\n'
                     '3. Открыть календарь',reply_markup = main_kb)

    

@rt.message(Command(commands = 'help'))
async def help_command(msg: Message):
    await msg.answer(text = 'Тебе тут не помогут')


@rt.message(Command(commands = 'cancel'),~StateFilter(default_state))
async def cancel_command(msg:Message, state:FSMContext):
    await msg.answer(text = 'Вы вышли из состояния ввода задачи.' 
                     'Чтобы заполнить снова, нажмите кнопку "✍️"\n'
                     '1. Записать новую задачу\n'
                     '2. Просмотр активных задач\n'
                     '3. Открыть календарь', reply_markup = main_kb)
    await state.clear()


@rt.message((F.text == '✍️'), StateFilter(default_state))
async def process_button_write_task(msg: Message, state: FSMContext):
    await msg.answer(text = "Выберите дату для установки задачи",reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(FSM_calendar.select_date)



@rt.callback_query(SimpleCalendarCallback.filter(),StateFilter(FSM_calendar.select_date))
async def process_simple_calendar(callback_query: CallbackQuery,callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query,callback_data)
    if selected:
           
        await state.update_data(sel_date = f'{date.strftime("%d.%m.%Y")}')
        await callback_query.message.answer(text = f'Дата {date} выбрана. Теперь напишите вашу задачу')
        await state.set_state(FSM_calendar.write_task)
        


@rt.message(StateFilter(FSM_calendar.select_date))
async def not_select(msg:Message):
    await msg.answer(text = 'Выберите дату для установки/удаления задачи. Для прерывания выбора напишите /cancel',reply_markup=await SimpleCalendar().start_calendar())


@rt.message(StateFilter(FSM_calendar.write_task))
async def process_write_task(msg:Message,state = FSMContext):
    
    data = await state.get_data()
    date = data['sel_date']

    if msg.from_user.id not in tasks:
        tasks[msg.from_user.id] = {}
    if date not in tasks[msg.from_user.id]:
        tasks[msg.from_user.id][date] = [msg.text]
    else:
        tasks[msg.from_user.id][date].append(msg.text)

    await msg.answer('Задача сохранена. Скорейшего выполнения!')
    await state.clear()
    await msg.answer(text = 'Для просмотра активных задач нажмите на кнопку "👀"\n'
                     '1. Записать новую задачу\n'
                     '2. Просмотр активных задач\n'
                     '3. Открыть календарь', reply_markup = main_kb) 
    

@rt.message(F.text == '🔙')
async def back_button(msg:Message):
    await msg.answer(text = '1. Записать новую задачу\n'
                            '2. Просмотр активных задач\n'
                            '3. Открыть календарь',reply_markup=main_kb)


@rt.message((F.text == '❌'),StateFilter(default_state))
async def delete_task(msg:Message,state:FSMContext):
    await msg.answer(text = 'Какую задачу вы хотите удалить?\n'
                            'Выберите дату',reply_markup = await SimpleCalendar().start_calendar())
    await state.set_state(FSM_calendar.select_date_for_del)
    

@rt.callback_query(SimpleCalendarCallback.filter(),StateFilter(FSM_calendar.select_date_for_del))
async def select_date_for_delete(callback_query: CallbackQuery,callback_data: CallbackData, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query,callback_data)
    if selected:
        if date.strftime("%d.%m.%Y") in tasks[callback_query.from_user.id]:
                await state.update_data(select_date = f'{date.strftime("%d.%m.%Y")}')
                await callback_query.message.answer(text = f'Дата {date} выбрана. Введите номер задачи для удаления')
                await state.set_state(FSM_calendar.select_task)
        else:
            await callback_query.message.answer('На эту дату заметок нет.\nПопробуйте снова.', reply_markup = await SimpleCalendar().start_calendar())




@rt.message(F.text.isdigit(),StateFilter(FSM_calendar.select_task))
async def select_task_for_delete(msg:Message,state:FSMContext):
    data = await state.get_data()
    date = data['select_date']

    # for date, tasks_list in tasks[msg.from_user.id].items():
    #     for task in tasks_list:
    #         if msg.text in task:
    del tasks[msg.from_user.id][date][(int(msg.text)-1)]
    if len(tasks[msg.from_user.id][date])==0:
        del tasks[msg.from_user.id][date]
    await msg.answer('Задача удалена.')
    await state.clear()
    await msg.answer(text = 'Для просмотра активных задач нажмите на кнопку "👀"\n'
                     '1. Записать новую задачу\n'
                     '2. Просмотр активных задач\n'
                     '3. Открыть календарь', reply_markup = main_kb)


@rt.message(F.text,StateFilter(FSM_calendar.select_task))
async def not_select_number(msg:Message):
    await msg.answer(text = 'Введите номер задачи для удаления. Для прерывания выбора напишите /cancel')



@rt.message(F.text == '👀')
async def open_task(msg:Message):
        
    if msg.from_user.id not in tasks or len(tasks[msg.from_user.id])<1:
        await msg.answer(text = 'У вас пока нет активных задач')
    else:
        response = "Ваши задачи:\n"
        for date, task_list in tasks[msg.from_user.id].items():     
            response += '\n'f'- {date}\n'
            response += '\n'.join([f'{(list(tasks[msg.from_user.id][date]).index(task))+1}) {task}' for task in task_list])
        await msg.answer(response)
        await msg.answer(text = dict_ru['buttons_del_active_task'],reply_markup = del_kb)



@rt.message(F.text == '🗓️')
async def open_calendar(msg: Message):
    await msg.answer(text = "Календарь с вашими задачами",reply_markup=await SimpleCalendar().start_calendar())
    await msg.answer(text = dict_ru['buttons_menu'],reply_markup = main_kb)

  
