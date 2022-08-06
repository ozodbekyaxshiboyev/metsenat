from django.contrib import admin, messages
from .models import Sponsor,Student,StudentSponsor,OTM
from django.core.exceptions import ValidationError
from django.db.models import Sum


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'phone',)
    list_display = ('full_name', 'phone','amount_pay','is_company','status','created_date',)
    list_filter = ('created_date', 'status',)
    readonly_fields = ('created_date',)

    def delete_model(self, request, obj):
        if obj.status == "Tasdiqlangan":
            messages.add_message(request, messages.ERROR, 'Tasdiqlangan homiyni o`chirib bo`lmaydi!!!')
        else:
            super().delete_model(request, obj)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'phone',)
    list_display = ('full_name', 'phone','type_student','amount_contract','otm','created_date',)
    list_filter = ('type_student', 'created_date',)
    readonly_fields = ('created_date',)


@admin.register(StudentSponsor)
class StudentSponsorAdmin(admin.ModelAdmin):
    search_fields = ('student', 'sponsor',)
    list_display = ('student', 'sponsor','amount','created_date',)
    list_filter = ('amount', 'created_date',)
    autocomplete_fields = ('student','sponsor',)
    readonly_fields = ('created_date',)


    # def save_model(self, request, obj, form, change):
    #     if change:
    #         object = StudentSponsor.objects.get(pk=obj.pk)
    #     else:
    #         super().save_model(request, obj, form, change)


@admin.register(OTM)
class OtmAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    list_filter = ('name',)