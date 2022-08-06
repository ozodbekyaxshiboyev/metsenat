from django.db import models
from django.core.exceptions import ValidationError as valid_er
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, ProtectedError


def validate_amount(value):
    if value <= 0:
        raise valid_er(
            _('Kiritilayotgan mablag` 0 dan katta bo`lishi kerak!'),
            params={'value': value},
        )
    return value    #todo xatolik bor

def validate_activ(value):
    sponsor = Sponsor.objects.get(pk=value) #admin panelda ishlayapti
    # sponsor = Sponsor.objects.get(pk=value.pk) #restda ishlayapti
    if sponsor.status != 'Tasdiqlangan':
        raise valid_er(
            _('Homiy hali tasdiqlanmagan'),
            params={'value': value},
        )
    return value   #todo xatolik bor


class OTM(models.Model):
    name = models.CharField(max_length=200,unique=True)

    def __str__(self) -> str:
        return self.name


class Sponsor(models.Model):
    CHOICES1 = (
        ('Yangi', 'Yangi'),
        ('Moderatsiyada', 'Moderatsiyada'),
        ('Tasdiqlangan', 'Tasdiqlangan'),
        ('Bekor qilingan', 'Bekor qilingan'),
    )

    CHOICES2 = (
        ('Naqd', 'Naqd'),
        ('Pul o`tkazmasi', 'Pul o`tkazmasi'),
    )

    full_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^998[0-9]{2}[0-9]{7}$',
                                 message="Faqat O`zbekiston mobil raqamlari tasdiqlanadi('+' belgisiz!)")
    phone = models.CharField(_('Telefon raqam'), validators=[phone_regex], max_length=17, unique=True)
    amount_pay = models.FloatField(validators=[validate_amount])
    is_company = models.BooleanField(default=False)
    status = models.CharField(max_length=30, choices=CHOICES1, default='Yangi')
    company_name = models.CharField(max_length=100,blank=True,null=True)
    created_date = models.DateField(auto_now_add=True)
    pay_type = models.CharField(max_length=30,choices=CHOICES2,default=None,blank=True,null=True)

    def clean(self):
        if self.pk:
            sponsor = Sponsor.objects.get(pk=self.pk)
            if (sponsor.status == "Tasdiqlangan" or sponsor.status == "Moderatsiyada") and self.status == "Yangi":
                raise valid_er("Statusni dastlabki holatga qaytarib bo`lmaydi!")
        if self.is_company and self.company_name is None:
            raise valid_er("Korxona nomi kiritilmadi")
        if self.is_company is False and self.company_name:
            raise valid_er("Bu homiy yuridik shaxs emas! Korxona nomini kiritmang!")
        if (self.status == "Yangi" or self.status == "Moderatsiyada") and self.pay_type:
            raise valid_er("Tasdiqlanmagan homiy uchun to`lov turini tanlab bo`lmaydi!")
        if self.status == "Tasdiqlangan" and self.pay_type is None:
            raise valid_er("To`lov turi tanlanmadi!")
        sponsor_all_give = self.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        new_amount = self.amount_pay
        if sponsor_all_give is None:
            sponsor_all_give = 0
        if sponsor_all_give > new_amount:
            name = "Xatolik. Bu homiyning hisobidan yangi kiritilgan mablag`dan ko`proq mablag` homiylikka yo`naltirib bo`lingan!"
            raise valid_er(f"{name} {sponsor_all_give} sum")


    def __str__(self) -> str:
        return self.full_name


class Student(models.Model):
    CHOICES3 = (
        ('bakalavr','Bakalavr'),
        ('magistr','Magistr'),
    )

    full_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^998[0-9]{2}[0-9]{7}$',
                                 message="Faqat O`zbekiston mobil raqamlari tasdiqlanadi('+' belgisiz!)!")
    phone = models.CharField(_('Telefon raqam'), validators=[phone_regex], max_length=17, unique=True)
    type_student = models.CharField(max_length=20,choices=CHOICES3)
    amount_contract = models.FloatField(validators=[validate_amount])
    otm = models.ForeignKey(OTM, on_delete=models.PROTECT)
    created_date = models.DateField(auto_now_add=True,editable=True)
    sponsor = models.ManyToManyField(Sponsor,through='StudentSponsor',related_name='student')

    def clean(self):
        student_all_get = self.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
        if student_all_get is None:
            student_all_get = 0
        new_amount = self.amount_contract
        if student_all_get is None:
            sponsor_all_give = 0
        if student_all_get > new_amount:
            name = "Xatolik. Bu talaba yangi kiritilgan mablag`dan oshiqcha sum hisobiga o`tkazilgan"
            raise valid_er(f"{name} {student_all_get} sum")

    def __str__(self) -> str:
        return self.full_name


class StudentSponsor(models.Model):

    student = models.ForeignKey(Student,on_delete=models.PROTECT)
    sponsor = models.ForeignKey(Sponsor,on_delete=models.PROTECT)
    amount = models.FloatField(validators=[validate_amount])
    created_date = models.DateField(auto_now_add=True)

    def clean(self):
        if self.pk:
            object = StudentSponsor.objects.get(pk=self.pk)
            if object.sponsor != self.sponsor:
                raise valid_er("Homiyni o`zgartirish mumkin emas!")
            if object.student != self.student:
                raise valid_er("Talabani o`zgartirish mumkin emas!")
            student_all_get = object.student.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
            sponsor_all_give = object.sponsor.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
            new_amount = self.amount
            last_amount = object.amount
            print(1, last_amount)
            print(2, new_amount)
            if student_all_get is None:
                student_all_get = 0
            if sponsor_all_give is None:
                sponsor_all_give = 0

            errorr: str = ""
            if self.sponsor.status != "Tasdiqlangan":
                errorr += "Tasdqilanmagan homiy hisobidan mablag` ajratilmaydi"
                raise valid_er(errorr)
            if student_all_get - last_amount + new_amount > object.student.amount_contract:
                errorr += "Miqdor talaba kontrak miqdoridan ko`p, "
            if object.sponsor.amount_pay < sponsor_all_give - last_amount + new_amount:
                errorr += "homiyning mablag`i bu o`tkazmaga yetmaydi!"
            if errorr != "":
                raise valid_er(errorr)
        else:
            student_all_get = self.student.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
            sponsor_all_give = self.sponsor.studentsponsor_set.all().aggregate(Sum('amount')).get('amount__sum')
            new_amount = self.amount
            if student_all_get is None:
                student_all_get = 0
            if sponsor_all_give is None:
                sponsor_all_give = 0

            errorr: str = ""
            if self.sponsor.status != "Tasdiqlangan":
                errorr += "Tasdqilanmagan homiy hisobidan mablag` ajratilmaydi"
                raise valid_er(errorr)
            if student_all_get + new_amount > self.student.amount_contract:
                errorr += "Miqdor talaba kontrak miqdoridan ko`p, "
            if self.sponsor.amount_pay < sponsor_all_give + new_amount:
                errorr += "homiyning mablag`i bu o`tkazmaga yetmaydi!"
            if errorr != "":
                raise valid_er(errorr)


    def __str__(self) -> str:
        return f"{self.student} | {self.sponsor}"