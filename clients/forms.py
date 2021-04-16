from django.views.generic import CreateView
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from clients.models import Client, Modalidade, Boat, Profile,Booking
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)


class ClientUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Client
        fields = ['name', 'email', 'gender', 'birthday',
                  'country', 'phone', 'nIF', 'balance', 'debt', 'discount', 'notes']


class ClientFilterForm(forms.Form):
    idOrder = forms.ChoiceField(
        choices=(
            ("------", "------"),
            ("descending", "Descending"),
            ("ascending", "Ascending")
        ),
        label='Id Order')

    balance = forms.ChoiceField(
        choices=(
            ("------", "------"),
            ("descending", "Descending"),
            ("ascending", "Ascending")
        ),
        label='Balance')

    debt = forms.ChoiceField(
        choices=(
            ("------", "------"),
            ("descending", "Descending"),
            ("ascending", "Ascending")
        ),
        label='Debt')

    discount = forms.ChoiceField(
        choices=(
            ("------", "------"),
            ("descending", "Descending"),
            ("ascending", "Ascending")
        ),
        label='Discount')

    class Meta:
        fields = ('idOrder', 'balance', 'debt', 'discount')


class SessionFilterForm(forms.Form):

    payed = forms.ChoiceField(
        choices=(
            ("All", "------"),
            ("True", "yes"),
            ("False", "no"),
        ),
        label='Payed',
    )

    time = forms.ChoiceField(
        choices=(
            ("indifferent", "------"),
            ("ascending", "Ascending"),
            ("descending", "Descending"),
        ),
        label='Time'
    )

    sessionOrder = forms.ChoiceField(
        choices=(
            ("descending", "Descending"),
            ("ascending", "Ascending")
        ),
        label='Session Order')

    choicesModalidade = [("All", "------")]
    choicesDiver = [("All", "------")]
    choicesInstruct = [("All", "------")]
    choicesBoat = [("All", "------")]

    modalidades_qs = []
    driver_qs = []
    instructor_qs = []
    boat_qs = []

    try:
        modalidades = Modalidade.objects.all()
        print(modalidades)
        modalidades_qs = modalidades

        drivers = Profile.objects.all()
        print(drivers)
        driver_qs = drivers

        instructors = Profile.objects.all()
        print(instructors)
        instructor_qs = instructors

        boats = Boat.objects.all()
        print(boats)
        boat_qs = boats

    except Exception:
        print("tabela nao existe")
    else:
        print("chegou")

    print(modalidades_qs)
    for modalidade in modalidades_qs:
        choicesModalidade.append((modalidade.name, modalidade.name))

    modality = forms.ChoiceField(
        choices=choicesModalidade,
        label='Modality')

    for driver in driver_qs:
        if driver.driver == True:
            choicesDiver.append((driver.firstName, driver.firstName))

    driver = forms.ChoiceField(
        choices=choicesDiver,
        label='Driver')

    for instructor in instructor_qs:
        if instructor.instructor == True:
            choicesInstruct.append(
                (instructor.firstName, instructor.firstName))

    instructor = forms.ChoiceField(
        choices=choicesInstruct,
        label='Instructor')

    for boat in boat_qs:
        choicesBoat.append((boat.name, boat.name))

    boat = forms.ChoiceField(
        choices=choicesBoat,
        label='Boat')


class Meta:
    fields = ('sessionOrder', 'payed', 'modality',
              'driver', 'instructor', 'boat', 'time')


##Booking Stuff

class AvailabilityForm(forms.Form):
    check_in = forms.DateTimeField(required=True, input_formats=["%Y-%m-%dT%H:%M", ] )
    check_out = forms.DateTimeField(required=True, input_formats=["%Y-%m-%dT%H:%M", ] )
    

class EventFormBooking(ModelForm):
    class Meta:
        model = Booking
        # datetime-local is a HTML5 input type, format to make date time show on fields
        widgets = {
            'start_time': model.check_in,
            'end_time': model.check_out,
        }
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EventFormBooking, self).__init__(*args, **kwargs)
        # input_formats parses HTML5 datetime-local input to datetime field
        self.fields['start_time'].input_formats = ('%Y-%m-%dT%H:%M',)
        self.fields['end_time'].input_formats = ('%Y-%m-%dT%H:%M',)