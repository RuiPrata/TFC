from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.urls import reverse, reverse_lazy
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField
from django.conf import settings 
# Create your models here.

GENDER_CHOICES = (
    ("male", "male"),
    ("female", "female"),
)


class Client(models.Model):
    name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES,
                              max_length=254, blank=True, default=GENDER_CHOICES[0])
    birthday = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True, default="Portugal")
    phone = models.CharField(max_length=12, blank=False)
    nIF = models.CharField(max_length=9, blank=True, validators=[RegexValidator(
        regex='^.{9}$', message='Length has to be 9', code='nomatch')])
    balance = models.FloatField(blank=True, default=0.0)
    debt = models.IntegerField(blank=True, default=0)
    discount = models.IntegerField(blank=True, default=0)
    notes = models.TextField(default="", blank=True)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name

    def get_absolute_url(self):
        return f"/clients/{self.id}/"


class Profile(models.Model):
    """ modelo do staff """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=30, blank=True, default="")
    lastName = models.CharField(max_length=30, blank=True, default="")
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=30, blank=True, default="")
    birthday = models.DateField(null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    driver = models.BooleanField(blank=True, default=False)
    instructor = models.BooleanField(blank=True, default=False)

    def __str__(self):
        return f'{self.user.username}'

    def delete_user(self):
        self.user.delete()

    def get_driver(self):
        if self.driver == True:
            return "yes"
        elif self.driver == False:
            return "no"
        else:
            return "None"

    def get_instructor(self):
        if self.instructor == True:
            return "yes"
        elif self.instructor == False:
            return "no"
        else:
            return "None"

    def get_absolute_url(self):
        return f"/profile/edit/{self.id}/"


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Gender(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name


class Driver(models.Model):
    name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=True)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name


class Modalidade(models.Model):
    name = models.CharField(blank=True, max_length=32, null=False)
    price = models.FloatField(blank=True, null=True)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name

    def getName(self):
        return self.name


class Boat(models.Model):
    name = models.CharField(blank=True, max_length=32, null=False)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name


class Instructor(models.Model):
    name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=254, blank=True)

    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.name


def get_clients():
    return Client.objects.all()


class Event(models.Model):
    client = models.ForeignKey(Client, null=False, blank=False, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=datetime.now())
    end_time = models.DateTimeField(default=datetime.now())
    time = models.IntegerField(default=0, blank=True)
    driver = models.ForeignKey(Profile, null=False, on_delete=models.CASCADE, blank=True, related_name='driverr')
    instructor = models.ForeignKey(Profile, null=False, on_delete=models.CASCADE, blank=True, related_name='instructorr')
    boat = models.ForeignKey(Boat, null=False, on_delete=models.CASCADE, blank=True)
    modality = models.ForeignKey(Modalidade, null=False, on_delete=models.CASCADE, default="")
    price = models.FloatField(blank=True, default=0)
    payed = models.BooleanField(default=False, blank=False)
    grades = models.TextField(blank=True, default="")


    def __str__(self):
        """ String para representar o objeto MyModelName (no site Admin)."""
        return self.client.name

    def getId(self):
        return self.id

    def get_absolute_url(self):
        return f"/event/{self.id}/edit/"

    def get_notes(self):
        if self.grades.__sizeof__ == 0:
            return "None"
        else:
            return self.grades

    def get_payed(self):
        if self.payed == True:
            return "yes"
        elif self.payed == False:
            return "no"

    def hour_auto(self):
        self.end_time = django.utils.timezone.now()
        return self

    @property
    def get_html_url(self):
        url = reverse('event_edit', args=(self.id,))    
        return f'<a href="{url}"> {self.client.name} {self.start_time} {self.end_time}a </a>'




##Booking stuff
class Room(models.Model):

    ROOM_CATEGORIES = ( 
        ('BLU','BLUE'),
        ('VER','GREEN'),
        ('AMA','YELLOW'),
        ('RED','RED'),
        ('SIL','SILVER'),
    
    )

    category = models.CharField(blank = True,max_length=3,choices=ROOM_CATEGORIES)
    descricao_quarto = models.CharField(blank= True, max_length= 32, null=False)
    num_camas = models.IntegerField()
    image = models.ImageField(default='logo.png', upload_to='static/')
    preco = models.IntegerField(default=60)
    def __str__(self):
        return f'{self.category}'
    
    @property
    def get_room_category(self):
        room_categories = dict(self.ROOM_CATEGORIES)
        room_category = room_categories.get(self.category)
        return room_category
    
    @property
    def get_room_color(self):
        if self.category == "VER":
            color = "#32CD32"
            return color 
        elif self.category == "BLU":
            color =  "#87CEFA"
            return color 
        elif self.category == "AMA":
            color =  "#CCCC00"
            return color 
        elif self.category == "RED":
            color =  "#FF0000"
            return color
        elif self.category == "SIL":
            color =  "#A9A9A9"
            return color

    
    @property
    def get_image(self):
        return self.image

class Epoca(models.Model):
    EPOCAS_CHOICES = (
        ("Alta","Alta"),
        ("Baixa","Baixa"),
    )
    epoca = models.CharField(max_length = 20, choices = EPOCAS_CHOICES, default = 'Alta')

    def __str__(self):
        return f'{self.epoca}'
        
        
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    client = models.ForeignKey(Client,on_delete=models.CASCADE, null = True)
    room = models.ForeignKey(Room,on_delete=models.CASCADE)   
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    preco_total = models.IntegerField(default=60)
    epoca = models.ForeignKey(Epoca, on_delete=models.CASCADE, null= True)
    premium = models.BooleanField(default=False, blank= True)

    

    def __str__(self):
        return f' {self.client} has booked {self.room} From {self.check_in.strftime("%d / %m / %Y  %H:%M ")}   To {self.check_out.strftime("%d / %m / %Y  %H:%M ")} epoca: {self.epoca} premium: {self.premium} TOTAL PRICE: {self.preco_total} €'

    def get_room_category(self):
        room_categories = dict(self.room.ROOM_CATEGORIES)
        room_category = room_categories.get(self.room.category)
        return room_category

    def cancel_booking_url(self):
        return reverse_lazy('CancelBookingView', args=[self.pk])

    @property 
    def get_html_url(self):
        url = reverse('CancelBookingView', args=(self.id,))
        return f'<div style="background-color:{self.room.get_room_color};border:1px solid black; margin-bottom: 5px"> <a style="color:black; margin-left: 5em" title = "Cancel Booking"href = "{url}">ID: {self.id} <br> {self.client.name} booked {self.room.get_room_category} {self.check_in.strftime("%H:%M")} <p> {self.preco_total} €</p></a></div>'
