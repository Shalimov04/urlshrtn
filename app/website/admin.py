from django.contrib import admin
from .models import OuterUrl, ShortenedUrl, Conversion


admin.site.register(OuterUrl)
admin.site.register(ShortenedUrl)

class ConversionAdmin(admin.ModelAdmin):
    fields = ('shortened_url', 'timestamp', 'data')
    list_display = ('shortened_url', 'timestamp')
    search_fields = ['shortened_url__path']

admin.site.register(Conversion, ConversionAdmin)
