from django.contrib import admin

from .models import City, CitySearchResult, Forecast


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("ref", "name", "latitude", "longitude", "country_code")


@admin.register(CitySearchResult)
class CitySearchResultAdmin(admin.ModelAdmin):
    list_display = ("city", "search")


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = (
        "city",
        "timestamp",
        "description",
        "temperature",
        "pressure",
        "humidity"
    )

    list_filter = (
        "city",
    )
