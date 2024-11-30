from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime, timedelta



class TaskCalendar(SimpleCalendar):
    def __init__(self, task_dates: dict):
        
        self.task_dates = task_dates  
    
    async def _get_days_kb(self, year: int, month: int) -> InlineKeyboardMarkup:
        
        kb = InlineKeyboardMarkup(row_width=7)
        month_days = self._get_month_days(year, month)
        
        for week in month_days:
            buttons = []
            for day in week:
                if day:
                    
                    date_str = datetime(year, month, day).strftime("%Y-%m-%d")
                    button_text = str(day)

                    
                    if date_str in self.task_dates:
                        button_text += " 📌"  

                    buttons.append(InlineKeyboardButton(
                        button_text,
                        callback_data=SimpleCalendarCallback(action="DAY", year=year, month=month, day=day).pack()
                    ))
                else:
                    buttons.append(InlineKeyboardButton(" ", callback_data="IGNORE"))

            kb.row(*buttons)

        
        kb.row(
            InlineKeyboardButton("<<", callback_data=SimpleCalendarCallback(action="PREV-MONTH", year=year, month=month).pack()),
            InlineKeyboardButton(">>", callback_data=SimpleCalendarCallback(action="NEXT-MONTH", year=year, month=month).pack())
        )
        return kb