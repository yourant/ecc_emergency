from django.urls import path

from apps.emergency.kafkadata.views import consumer_poll, overtime, omnibus, \
    fault_location, handle_database

urlpatterns = [
    path("poll", consumer_poll),
    path("overtime", overtime),
    path("omnibus", omnibus),
    path("fault", fault_location),
    path("db", handle_database),
]
