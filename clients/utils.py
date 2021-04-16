from datetime import datetime, timedelta
from calendar import HTMLCalendar
from clients.models import Event
from .models import Booking


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        d = ''
        for event in events_per_day:
            d += f'<li> {event.get_html_url} </li>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = Event.objects.filter(
            start_time__year=self.year, start_time__month=self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal


class CalendarBooking(HTMLCalendar):
    def __init__(self, year = None, month = None):
        self.year = year
        self.month = month
        super(CalendarBooking,self).__init__()

    def formatday(self, day, events):
        #queryset com todos os dias que tem evento
        event_per_day = events.filter(check_in__day = day)
        #event_check_out = events.filter(check_out__day = event_per_day.check_out)
        for event in event_per_day:
            print(event.check_out.strftime("%H:%M"))
        #print(event_per_day)
        d = ''
        c = ''
        for event in event_per_day:
            d += f'{event.get_html_url}'
            
            #print(d)
            

        if day != 0:
            return f"<td><span class = 'date'> {day} </span> <ul>{d}</ul> </td>"
        
        return '<td></td>'
    
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday, in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'
    
    def formatmonth(self, withyear = True):
        events = Booking.objects.filter(check_in__year = self.year, check_out__month = self.month)

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal
		
        

