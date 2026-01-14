from django.contrib import admin

from cinema.models import (
    CinemaHall,
    Genre,
    Actor,
    Movie,
    MovieSession,
    Order,
    Ticket,
)


class TicketInLine(admin.TabularInline):
    model = Ticket
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInLine]


admin.site.register(CinemaHall)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Movie)
admin.site.register(MovieSession)
admin.site.register(Ticket)
admin.site.register(Order, OrderAdmin)
