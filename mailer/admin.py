from django.contrib import admin

# Register your models here.
from .models import EmailTemplate, MessageTemplate


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject')
    list_filter = []
    search_fields = ['name', 'subject', 'msg_text']
    save_as = True
    # inlines = [ArtworkInline,]
    # exclude = ('artworks',)
    # change_form_template = "admin/artwork/change_form_collection.html",
    # form = CollectionAdminForm


admin.site.register(EmailTemplate, EmailTemplateAdmin)


class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'msg', 'owner', 'active')
    list_filter = ['active']
    search_fields = ['msg']
    save_as = True


admin.site.register(MessageTemplate, MessageTemplateAdmin)
